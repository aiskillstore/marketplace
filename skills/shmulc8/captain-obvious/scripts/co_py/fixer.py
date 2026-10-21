from __future__ import annotations
import ast
import os
import sys

from .models import TestRecord, Finding
from .ast_utils import split_lines_keepends

def _dangling_edits(rec, removed_nodes, lines):
    removed_ids = {id(n) for n in removed_nodes}
    used_in_removed, used_elsewhere = set(), set()
    for stmt in rec.node.body:
        names = {n.id for n in ast.walk(stmt)
                 if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        (used_in_removed if id(stmt) in removed_ids else used_elsewhere).update(names)
    newly_unused = used_in_removed - used_elsewhere
    edits = []
    for stmt in rec.node.body:
        if id(stmt) in removed_ids:
            continue
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 \
                and isinstance(stmt.targets[0], ast.Name):
            v = stmt.targets[0].id
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            v = stmt.target.id
        else:
            continue
        if v not in newly_unused:
            continue
        rhs = stmt.value
        src_line = lines[stmt.lineno - 1]
        indent = " " * (len(src_line) - len(src_line.lstrip()))
        eol = "\r\n" if src_line.endswith("\r\n") else ("\r" if src_line.endswith("\r") else "\n")
        if rhs is not None and any(isinstance(n, ast.Call) for n in ast.walk(rhs)):
            try:
                text = indent + " ".join(ast.unparse(rhs).split()) + eol
            except Exception:
                continue
            edits.append((stmt.lineno, stmt.end_lineno, text))
        else:
            edits.append((stmt.lineno, stmt.end_lineno, None))
    return edits


def plan_removals(records: list[TestRecord], root: str):
    """Decide what plain --fix would remove, without touching any file.

    Returns (edits_by_file, plan) where plan mirrors the TS report's shape:
    {"testsToRemove": [{file, line, test}], "assertionsToRemove": N}.
    """
    edits_by_file: dict[str, list[tuple[int, int, str | None]]] = {}
    file_lines: dict[str, list[str]] = {}
    tests_to_remove: list[dict] = []
    asserts_removed = 0

    def lines_of(f):
        if f not in file_lines:
            file_lines[f] = split_lines_keepends(
                open(f, encoding="utf-8", newline="").read())
        return file_lines[f]

    def want(f: Finding) -> bool:
        return f.deletable == "safe"

    for rec in records:
        if os.path.islink(rec.file):
            # never plan a removal in a symlinked test file — the write would
            # follow the link out of the scanned tree. Excluding it here (not
            # just at the write) keeps the reported counts and the --json plan
            # preview honest about what --fix will actually touch.
            print(f"captain-obvious: skipping {rec.file} — symlinked test files "
                  "are never rewritten (the write would follow the link)",
                  file=sys.stderr)
            continue
        del_nodes = {id(getattr(f.node, "_orig_stmt", f.node)) for f in rec.findings
                     if f.node is not None and want(f)}

        def _trivial(stmt):
            if isinstance(stmt, ast.Pass):
                return True
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                return True  # docstring / bare literal
            if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
                val = stmt.value
                return val is None or not any(
                    isinstance(n, ast.Call) for n in ast.walk(val))
            return False

        whole = False
        if rec.is_duplicate and any(f.category == "duplicate-test" and want(f) for f in rec.findings):
            whole = True
        elif any(f.category in ("never-asserts", "silent-smoke") and want(f) for f in rec.findings):
            whole = True
        else:
            deletable = [f for f in rec.findings if f.node is not None and want(f)
                         and f.category != "dead-assert"]
            if (rec.live_assert_count > 0 and len(deletable) == rec.live_assert_count
                    and rec.nonredundant == 0 and rec.conditional == 0 and rec.helper_asserts == 0):
                whole = all(id(s) in del_nodes or _trivial(s) for s in rec.node.body)

        spans = edits_by_file.setdefault(rec.file, [])
        if whole:
            start = min([d.lineno for d in rec.node.decorator_list] + [rec.node.lineno])
            spans.append((start, rec.node.end_lineno, None))
            tests_to_remove.append({"file": os.path.relpath(rec.file, root),
                                    "line": rec.node.lineno, "test": rec.name})
        else:
            removed_nodes = []
            for f in rec.findings:
                if f.node is not None and want(f):
                    report_only_asserts = sum(1 for x in rec.findings
                                              if x.node is not None and x.deletable == "report-only")
                    has_other_code = any(id(s) not in del_nodes and not _trivial(s) for s in rec.node.body)
                    ok_partial = (f.category == "dead-assert" or has_other_code or
                                  rec.nonredundant + rec.helper_asserts + rec.conditional
                                  + report_only_asserts > 0)
                    if ok_partial:
                        spans.append((f.node.lineno, f.node.end_lineno, None))
                        removed_nodes.append(getattr(f.node, "_orig_stmt", f.node))
                        asserts_removed += 1
            if removed_nodes:
                spans.extend(_dangling_edits(rec, removed_nodes, lines_of(rec.file)))

    plan = {"testsToRemove": tests_to_remove, "assertionsToRemove": asserts_removed}
    return edits_by_file, plan


def apply_fix(records: list[TestRecord], root: str):
    edits_by_file, plan = plan_removals(records, root)
    file_lines: dict[str, list[str]] = {}

    def lines_of(f):
        if f not in file_lines:
            file_lines[f] = split_lines_keepends(
                open(f, encoding="utf-8", newline="").read())
        return file_lines[f]

    files_changed = 0
    for file, spans in edits_by_file.items():
        if not spans:
            continue
        lines = lines_of(file)
        replace = {}   # 1-based start line -> replacement text
        drop = set()
        for s, e, repl in spans:
            drop.update(range(s, e + 1))
            if repl is not None:
                replace[s] = repl
        new = []
        for i, l in enumerate(lines, 1):
            if i in replace:
                new.append(replace[i])
            elif i not in drop:
                new.append(l)
        with open(file, "w", encoding="utf-8", newline="") as fh:
            fh.writelines(new)
        files_changed += 1
    return {"testsRemoved": len(plan["testsToRemove"]),
            "assertionsRemoved": plan["assertionsToRemove"],
            "filesChanged": files_changed}
