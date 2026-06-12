#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""generate_keyword_csv.py — 将 Sorftime 关键词数据导出为标准 CSV。

用法:
    python generate_keyword_csv.py --type detail  --data data.json --output 02_keyword_搜索量.csv
    python generate_keyword_csv.py --type trend   --data data.json --output 03_keyword_趋势.csv
    python generate_keyword_csv.py --type extends --data data.json --output 04_keyword_延伸词.csv

输入:
    JSON 文件，内容为 AI 整理后的结构化关键词数据。

    detail 格式:
    [{"关键词": "...", "周搜索量": 72, "搜索排名": 857746, "变化率": "...", "CPC": 0.69, "备注": "..."}]

    trend 格式:
    [{"关键词": "...", "日期": "2024-03", "月搜索量": 516, "搜索排名": 711062, "趋势方向": "波动"}]

    extends 格式:
    [{"延伸词": "...", "周搜索量": 72, "搜索排名": 857746, "关联度": "高"}]
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

# ── 列定义 ────────────────────────────────────────────────────────────

COLUMNS = {
    "detail": ["关键词", "周搜索量", "搜索排名", "变化率", "CPC", "数据来源", "来源类型", "来源链接/查询词", "原始文件名", "采集时间"],
    "trend": ["关键词", "日期", "月搜索量", "搜索排名", "趋势方向", "数据来源", "来源类型", "来源链接/查询词", "原始文件名", "采集时间"],
    "extends": ["延伸词", "周搜索量", "搜索排名", "关联度(高/中/低)", "数据来源", "来源类型", "来源链接/查询词", "原始文件名", "采集时间"],
}

SOURCE_TOOLS = {
    "detail": "mcp_sorftime_keyword_detail",
    "trend": "mcp_sorftime_keyword_trend",
    "extends": "mcp_sorftime_keyword_extends",
}


def load_data(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def default_captured_at() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def normalize_row(
    row: dict,
    csv_type: str,
    source_ref: str,
    raw_file: str,
    captured_at: str,
    source_type: str,
) -> dict:
    """确保每行都包含数据来源列，并对齐列名。"""
    out = {}
    cols = COLUMNS[csv_type]
    source_col = "数据来源"

    for col in cols:
        if col == source_col:
            out[col] = row.get(col, row.get("数据来源工具", SOURCE_TOOLS[csv_type]))
        elif col == "来源类型":
            out[col] = row.get(col, source_type)
        elif col == "来源链接/查询词":
            out[col] = row.get(col, source_ref)
        elif col == "原始文件名":
            out[col] = row.get(col, raw_file)
        elif col == "采集时间":
            out[col] = row.get(col, captured_at)
        elif col == "关联度(高/中/低)" and "关联度" in row:
            out[col] = row["关联度"]
        else:
            out[col] = row.get(col, "N/A")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Sorftime 关键词数据 → CSV")
    parser.add_argument("--type", required=True, choices=["detail", "trend", "extends"])
    parser.add_argument("--data", required=True, help="JSON 数据文件")
    parser.add_argument("--source-type", default="sorftime_mcp", help="来源类型")
    parser.add_argument("--source-ref", default="", help="来源链接或查询词")
    parser.add_argument("--raw-file", default=None, help="原始文件名")
    parser.add_argument("--captured-at", default=None, help="采集时间")
    parser.add_argument("--output", required=True, help="输出 CSV 路径")
    args = parser.parse_args()

    data = load_data(args.data)
    cols = COLUMNS[args.type]
    raw_file = args.raw_file or Path(args.data).name
    captured_at = args.captured_at or default_captured_at()
    rows = [
        normalize_row(
            r,
            args.type,
            args.source_ref,
            raw_file,
            captured_at,
            args.source_type,
        )
        for r in data
    ]

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)

    result = {"csv_path": args.output, "csv_rows": len(rows), "type": args.type}
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
