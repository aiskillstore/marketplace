#!/usr/bin/env python3
"""Check a completed public-facing draft against project-wide editorial rules."""

from __future__ import annotations

import argparse
from pathlib import Path


PROHIBITED = ("A" + "I", "\u2014")


def find_hits(text: str) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if PROHIBITED[0] in line or PROHIBITED[1] in line:
            hits.append((line_number, line))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description="Check editorial rules in a text file.")
    parser.add_argument("file", type=Path, help="UTF-8 text file to check")
    args = parser.parse_args()

    try:
        text = args.file.read_text(encoding="utf-8")
    except OSError as error:
        parser.error(f"cannot read {args.file}: {error}")

    hits = find_hits(text)
    if not hits:
        print("PASS: editorial rule check found no prohibited content.")
        return 0

    print(f"FAIL: found {len(hits)} prohibited line(s) in {args.file}.")
    for line_number, line in hits:
        print(f"  line {line_number}: {line}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
