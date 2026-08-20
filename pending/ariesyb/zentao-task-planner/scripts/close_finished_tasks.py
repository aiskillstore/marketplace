"""预览或关闭已完成但未关闭的禅道任务。"""

from __future__ import annotations

import argparse

from zentao_common import ZentaoClient, print_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="关闭已完成但未关闭的禅道任务")
    parser.add_argument("--comment", default="任务已完成，自动关闭")
    parser.add_argument("--env-file", help="技能包或本地的 .env 文件路径")
    parser.add_argument("--execute", action="store_true", help="实际执行关闭")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    client = ZentaoClient.from_env(env_file=args.env_file)
    if not client.login():
        raise SystemExit("登录禅道失败，请检查环境变量配置")

    result = client.close_finished_tasks(comment=args.comment, execute=args.execute)
    print_json(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
