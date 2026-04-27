"""根据标准 TSV 任务表创建禅道任务。"""

from __future__ import annotations

import argparse

from zentao_common import (
    ZentaoClient,
    print_json,
    read_json_input,
    read_text_input_with_stdin,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="根据标准化任务列表批量创建禅道任务")
    parser.add_argument("--plan-text", help="直接传入任务列表文本")
    parser.add_argument("--plan-file", help="任务列表文件路径")
    parser.add_argument("--username-mapping", help="用户名映射 JSON 文本")
    parser.add_argument("--username-mapping-file", help="用户名映射 JSON 文件")
    parser.add_argument("--env-file", help="技能包或本地的 .env 文件路径")
    parser.add_argument("--execute", action="store_true", help="实际执行创建")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    plan_text = read_text_input_with_stdin(args.plan_text, args.plan_file)
    username_mapping = read_json_input(args.username_mapping, args.username_mapping_file)

    client = ZentaoClient.from_env(env_file=args.env_file)
    if not client.login():
        raise SystemExit("登录禅道失败，请检查环境变量配置")

    result = client.batch_create_tasks_from_text(
        plan_text,
        username_mapping=username_mapping,
        execute_create=args.execute,
    )
    print_json(result)
    return 0 if result.get("validation_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
