"""从禅道页面获取任务类型枚举。"""

from __future__ import annotations

import argparse

from zentao_common import TASK_TYPE_DICT, ZentaoClient, print_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="从禅道页面获取任务类型枚举")
    parser.add_argument("--env-file", help="技能包或本地的 .env 文件路径")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    client = ZentaoClient.from_env(env_file=args.env_file)
    if not client.login():
        raise SystemExit("登录禅道失败，请检查环境变量配置")

    try:
        task_types = client.get_task_types()
        source = "dynamic"
    except Exception as exc:
        task_types = TASK_TYPE_DICT.copy()
        source = f"static-fallback: {exc}"

    print_json(
        {
            "source": source,
            "count": len(task_types),
            "task_types": task_types,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
