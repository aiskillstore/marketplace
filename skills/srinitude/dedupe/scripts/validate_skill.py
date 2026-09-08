#!/usr/bin/env python3
"""Static checks for a skill directory against the generation contract.

Verifies SKILL.md frontmatter, naming, body limits, required support
directories, and relative path depth. Prints one line per failure.

Exit codes:
  0  the skill passes every check
  1  at least one check failed
  2  usage or input error

Example:
  python3 scripts/validate_skill.py .
"""
import argparse
import re
import sys
from pathlib import Path

ALLOWED_KEYS = {"name", "description", "version", "author", "license",
                "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
REQUIRED_DIRS = ["references", "assets", "examples", "scripts", "evals"]
PATH_RE = re.compile(r"\b(?:references|assets|examples|scripts|tests|evals)/[\w./-]+")
MAX_BODY_LINES = 200
MAX_FILE_CHARS = 100_000


def split_frontmatter(text):
    if not text.startswith("---"):
        return None, None, "SKILL.md must open with --- frontmatter at byte 0"
    fence = re.search(r"\n---[ \t]*\n", text[3:])
    if not fence:
        return None, None, "frontmatter fence never closes"
    return text[3:3 + fence.start()], text[3 + fence.end():], None


def parse_header(header):
    fields = {}
    for line in header.splitlines():
        if line[:1].isalpha():
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def check_fields(fields, dirname, problems):
    unknown = sorted(set(fields) - ALLOWED_KEYS)
    for key in unknown:
        problems.append(f"unknown top-level frontmatter field: {key}")
    name = fields.get("name", "")
    if not NAME_RE.fullmatch(name) or len(name) > 64:
        problems.append(f"name must match ^[a-z0-9][a-z0-9._-]*$: {name!r}")
    if name != dirname:
        problems.append(f"name {name!r} must equal directory name {dirname!r}")
    description = fields.get("description", "")
    if not description or len(description) >= 60:
        problems.append("description must be 1 to 59 characters")
    if "Use when" not in description:
        problems.append('description must state "Use when" the skill applies')


def check_body(body, text, problems):
    if not body.strip():
        problems.append("SKILL.md needs body content after the frontmatter")
    lines = len(body.splitlines())
    if lines >= MAX_BODY_LINES:
        problems.append(f"body has {lines} lines; keep it under 200")
    if len(text) > MAX_FILE_CHARS:
        problems.append(f"SKILL.md is {len(text)} chars; cap is 100000")
    for token in PATH_RE.findall(body):
        if token.rstrip(".").count("/") > 2:
            problems.append(f"path deeper than one subdirectory: {token}")


def check_layout(skill, body, problems):
    for name in REQUIRED_DIRS + ["scripts/tests"]:
        if not (skill / name).is_dir():
            problems.append(f"missing required directory: {name}/")
        elif body and f"{name}/" not in body:
            problems.append(f"body never references {name}/")
    if not (skill / "evals" / "evals.json").is_file():
        problems.append("missing evals/evals.json")
    if not (skill / "mise.toml").is_file():
        problems.append("missing mise.toml task graph")


def validate(skill):
    problems = []
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    header, body, fatal = split_frontmatter(text)
    if fatal:
        problems.append(fatal)
        body = ""
    else:
        check_fields(parse_header(header), skill.name, problems)
        check_body(body, text, problems)
    check_layout(skill, body, problems)
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill_dir", help="path to the skill directory")
    args = parser.parse_args(argv)
    skill = Path(args.skill_dir).resolve()
    if not (skill / "SKILL.md").is_file():
        print(f"error: no SKILL.md inside {skill}", file=sys.stderr)
        return 2
    problems = validate(skill)
    for problem in problems:
        print(f"FAIL {problem}")
    print(f"{'FAIL' if problems else 'PASS'} {skill.name}: "
          f"{len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
