"""预览或修复任务填错的完成日期。"""

from __future__ import annotations

import argparse

from zentao_common import ZentaoClient, print_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="修复任务填错的完成日期")
    parser.add_argument("--task-id", type=int, required=True, help="要修复的禅道任务ID")
    parser.add_argument("--assigned-to", help="激活后指派人，默认使用任务当前指派人或登录账号")
    parser.add_argument("--left", type=float, default=1, help="激活时填写的剩余工时，默认 1")
    parser.add_argument("--comment", default="修复任务完成日期", help="激活任务时提交的备注")
    parser.add_argument("--env-file", help="技能包或本地的 .env 文件路径")
    parser.add_argument("--execute", action="store_true", help="实际执行修复")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    client = ZentaoClient.from_env(env_file=args.env_file)
    if not client.login():
        raise SystemExit("登录禅道失败，请检查环境变量配置")

    result = client.repair_task_wrong_finish_date(
        task_id=args.task_id,
        assigned_to=args.assigned_to,
        left=args.left,
        comment=args.comment,
        dry_run=not args.execute,
    )
    print_json(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
