#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通用 Top100 标题属性解析器。

输入:
- 一个 JSON 文件，内容为产品列表
- 一个规则 JSON 文件，定义维度与正则/关键词

输出:
- top100_parsed.json
- uncertain_products.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def match_dimension(title: str, rule: dict) -> tuple[str, str]:
    text = normalize_text(title)
    for item in rule.get("regex", []):
        match = re.search(item["pattern"], text, re.I)
        if match:
            value = item.get("value")
            if value == "$0":
                value = match.group(0)
            elif isinstance(value, str):
                value = re.sub(r"\$(\d+)", lambda m: match.group(int(m.group(1))), value)
            return value or match.group(0), "high"
    for item in rule.get("keywords", []):
        if any(keyword.lower() in text for keyword in item.get("terms", [])):
            return item["value"], "medium"
    return rule.get("default", "未知"), "low"


def parse_products(products: list[dict], rules: dict) -> tuple[list[dict], list[dict]]:
    parsed = []
    uncertain = []
    dimensions = rules.get("dimensions", {})
    for product in products:
        title = product.get("标题") or product.get("title") or ""
        row = dict(product)
        confidence_map = {}
        for dim_name, rule in dimensions.items():
            value, confidence = match_dimension(title, rule)
            row[dim_name] = value
            confidence_map[dim_name] = confidence
        row["解析置信度"] = confidence_map
        parsed.append(row)
        if any(level == "low" for level in confidence_map.values()):
            uncertain.append(
                {
                    "ASIN": product.get("ASIN") or product.get("asin") or "",
                    "标题": title,
                    "低置信度维度": [k for k, v in confidence_map.items() if v == "low"],
                }
            )
    return parsed, uncertain


def main() -> int:
    parser = argparse.ArgumentParser(description="解析 Top100 标题维度")
    parser.add_argument("--input", "-i", required=True, help="Top100 原始 JSON")
    parser.add_argument("--rules", "-r", required=True, help="规则 JSON")
    parser.add_argument("--output", "-o", required=True, help="解析结果 JSON")
    parser.add_argument("--uncertain", "-u", required=True, help="低置信度结果 JSON")
    args = parser.parse_args()

    products = load_json(Path(args.input))
    rules = load_json(Path(args.rules))
    parsed, uncertain = parse_products(products, rules)
    Path(args.output).write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.uncertain).write_text(json.dumps(uncertain, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"parsed={len(parsed)} uncertain={len(uncertain)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
