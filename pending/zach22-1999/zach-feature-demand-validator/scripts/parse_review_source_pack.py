#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""parse_review_source_pack.py — 解析 review_source_pack 并导出标准 Review CSV。

支持的 review_source_pack 结构：

review_source_pack/
├── source_manifest.json
└── raw/
    ├── reviews.csv
    ├── reviews.txt
    └── reviews.html

source_manifest.json 至少包含：
{
  "asin": "B0XXXX",
  "site": "US",
  "product_title": "...",
  "captured_at": "2026-03-19 14:30:00",
  "source_url": "https://www.amazon.com/...",
  "export_method": "manual_export_csv",
  "raw_files": ["reviews.csv"]
}
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
from pathlib import Path

from parse_reviews import (
    DEFAULT_DEMAND_SIGNALS,
    DEFAULT_MOISTURE_KEYWORDS,
    process_reviews,
    write_csv,
)

CSV_ALIASES = {
    "title": ["title", "review_title", "标题", "review title"],
    "body": ["body", "review_body", "review text", "评论", "内容", "text"],
    "rating": ["rating", "stars", "star", "评星", "星级"],
    "date": ["date", "review_date", "评论日期", "posted_at"],
}


def load_manifest(pack_dir: Path) -> dict:
    manifest_path = pack_dir / "source_manifest.json"
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    manifest["__path"] = str(manifest_path)
    return manifest


def pick_raw_files(pack_dir: Path, manifest: dict) -> list[Path]:
    raw_dir = pack_dir / "raw"
    listed = manifest.get("raw_files") or []
    if listed:
        return [raw_dir / name for name in listed]
    return sorted(path for path in raw_dir.iterdir() if path.is_file())


def normalize_header(name: str) -> str:
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", name.lower())


def read_csv_reviews(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        header_map = {
            normalize_header(key): key
            for key in (reader.fieldnames or [])
        }

        def lookup(alias_group: list[str]) -> str | None:
            for alias in alias_group:
                raw = header_map.get(normalize_header(alias))
                if raw:
                    return raw
            return None

        title_key = lookup(CSV_ALIASES["title"])
        body_key = lookup(CSV_ALIASES["body"])
        rating_key = lookup(CSV_ALIASES["rating"])
        date_key = lookup(CSV_ALIASES["date"])

        reviews: list[dict] = []
        for row in reader:
            reviews.append(
                {
                    "标题": (row.get(title_key, "") if title_key else "").strip(),
                    "评论": (row.get(body_key, "") if body_key else "").strip(),
                    "评星": coerce_rating(row.get(rating_key, "")) if rating_key else 0,
                    "评论日期": (row.get(date_key, "") if date_key else "").strip(),
                }
            )
    return reviews


def coerce_rating(value: str | float | int) -> float:
    text = str(value).strip()
    match = re.search(r"([0-5](?:\.\d)?)", text)
    return float(match.group(1)) if match else 0.0


def read_text_reviews(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    blocks = [
        block.strip()
        for block in re.split(r"\n\s*---+\s*\n|\n\s*\n(?=rating:|星级：|title:|标题：)", text)
        if block.strip()
    ]
    reviews: list[dict] = []
    for block in blocks:
        title = extract_prefixed_value(block, ["title:", "标题："])
        body = extract_prefixed_value(block, ["body:", "正文：", "评论："])
        rating = extract_prefixed_value(block, ["rating:", "星级："])
        review_date = extract_prefixed_value(block, ["date:", "日期："])

        if not body:
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if lines:
                if not title and len(lines) > 1:
                    title = lines[0]
                    body = " ".join(lines[1:])
                else:
                    body = " ".join(lines)

        reviews.append(
            {
                "标题": title,
                "评论": body,
                "评星": coerce_rating(rating),
                "评论日期": review_date,
            }
        )
    return reviews


def extract_prefixed_value(block: str, prefixes: list[str]) -> str:
    for line in block.splitlines():
        stripped = line.strip()
        for prefix in prefixes:
            if stripped.lower().startswith(prefix.lower()):
                return stripped[len(prefix):].strip()
    return ""


def read_html_reviews(path: Path) -> list[dict]:
    source = path.read_text(encoding="utf-8")
    block_pattern = re.compile(
        r'(<div[^>]+data-hook="review"[\s\S]*?</div>\s*</div>)',
        re.IGNORECASE,
    )
    blocks = block_pattern.findall(source)
    if not blocks:
        blocks = re.findall(r'(<div[^>]+review[\s\S]*?</div>)', source, re.IGNORECASE)

    reviews: list[dict] = []
    for block in blocks:
        title = clean_html(extract_first(block, [r'data-hook="review-title"[^>]*>(.*?)<', r'class="[^"]*review-title[^"]*"[^>]*>(.*?)<']))
        body = clean_html(extract_first(block, [r'data-hook="review-body"[^>]*>([\s\S]*?)<', r'class="[^"]*review-text[^"]*"[^>]*>([\s\S]*?)<']))
        rating = coerce_rating(clean_html(extract_first(block, [r'data-hook="review-star-rating"[^>]*>(.*?)<', r'([0-5](?:\.\d)?)\s+out of 5 stars'])))
        review_date = clean_html(extract_first(block, [r'data-hook="review-date"[^>]*>(.*?)<']))

        if body:
            reviews.append(
                {
                    "标题": title,
                    "评论": body,
                    "评星": rating,
                    "评论日期": review_date,
                }
            )
    return reviews


def extract_first(text: str, patterns: list[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def clean_html(text: str) -> str:
    stripped = re.sub(r"<[^>]+>", " ", text)
    return " ".join(html.unescape(stripped).split())


def load_reviews_from_file(path: Path) -> list[dict]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return read_csv_reviews(path)
    if suffix in {".txt", ".md"}:
        return read_text_reviews(path)
    if suffix in {".html", ".htm"}:
        return read_html_reviews(path)
    raise ValueError(f"不支持的原始文件格式: {path.name}")


def attach_metadata(reviews: list[dict], manifest: dict, raw_file: Path) -> list[dict]:
    source_ref = manifest.get("source_url") or manifest.get("source_query", "")
    source_type = manifest.get("export_method", "amazon_manual_export")
    captured_at = manifest.get("captured_at") or manifest.get("exported_at", "")
    return [
        {
            **review,
            "__source_tool": "amazon_review_source_pack",
            "__source_type": source_type,
            "__source_ref": source_ref,
            "__raw_file": raw_file.name,
            "__captured_at": captured_at,
        }
        for review in reviews
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="解析 review_source_pack 并导出标准 Review CSV")
    parser.add_argument("--pack", required=True, help="review_source_pack 目录")
    parser.add_argument("--keywords", required=True, help="功能关键词，逗号分隔")
    parser.add_argument(
        "--moisture-keywords",
        default=None,
        help="水分/干燥相关关键词，逗号分隔，可选",
    )
    parser.add_argument("--output", required=True, help="输出 CSV 路径")
    args = parser.parse_args()

    pack_dir = Path(args.pack)
    manifest = load_manifest(pack_dir)
    raw_files = pick_raw_files(pack_dir, manifest)
    feature_kws = [item.strip() for item in args.keywords.split(",") if item.strip()]
    moisture_kws = (
        [item.strip() for item in args.moisture_keywords.split(",") if item.strip()]
        if args.moisture_keywords
        else DEFAULT_MOISTURE_KEYWORDS
    )

    reviews: list[dict] = []
    for raw_file in raw_files:
        reviews.extend(attach_metadata(load_reviews_from_file(raw_file), manifest, raw_file))

    rows, stats = process_reviews(
        reviews=reviews,
        asin=manifest["asin"],
        feature_keywords=feature_kws,
        moisture_keywords=moisture_kws,
        demand_signals=DEFAULT_DEMAND_SIGNALS,
        source_tool="amazon_review_source_pack",
        source_type=manifest.get("export_method", "amazon_manual_export"),
        source_ref=manifest.get("source_url") or manifest.get("source_query", ""),
        captured_at=manifest.get("captured_at") or manifest.get("exported_at"),
    )
    write_csv(rows, args.output)

    stats["csv_path"] = args.output
    stats["csv_rows"] = len(rows)
    stats["pack_path"] = str(pack_dir)
    stats["raw_files"] = [file.name for file in raw_files]
    print(json.dumps(stats, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
