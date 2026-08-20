"""按日期范围预览或完成任务。"""

from __future__ import annotations

import argparse

from zentao_common import ZentaoClient, print_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="按日期预览或完成禅道任务")
    parser.add_argument("--start-date", required=True, help="开始日期，YYYY-MM-DD")
    parser.add_argument("--end-date", help="结束日期，默认等于开始日期")
    parser.add_argument(
        "--date-field",
        default="range",
        choices=["range", "estStarted", "deadline"],
        help="筛选依据字段",
    )
    parser.add_argument(
        "--statuses",
        default="wait,doing,pause",
        help="允许处理的状态列表，逗号分隔",
    )
    parser.add_argument("--comment", default="按预估工时自动完成任务")
    parser.add_argument("--env-file", help="技能包或本地的 .env 文件路径")
    parser.add_argument("--execute", action="store_true", help="实际执行完成")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    statuses = tuple(item.strip() for item in args.statuses.split(",") if item.strip())

    client = ZentaoClient.from_env(env_file=args.env_file)
    if not client.login():
        raise SystemExit("登录禅道失败，请检查环境变量配置")

    result = client.auto_finish_tasks_by_date(
        start_date=args.start_date,
        end_date=args.end_date,
        date_field=args.date_field,
        statuses=statuses,
        comment=args.comment,
        dry_run=not args.execute,
    )
    print_json(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
