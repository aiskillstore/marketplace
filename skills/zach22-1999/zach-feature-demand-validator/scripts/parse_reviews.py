#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""parse_reviews.py — 解析 Sorftime product_reviews 返回数据，筛选功能相关评论并导出 CSV。

用法:
    # 单 ASIN（Sorftime 场景）
    python parse_reviews.py --input reviews.json --asin B0CLTKGWQX --keywords "steam,steamer,steaming" --output 01_review.csv

    # 多 ASIN（每条 review JSON 中自带 ASIN 或 __asin 字段）
    python parse_reviews.py --input reviews_multi.json --keywords "steam,steamer" --output 01_review.csv

输入:
    Sorftime product_reviews 的 JSON 返回文件（支持嵌套结构和直接数组）。
    多 ASIN 场景下，每条 review 对象需包含 "ASIN" 或 "__asin" 字段。

输出:
    - CSV 文件（列定义见 references/csv_schema.md）
    - stdout: JSON 格式统计摘要（方便 AI 解析）
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# ── ASIN 格式校验 ─────────────────────────────────────────────────────

ASIN_PATTERN = re.compile(r"^[A-Z0-9]{10}$")

ASIN_BLOCKLIST = {
    "MULTI", "UNKNOWN", "N/A", "NA", "NONE", "TEST", "EXAMPLE",
    "B0XXXXXXXXX", "B0XXXXXXXX", "B0XXXXX", "PLACEHOLDER",
}


def is_valid_asin(asin: str) -> bool:
    """检查 ASIN 是否为合法的 10 位亚马逊 ASIN。"""
    if not asin or asin.upper() in ASIN_BLOCKLIST:
        return False
    return bool(ASIN_PATTERN.match(asin))


# ── 默认关键词 ──────────────────────────────────────────────────────

DEFAULT_DEMAND_SIGNALS = [
    "wish it had", "wish it could", "would be nice if",
    "missing", "if only", "should have", "needs a",
    "wish there was", "would love", "i want", "i wish",
]

DEFAULT_MOISTURE_KEYWORDS = [
    "moisture", "moist", "humid",
    "dry out", "dries out", "too dry", "dried out",
]

CSV_COLUMNS = [
    "ASIN",
    "评论日期",
    "星级",
    "评论内容",
    "功能相关(Y/N)",
    "情感(正/负/中)",
    "功能直接提及",
    "水分/干燥提及",
    "需求信号",
    "数据来源",
    "来源类型",
    "来源链接/查询词",
    "原始文件名",
    "采集时间",
]


# ── 核心函数 ─────────────────────────────────────────────────────────

def load_reviews(path: str) -> list[dict]:
    """读取 Sorftime product_reviews 的 JSON，兼容嵌套结构。"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list) and len(data) > 0:
        first = data[0]
        if isinstance(first, dict) and "text" in first:
            # 嵌套结构：[{"type": "text", "text": "前缀文字\n[{...}, ...]"}]
            text = first["text"]
            # 找到第一个 [ 的位置
            idx = text.find("[")
            if idx >= 0:
                return json.loads(text[idx:])
        elif "评论" in first or "评星" in first:
            return data

    return data


def default_captured_at() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def classify_sentiment(rating: float) -> str:
    if rating >= 4:
        return "正"
    if rating >= 3:
        return "中"
    return "负"


def matches_any(text: str, keywords: list[str]) -> bool:
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


def resolve_asin(review: dict, fallback_asin: str) -> str:
    """从 review 对象中解析 ASIN，优先级：ASIN > __asin > fallback。"""
    for key in ("ASIN", "__asin", "asin"):
        val = review.get(key, "").strip()
        if val and is_valid_asin(val):
            return val
    return fallback_asin


def process_reviews(
    reviews: list[dict],
    asin: str,
    feature_keywords: list[str],
    moisture_keywords: list[str],
    demand_signals: list[str],
    source_tool: str = "mcp_sorftime_product_reviews",
    source_type: str = "sorftime_mcp",
    source_ref: str = "",
    raw_file: str = "",
    captured_at: str | None = None,
) -> tuple[list[dict], dict]:
    """处理评论列表，返回 (行列表, 统计摘要)。"""
    rows: list[dict] = []
    captured_at = captured_at or default_captured_at()
    invalid_asins: list[str] = []
    stats = {
        "total": len(reviews),
        "feature_mentions": 0,
        "moisture_mentions": 0,
        "demand_signals": 0,
        "positive_feature": 0,
        "negative_feature": 0,
        "neutral_feature": 0,
    }

    for r in reviews:
        row_asin = resolve_asin(r, asin)
        if not is_valid_asin(row_asin):
            invalid_asins.append(row_asin)

        title = r.get("标题", "")
        body = r.get("评论", "")
        text = f"{title} {body}"
        rating = float(r.get("评星", 0))
        date = r.get("评论日期", "")
        sentiment = classify_sentiment(rating)

        is_feature = matches_any(text, feature_keywords)
        is_moisture = matches_any(text, moisture_keywords)
        is_demand = matches_any(text, demand_signals)

        func_related = "Y" if (is_feature or is_moisture) else "N"
        row_source_tool = r.get("__source_tool", source_tool)
        row_source_type = r.get("__source_type", source_type)
        row_source_ref = r.get("__source_ref", source_ref)
        row_raw_file = r.get("__raw_file", raw_file)
        row_captured_at = r.get("__captured_at", captured_at)

        if is_feature:
            stats["feature_mentions"] += 1
            if sentiment == "正":
                stats["positive_feature"] += 1
            elif sentiment == "负":
                stats["negative_feature"] += 1
            else:
                stats["neutral_feature"] += 1
        if is_moisture:
            stats["moisture_mentions"] += 1
        if is_demand:
            stats["demand_signals"] += 1

        rows.append(
            {
                "ASIN": row_asin,
                "评论日期": date,
                "星级": rating,
                "评论内容": f"{title}: {body}"[:300],
                "功能相关(Y/N)": func_related,
                "情感(正/负/中)": sentiment,
                "功能直接提及": "Y" if is_feature else "N",
                "水分/干燥提及": "Y" if is_moisture else "N",
                "需求信号": "Y" if is_demand else "N",
                "数据来源": row_source_tool,
                "来源类型": row_source_type,
                "来源链接/查询词": row_source_ref,
                "原始文件名": row_raw_file,
                "采集时间": row_captured_at,
            }
        )

    if invalid_asins:
        unique_bad = sorted(set(invalid_asins))
        stats["invalid_asin_count"] = len(invalid_asins)
        stats["invalid_asin_values"] = unique_bad

    return rows, stats


def write_csv(rows: list[dict], output_path: str) -> None:
    if not rows:
        print(json.dumps({"error": "no data to write"}))
        return
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


# ── CLI ──────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="解析 Sorftime product_reviews，筛选功能相关评论并导出 CSV",
    )
    parser.add_argument("--input", required=True, help="Sorftime reviews JSON 文件路径")
    parser.add_argument(
        "--asin", default="",
        help="产品 ASIN（单 ASIN 场景必填；多 ASIN 时可省略，由 JSON 中的 ASIN/__asin 字段提供）",
    )
    parser.add_argument(
        "--keywords", required=True,
        help="功能关键词（逗号分隔），如 'steam,steamer,steaming'",
    )
    parser.add_argument(
        "--moisture-keywords", default=None,
        help="水分/干燥相关关键词（逗号分隔，可选），默认使用内置列表",
    )
    parser.add_argument(
        "--source-url",
        default="",
        help="来源链接或查询词，默认留空",
    )
    parser.add_argument(
        "--source-type",
        default="sorftime_mcp",
        help="来源类型，默认 sorftime_mcp",
    )
    parser.add_argument(
        "--raw-file",
        default=None,
        help="原始文件名，默认使用 --input 的文件名",
    )
    parser.add_argument(
        "--captured-at",
        default=None,
        help="采集时间，默认当前本地时间",
    )
    parser.add_argument("--output", required=True, help="输出 CSV 路径")
    args = parser.parse_args()

    # ── ASIN 前置校验 ──────────────────────────────────────────────
    if args.asin and not is_valid_asin(args.asin):
        print(json.dumps({
            "error": "invalid_asin",
            "message": (
                f"--asin '{args.asin}' 不是合法的 10 位亚马逊 ASIN。"
                f"ASIN 必须为 10 位大写字母+数字（如 B0PUBLIC01）。"
                f"禁止使用 MULTI、UNKNOWN、B0XXXXX 等占位符。"
                f"如果是多 ASIN 场景，请在 JSON 中为每条 review 添加 ASIN 或 __asin 字段，"
                f"并省略 --asin 参数。"
            ),
        }, ensure_ascii=False))
        return 1

    feature_kws = [k.strip() for k in args.keywords.split(",") if k.strip()]
    moisture_kws = (
        [k.strip() for k in args.moisture_keywords.split(",") if k.strip()]
        if args.moisture_keywords
        else DEFAULT_MOISTURE_KEYWORDS
    )

    reviews = load_reviews(args.input)

    # ── 多 ASIN 场景：检查 JSON 中是否有 ASIN 字段 ─────────────────
    if not args.asin:
        missing = [
            i for i, r in enumerate(reviews)
            if not is_valid_asin(resolve_asin(r, ""))
        ]
        if missing:
            print(json.dumps({
                "error": "missing_asin_in_json",
                "message": (
                    f"未提供 --asin 参数，且 JSON 中有 {len(missing)} 条 review "
                    f"缺少合法的 ASIN/__asin 字段（行号: {missing[:5]}...）。"
                    f"多 ASIN 场景下，每条 review 必须包含合法的 ASIN 字段。"
                ),
            }, ensure_ascii=False))
            return 1

    rows, stats = process_reviews(
        reviews,
        args.asin,
        feature_kws,
        moisture_kws,
        DEFAULT_DEMAND_SIGNALS,
        source_type=args.source_type,
        source_ref=args.source_url,
        raw_file=args.raw_file or Path(args.input).name,
        captured_at=args.captured_at,
    )

    # ── 输出后校验：如果仍有非法 ASIN，报 warning ──────────────────
    if stats.get("invalid_asin_count"):
        stats["warning"] = (
            f"输出中有 {stats['invalid_asin_count']} 行 ASIN 格式异常: "
            f"{stats['invalid_asin_values']}。请检查输入数据。"
        )
        print(json.dumps(stats, ensure_ascii=False), file=sys.stderr)
        return 1

    write_csv(rows, args.output)

    stats["csv_path"] = args.output
    stats["csv_rows"] = len(rows)
    print(json.dumps(stats, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
