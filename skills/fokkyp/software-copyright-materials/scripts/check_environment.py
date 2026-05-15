#!/usr/bin/env python3
"""Check runtime capabilities at the beginning of the workflow."""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import subprocess
from pathlib import Path
from typing import Any

from common import ensure_dir, write_json


def command_version(command: list[str]) -> tuple[bool, str]:
    if not shutil.which(command[0]):
        return False, "not found"
    try:
        completed = subprocess.run(command, text=True, capture_output=True, timeout=20)
        output = (completed.stdout or completed.stderr).strip().splitlines()
        return completed.returncode == 0, output[0] if output else "available"
    except Exception as exc:
        return False, str(exc)


def run_docx_env(skill_dir: Path) -> tuple[bool, str]:
    env_script = skill_dir / "vendor/docx-toolkit/scripts/env_check.sh"
    if not env_script.exists():
        return False, "vendor/docx-toolkit/scripts/env_check.sh not found"
    try:
        completed = subprocess.run(["bash", str(env_script)], text=True, capture_output=True, timeout=40)
        return completed.returncode == 0, (completed.stdout + completed.stderr).strip()
    except Exception as exc:
        return False, str(exc)


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def check_environment(skill_dir: Path) -> dict[str, Any]:
    python_docx = module_available("docx")
    pandoc_ok, pandoc_version = command_version(["pandoc", "--version"])
    dotnet_ok, dotnet_version = command_version(["dotnet", "--version"])
    docx_ready, docx_output = run_docx_env(skill_dir)

    final_docx_mode = "docx-openxml" if docx_ready else ("python-docx" if python_docx else "basic-ooxml")
    requires_user_input = not docx_ready
    next_action = (
        "请选择：1) 安装完整 DOCX 环境；2) 使用基础 DOCX 兜底继续。回复选择后再进入项目分析。"
        if requires_user_input
        else "完整 DOCX 环境可用，可以进入项目分析。"
    )
    return {
        "output_directory": "当前目录/软件著作权申请资料",
        "capabilities": {
            "markdown_drafts": True,
            "application_txt": True,
            "basic_docx": python_docx or True,
            "python_docx": python_docx,
            "pandoc_preview": pandoc_ok,
            "docx_openxml_full": docx_ready,
            "dotnet_sdk": dotnet_ok,
        },
        "versions": {
            "pandoc": pandoc_version,
            "dotnet": dotnet_version,
        },
        "final_docx_mode": final_docx_mode,
        "recommendation": (
            "完整 DOCX OpenXML 环境已就绪，建议使用完整 Word 生成和校验流程。"
            if docx_ready
            else "完整 DOCX OpenXML 环境未就绪。可以继续使用兜底 DOCX 生成；如需更规范的 Word 结构和校验，请先安装 .NET SDK 并运行 vendor/docx-toolkit/scripts/setup.sh。"
        ),
        "install_prompt": (
            "是否安装完整 DOCX 环境？安装后文档生成和校验更规范；不安装也可以继续生成 Markdown、TXT 和基础 DOCX。"
            if not docx_ready
            else "无需安装，完整环境可用。"
        ),
        "requires_user_input": requires_user_input,
        "confirmation_stage": "environment" if requires_user_input else None,
        "next_action": next_action,
        "docx_env_output": docx_output,
    }


def write_markdown(path: Path, data: dict[str, Any]) -> None:
    caps = data["capabilities"]
    lines = [
        "# 软著申请资料生成环境检查",
        "",
        f"- 输出目录：`{data['output_directory']}`",
        f"- 最终 Word 模式：`{data['final_docx_mode']}`",
        "",
        "## 能力状态",
        "",
        f"- Markdown 草稿：{'可用' if caps['markdown_drafts'] else '不可用'}",
        f"- 申请表 TXT：{'可用' if caps['application_txt'] else '不可用'}",
        f"- 基础 DOCX 生成：{'可用' if caps['basic_docx'] else '不可用'}",
        f"- python-docx：{'可用' if caps['python_docx'] else '不可用'}",
        f"- pandoc 预览：{'可用' if caps['pandoc_preview'] else '不可用'}（{data['versions']['pandoc']}）",
        f"- .NET SDK：{'可用' if caps['dotnet_sdk'] else '不可用'}（{data['versions']['dotnet']}）",
        f"- DOCX OpenXML 完整环境：{'可用' if caps['docx_openxml_full'] else '不可用'}",
        "",
        "## 建议",
        "",
        data["recommendation"],
        "",
        "## 用户选择",
        "",
        data["install_prompt"],
        "",
        "如果完整 DOCX 环境不可用，必须先等待用户选择，并记录 `environment` 门禁后再继续。",
        "",
        "```text" if data.get("requires_user_input") else "",
        "STOP_FOR_USER" if data.get("requires_user_input") else "",
        f"NEXT_ACTION: {data['next_action']}" if data.get("requires_user_input") else "",
        "```" if data.get("requires_user_input") else "",
        "",
        "## DOCX 环境输出摘要",
        "",
        "```text",
        "\n".join(data["docx_env_output"].splitlines()[:40]),
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="软件著作权申请资料")
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parents[1]
    out_dir = ensure_dir(Path(args.out_dir))
    data = check_environment(skill_dir)
    write_json(out_dir / "环境检查.json", data)
    write_markdown(out_dir / "环境检查.md", data)
    print(f"OK environment check: {out_dir}")
    print(f"Final DOCX mode: {data['final_docx_mode']}")
    print(data["recommendation"])
    if data.get("requires_user_input"):
        print("STOP_FOR_USER")
        print(f"NEXT_ACTION: {data['next_action']}")


if __name__ == "__main__":
    main()
