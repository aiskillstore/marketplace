#!/usr/bin/env python3
"""Score a cold offer: a leak, a prototype, and email one.

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

# Email one sells the paid product when it asks the reader to buy it.
SELL_RE = re.compile(
    r"paid product|retainer|\bbook a demo\b|\bschedule a demo\b|"
    r"\bbuy (?:the|our)\b|\bpurchase\b|\bsubscribe\b|our pricing|"
    r"\bcheckout\b|core service|\bupsell\b|sign up for",
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


def sells_paid_product(email_one: str) -> bool:
    return SELL_RE.search(email_one) is not None


def main() -> int:
    parser = argparse.ArgumentParser(description="Score a cold offer draft")
    parser.add_argument("--file", help="Path to a JSON object")
    parser.add_argument("--stdin", action="store_true", help="Read a JSON object from stdin")
    args = parser.parse_args()
    data = load_payload(args)
    if not isinstance(data, dict):
        fail_input("JSON must be an object")

    leak = nonempty_text(data.get("leak"))
    prototype = nonempty_text(data.get("prototype"))
    email_one = nonempty_text(data.get("email_one"))

    if sells_paid_product(email_one):
        print("email one that sells the paid product")
        return 1

    if not leak or not prototype or not email_one:
        print("draft is incomplete")
        return 1

    print(f"leak: {leak}")
    print(f"prototype: {prototype}")
    print(f"email one: {email_one}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
