#!/usr/bin/env python3
"""Fail a skill that still carries scaffold placeholder text.

Scans every markdown and JSON file under the target for the scaffold
sentinel token, unfilled template tokens such as a doubled-brace NAME,
and the boilerplate sentences the templates ship. Markdown fenced code
is exempt, so a worked example may quote a real failing run. Files
under assets/ are exempt, because templates hold the sentinel by
design. Prints one line per hit as path:line: message.

Exit codes:
  0  no placeholder text found
  1  at least one placeholder found
  2  usage or input error

Examples:
  python3 scripts/check_placeholders.py .
  python3 scripts/check_placeholders.py path/to/skill SKILL.md
"""
import argparse
import re
import sys
from pathlib import Path

SENTINEL = "SCAFFOLD-" + "PLACEHOLDER"
TEMPLATE_RE = re.compile(r"\{\{[A-Za-z0-9_]+\}\}")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
SUFFIXES = (".md", ".json")
BOILERPLATE = [
    "replace this paragraph",
    "replace this block",
    "replace this section",
    "replace this line",
    "replace every placeholder",
    "this skill was scaffolded by a skill factory",
]


def line_problems(line):
    found = []
    if SENTINEL in line:
        found.append(f"scaffold sentinel {SENTINEL} still present")
    for token in TEMPLATE_RE.findall(line):
        found.append(f"unfilled template token {token}")
    lowered = line.lower()
    for phrase in BOILERPLATE:
        if phrase in lowered:
            found.append(f'scaffold boilerplate "{phrase}"')
    return found


def scan_lines(lines, fenced):
    """Yield (line number, message) for every placeholder outside code."""
    fence = False
    for number, line in enumerate(lines, start=1):
        if fenced and FENCE_RE.match(line):
            fence = not fence
            continue
        if fence:
            continue
        for message in line_problems(line):
            yield number, message


def check_file(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    fenced = path.suffix == ".md"
    return [f"{path}:{number}: {message}"
            for number, message in scan_lines(lines, fenced)]


def wanted(path, root):
    if path.suffix not in SUFFIXES or not path.is_file():
        return False
    parts = path.relative_to(root).parts
    return "assets" not in parts and "__pycache__" not in parts


def collect(targets):
    files = []
    for target in targets:
        path = Path(target)
        if path.is_dir():
            files.extend(p for p in sorted(path.rglob("*"))
                         if wanted(p, path))
        elif path.is_file():
            files.append(path)
        else:
            raise FileNotFoundError(target)
    return files


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("targets", nargs="+",
                        help="skill directories or files to scan")
    args = parser.parse_args(argv)
    try:
        files = collect(args.targets)
    except FileNotFoundError as missing:
        print(f"error: no such file or directory: {missing}", file=sys.stderr)
        return 2
    problems = []
    for path in files:
        problems.extend(check_file(path))
    for problem in problems:
        print(problem)
    print(f"checked {len(files)} files, {len(problems)} placeholders")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
