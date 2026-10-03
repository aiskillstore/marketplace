#!/usr/bin/env python3
"""Score a lifecycle email: welcome, bargain, then nurture on the pain.

Stdlib only. No network. Does not send.

  python3 scripts/score.py --file draft.json
  python3 scripts/score.py --stdin
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


MAX_INPUT_BYTES = 2_000_000
REFUSAL = "a generic drip and a cold email"

DRIP_RE = re.compile(
    r"generic drip|\bday\s*1\b|\bday\s*3\b|\bday\s*7\b|tip series",
    re.IGNORECASE,
)
COLD_RE = re.compile(
    r"cold email|never opted|stranger|\bintroduce our\b|first touch",
    re.IGNORECASE,
)


def fail_input(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


def read_text(path: Path) -> str:
    try:
        if not path.exists():
            fail_input("file not found")
        if not path.is_file():
            fail_input("not a file")
        if path.stat().st_size > MAX_INPUT_BYTES:
            fail_input("file is too large")
        raw = path.read_bytes()
    except SystemExit:
        raise
    except OSError:
        fail_input("cannot read file")
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        fail_input("file is not UTF-8 text")


def load_payload(args: argparse.Namespace) -> object:
    if args.file and args.stdin:
        fail_input("pass --file or --stdin, not both")
    if args.stdin:
        raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
        if len(raw) > MAX_INPUT_BYTES:
            fail_input("input is too large")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            fail_input("input is not UTF-8 text")
    elif args.file:
        text = read_text(Path(args.file))
    else:
        fail_input("pass --file or --stdin")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        fail_input("invalid JSON")


def nonempty_text(value: object) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return ""


def refused(blob: str) -> bool:
    return DRIP_RE.search(blob) is not None or COLD_RE.search(blob) is not None


def main() -> int:
    parser = argparse.ArgumentParser(description="Score a lifecycle email draft")
    parser.add_argument("--file", help="Path to a JSON object")
    parser.add_argument("--stdin", action="store_true", help="Read a JSON object from stdin")
    args = parser.parse_args()
    data = load_payload(args)
    if not isinstance(data, dict):
        fail_input("JSON must be an object")

    pain = nonempty_text(data.get("pain"))
    welcome = nonempty_text(data.get("welcome"))
    bargain = nonempty_text(data.get("bargain"))
    nurture = nonempty_text(data.get("nurture"))
    blob = "\n".join([welcome, bargain, nurture])

    if refused(blob):
        print(REFUSAL)
        return 1

    if not pain or not welcome or not bargain or not nurture:
        print("draft is incomplete")
        return 1

    if pain.lower() not in nurture.lower():
        print(REFUSAL)
        return 1

    print(f"welcome: {welcome}")
    print(f"bargain: {bargain}")
    print(f"nurture: {nurture}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
