#!/usr/bin/env python3
"""Size and nesting limits for code files.

Rules, applied to every .py and .sh file under the target:
  max 200 lines of code per file (blank and comment lines excluded)
  max 30 lines of code per function or class, own lines only
  max block nesting depth of 3 inside any function
  no leftover work markers in any code file

Exit codes:
  0  every file passed
  1  at least one rule broken
  2  usage or input error

Example:
  python3 scripts/check_code_rules.py .
"""
import argparse
import ast
import sys
from pathlib import Path

MAX_FILE = 200
MAX_CONSTRUCT = 30
MAX_DEPTH = 3
MARKERS = ("TO" + "DO", "FIX" + "ME", "XX" + "X")
BLOCK_NAMES = ["If", "For", "While", "With", "Try", "TryStar", "Match",
               "AsyncFor", "AsyncWith", "FunctionDef", "AsyncFunctionDef",
               "ClassDef"]
BLOCKS = tuple(getattr(ast, n) for n in BLOCK_NAMES if hasattr(ast, n))
DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
FUNCS = (ast.FunctionDef, ast.AsyncFunctionDef)


def loc(lines):
    stripped = (line.strip() for line in lines)
    return sum(1 for line in stripped if line and not line.startswith("#"))


def segment_loc(node, lines):
    return loc(lines[node.lineno - 1:node.end_lineno])


def own_loc(node, lines):
    total = segment_loc(node, lines)
    for child in node.body:
        if isinstance(child, DEFS):
            total -= segment_loc(child, lines)
    return total


def block_depth(node):
    deepest = 0
    for child in ast.iter_child_nodes(node):
        depth = block_depth(child)
        if isinstance(child, BLOCKS):
            depth += 1
        deepest = max(deepest, depth)
    return deepest


def check_construct(node, lines, path, problems):
    size = own_loc(node, lines)
    if size > MAX_CONSTRUCT:
        problems.append(f"{path}:{node.lineno}: {node.name} has {size} "
                        f"lines of code; cap is {MAX_CONSTRUCT}")
    if isinstance(node, FUNCS) and block_depth(node) > MAX_DEPTH:
        problems.append(f"{path}:{node.lineno}: {node.name} nesting is "
                        f"{block_depth(node)}; cap is {MAX_DEPTH}")


def check_markers(path, text, problems):
    for number, line in enumerate(text.splitlines(), start=1):
        for marker in MARKERS:
            if marker in line:
                problems.append(f"{path}:{number}: work marker {marker}")


def check_python(path, text, problems):
    lines = text.splitlines()
    if loc(lines) > MAX_FILE:
        problems.append(f"{path}: {loc(lines)} lines of code; cap is 200")
    try:
        tree = ast.parse(text)
    except SyntaxError as error:
        problems.append(f"{path}: does not parse: {error}")
        return
    for node in ast.walk(tree):
        if isinstance(node, DEFS):
            check_construct(node, lines, path, problems)


def check_shell(path, text, problems):
    lines = text.splitlines()
    if loc(lines) > MAX_FILE:
        problems.append(f"{path}: {loc(lines)} lines of code; cap is 200")


def check_file(path, problems):
    text = path.read_text(encoding="utf-8")
    check_markers(path, text, problems)
    if path.suffix == ".py":
        check_python(path, text, problems)
    else:
        check_shell(path, text, problems)


def collect(target):
    path = Path(target)
    if path.is_dir():
        return sorted(path.rglob("*.py")) + sorted(path.rglob("*.sh"))
    if path.is_file():
        return [path]
    raise FileNotFoundError(target)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("target", help="code file or directory to scan")
    args = parser.parse_args(argv)
    try:
        files = collect(args.target)
    except FileNotFoundError as missing:
        print(f"error: no such file or directory: {missing}",
              file=sys.stderr)
        return 2
    problems = []
    for path in files:
        check_file(path, problems)
    for problem in problems:
        print(problem)
    print(f"checked {len(files)} files, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
