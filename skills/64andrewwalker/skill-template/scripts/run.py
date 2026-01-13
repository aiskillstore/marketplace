#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Template skill entrypoint")
    parser.add_argument("--test", action="store_true", help="Run self-test")
    ns = parser.parse_args(argv)

    if ns.test:
        print("Template skill: PASS")
        return 0

    print("Template skill: nothing to do (copy this template into a real skill).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

