#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通用交叉分析脚本。

输入:
- 解析后的产品 JSON
- 交叉分析配置 JSON

输出:
- cross_analysis.json
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def cross_table(products: list[dict], dim1: str, dim2: str) -> dict:
    matrix = defaultdict(lambda: defaultdict(lambda: {"count": 0, "sales": 0, "revenue": 0.0}))
    for product in products:
        v1 = product.get(dim1, "未知")
        v2 = product.get(dim2, "未知")
        matrix[v1][v2]["count"] += 1
        matrix[v1][v2]["sales"] += int(product.get("月销量", 0) or 0)
        matrix[v1][v2]["revenue"] += float(product.get("月销额", 0) or 0)
    return {k: dict(v) for k, v in matrix.items()}


def find_gaps(matrix: dict, scarcity_threshold: int = 2) -> list[dict]:
    gaps = []
    for dim1_value, dim2_map in matrix.items():
        for dim2_value, metrics in dim2_map.items():
            count = metrics["count"]
            if count <= scarcity_threshold:
                gaps.append(
                    {
                        "组合": f"{dim1_value} × {dim2_value}",
                        "产品数": count,
                        "月销量": metrics["sales"],
                        "状态": "空白" if count == 0 else "薄供给",
                    }
                )
    return sorted(gaps, key=lambda item: (item["产品数"], -item["月销量"]))


def main() -> int:
    parser = argparse.ArgumentParser(description="生成通用交叉分析")
    parser.add_argument("--input", "-i", required=True, help="解析后的产品 JSON")
    parser.add_argument("--config", "-c", required=True, help="交叉分析配置 JSON")
    parser.add_argument("--output", "-o", required=True, help="输出 JSON")
    args = parser.parse_args()

    products = load_json(Path(args.input))
    config = load_json(Path(args.config))
    analyses = {}
    for item in config.get("pairs", []):
        dim1 = item["dim1"]
        dim2 = item["dim2"]
        matrix = cross_table(products, dim1, dim2)
        analyses[f"{dim1}×{dim2}"] = {
            "dim1": dim1,
            "dim2": dim2,
            "matrix": matrix,
            "gaps": find_gaps(matrix, item.get("scarcity_threshold", 2)),
        }
    Path(args.output).write_text(json.dumps(analyses, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"analyses={len(analyses)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
