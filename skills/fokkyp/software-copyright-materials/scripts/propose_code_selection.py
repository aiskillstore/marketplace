#!/usr/bin/env python3
"""Create an editable source-file evidence list before code extraction."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import COPYRIGHT_CODE_EXTS, FRONTEND_EXTS, ensure_dir, iter_project_files, read_json, rel, write_json
from extract_code_material import LINES_PER_PAGE, SPLIT_THRESHOLD_PAGES, category_weight, should_skip_file


DEFAULT_MAX_FILES = 0


def evidence_for(path: Path, project: Path) -> str:
    priority, _ = category_weight(path, project)
    if priority == 0:
        return "入口文件证据"
    if priority == 10:
        return "路由文件证据"
    if priority == 20:
        return "页面文件证据"
    if priority == 30:
        return "数据交互文件证据"
    if priority == 40:
        return "状态或数据文件证据"
    if priority == 50:
        return "页面组成文件证据"
    if priority == 60:
        return "通用能力文件证据"
    if priority == 90:
        return "样式文件证据"
    if path.suffix.lower() not in FRONTEND_EXTS:
        return "补充源码证据"
    return "普通源码文件"


def build_candidates(project: Path) -> list[dict[str, Any]]:
    files = [p for p in iter_project_files(project, COPYRIGHT_CODE_EXTS) if not should_skip_file(p)]
    files.sort(key=lambda p: category_weight(p, project))
    candidates: list[dict[str, Any]] = []
    for path in files:
        try:
            line_count = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        except Exception:
            line_count = 0
        priority, _ = category_weight(path, project)
        candidates.append(
            {
                "path": rel(path, project),
                "selected": False,
                "start_line": 1,
                "end_line": None,
                "line_count": line_count,
                "priority": priority,
                "selection_tier": "frontend" if path.suffix.lower() in FRONTEND_EXTS else "supplement",
                "evidence": evidence_for(path, project),
                "model_reason": "",
            }
        )
    return candidates


def selected_line_estimate(item: dict[str, Any]) -> int:
    return int(item.get("line_count") or 0) + 2


def selection_stats(candidates: list[dict[str, Any]]) -> dict[str, int]:
    selected_items = [item for item in candidates if item.get("selected")]
    return {
        "selected_count": len(selected_items),
        "selected_lines": sum(selected_line_estimate(item) for item in selected_items),
    }


def all_candidate_lines(candidates: list[dict[str, Any]]) -> int:
    return sum(selected_line_estimate(item) for item in candidates)


def write_selection_md(path: Path, data: dict[str, Any]) -> None:
    lines = [
        "# 代码文件候选清单",
        "",
        "请先确认要抽取哪些源码文件，再运行代码材料抽取。",
        "",
        "本清单只列出候选源码证据，不默认决定抽取文件。",
        "模型需要先理解项目业务、页面入口和源码职责，再填写 `selected/start_line/end_line/model_reason`。",
        f"当前已选约 {data['estimated_selected_pages']} 页，全部候选源码约 {data['estimated_all_candidate_pages']} 页。",
        "",
        "```text",
        "STOP_FOR_USER",
        "NEXT_ACTION: 请由模型先填写 草稿/代码文件选择.json 的抽取选择和选择理由，再让用户确认；确认后运行 confirm_stage.py --stage code-selection。",
        "```",
        "",
        "确认方式：",
        "",
        "1. 模型根据项目业务和代码入口选择最能体现软件功能的文件。",
        "2. 把需要抽取的文件设为 `selected: true`，并填写 `model_reason`。",
        "3. 如只想抽取某个文件中间部分，可填写 `start_line` 和 `end_line`。",
        "4. 用户确认模型选择后，再记录 `code-selection` 门禁。",
        "",
        "## 默认选中文件",
        "",
        "| 文件 | 行数 | 抽取范围 | 模型选择理由 |",
        "| --- | ---: | --- | --- |",
    ]
    for item in data["files"]:
        if item.get("selected"):
            end = item.get("end_line") or item.get("line_count")
            lines.append(f"| `{item['path']}` | {item['line_count']} | {item['start_line']}-{end} | {item.get('model_reason') or '待模型填写'} |")

    lines.extend(["", "## 未选候选文件", "", "| 文件 | 行数 | 证据类型 |", "| --- | ---: | --- |"])
    for item in data["files"]:
        if not item.get("selected"):
            lines.append(f"| `{item['path']}` | {item['line_count']} | {item['evidence']} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--analysis", help="Optional project analysis JSON; retained for workflow traceability")
    parser.add_argument("--out-dir", default="软件著作权申请资料/草稿")
    parser.add_argument("--max-files", type=int, default=DEFAULT_MAX_FILES, help="Only limits candidate inventory size; does not auto-select files")
    parser.add_argument("--target-pages", type=int, default=SPLIT_THRESHOLD_PAGES)
    parser.add_argument("--lines-per-page", type=int, default=LINES_PER_PAGE)
    args = parser.parse_args()

    project = Path(args.project)
    if not project.exists():
        raise SystemExit(f"Project not found: {project}")
    if args.analysis and not Path(args.analysis).exists():
        raise SystemExit(f"Analysis JSON not found: {args.analysis}")

    out_dir = ensure_dir(Path(args.out_dir))
    candidates = build_candidates(project)
    target_lines = max(1, args.target_pages) * max(1, args.lines_per_page)
    if args.max_files:
        candidates = candidates[: args.max_files]
    stats = selection_stats(candidates)
    candidate_lines = all_candidate_lines(candidates)
    selected_pages = (stats["selected_lines"] + args.lines_per_page - 1) // args.lines_per_page if stats["selected_lines"] else 0
    all_pages = (candidate_lines + args.lines_per_page - 1) // args.lines_per_page if candidate_lines else 0
    data = {
        "project_root": str(project.resolve()),
        "selection_required": True,
        "model_selection_required": True,
        "confirmation_required": True,
        "user_confirmed": False,
        "target_pages": args.target_pages,
        "lines_per_page": args.lines_per_page,
        "target_lines": target_lines,
        "estimated_selected_lines": stats["selected_lines"],
        "estimated_selected_pages": selected_pages,
        "estimated_all_candidate_lines": candidate_lines,
        "estimated_all_candidate_pages": all_pages,
        "supplement_rule": "模型优先选择能体现软件核心功能和真实运行逻辑的源码；不足60页时再从其他相关源码中补充；候选源码仍不足时才生成全部代码材料。",
        "confirmation_stage": "code-selection",
        "next_action": "请由模型填写 草稿/代码文件选择.json 的抽取选择和选择理由，再让用户确认；确认后运行 confirm_stage.py --stage code-selection。",
        "instructions": "The script only inventories source files. The model must choose selected/start_line/end_line/model_reason before user confirmation.",
        "files": candidates,
    }
    write_json(out_dir / "代码文件选择.json", data)
    write_selection_md(out_dir / "代码文件候选清单.md", data)
    selected_count = sum(1 for item in candidates if item.get("selected"))
    print(f"OK code selection draft: {out_dir}")
    print(f"Candidates: {len(candidates)}")
    print(f"Model selected: {selected_count}")
    print(f"Estimated selected pages: {selected_pages}")
    print(f"Estimated all candidate pages: {all_pages}")
    print("STOP_FOR_USER")
    print(f"NEXT_ACTION: {data['next_action']}")


if __name__ == "__main__":
    main()
