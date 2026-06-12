#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""generate_community_csv.py — 将社区讨论数据导出为标准 CSV。

用法:
    python generate_community_csv.py --data community.json --output 05_社区_讨论摘要.csv

输入:
    JSON 文件，内容为 AI 整理后的结构化社区讨论数据:
    [
      {
        "来源": "Reddit",
        "帖子标题": "...",
        "URL": "https://...",
        "发布日期": "2025-03",
        "讨论热度": "高",
        "用户态度摘要": "期待/推荐/质疑",
        "WebSearch查询词": "site:reddit.com ..."
      }
    ]
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

COLUMNS = [
    "来源(Reddit/Quora)",
    "帖子标题",
    "URL",
    "发布日期",
    "讨论热度",
    "用户态度摘要",
    "WebSearch查询词",
    "数据来源",
    "来源类型",
    "来源链接/查询词",
    "原始文件名",
    "采集时间",
]


def load_data(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def default_captured_at() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def normalize_row(row: dict, raw_file: str, captured_at: str, source_type: str, source_ref: str) -> dict:
    query = row.get("WebSearch查询词", source_ref)
    return {
        "来源(Reddit/Quora)": row.get("来源", row.get("来源(Reddit/Quora)", "未知")),
        "帖子标题": row.get("帖子标题", ""),
        "URL": row.get("URL", "N/A"),
        "发布日期": row.get("发布日期", "未标注"),
        "讨论热度": row.get("讨论热度", ""),
        "用户态度摘要": row.get("用户态度摘要", ""),
        "WebSearch查询词": query,
        "数据来源": row.get("数据来源", "web_search"),
        "来源类型": row.get("来源类型", source_type),
        "来源链接/查询词": row.get("来源链接/查询词", query or row.get("URL", "N/A")),
        "原始文件名": row.get("原始文件名", raw_file),
        "采集时间": row.get("采集时间", captured_at),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="社区讨论数据 → CSV")
    parser.add_argument("--data", required=True, help="JSON 数据文件")
    parser.add_argument("--source-type", default="public_web_search", help="来源类型")
    parser.add_argument("--source-ref", default="", help="来源链接或查询词")
    parser.add_argument("--raw-file", default=None, help="原始文件名")
    parser.add_argument("--captured-at", default=None, help="采集时间")
    parser.add_argument("--output", required=True, help="输出 CSV 路径")
    args = parser.parse_args()

    data = load_data(args.data)
    raw_file = args.raw_file or Path(args.data).name
    captured_at = args.captured_at or default_captured_at()
    rows = [normalize_row(r, raw_file, captured_at, args.source_type, args.source_ref) for r in data]

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    result = {"csv_path": args.output, "csv_rows": len(rows)}
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
