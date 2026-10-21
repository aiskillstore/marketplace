from __future__ import annotations
import ast
import os
import re
import shutil
import subprocess
import sys

from .models import Probe, TestRecord, Finding
from .ast_utils import walk_no_nested_funcs, call_name, split_lines_keepends
from .discovery import SKIP_DIRS, SHADOW_PREFIX, is_test_filename

REVEAL_RE = re.compile(r'^(.*?):(\d+):(?:\d+:)?\s*note: Revealed type is "(.*)"\s*$')
ANY_RETURN_RE = re.compile(r'^(.*?):(\d+):(?:\d+:)?\s*(?:error|warning):.*\[no-any-return\]\s*$')

def strip_generics(t: str) -> str:
    return t.split("[", 1)[0]


def base_name(t: str) -> str:
    t = t.strip().rstrip("*").strip('"')
    if t.startswith("Literal["):
        inner = t[len("Literal["):-1]
        if inner and (inner[0] in "'\""):
            return "str"
        if inner in ("True", "False"):
            return "bool"
        if re.fullmatch(r"-?\d+", inner):
            return "int"
        return "Literal"
    t = strip_generics(t)
    return t.split(".")[-1]


def union_members(t: str) -> list[str]:
    t = t.strip().rstrip("*")
    if t.startswith("Union[") and t.endswith("]"):
        inner, out, depth, cur = t[6:-1], [], 0, ""
        for ch in inner:
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
            if ch == "," and depth == 0:
                out.append(cur.strip())
                cur = ""
            else:
                cur += ch
        out.append(cur.strip())
        return out
    if " | " in t:
        # split on top-level pipes only
        out, depth, cur = [], 0, ""
        for ch in t:
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
            if ch == "|" and depth == 0:
                out.append(cur.strip())
                cur = ""
            else:
                cur += ch
        out.append(cur.strip())
        return out
    if t.startswith("Optional[") and t.endswith("]"):
        return [t[9:-1].strip(), "None"]
    return [t]


def enclosing_function_names(sites: set[tuple[str, int]]) -> set[str]:
    """Map (file, line) sites to the names of their enclosing functions."""
    names: set[str] = set()
    by_file: dict[str, list[int]] = {}
    for f, ln in sites:
        by_file.setdefault(f, []).append(ln)
    for f, lns in by_file.items():
        try:
            tree = ast.parse(open(f, encoding="utf-8").read())
        except (OSError, SyntaxError):
            continue
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.end_lineno:
                if any(n.lineno <= ln <= n.end_lineno for ln in lns):
                    names.add(n.name)
    return names


def propagate_laundering(root: str, seed: set[str]) -> set[str]:
    """Grow the Any-laundering function set transitively."""
    if not seed:
        return set()   # nothing to propagate — skip the whole-repo parse
    returns_calls: dict[str, set[str]] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if not fn.endswith(".py") or fn.startswith(SHADOW_PREFIX):
                continue
            try:
                tree = ast.parse(open(os.path.join(dirpath, fn), encoding="utf-8").read())
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                for r in ast.walk(node):
                    if isinstance(r, ast.Return) and r.value is not None:
                        v = r.value
                        if isinstance(v, ast.Await):
                            v = v.value
                        if isinstance(v, ast.Call):
                            cn = call_name(v)
                            if cn:
                                returns_calls.setdefault(node.name, set()).add(cn)

    laundering = set(seed)
    changed = True
    while changed:
        changed = False
        for fname, callees in returns_calls.items():
            if fname not in laundering and (callees & laundering):
                laundering.add(fname)
                changed = True
    return laundering


def run_mypy_probes(probes: list[Probe], root: str,
                    mypy_cmd: list[str] | None) -> tuple[str | None, set[str], bool]:
    """Insert reveal_type() shadow files, run mypy once, map notes back.

    Returns (note, laundering_functions, laundering_visible). laundering_visible
    is False when no source targets could be found for mypy — the Any-laundering
    guard cannot run, so type-guaranteed findings must not be promoted to proven.
    """
    if not probes:
        return None, set(), True
    by_file: dict[str, list[Probe]] = {}
    for p in probes:
        by_file.setdefault(p.file, []).append(p)

    shadow_map = {}   # shadow_path -> {shadow_line: probe}
    shadow_files = []
    skipped_shadow = []   # basenames skipped due to a pre-existing shadow symlink
    try:
        for file, plist in by_file.items():
            src_lines = [l.rstrip("\r\n") for l in split_lines_keepends(
                open(file, encoding="utf-8", newline="").read())]
            plist.sort(key=lambda p: p.line)
            out_lines, li, inserted = [], 0, 0
            line_map = {}
            for p in plist:
                while li < p.line - 1:
                    out_lines.append(src_lines[li])
                    li += 1
                out_lines.append(" " * p.indent + f"reveal_type(({p.expr_src}))")
                inserted += 1
                line_map[len(out_lines)] = p
            out_lines.extend(src_lines[li:])
            shadow = os.path.join(os.path.dirname(file),
                                  SHADOW_PREFIX + os.path.basename(file))
            if os.path.islink(shadow):
                # a pre-existing symlink under the shadow name would be
                # written through — skip this file's probes instead, and
                # record it so the skip is not silent (see note below)
                skipped_shadow.append(os.path.basename(file))
                continue
            with open(shadow, "w", encoding="utf-8") as f:
                f.write("\n".join(out_lines) + "\n")
            shadow_files.append(shadow)
            shadow_map[os.path.abspath(shadow)] = line_map

        cmds = [mypy_cmd] if mypy_cmd else []
        if not cmds:
            if os.path.exists(os.path.join(root, "uv.lock")) and shutil.which("uv"):
                cmds.append(["uv", "run", "mypy"])
            if shutil.which("mypy"):
                cmds.append(["mypy"])
            cmds.append([sys.executable, "-m", "mypy"])

        # mypy only reports errors for explicitly-listed targets, so the source
        # tree must be in the run for [no-any-return] laundering detection
        src_targets = []
        if os.path.isdir(os.path.join(root, "src")):
            src_targets.append(os.path.join(root, "src"))
        else:
            for d in sorted(os.listdir(root)):
                if d in SKIP_DIRS or d.startswith(".") or d in ("tests", "test"):
                    continue
                if os.path.isfile(os.path.join(root, d, "__init__.py")):
                    src_targets.append(os.path.join(root, d))
        if not src_targets:
            # flat layout: top-level modules are the source tree
            for fn in sorted(os.listdir(root)):
                if fn.endswith(".py") and not fn.startswith(SHADOW_PREFIX) \
                        and not is_test_filename(fn):
                    src_targets.append(os.path.join(root, fn))
        laundering_visible = bool(src_targets)

        proc = None
        usable = False
        for cmd in cmds:
            try:
                proc = subprocess.run(
                    cmd + ["--no-error-summary", "--no-pretty",
                           "--check-untyped-defs",
                           "--warn-return-any",
                           "--show-error-codes",
                           "--show-column-numbers"] + shadow_files + src_targets,
                    cwd=root, capture_output=True, text=True, timeout=600)
                if "Revealed type" in proc.stdout or proc.returncode in (0, 1):
                    if "No module named mypy" in (proc.stderr or "") or "No module named mypy" in (proc.stdout or ""):
                        proc = None
                        continue
                    usable = True
                    break
            except (FileNotFoundError, subprocess.TimeoutExpired):
                proc = None
                continue
        if proc is None:
            return ("mypy not runnable — type-guaranteed checks skipped (install mypy or pass --mypy)",
                    set(), True)
        if not usable:
            # mypy ran but exited >=2 (fatal / bad config / unreadable source).
            # Without this branch every probe keeps revealed=None, resolve_probes
            # quietly reclassifies them as nonredundant, and the whole
            # type-guaranteed category vanishes with no user-facing signal.
            detail = (proc.stderr or proc.stdout or "").strip().splitlines()
            first = detail[0][:200] if detail else f"exit {proc.returncode}"
            return (f"mypy failed ({first}) — type-guaranteed checks skipped", set(), True)

        any_return_sites: set[tuple[str, int]] = set()
        for line in proc.stdout.splitlines():
            m = REVEAL_RE.match(line)
            if m:
                fpath, lno, revealed = os.path.abspath(os.path.join(root, m.group(1))), int(m.group(2)), m.group(3)
                if fpath not in shadow_map:
                    fpath = os.path.abspath(m.group(1))
                probe = shadow_map.get(fpath, {}).get(lno)
                if probe:
                    probe.revealed = revealed
                continue
            m = ANY_RETURN_RE.match(line)
            if m:
                fpath = os.path.abspath(os.path.join(root, m.group(1)))
                if not os.path.exists(fpath):
                    fpath = os.path.abspath(m.group(1))
                any_return_sites.add((fpath, int(m.group(2))))
        seed = enclosing_function_names(any_return_sites)
        note = None
        if not laundering_visible:
            note = ("no source packages or top-level modules found under the project root — "
                    "mypy cannot see the code under test, so the Any-laundering guard is "
                    "unavailable; type-guaranteed findings demoted to advisory")
        if skipped_shadow:
            # don't let the islink skip vanish silently — every other
            # degradation in this module says so
            skip_note = (f"{len(skipped_shadow)} file(s) skipped for type-guaranteed "
                         f"checks — a pre-existing shadow symlink "
                         f"({', '.join(sorted(skipped_shadow))})")
            note = f"{note}; {skip_note}" if note else skip_note
        return note, propagate_laundering(root, seed), laundering_visible
    except OSError as e:
        # e.g. read-only checkout: shadow files cannot be written next to the
        # tests. Degrade to the syntactic categories instead of crashing the
        # whole scan — and say so, like every other degradation path.
        return (f"cannot write reveal_type() shadow files ({e}) — "
                "type-guaranteed checks skipped", set(), True)
    finally:
        for s in shadow_files:
            try:
                os.remove(s)
            except OSError:
                pass


def resolve_probes(probes: list[Probe], records: list[TestRecord], root: str,
                    laundering: set[str] | None = None,
                    laundering_visible: bool = True):
    laundering = laundering or set()
    recs_by_key = {}
    for r in records:
        recs_by_key.setdefault((r.file, r.name), r)

    def touches_laundering(p: Probe, rec: TestRecord) -> bool:
        if not laundering:
            return False
        try:
            expr = ast.parse(p.expr_src, mode="eval").body
        except SyntaxError:
            return True  # can't reason — stay safe
        called = {call_name(n) for n in ast.walk(expr) if isinstance(n, ast.Call)}
        for n in ast.walk(expr):
            if isinstance(n, ast.Name):
                for d in walk_no_nested_funcs(rec.node):
                    if isinstance(d, ast.Assign) and any(
                            isinstance(t, ast.Name) and t.id == n.id for t in d.targets):
                        called |= {call_name(c) for c in ast.walk(d.value) if isinstance(c, ast.Call)}
        return bool((called - {None}) & laundering)

    for p in probes:
        rec = recs_by_key.get((p.file, p.finding_slot[0]))
        if rec is None:
            continue
        a = p.finding_slot[1]
        f = None
        if p.revealed and touches_laundering(p, rec):
            rec.nonredundant += 1
            continue
        if p.revealed:
            members = union_members(p.revealed)
            bad = any(base_name(m) in ("Any", "") for m in members)
            if p.kind == "not-none" and not bad and "None" not in [base_name(m) for m in members]:
                f = Finding(p.file, p.line, rec.name, "type-guaranteed", "proven", "safe",
                            f'mypy already guarantees non-None (revealed type: "{p.revealed}")', node=a)
            elif p.kind == "isinstance" and not bad \
                    and all(base_name(m) in p.extra for m in members):
                f = Finding(p.file, p.line, rec.name, "type-guaranteed", "proven", "safe",
                            f'mypy already guarantees isinstance (revealed type: "{p.revealed}")', node=a)
            elif p.kind == "exact-type" and not bad and len(members) == 1 \
                    and base_name(members[0]) in p.extra:
                f = Finding(p.file, p.line, rec.name, "type-guaranteed", "advisory", "aggressive",
                            f'revealed type is "{p.revealed}", but a subclass instance would still fail type() is — advisory', node=a)
        if f is not None and f.level == "proven" and not laundering_visible:
            # without source targets mypy never emits [no-any-return], so the
            # laundering exemption can't clear this finding — don't auto-delete
            f.level, f.deletable = "advisory", "report-only"
            f.reason += (" — but mypy could not see the source tree, so an Any-laundering "
                         "annotation may be behind this type; verify before removing")
        if f is not None:
            rec.findings.append(f)
        else:
            rec.nonredundant += 1
