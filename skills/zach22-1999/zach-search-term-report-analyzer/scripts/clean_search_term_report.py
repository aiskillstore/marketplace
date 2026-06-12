#!/usr/bin/env python3
"""清洗并标准化亚马逊广告搜索词报告。"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

ASIN_RE = re.compile(r"\bB0[A-Z0-9]{8}\b", re.IGNORECASE)
ASIN_EXTRACT_PATTERN = r"(\bB0[A-Z0-9]{8}\b)"

FIELD_ALIASES = {
    "date": ["日期", "date", "start date", "report date"],
    "brand": ["品牌", "brand"],
    "asin": ["asin", "advertised asin"],
    "campaign_name": ["广告活动名称", "campaign name"],
    "ad_group_name": ["广告组名称", "ad group name"],
    "targeting": ["投放", "targeting", "keyword", "target"],
    "match_type": ["匹配类型", "match type"],
    "search_term": ["客户搜索词", "搜索词", "customer search term", "search term", "query"],
    "impressions": ["展示量", "impressions"],
    "clicks": ["点击量", "clicks"],
    "ctr": ["点击率 (ctr)", "点击率(ctr)", "ctr", "click-through rate"],
    "cpc": ["单次点击成本 (cpc)", "单次点击成本(cpc)", "cpc", "cost per click"],
    "spend": ["花费", "spend", "cost"],
    "orders": ["7天总订单数(#)", "orders", "7 day total orders (#)", "7 day total orders"],
    "sales": ["7天总销售额", "sales", "7 day total sales"],
    "cvr": ["7天的转化率", "cvr", "conversion rate", "7 day conversion rate"],
    "acos": ["广告投入产出比 (acos)", "广告投入产出比(acos)", "acos"],
    "roas": ["总广告投资回报率 (roas)", "总广告投资回报率(roas)", "roas"],
}

CORE_FIELDS = ["date", "search_term", "clicks", "spend"]
NUMERIC_FIELDS = [
    "impressions",
    "clicks",
    "ctr",
    "cpc",
    "spend",
    "orders",
    "sales",
    "cvr",
    "acos",
    "roas",
]


def normalize_header(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.strip().replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text


def clean_text_cell(value: Any) -> Any:
    if value is None or pd.isna(value):
        return value
    text = str(value)
    text = text.replace("\ufeff", " ").replace("\u3000", " ").replace("\xa0", " ").replace("\ufffc", " ")
    text = re.sub(r"[\u200b-\u200f\u202a-\u202e\u2060]", "", text)
    text = text.strip().replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_search_term(value: Any) -> Any:
    text = clean_text_cell(value)
    if text is None or pd.isna(text) or not str(text).strip():
        return pd.NA
    return str(text).lower()


def load_table(input_path: Path) -> pd.DataFrame:
    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(input_path)
    elif suffix in {".xlsx", ".xlsm", ".xls"}:
        df = pd.read_excel(input_path, sheet_name=0)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    df.columns = [normalize_header(col) for col in df.columns]
    df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")
    return df


def canonicalize_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    mapping: dict[str, str] = {}
    used_raw: set[str] = set()

    normalized_lookup = {col.lower(): col for col in df.columns}
    for canonical, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            raw = normalized_lookup.get(alias.lower())
            if raw and raw not in used_raw:
                mapping[raw] = canonical
                used_raw.add(raw)
                break

    renamed = df.rename(columns=mapping).copy()
    return renamed, mapping


def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for field in ("brand", "asin", "campaign_name", "ad_group_name", "targeting", "match_type"):
        if field in result.columns:
            result[field] = result[field].map(clean_text_cell)
    if "search_term" in result.columns:
        result["search_term_raw"] = result["search_term"].map(clean_text_cell)
        result["search_term"] = result["search_term_raw"].map(normalize_search_term)

    if "date" in result.columns:
        result["date"] = pd.to_datetime(result["date"], errors="coerce")

    for field in NUMERIC_FIELDS:
        if field in result.columns:
            result[field] = pd.to_numeric(result[field], errors="coerce")

    if "ctr" not in result.columns and {"clicks", "impressions"}.issubset(result.columns):
        denom = result["impressions"].replace({0: pd.NA})
        result["ctr"] = result["clicks"] / denom
    if "cpc" not in result.columns and {"spend", "clicks"}.issubset(result.columns):
        denom = result["clicks"].replace({0: pd.NA})
        result["cpc"] = result["spend"] / denom
    if "cvr" not in result.columns and {"orders", "clicks"}.issubset(result.columns):
        denom = result["clicks"].replace({0: pd.NA})
        result["cvr"] = result["orders"] / denom
    if "acos" not in result.columns and {"spend", "sales"}.issubset(result.columns):
        denom = result["sales"].replace({0: pd.NA})
        result["acos"] = result["spend"] / denom
    if "roas" not in result.columns and {"sales", "spend"}.issubset(result.columns):
        denom = result["spend"].replace({0: pd.NA})
        result["roas"] = result["sales"] / denom
    return result


def extract_asin_from_text(text: Any) -> str | None:
    if text is None:
        return None
    match = ASIN_RE.search(str(text).upper())
    return match.group(0).upper() if match else None


def infer_row_asin(df: pd.DataFrame) -> pd.Series:
    if "asin" in df.columns:
        series = df["asin"].astype(str).str.upper().str.extract(ASIN_EXTRACT_PATTERN, expand=False)
        if series.notna().any():
            return series

    asin_series = pd.Series(index=df.index, dtype="object")
    for field in ("campaign_name", "ad_group_name"):
        if field in df.columns:
            extracted = df[field].map(extract_asin_from_text)
            asin_series = asin_series.fillna(extracted)
    return asin_series


def detect_report_type(input_path: Path, df: pd.DataFrame) -> str:
    haystacks = [input_path.name.lower()]
    for field in ("campaign_name", "ad_group_name"):
        if field in df.columns:
            sample = " ".join(df[field].dropna().astype(str).head(50).tolist()).lower()
            haystacks.append(sample)
    blob = " ".join(haystacks)

    if re.search(r"\bsd\b|sponsored display|display", blob):
        return "SD"
    if re.search(r"\bsb\b|sponsored brands|hsa", blob):
        return "SB"
    if re.search(r"\bsp\b|sponsored product|商品推广", blob):
        return "SP"
    return "UNKNOWN"


def infer_brand_candidates(input_path: Path, df: pd.DataFrame, explicit_brand: str | None) -> list[dict[str, Any]]:
    scores: Counter[str] = Counter()
    if explicit_brand:
        scores[explicit_brand] += 100

    if "brand" in df.columns:
        for value, count in df["brand"].dropna().astype(str).str.strip().value_counts().head(10).items():
            if value:
                scores[value] += int(count)

    filename_match = re.search(r"(?:brand|品牌)[-_ ]?([A-Za-z0-9][A-Za-z0-9_-]{1,40})", input_path.stem)
    if filename_match:
        scores[filename_match.group(1)] += 5

    if not scores:
        return []
    return [{"brand": brand, "score": count} for brand, count in scores.most_common()]


def build_normalized_frame(input_path: Path, brand: str | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    raw_df = load_table(input_path)
    mapped_df, mapping = canonicalize_columns(raw_df)
    mapped_df = coerce_types(mapped_df)

    mapped_df["asin"] = infer_row_asin(mapped_df)
    if "asin" in mapped_df.columns:
        mapped_df["asin"] = mapped_df["asin"].astype("string").str.upper()
    report_type = detect_report_type(input_path, mapped_df)
    brand_candidates = infer_brand_candidates(input_path, mapped_df, brand)
    selected_brand = brand or (brand_candidates[0]["brand"] if brand_candidates else None)
    if selected_brand:
        mapped_df["brand"] = selected_brand
    elif "brand" not in mapped_df.columns:
        mapped_df["brand"] = None
    mapped_df["report_type"] = report_type
    mapped_df["source_file"] = str(input_path)

    asin_counts = (
        mapped_df["asin"].dropna().astype(str).str.upper().value_counts().head(20)
        if "asin" in mapped_df.columns
        else pd.Series(dtype="int64")
    )

    missing_core_fields = [field for field in CORE_FIELDS if field not in mapped_df.columns]
    metadata = {
        "input_file": str(input_path),
        "report_type": report_type,
        "row_count": int(len(mapped_df)),
        "column_count": int(len(mapped_df.columns)),
        "mapped_columns": mapping,
        "missing_core_fields": missing_core_fields,
        "brand_candidates": brand_candidates,
        "asin_candidates": [
            {"asin": asin, "rows": int(count)} for asin, count in asin_counts.items()
        ],
    }

    preferred_cols = [
        "source_file",
        "report_type",
        "brand",
        "asin",
        "date",
        "campaign_name",
        "ad_group_name",
        "targeting",
        "match_type",
        "search_term_raw",
        "search_term",
        "impressions",
        "clicks",
        "ctr",
        "cpc",
        "spend",
        "orders",
        "sales",
        "cvr",
        "acos",
        "roas",
    ]
    existing_cols = [col for col in preferred_cols if col in mapped_df.columns]
    remaining = [col for col in mapped_df.columns if col not in existing_cols]
    normalized = mapped_df[existing_cols + remaining].copy()
    return normalized, metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="清洗并标准化亚马逊广告搜索词报告")
    parser.add_argument("input_file", help="原始搜索词报告路径（csv/xlsx）")
    parser.add_argument("--output-dir", help="输出目录，默认在输入文件同级创建 cleaned/")
    parser.add_argument("--brand", help="显式指定品牌，覆盖自动识别")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input_file).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else input_path.parent / "cleaned"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    normalized_df, metadata = build_normalized_frame(input_path, brand=args.brand)

    csv_path = output_dir / f"{input_path.stem}_normalized.csv"
    metadata_path = output_dir / f"{input_path.stem}_metadata.json"

    normalized_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary = {
        "status": "ok" if not metadata["missing_core_fields"] else "partial",
        "normalized_csv": str(csv_path),
        "metadata_json": str(metadata_path),
        "report_type": metadata["report_type"],
        "asin_candidates": metadata["asin_candidates"][:10],
        "brand_candidates": metadata["brand_candidates"][:5],
        "missing_core_fields": metadata["missing_core_fields"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
