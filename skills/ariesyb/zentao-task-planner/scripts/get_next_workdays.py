"""查看当前或下一段连续工作日。"""

from __future__ import annotations

import argparse

from zentao_common import get_next_workdays, print_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="查看当前或下一段连续工作日")
    parser.add_argument(
        "--week-type",
        default="next",
        choices=["current", "next"],
        help="current 为当前连续工作日，next 为下一段连续工作日",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    print_json(get_next_workdays(week_type=args.week_type))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
