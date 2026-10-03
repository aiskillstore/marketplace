#!/usr/bin/env python3
"""Score a page: one URL, one offer, and one action. Refuse a sitemap.

Stdlib only. No network. Does not publish.

  python3 scripts/score.py --file draft.json
  python3 scripts/score.py --stdin
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


MAX_INPUT_BYTES = 2_000_000


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


def is_sitemap(data: dict) -> bool:
    kind = nonempty_text(data.get("kind")).lower()
    if kind == "sitemap":
        return True
    if isinstance(data.get("urls"), list):
        return True
    url = nonempty_text(data.get("url")).lower()
    if "sitemap" in url:
        return True
    return False


def is_url(value: str) -> bool:
    return value.startswith("https://") or value.startswith("http://")


def main() -> int:
    parser = argparse.ArgumentParser(description="Score a page draft")
    parser.add_argument("--file", help="Path to a JSON object")
    parser.add_argument("--stdin", action="store_true", help="Read a JSON object from stdin")
    args = parser.parse_args()
    data = load_payload(args)
    if not isinstance(data, dict):
        fail_input("JSON must be an object")

    if is_sitemap(data):
        print("a sitemap")
        return 1

    url = nonempty_text(data.get("url"))
    offer = nonempty_text(data.get("offer"))
    action = nonempty_text(data.get("action"))

    if not is_url(url) or not offer or not action:
        print("draft is incomplete")
        return 1

    print(f"url: {url}")
    print(f"offer: {offer}")
    print(f"action: {action}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
