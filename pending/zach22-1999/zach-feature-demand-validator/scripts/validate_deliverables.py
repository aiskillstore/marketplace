#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_deliverables.py — 校验功能需求验证报告的交付完整性。

用法:
    python validate_deliverables.py --dir outputs/feature-validation/

检查项:
    1. 报告 MD 文件存在且 YAML 头完整
    2. 数据源目录存在
    3. 5 个 CSV 文件均存在
    4. 每个 CSV 包含必要列（含"数据来源"列）
    5. 每个 CSV 至少有 1 行数据

输出:
    stdout: JSON {"status": "validate_ok"} 或 {"status": "validate_fail", "errors": [...]}
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
from pathlib import Path

# ── CSV 必须列定义 ─────────────────────────────────────────────────

REQUIRED_COLUMNS = {
    "01_review": ["ASIN", "评论日期", "星级", "功能相关(Y/N)", "情感(正/负/中)", "数据来源", "来源类型", "来源链接/查询词", "原始文件名", "采集时间"],
    "02_keyword_信号_搜索量": ["关键词", "周搜索量", "数据来源", "来源类型", "来源链接/查询词", "原始文件名", "采集时间"],
    "03_keyword_信号_趋势": ["关键词", "日期", "数据来源", "来源类型", "来源链接/查询词", "原始文件名", "采集时间"],
    "04_keyword_信号_延伸词": ["延伸词", "周搜索量", "数据来源", "来源类型", "来源链接/查询词", "原始文件名", "采集时间"],
    "05_社区_信号_讨论摘要": ["帖子标题", "URL", "用户态度摘要", "数据来源", "来源类型", "来源链接/查询词", "原始文件名", "采集时间"],
}

REQUIRED_YAML_FIELDS = ["created", "topic", "type", "data_sources"]

# ── ASIN 格式校验 ─────────────────────────────────────────────────────

ASIN_PATTERN = re.compile(r"^[A-Z0-9]{10}$")

ASIN_BLOCKLIST = {
    "MULTI", "UNKNOWN", "N/A", "NA", "NONE", "TEST", "EXAMPLE",
    "B0XXXXXXXXX", "B0XXXXXXXX", "B0XXXXX", "PLACEHOLDER",
}


def is_valid_asin(asin: str) -> bool:
    """检查 ASIN 是否为合法的 10 位亚马逊 ASIN。"""
    if not asin or asin.strip().upper() in ASIN_BLOCKLIST:
        return False
    return bool(ASIN_PATTERN.match(asin.strip()))


def find_report_md(base_dir: str) -> str | None:
    """在目录中查找验证报告 MD 文件。"""
    patterns = [
        os.path.join(base_dir, "*功能需求验证报告.md"),
        os.path.join(base_dir, "*验证报告.md"),
    ]
    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
    return None


def find_data_dir(base_dir: str) -> str | None:
    """在目录中查找数据源子目录。"""
    patterns = [
        os.path.join(base_dir, "*数据源"),
        os.path.join(base_dir, "*数据源/"),
    ]
    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches and os.path.isdir(matches[0]):
            return matches[0]
    return None


def check_yaml_header(md_path: str) -> list[str]:
    """检查 MD 文件的 YAML 头是否完整。"""
    errors = []
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        errors.append(f"报告缺少 YAML 头: {md_path}")
        return errors

    match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        errors.append(f"YAML 头格式错误: {md_path}")
        return errors

    yaml_text = match.group(1)
    for field in REQUIRED_YAML_FIELDS:
        if f"{field}:" not in yaml_text:
            errors.append(f"YAML 头缺少字段: {field}")

    return errors


def check_csv(csv_path: str, prefix: str) -> list[str]:
    """检查单个 CSV 文件的列完整性和数据质量。"""
    errors = []

    if not os.path.exists(csv_path):
        errors.append(f"CSV 文件缺失: {csv_path}")
        return errors

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        if not header:
            errors.append(f"CSV 文件为空: {csv_path}")
            return errors

        rows = list(reader)
        if len(rows) == 0:
            errors.append(f"CSV 无数据行: {csv_path}")

    # 查找匹配的列定义
    matched_key = None
    for key in REQUIRED_COLUMNS:
        if key in os.path.basename(csv_path):
            matched_key = key
            break

    if matched_key:
        required = REQUIRED_COLUMNS[matched_key]
        header_set = set(header)
        for col in required:
            # 模糊匹配：允许列名包含必须列名
            if not any(col in h for h in header_set):
                errors.append(f"CSV {os.path.basename(csv_path)} 缺少列: {col}")

    # ── Review CSV 专属校验：ASIN 格式 ────────────────────────────
    if matched_key == "01_review" and rows and "ASIN" in header:
        invalid_asins = []
        for i, row in enumerate(rows):
            asin_val = (row.get("ASIN") or "").strip()
            if not is_valid_asin(asin_val):
                invalid_asins.append((i + 2, asin_val))  # +2: 1-indexed + header
        if invalid_asins:
            bad_samples = invalid_asins[:5]
            sample_str = ", ".join(f"行{ln}: '{v}'" for ln, v in bad_samples)
            errors.append(
                f"CSV {os.path.basename(csv_path)} 有 {len(invalid_asins)} 行 ASIN 格式非法"
                f"（必须为 10 位大写字母+数字，如 B0PUBLIC01，"
                f"禁止 MULTI/UNKNOWN/B0XXXXX 等占位符）。"
                f"示例: {sample_str}"
            )

    return errors


def review_uses_fallback(csv_path: str) -> bool:
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            source_type = (row.get("来源类型") or "").lower()
            if "manual" in source_type or "amazon" in source_type:
                return True
    return False


def find_review_source_pack(data_dir: str) -> Path | None:
    data_path = Path(data_dir)
    candidates = [
        data_path / "review_source_pack",
        data_path / "06_review_source_pack",
        data_path,
    ]
    for candidate in candidates:
        manifest = candidate / "source_manifest.json"
        raw_dir = candidate / "raw"
        if manifest.exists() and raw_dir.is_dir():
            return candidate
    return None


def check_review_source_pack(data_dir: str) -> list[str]:
    errors: list[str] = []
    pack_dir = find_review_source_pack(data_dir)
    if not pack_dir:
        return ["fallback 场景缺少 review_source_pack/source_manifest.json 或 raw/ 原始文件目录"]

    manifest_path = pack_dir / "source_manifest.json"
    raw_dir = pack_dir / "raw"
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    required_fields = ["asin", "site", "captured_at", "source_url", "export_method"]
    for field in required_fields:
        if field not in manifest or not str(manifest[field]).strip():
            errors.append(f"source_manifest.json 缺少字段: {field}")

    raw_files = [path for path in raw_dir.iterdir() if path.is_file()]
    if not raw_files:
        errors.append("review_source_pack/raw/ 下没有原始文件")
    return errors


def validate(base_dir: str) -> dict:
    """执行完整校验，返回结果。"""
    errors: list[str] = []

    # 1. 检查报告 MD
    md_path = find_report_md(base_dir)
    if not md_path:
        errors.append(f"未找到验证报告 MD 文件 (目录: {base_dir})")
    else:
        errors.extend(check_yaml_header(md_path))

    # 2. 检查数据源目录
    data_dir = find_data_dir(base_dir)
    if not data_dir:
        errors.append(f"未找到数据源目录 (目录: {base_dir})")
        return {"status": "validate_fail", "errors": errors}

    # 3. 检查 5 个 CSV
    expected_prefixes = ["01_review", "02_keyword", "03_keyword", "04_keyword", "05_社区"]
    csv_files = sorted(glob.glob(os.path.join(data_dir, "*.csv")))

    if len(csv_files) < 5:
        errors.append(f"CSV 文件不足: 期望 5 个, 实际 {len(csv_files)} 个")

    review_csv_path = None
    for prefix in expected_prefixes:
        matched = [f for f in csv_files if prefix in os.path.basename(f)]
        if not matched:
            errors.append(f"缺少 CSV: {prefix}_*.csv")
        else:
            if prefix == "01_review":
                review_csv_path = matched[0]
            errors.extend(check_csv(matched[0], prefix))

    if review_csv_path and review_uses_fallback(review_csv_path):
        errors.extend(check_review_source_pack(data_dir))

    if errors:
        return {"status": "validate_fail", "errors": errors}
    return {"status": "validate_ok", "report": md_path, "data_dir": data_dir, "csv_count": len(csv_files)}


def main() -> int:
    parser = argparse.ArgumentParser(description="校验功能需求验证报告的交付完整性")
    parser.add_argument("--dir", required=True, help="报告输出目录")
    args = parser.parse_args()

    result = validate(args.dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "validate_ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
