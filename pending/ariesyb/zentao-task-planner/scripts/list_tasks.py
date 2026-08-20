"""查看当前禅道任务列表。"""

from __future__ import annotations

import argparse
import csv
import sys

from zentao_common import ZentaoClient, print_json


TSV_FIELDS = [
    "id",
    "name",
    "status",
    "pri",
    "assignedTo",
    "estimate",
    "consumed",
    "left",
    "estStarted",
    "deadline",
    "closed",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="查看当前禅道任务列表")
    parser.add_argument(
        "--view",
        default="active",
        choices=["active", "assignedTo", "finishedBy", "closedBy"],
        help="任务视图，默认 active",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="仅输出常用字段",
    )
    parser.add_argument(
        "--output",
        default="json",
        choices=["json", "tsv"],
        help="输出格式，默认 json",
    )
    parser.add_argument("--env-file", help="技能包或本地的 .env 文件路径")
    return parser


def build_summary_task(task: dict, status: str, closed: bool) -> dict:
    return {
        "id": task.get("id"),
        "name": task.get("name"),
        "status": status,
        "pri": task.get("pri"),
        "assignedTo": task.get("assignedTo"),
        "estimate": task.get("estimate"),
        "consumed": task.get("consumed"),
        "left": task.get("left"),
        "estStarted": task.get("estStarted"),
        "deadline": task.get("deadline"),
        "closed": closed,
    }


def select_tasks(
    tasks: list[dict],
    summary_only: bool = False,
    output: str = "json",
) -> list[dict]:
    results = []
    for task in tasks:
        status = str(task.get("status", "")).strip()
        closed = ZentaoClient.is_task_closed(task)

        summary_task = build_summary_task(task, status, closed)

        if output == "tsv" or summary_only:
            results.append(summary_task)
        else:
            results.append(task)
    return results


def print_tsv(tasks: list[dict]) -> None:
    writer = csv.DictWriter(sys.stdout, fieldnames=TSV_FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for task in tasks:
        writer.writerow({field: task.get(field, "") for field in TSV_FIELDS})


def main() -> int:
    args = build_parser().parse_args()

    client = ZentaoClient.from_env(env_file=args.env_file)
    if not client.login():
        raise SystemExit("登录禅道失败，请检查环境变量配置")

    tasks_data = client.get_my_tasks(view=args.view)
    task_list = client._normalize_task_list(tasks_data.get("tasks", []))

    results = select_tasks(
        task_list,
        summary_only=args.summary_only,
        output=args.output,
    )

    if args.output == "tsv":
        print_tsv(results)
        return 0

    print_json(
        {
            "matched_count": len(results),
            "filters": {
                "task_view": args.view,
                "summary_only": args.summary_only,
                "output": args.output,
            },
            "tasks": results,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
