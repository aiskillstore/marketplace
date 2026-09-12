#!/usr/bin/env python3
"""Drive & archive the 77 behavioural self-tests (references/self-test.md).

The 77 self-tests are prompt->expected pairs that only genuinely pass when a
host model chooses to follow the rules; no tool can prove them. This runner
makes them operable and archivable WITHOUT faking a verdict:

  list    - print every case (num / title / prompt / expectations) so you can
            drive host AIs one by one.
  schema  - generate a judgement sheet (markdown) under docs/selftest-run/:
            one row per case with a PASS/PARTIAL/FAIL/? slot for a human to
            fill. Does not populate the verdict.
  archive - given a filled sheet, compute pass/total stats and a content
            fingerprint and emit a dated, reproducible report. The verdict
            column is decided by a human; this tool only tallies + fingerprints.

Honesty: the verdict is human judgement. This tool never marks a case as
passed on its own; it only structures, fingerprints, and archives.

Usage:
  python scripts/selftest-runner.py list
  python scripts/selftest-runner.py schema [--out docs/selftest-run/judgement-<date>.md]
  python scripts/selftest-runner.py archive <sheet.md> [--commit <sha>]
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import pathlib
import re
import sys

import _selftest_parser

ROOT = pathlib.Path(__file__).resolve().parent.parent
SELF = ROOT / "references" / "self-test.md"
SHEETS_DIR = ROOT / "docs" / "selftest-run"

ALLOWED = {"PASS", "PARTIAL", "FAIL", "?"}


def _cell(s: str) -> str:
    """Make a string safe for one markdown table cell.

    The archive parser splits rows on "|" verbatim, so an unescaped pipe in a
    title/fixture would corrupt the sheet AND then mis-split it on re-archive.
    Replace rather than backslash-escape so writer and parser stay in sync.
    """
    return s.replace("|", "/").replace("\n", " ")


def parse() -> list:
    try:
        text = SELF.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        # Structured failure instead of a raw traceback (parity with cmd_archive).
        print("ERROR: self-test.md is not valid UTF-8 -- " + str(exc))
        raise SystemExit(2)
    except OSError as exc:
        print("ERROR: cannot read self-test.md -- " + str(exc))
        raise SystemExit(2)
    # Shared parser (M1): keep this tool and selfcheck.py in lockstep on format.
    cases, malformed = _selftest_parser.parse(text)
    for head in malformed:
        # A silently skipped block would under-count TOTAL CASES with no
        # trace; surface it so formatting drift is visible immediately.
        sys.stderr.write("WARNING: skipped malformed Test header: %r\n" % head[:60])
    out = []
    for c in cases:
        out.append({
            "num": c["num"],
            "title": c["title"],
            "prompt": "\n---\n".join(c["fences"]) if c["fences"] else "",
            "expect": c["expect"],
            "fixture": c["fixture"],
        })
    return out


def cmd_list() -> int:
    cases = parse()
    if not cases:
        print("ERROR: could not parse any cases from " + str(SELF))
        return 2
    for c in cases:
        print("=" * 70)
        print("Test {}: {}".format(c["num"], c["title"]))
        print("PROMPT >>>")
        print(c["prompt"] or "(no prompt captured)")
        if c.get("fixture"):
            print("FIXTURE (pre-supplied truth) >>>")
            print("  - " + c["fixture"])
        print("EXPECT ({} items) >>>".format(len(c["expect"])))
        for e in c["expect"]:
            print("  - " + e)
    print("=" * 70)
    print("TOTAL CASES:", len(cases))
    return 0


def cmd_schema(out: str) -> int:
    cases = parse()
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# Self-Test Judgement Sheet / 自测判定表",
        "",
        "- Generated (UTC): `{}`".format(now),
        "- Source: `references/self-test.md`",
        "- Fill the **判定** column yourself (PASS / PARTIAL / FAIL / ?). The tool",
        "  does not decide behaviour; it only archives what you record.",
        "- To drive a case, run `python scripts/selftest-runner.py list` and copy the",
        "  prompt of the matching Test N into the host AI.",
        "",
        "| # | Title / 标题 | Fixture 预置真相 | Status | 判定 verdict | Evidence / 证据句 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for c in cases:
        lines.append("| {} | {} | {} | ? |  |  |".format(
            c["num"], _cell(c["title"]), _cell(c.get("fixture") or "")))
    lines += [
        "",
        "Fill legend (verdict): PASS = host behaved as expected and a human confirmed; PARTIAL =",
        "covered partially / needed a nudge; FAIL = did not; ? = not tested yet (ranked as",
        "NOT RUN, never as passed).",
        "",
        "Status legend (orthogonal to verdict): RULE-ONLY = a pure rule statement, not a scripted",
        "scenario; EXAMPLE = an illustrative case; FIELD-TESTED = actually executed with recorded",
        "evidence; ?/blank = not yet classified. Defaults to ?. Never mark FIELD-TESTED without a",
        "recorded run.",
        "",
        "Fixture 预置真相：注明该测试需要的预置工作准备（如预置项目 / 预置 git 状态 / 已知通过数），不同宿主上结果才可比；空则为无需预置。",
    ]
    dest = pathlib.Path(out if out else SHEETS_DIR / ("judgement-" + now[:10] + ".md"))
    if not dest.is_absolute():
        dest = ROOT / dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    # LF is pinned via open(newline=): Path.write_text gained newline= only in
    # Python 3.10 and CI runs 3.9 -- the open() form works on every version.
    with dest.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))
    print("judgement sheet written:", dest)
    return 0


def _verdict_index(text: str) -> int:
    """Locate the verdict column by header, not by hardcoded position.

    The generated sheet has 6 columns and verdict at index 4; a hardcoded
    cols[2] would read the Fixture column and silently tally zero verdicts.
    Headerless/legacy sheets fall back to index 2.
    """
    for line in text.splitlines():
        if line.startswith("| #"):
            cols = [x.strip().lower() for x in line.strip("|").split("|")]
            for i, c in enumerate(cols):
                if "verdict" in c or "判定" in c:
                    return i
            break
    # L1: the fallback exists for legacy 3-column sheets; on the current
    # 6-column layout index 2 would silently tally the wrong column.
    sys.stderr.write("WARNING: verdict column not found in header; falling back to index 2\n")
    return 2


def cmd_archive(sheet: str, commit: str) -> int:
    p = pathlib.Path(sheet)
    if not p.is_absolute():
        p = ROOT / p
    try:
        text = p.read_text(encoding="utf-8")
    except FileNotFoundError:
        print("ERROR: sheet not found: " + str(p))
        return 2
    except UnicodeDecodeError as exc:
        print("ERROR: sheet is not valid UTF-8 -- " + str(exc))
        return 2
    vidx = _verdict_index(text)
    rows = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cols = [x.strip() for x in line.strip("|").split("|")]
        if len(cols) < 3:
            continue
        try:
            num = int(cols[0])
        except ValueError:
            continue
        verdict = cols[vidx] if len(cols) > vidx else ""
        rows.append({"num": num, "title": cols[1], "verdict": verdict})
    if not rows:
        print("ERROR: no data rows found in " + str(p))
        return 2
    human = [r["verdict"] for r in rows]
    decided = sum(1 for v in human if v in {"PASS", "PARTIAL", "FAIL"})
    pass_n = sum(1 for v in human if v == "PASS")
    partial_n = sum(1 for v in human if v == "PARTIAL")
    fail_n = sum(1 for v in human if v == "FAIL")
    open_n = sum(1 for v in human if v == "?" or v == "")
    # column must be one of allowed; anything else is a parse warning
    unknown = {v for v in human if v and v not in ALLOWED}
    fingerprint = hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rate = (pass_n + partial_n) / decided if decided else 0.0
    report = [
        "# Self-Test Run Report / 自测运行报表",
        "",
        "- Source sheet: `{}`".format(str(p)),
        "- Commit / label: `{}`".format(commit or "local"),
        "- Time (UTC): `{}`".format(now),
        "- Cases tallied: {}".format(len(rows)),
        "- PASS: {} · PARTIAL: {} · FAIL: {} · open(/?): {}".format(
            pass_n, partial_n, fail_n, open_n),
        "- Decided (human): {} / {}".format(decided, len(rows)),
        "- Effective pass rate (PASS+PARTIAL)/decided: {:.0%}".format(rate),
        "- Fingerprint: `{}`".format(fingerprint),
        "",
        "> Verdicts come from a human-filled sheet. '?' / blank = NOT RUN, and is",
        "> NEVER counted as passed. The fingerprint above lets you reproduce this",
        "> exact report from the archived sheet.",
    ]
    if unknown:
        report.append("WARNING unknown verdict tokens: " + ", ".join(sorted(unknown)))
    out = p.with_name(p.stem + "-report.md")
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(report))
    print("\n".join(report))
    print("report written:", out)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Drive/archive the 77 behavioural self-tests")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("list")
    sp = sub.add_parser("schema")
    sp.add_argument("--out")
    ar = sub.add_parser("archive")
    ar.add_argument("sheet")
    ar.add_argument("--commit", default="")
    args = ap.parse_args()

    if args.cmd == "list":
        return cmd_list()
    if args.cmd == "schema":
        return cmd_schema(args.out)
    if args.cmd == "archive":
        return cmd_archive(args.sheet, args.commit)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())