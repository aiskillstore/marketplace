from __future__ import annotations
import ast
import os
import re

from .models import TestRecord, Finding

# snapshot/baseline fixtures (syrupy, pytest-regressions, approvaltests): the
# test BODY is identical by design — each test is keyed to a distinct stored
# baseline by its name, so deleting an apparent duplicate orphans that baseline
# (and suites running with unused-snapshot checks then fail).
BASELINE_NAMES = {"snapshot", "snapshot_json", "data_regression", "file_regression",
                  "image_regression", "num_regression", "ndarrays_regression",
                  "dataframe_regression", "verify", "verify_file", "verify_as_json"}


def _uses_baseline(node: ast.AST) -> bool:
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and n.id in BASELINE_NAMES:
            return True
        if isinstance(n, ast.Attribute) and n.attr in BASELINE_NAMES:
            return True
    return False


def _name_tokens(name: str) -> set[str]:
    words = re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])", name)
    return {w.lower() for w in words if w.lower() not in ("test",) and not w.isdigit()}


def _names_diverge(a: str, b: str) -> bool:
    ta, tb = _name_tokens(a), _name_tokens(b)
    if not ta or not tb:
        return False
    overlap = len(ta & tb) / len(ta | tb)
    return overlap < 0.6


def mark_duplicates(records: list[TestRecord]):
    seen = {}          # same file + same class scope → proven, auto-deletable
    seen_global = {}   # anywhere (cross-file / cross-class) → advisory only
    for rec in records:
        try:
            body_dump = ast.dump(ast.Module(body=rec.node.body, type_ignores=[]))
            deco_dump = "|".join(ast.dump(d) for d in rec.node.decorator_list)
        except Exception:
            continue
        if len(body_dump) < 60:
            continue
        if _uses_baseline(rec.node):
            continue
        key = (rec.file, rec.scope_key, deco_dump, body_dump)
        if key in seen:
            first = seen[key]
            rec.is_duplicate = True
            reason = f'body is identical to "{first.name}" (line {first.node.lineno}) in the same scope'
            if _names_diverge(rec.name, first.name):
                reason += (' — names differ, so this is likely a copy-paste that leaves '
                           "this test's named behaviour untested; deleting is coverage-safe "
                           'but consider fixing the body instead')
            rec.findings.append(Finding(
                rec.file, rec.node.lineno, rec.name, "duplicate-test", "proven", "safe", reason))
        else:
            seen[key] = rec

        gkey = (deco_dump, body_dump)
        if gkey in seen_global:
            first = seen_global[gkey]
            if not rec.is_duplicate and (first.file, first.scope_key) != (rec.file, rec.scope_key):
                where = f"{os.path.basename(first.file)}:{first.node.lineno}"
                rec.findings.append(Finding(
                    rec.file, rec.node.lineno, rec.name, "duplicate-test", "advisory", "report-only",
                    f'body is identical to "{first.name}" ({where}) in a different scope — '
                    "likely redundant, but conftest/fixtures may differ, so review before removing"))
        else:
            seen_global[gkey] = rec
