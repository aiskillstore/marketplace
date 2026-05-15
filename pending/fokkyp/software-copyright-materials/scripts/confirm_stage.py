#!/usr/bin/env python3
"""Record explicit user confirmations for gated workflow stages."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import read_json, write_json


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return read_json(path)


def write_confirmation(path: Path, data: dict[str, Any], key: str, note: str) -> None:
    data[key] = True
    data["confirmation_note"] = note
    data["confirmed_at"] = timestamp()
    write_json(path, data)


def pending_application_fields(md_path: Path) -> list[str]:
    if not md_path.exists():
        return [f"缺少 {md_path}"]
    return [line.strip() for line in md_path.read_text(encoding="utf-8").splitlines() if "待用户确认" in line]


def confirm_environment(workdir: Path, note: str) -> Path:
    out_path = workdir / "环境确认.json"
    data = load_json_or_empty(out_path)
    write_confirmation(out_path, data, "environment_confirmed", note)
    return out_path


def confirm_project(workdir: Path, note: str) -> Path:
    out_path = workdir / "项目确认.json"
    data = load_json_or_empty(out_path)
    write_confirmation(out_path, data, "project_confirmed", note)
    return out_path


def confirm_business(workdir: Path, note: str) -> Path:
    path = workdir / "草稿/业务理解.json"
    if not path.exists():
        raise SystemExit("Missing 草稿/业务理解.json")
    data = read_json(path)
    write_confirmation(path, data, "user_confirmed", note)
    return path


def confirm_code_selection(workdir: Path, note: str) -> Path:
    path = workdir / "草稿/代码文件选择.json"
    if not path.exists():
        raise SystemExit("Missing 草稿/代码文件选择.json")
    data = read_json(path)
    files = data.get("files") if isinstance(data, dict) else []
    selected = [item for item in files if isinstance(item, dict) and item.get("selected")]
    if not selected:
        raise SystemExit(
            "STOP_FOR_USER\n"
            "NEXT_ACTION: 代码文件选择尚未由模型填写。请先选择至少一个源码文件并填写选择理由，再让用户确认。"
        )
    missing_reason = [item.get("path") for item in selected if not str(item.get("model_reason") or "").strip()]
    if data.get("model_selection_required") and missing_reason:
        raise SystemExit(
            "STOP_FOR_USER\n"
            "NEXT_ACTION: 已选源码缺少模型选择理由，请补全 `model_reason` 后再确认。\n"
            + "\n".join(f"- {item}" for item in missing_reason[:20])
        )
    write_confirmation(path, data, "user_confirmed", note)
    return path


def parse_screenshot_method(method: str, note: str) -> str:
    value = (method or note or "").lower()
    if any(key in value for key in ("skip", "no-screenshot", "none", "不截图", "跳过", "暂不", "先不", "不要截图", "无需截图")):
        return "skip"
    if any(key in value for key in ("chrome", "devtools", "mcp")):
        return "chrome-devtools"
    if any(key in value for key in ("computer", "use", "电脑", "桌面")):
        return "computer-use"
    if any(key in value for key in ("user", "manual", "self", "手动", "自己", "用户")):
        return "user-supplied"
    raise SystemExit(
        "STOP_FOR_USER\n"
        "NEXT_ACTION: 请明确截图方式：chrome-devtools、computer-use、user-supplied 或 skip。"
    )


def confirm_screenshot_method(workdir: Path, note: str, method: str) -> Path:
    selected = parse_screenshot_method(method, note)
    out_path = workdir / "截图方式确认.json"
    data = load_json_or_empty(out_path)
    data["screenshot_method"] = selected
    write_confirmation(out_path, data, "screenshot_method_confirmed", note)
    return out_path


def confirm_application_fields(workdir: Path, note: str) -> Path:
    pending = pending_application_fields(workdir / "草稿/申请表信息.md")
    if pending:
        raise SystemExit(
            "STOP_FOR_USER\n"
            "NEXT_ACTION: 申请表信息仍包含“待用户确认”。请先补全字段，再重新确认。\n"
            + "\n".join(f"- {item}" for item in pending[:20])
        )
    out_path = workdir / "草稿/申请表字段确认.json"
    data = load_json_or_empty(out_path)
    write_confirmation(out_path, data, "application_fields_confirmed", note)
    return out_path


def confirm_markdown(workdir: Path, note: str) -> Path:
    issues = []
    business = workdir / "草稿/业务理解.json"
    selection = workdir / "草稿/代码文件选择.json"
    screenshot = workdir / "截图方式确认.json"
    fields = workdir / "草稿/申请表字段确认.json"

    if not business.exists() or not read_json(business).get("user_confirmed"):
        issues.append("业务理解尚未确认")
    if not selection.exists() or not read_json(selection).get("user_confirmed"):
        issues.append("代码文件选择尚未确认")
    if not screenshot.exists() or not read_json(screenshot).get("screenshot_method_confirmed"):
        issues.append("截图方式尚未确认")
    if not fields.exists() or not read_json(fields).get("application_fields_confirmed"):
        issues.append("申请表字段尚未确认")
    pending = pending_application_fields(workdir / "草稿/申请表信息.md")
    if pending:
        issues.append("申请表信息仍包含“待用户确认”")

    if issues:
        raise SystemExit(
            "STOP_FOR_USER\n"
            "NEXT_ACTION: Markdown 草稿确认前需要先处理以下事项：\n"
            + "\n".join(f"- {item}" for item in issues)
        )

    out_path = workdir / "草稿/最终生成确认.json"
    data = load_json_or_empty(out_path)
    write_confirmation(out_path, data, "markdown_confirmed", note)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", default="软件著作权申请资料")
    parser.add_argument(
        "--stage",
        required=True,
        choices=[
            "environment",
            "project",
            "business",
            "code-selection",
            "screenshot-method",
            "application-fields",
            "markdown",
        ],
    )
    parser.add_argument("--note", default="用户已确认")
    parser.add_argument(
        "--method",
        choices=["chrome-devtools", "computer-use", "user-supplied", "skip"],
        help="Screenshot capture method when --stage screenshot-method",
    )
    args = parser.parse_args()

    workdir = Path(args.workdir)
    if args.stage == "environment":
        path = confirm_environment(workdir, args.note)
    elif args.stage == "project":
        path = confirm_project(workdir, args.note)
    elif args.stage == "business":
        path = confirm_business(workdir, args.note)
    elif args.stage == "code-selection":
        path = confirm_code_selection(workdir, args.note)
    elif args.stage == "screenshot-method":
        path = confirm_screenshot_method(workdir, args.note, args.method or "")
    elif args.stage == "application-fields":
        path = confirm_application_fields(workdir, args.note)
    else:
        path = confirm_markdown(workdir, args.note)

    print(f"OK confirmation recorded: {args.stage}")
    print(path)


if __name__ == "__main__":
    main()
