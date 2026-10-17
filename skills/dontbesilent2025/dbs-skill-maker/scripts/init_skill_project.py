#!/usr/bin/env python3
"""Create a minimal single-Skill project without overwriting existing files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESOURCE_NAMES = {"references", "scripts", "assets"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="创建单个 Skill 的最小项目骨架")
    parser.add_argument("name", help="Skill 名称，小写英文、数字和连字符")
    parser.add_argument("--output", required=True, help="Skill 父目录")
    parser.add_argument("--description", required=True, help="能力与使用条件")
    parser.add_argument("--task", required=True, help="反复解决的问题与交付结果")
    parser.add_argument(
        "--workflow",
        action="append",
        required=True,
        help="一个关键工作动作，可重复传入",
    )
    parser.add_argument(
        "--done",
        action="append",
        required=True,
        help="一条可观察的完成证据，可重复传入",
    )
    parser.add_argument(
        "--resources",
        default="",
        help="按需创建 references,scripts,assets，使用英文逗号分隔",
    )
    parser.add_argument("--short-description", default="", help="Codex UI 短描述")
    parser.add_argument("--explicit-only", action="store_true", help="只允许显式调用")
    return parser.parse_args()


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def main() -> int:
    args = parse_args()
    name = args.name.strip()
    description = " ".join(args.description.split())
    task = " ".join(args.task.split())
    workflow = [" ".join(item.split()) for item in args.workflow if item.strip()]
    done = [" ".join(item.split()) for item in args.done if item.strip()]

    if not NAME_PATTERN.fullmatch(name) or len(name) >= 64:
        raise SystemExit("名称必须少于 64 个字符，并只使用小写英文、数字和连字符")
    if not 1 <= len(description) <= 1024:
        raise SystemExit("description 必须在 1～1,024 个字符之间")
    if not task:
        raise SystemExit("task 不能为空")
    if not workflow:
        raise SystemExit("至少需要一个 workflow")
    if not done:
        raise SystemExit("至少需要一条 done")

    resources = {item.strip() for item in args.resources.split(",") if item.strip()}
    unknown = sorted(resources - RESOURCE_NAMES)
    if unknown:
        raise SystemExit(f"未知资源目录：{', '.join(unknown)}")

    short_description = args.short_description.strip() or f"把明确问题制作成可验证的 {name} Skill"
    if not 25 <= len(short_description) <= 64:
        raise SystemExit("short-description 应在 25～64 个字符之间")

    target = Path(args.output).expanduser().resolve() / name
    if target.exists():
        raise SystemExit(f"目标已经存在，未覆盖：{target}")

    target.mkdir(parents=True)
    agents_dir = target / "agents"
    agents_dir.mkdir()
    for resource in sorted(resources):
        (target / resource).mkdir()

    workflow_lines = "\n".join(f"{index}. {item}" for index, item in enumerate(workflow, 1))
    done_lines = "\n".join(f"- {item}" for item in done)
    skill_text = f"""---
name: {name}
description: {description}
---

# {name}

## 任务

{task}

## 工作方式

{workflow_lines}

## 完成条件

{done_lines}
"""
    (target / "SKILL.md").write_text(skill_text, encoding="utf-8")

    openai_lines = [
        "interface:",
        f"  display_name: {yaml_string(name)}",
        f"  short_description: {yaml_string(short_description)}",
        f"  default_prompt: {yaml_string(f'使用 ${name} 完成它所解决的任务，并按可观察标准检查结果。')}",
    ]
    if args.explicit_only:
        openai_lines.extend(["policy:", "  allow_implicit_invocation: false"])
    (agents_dir / "openai.yaml").write_text("\n".join(openai_lines) + "\n", encoding="utf-8")

    print(f"已创建：{target}")
    print("下一步：补全适用条件、边界和停止条件，再运行 validate_skill_project.py。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
