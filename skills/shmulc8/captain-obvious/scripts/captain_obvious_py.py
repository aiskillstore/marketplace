#!/usr/bin/env python3
"""
captain-obvious — Python detector

Deterministically finds pytest tests that can never fail or check nothing,
and optionally deletes them.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import shutil
import subprocess
import sys

from co_py.discovery import find_test_files
from co_py.analyzer import analyze_file
from co_py.models import Probe, TestRecord
from co_py.mypy_pass import run_mypy_probes, resolve_probes
from co_py.duplicates import mark_duplicates
from co_py.coverage import load_coverage
from co_py.fixer import apply_fix, plan_removals
from co_py.gitguard import fix_blocker


def single_file(args) -> int:
    """Syntactic-only scan of one file, JSON to stdout.

    Built for write-time hooks: no discovery, no gitguard, no mypy, no
    subprocess, no shadow files — a pure parse of the given content.
    """
    path = os.path.abspath(args.file)
    root = os.path.dirname(path)
    report = {"tool": "captain-obvious/py", "file": path, "mode": "single-file",
              "mypyNote": "type checks skipped (single-file mode is syntactic only)",
              "note": None, "testsScanned": 0, "findings": [], "summary": {}}
    try:
        src = sys.stdin.read() if args.stdin else open(path, encoding="utf-8").read()
        tree = ast.parse(src)
    except (OSError, SyntaxError, UnicodeDecodeError, ValueError) as e:
        report["note"] = f"parse failed — skipped ({e})"
        print(json.dumps(report, indent=2))
        return 0

    probes: list[Probe] = []
    records: list[TestRecord] = []
    analyze_file(path, src, tree, root, probes, records)
    for p in probes:
        p.revealed = None            # the existing --no-types degradation path
    resolve_probes(probes, records, root)
    mark_duplicates(records)

    findings = [f for r in records for f in r.findings]
    for f in findings:
        report["summary"].setdefault(f.category, {"proven": 0, "advisory": 0})[f.level] += 1
    report["testsScanned"] = len(records)
    report["findings"] = [f.to_dict(root) for f in findings]
    print(json.dumps(report, indent=2))
    return 0


def run_check(base: str, root: str, findings: list[dict]) -> int:
    """Report-only CI gate (plan 011): exit 1 iff a proven *syntactic* finding
    is newly introduced (present now, absent in `base`) in a file changed vs
    `base`. Every git failure other than 'file absent in base' fails OPEN
    (stderr note + exit 0) — a gate must never invent a CI failure.

    Base-vs-current findings are keyed on (category, test) — the exact key
    hooks/prevent.py uses (line numbers shift across edits). Shared BY
    CONVENTION; if one keying changes, change both.
    """
    def git(*a, cwd, text=True):
        return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=text)

    def fail_open(msg: str) -> int:
        print(f"captain-obvious: --check could not compare against {base} "
              f"({msg}) — treating as clean (fail-open)", file=sys.stderr)
        return 0

    def clean() -> int:
        print(f"captain-obvious: --check clean — no newly-introduced proven "
              f"findings vs {base}", file=sys.stderr)
        return 0

    if shutil.which("git") is None:
        return fail_open("git not found on PATH")

    top = git("rev-parse", "--show-toplevel", cwd=root)
    if top.returncode != 0:
        return fail_open((top.stderr.strip().splitlines() or ["not a git repository"])[0])
    repo = os.path.realpath(top.stdout.strip())

    # invalid ref → fail open; a valid ref with a file merely absent means NEW
    if git("cat-file", "-e", base, cwd=repo).returncode != 0:
        return fail_open(f"no such ref {base}")

    diff = git("diff", "--name-only", f"{base}...HEAD", cwd=repo)
    if diff.returncode != 0:
        return fail_open((diff.stderr.strip().splitlines() or ["git diff failed"])[0])
    # realpath both sides: on macOS `git` yields /private/var while abspath keeps
    # the /var symlink — un-normalized, the intersection would be silently empty
    changed = {os.path.realpath(os.path.join(repo, p)) for p in diff.stdout.splitlines()}

    def absfile(f) -> str:
        return os.path.realpath(os.path.join(root, f["file"]))

    # syntactic proven only: the base-side scan is single-file (no mypy, no
    # coverage), so categories whose proven status depends on either —
    # type-guaranteed (mypy) and coverage-promoted conditional-assert — can
    # never appear proven on the base side and would over-fire the gate
    candidates = [f for f in findings
                  if f["level"] == "proven"
                  and f["category"] not in ("type-guaranteed", "conditional-assert")
                  and absfile(f) in changed]
    if not candidates:
        return clean()

    seen_by_file: dict[str, set] = {}
    for abs_f in {absfile(f) for f in candidates}:
        rel = os.path.relpath(abs_f, repo).replace(os.sep, "/")
        show = git("show", f"{base}:{rel}", cwd=repo, text=False)
        if show.returncode != 0:
            seen_by_file[abs_f] = set()       # absent in base → the whole file is NEW
            continue
        scan = subprocess.run([sys.executable, __file__, "--file", abs_f, "--stdin"],
                              input=show.stdout, capture_output=True)
        try:
            base_findings = json.loads(scan.stdout)["findings"]
        except (ValueError, KeyError):
            return fail_open(f"base scan of {rel} failed")
        seen_by_file[abs_f] = {(f["category"], f["test"]) for f in base_findings
                               if f.get("level") == "proven"}

    new = [f for f in candidates
           if (f["category"], f["test"]) not in seen_by_file[absfile(f)]]
    if not new:
        return clean()
    for f in new:
        print(f'captain-obvious: NEW proven finding: {f["file"]}:{f["line"]} '
              f'({f["category"]}) "{f["test"]}" — {f["reason"]}', file=sys.stderr)
    return 1


def main():
    if sys.version_info < (3, 9):
        print("captain-obvious: requires Python 3.9+ (this is Python "
              f"{sys.version_info.major}.{sys.version_info.minor}; ast.unparse is missing below 3.9)",
              file=sys.stderr)
        return 2
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=".")
    ap.add_argument("--file", help="scan a single file (syntactic categories only; "
                                   "JSON to stdout; no mypy, no shadow files)")
    ap.add_argument("--stdin", action="store_true",
                    help="with --file: read the file's content from stdin "
                         "(the path is used for naming only)")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--json")
    ap.add_argument("--mypy", help='mypy command, e.g. "uv run mypy"')
    ap.add_argument("--no-types", action="store_true", help="skip the mypy pass")
    ap.add_argument("--coverage", help="coverage file (coverage.py json / lcov / istanbul json): "
                                       "confirm conditional-assert findings against real line coverage")
    ap.add_argument("--force", action="store_true",
                    help="allow --fix on a dirty or non-git tree (no undo path)")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any proven syntactic finding is newly introduced "
                         "vs --base (report-only; implies no writes)")
    ap.add_argument("--base", default=None,
                    help="git ref to compare against for --check (e.g. origin/main)")
    args = ap.parse_args()

    if args.check and args.fix:
        ap.error("--check is report-only — it cannot be combined with --fix")
    if args.check and not args.base:
        ap.error("--check requires --base <ref>")
    if args.stdin and not args.file:
        ap.error("--stdin requires --file")
    if args.file:
        if args.fix:
            ap.error("--fix is not supported with --file (single-file mode is report-only)")
        return single_file(args)

    root = os.path.abspath(args.path)

    if args.fix and not args.force:
        blocker = fix_blocker(root)
        if blocker:
            print(f"captain-obvious: refusing to --fix — {blocker}.\n"
                  "  --fix rewrites test files in place with no backup. Commit or stash\n"
                  "  first so `git checkout -- <files>` can undo it, or pass --force.",
                  file=sys.stderr)
            return 2
    files = find_test_files(root)
    if not files:
        print(f"captain-obvious: no test files (test_*.py / *_test.py) under {root}")
        return 0

    probes: list[Probe] = []
    records: list[TestRecord] = []
    for f in files:
        try:
            src = open(f, encoding="utf-8").read()
            tree = ast.parse(src)
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"  skipping {f}: {e}", file=sys.stderr)
            continue
        analyze_file(f, src, tree, root, probes, records)

    mypy_note = None
    laundering: set[str] = set()
    laundering_visible = True
    if args.no_types:
        for p in probes:
            p.revealed = None
        mypy_note = "type checks skipped (--no-types)"
    else:
        mypy_note, laundering, laundering_visible = run_mypy_probes(
            probes, root, args.mypy.split() if args.mypy else None)
    resolve_probes(probes, records, root, laundering, laundering_visible)

    mark_duplicates(records)

    findings = [f for r in records for f in r.findings]

    # coverage confirmation: turn the static conditional-assert guess into a fact
    cov = load_coverage(args.coverage, root) if args.coverage else None
    cov_promoted, cov_suppressed = 0, 0
    cov_note = None
    cov_warn = None
    if args.coverage and cov is None:
        cov_note = "could not parse coverage (expected coverage.py json / lcov / istanbul json)"
    elif cov is not None:
        covered_files = {f for f, _ in cov}
        inert_files: set[str] = set()
        kept = []
        for f in findings:
            if f.category == "conditional-assert":
                rel = os.path.relpath(f.file, root).replace(os.sep, "/")
                if rel not in covered_files:
                    inert_files.add(rel)
                hits = cov.get((rel, f.line))
                if hits == 0:
                    f.level = "proven"
                    f.reason += (" — coverage confirms it ran 0 times: rotten (ICSE'19). "
                                 "Fix the guard so it fires, or remove it")
                    cov_promoted += 1
                elif hits is not None and hits > 0:
                    cov_suppressed += 1
                    continue  # demonstrably executes — not rotten, drop it
            kept.append(f)
        findings = kept
        if inert_files:
            # coverage configs usually measure only src/ — then test-file lines
            # are absent and this whole mode silently confirms nothing
            cov_warn = (f"coverage data has no lines for {len(inert_files)} test file(s) "
                        f"({', '.join(sorted(inert_files)[:3])}...) — coverage mode is inert "
                        "for them; include test files in coverage collection "
                        "(e.g. run coverage over the whole repo, not just src/)")

    summary: dict[str, dict[str, int]] = {}
    for f in findings:
        summary.setdefault(f.category, {"proven": 0, "advisory": 0})[f.level] += 1

    _, plan = plan_removals(records, root)
    fixed = apply_fix(records, root) if args.fix else None

    report = {
        "tool": "captain-obvious/py",
        "project": root,
        "mypyNote": mypy_note,
        "testFilesScanned": len(files),
        "testsScanned": len(records),
        "findings": [f.to_dict(root) for f in findings],
        "summary": summary,
        "coverage": ({"file": args.coverage, "conditionalAssertsPromoted": cov_promoted,
                      "conditionalAssertsSuppressed": cov_suppressed,
                      "warning": cov_warn} if cov is not None
                     else ({"file": args.coverage, "error": cov_note} if args.coverage else None)),
        "plan": plan,
        "fixed": fixed,
    }
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(report, fh, indent=2)

    print(f"\ncaptain-obvious (py) — {len(records)} tests scanned in {len(files)} files")
    if mypy_note:
        print(f"  note: {mypy_note}")
    print()
    for cat, c in summary.items():
        print(f"  {cat:<20} proven: {c['proven']}  advisory: {c['advisory']}")
    if plan["testsToRemove"] or plan["assertionsToRemove"]:
        print(f"\n  tests fully removable: {len(plan['testsToRemove'])}")
        print(f"  individual assertions removable: {plan['assertionsToRemove']}")
    if cov is not None:
        print(f"  coverage: {cov_promoted} conditional-assert(s) confirmed rotten, "
              f"{cov_suppressed} confirmed reached (dropped)")
        if cov_warn:
            print(f"  coverage warning: {cov_warn}")
    elif cov_note:
        print(f"  coverage: {cov_note}")
    if findings:
        print("\nFindings:")
        for f in findings:
            tag = "PROVEN  " if f.level == "proven" else "ADVISORY"
            print(f"  [{tag}] {os.path.relpath(f.file, root)}:{f.line} ({f.category}) \"{f.test}\"")
            print(f"             {f.reason}")
    if fixed:
        print(f"\nFixed: removed {fixed['testsRemoved']} tests and {fixed['assertionsRemoved']} assertions "
              f"across {fixed['filesChanged']} files.")
        print("Re-run your typechecker and test suite now.")
    if args.check:
        return run_check(args.base, root, report["findings"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
