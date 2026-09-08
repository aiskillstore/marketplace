#!/usr/bin/env python3
"""Print this skill's name and description as JSON.

Reads the SKILL.md one directory above this script and prints a JSON
object with name and description fields to stdout.

Exit codes:
  0  success
  1  SKILL.md missing or malformed
  2  usage error

Example:
  python3 scripts/skill_info.py
"""
import argparse
import json
import re
import sys
from pathlib import Path


def read_header(text):
    if not text.startswith("---"):
        return None
    fence = re.search(r"\n---[ \t]*\n", text[3:])
    if not fence:
        return None
    return text[3:3 + fence.start()]


def parse_fields(header):
    fields = {}
    for line in header.splitlines():
        if line[:1].isalpha():
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args(argv)
    path = Path(__file__).resolve().parents[1] / "SKILL.md"
    if not path.is_file():
        print(f"error: {path} not found", file=sys.stderr)
        return 1
    header = read_header(path.read_text(encoding="utf-8"))
    if header is None:
        print("error: SKILL.md has no closed frontmatter", file=sys.stderr)
        return 1
    fields = parse_fields(header)
    print(json.dumps({"name": fields.get("name", ""),
                      "description": fields.get("description", "")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
