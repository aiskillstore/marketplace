#!/usr/bin/env python3
"""按单 ASIN 生成搜索词决策分析结果。"""

from __future__ import annotations

import argparse
from difflib import SequenceMatcher
import json
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from clean_search_term_report import build_normalized_frame
from fetch_listing_context import fetch_listing_context

DEFAULT_THRESHOLDS = {
    "min_clicks_for_judgement": 8,
    "min_clicks_for_priority": 15,
    "min_clicks_for_scale_up": 12,
    "min_clicks_for_listing_feedback": 10,
    "min_spend_for_attention": 10.0,
    "high_spend_without_orders": 15.0,
    "near_avg_cvr_band": 0.15,
    "high_cvr_band": 0.20,
    "low_cvr_band": 0.20,
    "trend_change_band": 0.20,
    "max_target_acos_multiple_for_scale_up": 1.15,
    "very_high_target_acos_multiple": 1.50,
    "brand_similarity_threshold": 0.82,
    "competitor_frequency_min": 2,
}
ASIN_PATTERN = re.compile(r"\bB0[A-Z0-9]{8}\b", re.IGNORECASE)

STOP_WORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "into",
    "your",
    "that",
    "this",
    "a",
    "an",
    "of",
    "to",
    "in",
    "on",
    "amazon",
    "best",
    "top",
    "buy",
    "near",
    "me",
    "all",
    "one",
    "built",
}
SCENARIO_TOKENS = {
    "adult",
    "adults",
    "family",
    "kids",
    "party",
    "wedding",
    "home",
    "outdoor",
    "gift",
    "birthday",
    "travel",
    "portable",
    "office",
    "school",
    "studio",
    "tv",
    "christmas",
    "holiday",
    "duet",
    "singing",
}
ATTRIBUTE_TOKENS = {
    "screen",
    "display",
    "lyric",
    "lyrics",
    "bluetooth",
    "wireless",
    "microphone",
    "microphones",
    "foldable",
    "adjustable",
    "smart",
    "black",
    "white",
    "pink",
    "red",
    "blue",
    "mini",
    "pro",
    "inch",
    "watt",
    "speaker",
    "stand",
    "library",
    "autotune",
    "mic",
    "mics",
    "songs",
    "led",
    "light",
    "lights",
    "touchscreen",
    "rechargeable",
    "wifi",
    "app",
}
IRRELEVANT_HINTS = {
    "adapter",
    "replacement",
    "repair",
    "manual",
    "used",
    "free",
    "cheap",
    "download",
    "parts",
    "case",
    "cover",
    "charger",
    "remote",
}
NON_BRAND_TOKENS = STOP_WORDS | SCENARIO_TOKENS | ATTRIBUTE_TOKENS | IRRELEVANT_HINTS | {
    "karaoke",
    "machine",
    "machines",
    "system",
    "systems",
    "speaker",
    "speakers",
    "sing",
    "player",
    "professional",
    "quality",
    "grade",
    "profesional",
    "box",
}
CORE_CATEGORY_MARKERS = {"karaoke", "videoke", "machine", "machines", "system", "systems", "player"}
COMPETITOR_STOP_TOKENS = NON_BRAND_TOKENS | {
    "videoke",
    "chinese",
    "korean",
    "high",
    "highest",
    "rated",
    "commercial",
    "equipment",
    "platinum",
    "small",
    "end",
}
TOKEN_EQUIVALENTS = {
    "screen": "display",
    "lyric": "lyrics",
    "mic": "microphone",
    "mics": "microphone",
    "microphones": "microphone",
    "wireless": "bluetooth",
}


@dataclass
class AnalysisContext:
    brand: str | None
    asin: str
    site_code: str
    report_type: str
    target_acos: float | None
    core_tokens: set[str]
    brand_tokens: set[str]
    competitor_tokens: set[str]
    listing_title: str | None
    listing_context_text: str | None
    listing_tokens: set[str]
    listing_source: str | None


def load_known_brands(explicit_brand: str | None) -> list[str]:
    return [explicit_brand] if explicit_brand else []


def load_text_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def infer_title_from_context(text: str | None) -> str | None:
    if not text:
        return None
    for line in text.splitlines():
        title = line.strip().lstrip("#").strip()
        if title:
            return title[:240]
    return None


def load_listing_context_live(asin: str, site_code: str) -> tuple[str | None, str | None, str | None]:
    try:
        payload = fetch_listing_context(asin, site_code)
    except Exception:
        return None, None, None
    if payload.get("page_status") != "ok":
        return None, None, None
    text_parts = []
    if payload.get("description"):
        text_parts.append(str(payload["description"]))
    bullets = payload.get("bullets") or []
    if bullets:
        text_parts.extend(str(item) for item in bullets)
    overview = payload.get("product_overview") or {}
    for key, value in overview.items():
        text_parts.append(f"{key}: {value}")
    breadcrumb = payload.get("breadcrumb")
    if breadcrumb:
        text_parts.append(str(breadcrumb))
    context_text = "\n".join(part for part in text_parts if part).strip() or None
    return payload.get("title") or None, context_text, f"live_amazon_frontend:{site_code.upper()}"


def extract_listing_tokens(title: str | None, extra_text: str | None, brand_tokens: set[str]) -> set[str]:
    token_pool = tokenize(title or "") + tokenize(extra_text or "")
    tokens: set[str] = set()
    for token in token_pool:
        token = normalize_token(token)
        if (
            len(token) < 3
            or token.isdigit()
            or token in STOP_WORDS
            or token in brand_tokens
        ):
            continue
        tokens.add(token)
    return tokens


def tokenize(text: Any) -> list[str]:
    if text is None or (isinstance(text, float) and math.isnan(text)):
        return []
    return re.findall(r"[a-z0-9]+", str(text).lower())


def normalize_token(token: str) -> str:
    return TOKEN_EQUIVALENTS.get(token, token)


def token_similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    if left == right:
        return 1.0
    return SequenceMatcher(None, left, right).ratio()


def token_matches_any(token: str, candidates: set[str], threshold: float) -> bool:
    for candidate in candidates:
        if token == candidate:
            return True
        if len(token) >= 4 and len(candidate) >= 4 and token_similarity(token, candidate) >= threshold:
            return True
    return False


def summarize_candidates(metadata: dict[str, Any]) -> str:
    asin_candidates = metadata.get("asin_candidates") or []
    if not asin_candidates:
        return "未识别到候选 ASIN"
    return ", ".join(f"{item['asin']}({item['rows']})" for item in asin_candidates[:10])


def select_asin(df: pd.DataFrame, metadata: dict[str, Any], asin: str | None) -> str:
    candidates = [item["asin"] for item in metadata.get("asin_candidates") or []]
    if asin:
        asin_upper = asin.upper()
        if candidates and asin_upper not in candidates:
            raise ValueError(
                f"指定的 ASIN {asin_upper} 不在候选列表中。候选：{summarize_candidates(metadata)}"
            )
        return asin_upper

    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        raise ValueError(
            "识别到多个 ASIN，请显式指定 --asin。候选："
            f"{summarize_candidates(metadata)}"
        )

    raise ValueError("未能从报表中识别 ASIN，请显式指定 --asin 或先检查原始报表。")


def infer_core_tokens(df: pd.DataFrame) -> set[str]:
    counter: Counter[str] = Counter()
    for field in ("targeting", "campaign_name", "ad_group_name", "search_term"):
        if field not in df.columns:
            continue
        for value in df[field].dropna().astype(str).head(1500):
            for token in tokenize(value):
                token = normalize_token(token)
                if token in NON_BRAND_TOKENS or token.isdigit() or len(token) <= 1:
                    continue
                counter[token] += 1
    return {token for token, count in counter.most_common(20) if count >= 2}


def is_asin_like_term(term: str) -> bool:
    return bool(ASIN_PATTERN.search(str(term).upper()))


def infer_competitor_tokens(
    df: pd.DataFrame,
    own_brand_tokens: set[str],
    known_brands: list[str],
    core_tokens: set[str],
    threshold: float,
    min_frequency: int,
) -> set[str]:
    candidates: Counter[str] = Counter()
    weighted_clicks: Counter[str] = Counter()
    known_other_tokens = {
        normalize_token(token)
        for brand in known_brands
        for token in tokenize(brand)
        if token and normalize_token(token) not in own_brand_tokens
    }

    sample_df = df[[col for col in ("search_term", "clicks") if col in df.columns]].copy()
    for _, record in sample_df.dropna(subset=["search_term"]).head(3000).iterrows():
        term = str(record["search_term"])
        click_weight = float(record.get("clicks") or 0)
        tokens = [normalize_token(token) for token in tokenize(term)]
        if not tokens:
            continue
        token_set = set(tokens)
        if not (token_set & core_tokens or any(token in known_other_tokens for token in token_set)):
            continue
        for token in tokens[:3]:
            if (
                len(token) < 3
                or token.isdigit()
                or token in COMPETITOR_STOP_TOKENS
                or token in own_brand_tokens
                or token in core_tokens
                or is_asin_like_term(token)
            ):
                continue
            candidates[token] += 1
            weighted_clicks[token] += max(1.0, click_weight)

    inferred = {
        token
        for token, count in candidates.items()
        if count >= min_frequency or weighted_clicks[token] >= 20
    }
    for token in known_other_tokens:
        if token in candidates:
            inferred.add(token)

    # Exclude tokens too similar to the current brand to avoid near-brand typos being treated as competitors.
    return {
        token
        for token in inferred
        if not token_matches_any(token, own_brand_tokens, threshold)
    }


def detect_term_category(term: str, context: AnalysisContext, threshold: float) -> str:
    tokens = {normalize_token(token) for token in tokenize(term)}
    if is_asin_like_term(term):
        return "asin_term"
    if context.brand_tokens and any(
        token_matches_any(token, context.brand_tokens, threshold) for token in tokens
    ):
        return "brand_term"
    if context.competitor_tokens and any(
        token_matches_any(token, context.competitor_tokens, threshold) for token in tokens
    ):
        return "competitor_term"

    core_hits = tokens & context.core_tokens
    attribute_hits = tokens & ATTRIBUTE_TOKENS
    scenario_hits = tokens & SCENARIO_TOKENS

    if tokens & IRRELEVANT_HINTS and not (core_hits or attribute_hits or scenario_hits):
        return "irrelevant_term"
    if attribute_hits and len(attribute_hits) >= len(scenario_hits):
        return "attribute_term"
    if scenario_hits:
        return "scenario_term"
    if core_hits or (tokens & CORE_CATEGORY_MARKERS and {"karaoke", "videoke"} & tokens):
        return "core_category_term"
    if tokens & IRRELEVANT_HINTS:
        return "irrelevant_term"
    return "uncertain_term"


def compute_listing_alignment(term: str, context: AnalysisContext, threshold: float) -> tuple[float, list[str]]:
    tokens = [
        normalize_token(token)
        for token in tokenize(term)
        if len(token) >= 3 and normalize_token(token) not in STOP_WORDS and not token.isdigit()
    ]
    if not tokens or not context.listing_tokens:
        return 0.0, []
    matches: list[str] = []
    comparable = [
        token for token in tokens
        if token not in context.brand_tokens and token not in CORE_CATEGORY_MARKERS and token not in {"karaoke"}
    ]
    base_tokens = comparable or tokens
    for token in base_tokens:
        if token_matches_any(token, context.listing_tokens, threshold):
            matches.append(token)
    score = len(set(matches)) / max(1, len(set(base_tokens)))
    return score, sorted(set(matches))


def aggregate_window(df: pd.DataFrame, window_days: int, anchor_date: pd.Timestamp) -> pd.DataFrame:
    start_date = anchor_date - pd.Timedelta(days=window_days - 1)
    window_df = df[df["date"] >= start_date].copy()
    for column in ("impressions", "clicks", "spend", "orders", "sales"):
        if column not in window_df.columns:
            window_df[column] = 0
    if "match_type" not in window_df.columns:
        window_df["match_type"] = ""
    if window_df.empty:
        return pd.DataFrame(columns=["search_term", "match_type"])

    group_cols = ["search_term"]
    agg = (
        window_df.groupby(group_cols, dropna=False)
        .agg(
            clicks=("clicks", "sum"),
            impressions=("impressions", "sum"),
            spend=("spend", "sum"),
            orders=("orders", "sum"),
            sales=("sales", "sum"),
            match_type=("match_type", lambda x: ",".join(sorted({str(v) for v in x.dropna()}))),
        )
        .reset_index()
    )
    agg["ctr"] = agg["clicks"] / agg["impressions"].replace({0: pd.NA})
    agg["cvr"] = agg["orders"] / agg["clicks"].replace({0: pd.NA})
    agg["cpc"] = agg["spend"] / agg["clicks"].replace({0: pd.NA})
    agg["acos"] = agg["spend"] / agg["sales"].replace({0: pd.NA})
    agg["roas"] = agg["sales"] / agg["spend"].replace({0: pd.NA})
    suffix = f"{window_days}d"
    rename_map = {
        "clicks": f"{suffix}_clicks",
        "impressions": f"{suffix}_impressions",
        "spend": f"{suffix}_spend",
        "orders": f"{suffix}_orders",
        "sales": f"{suffix}_sales",
        "ctr": f"{suffix}_ctr",
        "cvr": f"{suffix}_cvr",
        "cpc": f"{suffix}_cpc",
        "acos": f"{suffix}_acos",
        "roas": f"{suffix}_roas",
        "match_type": "match_type",
    }
    return agg.rename(columns=rename_map)


def choose_primary_match_type(values: pd.Series) -> str:
    valid = [str(v) for v in values.dropna() if str(v).strip()]
    if not valid:
        return ""
    return Counter(valid).most_common(1)[0][0]


def safe_float(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def build_analysis_frame(
    df: pd.DataFrame,
    context: AnalysisContext,
    thresholds: dict[str, float],
) -> tuple[pd.DataFrame, float, float | None]:
    anchor_date = df["date"].dropna().max()
    if pd.isna(anchor_date):
        raise ValueError("报表中缺少可用日期，无法做时间窗分析。")

    window_frames = [aggregate_window(df, window, anchor_date) for window in (7, 14, 30)]
    merged = window_frames[2]
    for frame in window_frames[:2]:
        merged = merged.merge(frame, on=["search_term", "match_type"], how="outer")

    base_window_df = df[df["date"] >= anchor_date - pd.Timedelta(days=29)].copy()
    baseline_clicks = base_window_df["clicks"].sum()
    baseline_orders = base_window_df["orders"].sum()
    baseline_spend = base_window_df["spend"].sum()
    baseline_sales = base_window_df["sales"].sum()
    asin_baseline_cvr = float(baseline_orders / baseline_clicks) if baseline_clicks else 0.0
    asin_baseline_acos = float(baseline_spend / baseline_sales) if baseline_sales else None

    merged["term_category"] = merged["search_term"].astype(str).map(
        lambda value: detect_term_category(
            value,
            context,
            thresholds["brand_similarity_threshold"],
        )
    )
    alignment_pairs = merged["search_term"].astype(str).map(
        lambda value: compute_listing_alignment(
            value,
            context,
            thresholds["brand_similarity_threshold"],
        )
    )
    merged["listing_alignment_score"] = alignment_pairs.map(lambda item: item[0])
    merged["listing_alignment_tokens"] = alignment_pairs.map(lambda item: ", ".join(item[1]))
    merged["relative_cvr_to_baseline"] = merged["30d_cvr"].map(
        lambda value: (float(value) / asin_baseline_cvr - 1) if pd.notna(value) and asin_baseline_cvr else pd.NA
    )
    target_reference = context.target_acos if context.target_acos is not None else asin_baseline_acos
    merged["relative_acos_to_target"] = merged["30d_acos"].map(
        lambda value: (float(value) / target_reference - 1)
        if pd.notna(value) and target_reference not in (None, 0, 0.0)
        else pd.NA
    )

    return merged.fillna(pd.NA), asin_baseline_cvr, asin_baseline_acos


def pct_change(current: Any, base: Any) -> float | None:
    if pd.isna(current) or pd.isna(base) or base in (0, 0.0):
        return None
    return float((current - base) / base)


def determine_trend(row: pd.Series, band: float) -> str:
    cvr_change = pct_change(row.get("7d_cvr"), row.get("30d_cvr"))
    acos_change = pct_change(row.get("7d_acos"), row.get("30d_acos"))
    improving = 0
    worsening = 0
    if cvr_change is not None:
        if cvr_change >= band:
            improving += 1
        elif cvr_change <= -band:
            worsening += 1
    if acos_change is not None:
        if acos_change <= -band:
            improving += 1
        elif acos_change >= band:
            worsening += 1
    if cvr_change is None and acos_change is None:
        return "insufficient_data"
    if improving and worsening:
        return "mixed"
    if improving:
        return "improving"
    if worsening:
        return "worsening"
    return "stable"


def determine_confidence(row: pd.Series, category: str, trend_flag: str, thresholds: dict[str, float]) -> str:
    clicks = safe_float(row.get("30d_clicks")) or 0.0
    spend = safe_float(row.get("30d_spend")) or 0.0
    orders = safe_float(row.get("30d_orders")) or 0.0
    score = 0.0
    if clicks >= thresholds["min_clicks_for_priority"]:
        score += 2.0
    elif clicks >= thresholds["min_clicks_for_judgement"]:
        score += 1.0
    if spend >= thresholds["min_spend_for_attention"]:
        score += 0.5
    if orders >= 3:
        score += 1.5
    elif orders >= 1:
        score += 0.5
    if pd.notna(row.get("7d_cvr")) and pd.notna(row.get("14d_cvr")) and pd.notna(row.get("30d_cvr")):
        score += 1.0
    if trend_flag == "mixed":
        score -= 0.5
    if trend_flag == "insufficient_data":
        score -= 1.0
    if category in {"uncertain_term", "asin_term"}:
        score -= 1.0
    if score >= 3:
        return "high"
    if score >= 1.5:
        return "medium"
    return "low"


def is_listing_feedback_candidate(row: pd.Series, thresholds: dict[str, float]) -> bool:
    category = row.get("term_category")
    clicks = safe_float(row.get("30d_clicks")) or 0.0
    trend_flag = row.get("trend_flag")
    listing_alignment_score = safe_float(row.get("listing_alignment_score")) or 0.0
    if category not in {"attribute_term", "scenario_term"}:
        return False
    if clicks < thresholds["min_clicks_for_listing_feedback"]:
        return False
    if trend_flag == "improving":
        return True
    cvr_30d = safe_float(row.get("30d_cvr")) or 0.0
    return cvr_30d > 0 or listing_alignment_score < 0.34


def choose_decision_tag(
    row: pd.Series,
    context: AnalysisContext,
    asin_baseline_cvr: float,
    asin_baseline_acos: float | None,
    thresholds: dict[str, float],
) -> tuple[str, str]:
    clicks = safe_float(row.get("30d_clicks")) or 0.0
    spend = safe_float(row.get("30d_spend")) or 0.0
    orders = safe_float(row.get("30d_orders")) or 0.0
    cvr = safe_float(row.get("30d_cvr"))
    acos = safe_float(row.get("30d_acos"))
    category = row.get("term_category") or "uncertain_term"
    trend_flag = row.get("trend_flag")
    confidence = row.get("confidence_level") or "low"
    listing_alignment_score = safe_float(row.get("listing_alignment_score")) or 0.0
    listing_alignment_tokens = row.get("listing_alignment_tokens") or ""
    target_acos = context.target_acos if context.target_acos is not None else asin_baseline_acos
    enough_sample = clicks >= thresholds["min_clicks_for_judgement"] or spend >= thresholds["min_spend_for_attention"]
    enough_for_scale = clicks >= thresholds["min_clicks_for_scale_up"]
    priority_sample = clicks >= thresholds["min_clicks_for_priority"]
    no_orders = orders <= 0
    acos_high = (
        target_acos is not None and acos is not None and acos > target_acos
    )
    acos_too_high_for_scale = (
        target_acos is not None
        and acos is not None
        and acos > target_acos * thresholds["max_target_acos_multiple_for_scale_up"]
    )
    acos_very_high = (
        target_acos is not None
        and acos is not None
        and acos > target_acos * thresholds["very_high_target_acos_multiple"]
    )

    if category == "brand_term":
        if priority_sample and (acos_very_high or (no_orders and spend >= thresholds["high_spend_without_orders"])):
            return "reduce_bid", "品牌词成本已偏高，先控 bid，不直接否定"
        return "hold_test", "品牌词单独标记，不直接作为重点放量或否词"
    if category == "asin_term":
        if priority_sample:
            return "manual_review", "ASIN 型搜索词单独标记，需人工判断是竞品流量还是品牌承接"
        return "observe", "点击量和花费都偏低，先观察"
    if category == "competitor_term":
        if priority_sample and (acos_very_high or (no_orders and spend >= thresholds["high_spend_without_orders"])):
            return "manual_review", "竞品词已有明显消耗，但不自动否定，建议人工复核"
        return "hold_test", "竞品词先单独标记，不直接按普通词处理"
    if not enough_sample:
        return "observe", "点击量和花费都偏低，先观察"

    if cvr is not None and asin_baseline_cvr > 0:
        high_line = asin_baseline_cvr * (1 + thresholds["high_cvr_band"])
        low_line = asin_baseline_cvr * (1 - thresholds["low_cvr_band"])
        near_low = asin_baseline_cvr * (1 - thresholds["near_avg_cvr_band"])
        near_high = asin_baseline_cvr * (1 + thresholds["near_avg_cvr_band"])

        if cvr >= high_line and category != "irrelevant_term":
            if confidence == "low" or not enough_for_scale:
                if row.get("listing_feedback_candidate"):
                    return "listing_feedback", "词表现高于基准，但样本仍偏小，建议先反馈到 Listing / 投放语义并继续测试"
                return "hold_test", "高于该 ASIN 基准 CVR，但样本仍偏小，先保持测试"
            if acos_too_high_for_scale:
                return "hold_test", "转化高于基准，但 ACOS 偏高，先控成本再决定是否放量"
            if category in {"attribute_term", "scenario_term"}:
                return "scale_up", "高于该 ASIN 基准 CVR，且具备属性/场景扩展价值"
            return "scale_up", "高于该 ASIN 基准 CVR，可优先考虑放量"

        if near_low <= cvr <= near_high:
            if acos_high:
                if priority_sample or trend_flag == "worsening":
                    return "reduce_bid", "CVR 接近基准，但 ACOS 高于目标，先控 bid"
                return "hold_test", "CVR 接近基准，但成本偏高，先保持并跟踪"
            if row.get("listing_feedback_candidate") and trend_flag in {"improving", "stable"}:
                return "listing_feedback", "属性/场景词接近基准且语义有价值，建议反馈到 Listing / 投放策略"
            return "hold_test", "CVR 接近基准，可保持或小幅测试"

        if cvr <= low_line:
            if category == "irrelevant_term" or (
                category in {"uncertain_term", "core_category_term"}
                and listing_alignment_score <= 0.15
                and no_orders
                and priority_sample
            ):
                if priority_sample or spend >= thresholds["high_spend_without_orders"] or trend_flag == "worsening":
                    return "negative_candidate", "低于该 ASIN 基准 CVR，且与 Listing 卖点弱相关"
                return "observe", "词义偏弱相关，但当前样本还不够强"
            if no_orders and (priority_sample or spend >= thresholds["high_spend_without_orders"]):
                if category in {"attribute_term", "scenario_term"} and row.get("listing_feedback_candidate"):
                    return "listing_feedback", "搜索词转化偏弱，但反映了真实属性/场景需求，建议反馈给 Listing 后再继续观察"
                if category in {"core_category_term", "attribute_term", "scenario_term"}:
                    if spend >= thresholds["high_spend_without_orders"] or priority_sample or trend_flag in {"worsening", "mixed"}:
                        return "reduce_bid", "低于基准且已产生明显消耗，先降 bid 控成本"
                    return "observe", "低于基准，但当前更适合继续观察或补充样本"
            if acos_high and (priority_sample or trend_flag == "worsening"):
                return "reduce_bid", "低于基准且 ACOS 偏高，先降 bid 控成本"
            if row.get("listing_feedback_candidate") and trend_flag == "improving":
                return "listing_feedback", "搜索词长期表现一般，但短期趋势改善，建议先反馈到 Listing / 投放语义"
            if category in {"attribute_term", "scenario_term", "core_category_term"}:
                return "observe", "低于基准，但当前更适合继续观察或补充样本"
            if confidence == "high":
                if listing_alignment_score >= 0.3:
                    return "manual_review", f"低于基准且样本充足，但与 Listing 仍有相关词（{listing_alignment_tokens or '已命中'}），需人工复核"
                return "observe", "低于基准且词义不够清晰，先观察"
            return "observe", "低于基准，但当前证据不足以下强结论"

    if row.get("listing_feedback_candidate") and trend_flag == "improving":
        return "listing_feedback", "属性/场景词趋势改善，建议反馈给 Listing 与投放策略"
    if category == "uncertain_term" and priority_sample:
        return "manual_review", "词义暂不明确，但已有较多点击，建议人工复核"
    if acos_high and priority_sample:
        return "reduce_bid", "成本已偏高，先控 bid"
    return "observe", "未命中强规则，先观察"


def add_decision_columns(
    frame: pd.DataFrame,
    context: AnalysisContext,
    asin_baseline_cvr: float,
    asin_baseline_acos: float | None,
    thresholds: dict[str, float],
) -> pd.DataFrame:
    result = frame.copy()
    result["trend_flag"] = result.apply(
        lambda row: determine_trend(row, thresholds["trend_change_band"]), axis=1
    )
    result["confidence_level"] = result.apply(
        lambda row: determine_confidence(row, row.get("term_category") or "uncertain_term", row.get("trend_flag"), thresholds),
        axis=1,
    )
    result["listing_feedback_candidate"] = result.apply(
        lambda row: is_listing_feedback_candidate(row, thresholds),
        axis=1,
    )
    tags: list[str] = []
    reasons: list[str] = []
    for _, row in result.iterrows():
        tag, reason = choose_decision_tag(row, context, asin_baseline_cvr, asin_baseline_acos, thresholds)
        tags.append(tag)
        reasons.append(reason)
    result["decision_tag"] = tags
    result["decision_reason"] = reasons
    result["listing_feedback"] = result.apply(
        lambda row: bool(row["listing_feedback_candidate"]) or row["decision_tag"] == "listing_feedback",
        axis=1,
    )
    result["priority_score"] = (
        result["30d_clicks"].fillna(0) * 2
        + result["30d_spend"].fillna(0)
        + result["listing_feedback_candidate"].map(lambda flag: 3 if flag else 0)
        + result["decision_tag"].map(
            {
                "negative_candidate": 6,
                "reduce_bid": 5,
                "scale_up": 4,
                "listing_feedback": 3,
                "manual_review": 2,
            }
        ).fillna(0)
    )
    result = result.sort_values(["priority_score", "30d_clicks"], ascending=False)
    return result


def export_outputs(
    frame: pd.DataFrame,
    context: AnalysisContext,
    asin_baseline_cvr: float,
    asin_baseline_acos: float | None,
    output_dir: Path,
    windows_label: str,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    date_prefix = pd.Timestamp.today().strftime("%Y-%m-%d")
    brand_label = context.brand or "未识别品牌"

    details_path = output_dir / f"{date_prefix}_{brand_label}_{context.asin}_{windows_label}_搜索词分析明细.csv"
    anomalies_path = output_dir / f"{date_prefix}_{brand_label}_{context.asin}_{windows_label}_异常清单.csv"
    report_path = output_dir / f"{date_prefix}_{brand_label}_{context.asin}_{windows_label}_搜索词报告分析.md"
    summary_path = output_dir / f"{date_prefix}_{brand_label}_{context.asin}_{windows_label}_run_summary.json"

    details_cols = [
        "search_term",
        "term_category",
        "decision_tag",
        "decision_reason",
        "confidence_level",
        "match_type",
        "7d_clicks",
        "14d_clicks",
        "30d_clicks",
        "30d_orders",
        "30d_spend",
        "7d_cvr",
        "14d_cvr",
        "30d_cvr",
        "30d_acos",
        "trend_flag",
        "relative_cvr_to_baseline",
        "relative_acos_to_target",
        "listing_alignment_score",
        "listing_alignment_tokens",
        "listing_feedback",
    ]
    existing_detail_cols = [col for col in details_cols if col in frame.columns]
    frame[existing_detail_cols].to_csv(details_path, index=False, encoding="utf-8-sig")

    anomaly_mask = frame["decision_tag"].isin(
        ["negative_candidate", "reduce_bid", "manual_review"]
    )
    frame.loc[anomaly_mask, existing_detail_cols].to_csv(
        anomalies_path, index=False, encoding="utf-8-sig"
    )

    counts = frame["decision_tag"].value_counts().to_dict()
    potential_attribute_mask = frame["listing_feedback"].fillna(False)
    attribute_count = int(potential_attribute_mask.sum())
    observe_count = int(counts.get("observe", 0) + counts.get("manual_review", 0))
    negative_count = int(counts.get("negative_candidate", 0))
    reduce_bid_count = int(counts.get("reduce_bid", 0))
    scale_up_count = int(counts.get("scale_up", 0))
    listing_feedback_count = int(counts.get("listing_feedback", 0))

    report_lines = [
        "# 亚马逊搜索词报告分析",
        "",
        "## 分析对象",
        f"- 品牌：{brand_label}",
        f"- ASIN：{context.asin}",
        f"- 站点：{context.site_code}",
        f"- 报告类型：{context.report_type}",
        f"- 分析窗口：{windows_label}",
        f"- ASIN广告CVR基准：{asin_baseline_cvr:.2%}" if asin_baseline_cvr else "- ASIN广告CVR基准：暂无",
        (
            f"- ASIN广告ACOS基准：{asin_baseline_acos:.2%}"
            if asin_baseline_acos is not None
            else "- ASIN广告ACOS基准：暂无"
        ),
        (f"- Listing标题：{context.listing_title}" if context.listing_title else "- Listing标题：暂无本地上下文"),
        (f"- Listing上下文来源：{context.listing_source}" if context.listing_source else "- Listing上下文来源：暂无"),
        (
            f"- 识别到的竞品品牌/词根：{', '.join(sorted(context.competitor_tokens)[:10])}"
            if context.competitor_tokens
            else "- 识别到的竞品品牌/词根：暂无明确候选"
        ),
        "",
        "## 核心结论摘要",
        f"- 否词候选：{negative_count} 个",
        f"- 先控 bid / 成本偏高：{reduce_bid_count} 个",
        f"- 放量候选：{scale_up_count} 个",
        f"- 潜力属性词 / 场景词：{attribute_count} 个",
        f"- 直接进入 Listing / 投放语义反馈：{listing_feedback_count} 个",
        f"- 需继续观察或人工复核：{observe_count} 个",
        "",
        "## 否词候选",
        "| 搜索词 | 原因 | 30天点击 | 30天CVR | 30天ACOS |",
        "|--------|------|----------|---------|----------|",
    ]
    negatives = frame[frame["decision_tag"] == "negative_candidate"].head(20)
    if negatives.empty:
        report_lines.append("| — | 暂无 | — | — | — |")
    else:
        for _, row in negatives.iterrows():
            cvr_text = "" if pd.isna(row.get("30d_cvr")) else f"{float(row['30d_cvr']):.2%}"
            acos_text = "" if pd.isna(row.get("30d_acos")) else f"{float(row['30d_acos']):.2%}"
            report_lines.append(
                f"| {row['search_term']} | {row['decision_reason']} | "
                f"{int(row.get('30d_clicks') or 0)} | "
                f"{cvr_text} | "
                f"{acos_text} |"
            )

    report_lines.extend(
        [
            "",
            "## 控成本候选",
            "| 搜索词 | 分类 | 原因 | 30天点击 | 30天ACOS |",
            "|--------|------|------|----------|----------|",
        ]
    )
    reduce_bids = frame[frame["decision_tag"] == "reduce_bid"].head(20)
    if reduce_bids.empty:
        report_lines.append("| — | — | 暂无 | — | — |")
    else:
        for _, row in reduce_bids.iterrows():
            acos_text = "" if pd.isna(row.get("30d_acos")) else f"{float(row['30d_acos']):.2%}"
            report_lines.append(
                f"| {row['search_term']} | {row['term_category']} | {row['decision_reason']} | "
                f"{int(row.get('30d_clicks') or 0)} | {acos_text} |"
            )

    report_lines.extend(
        [
            "",
            "## 放量候选",
            "| 搜索词 | 分类 | 原因 | 30天点击 | 30天CVR | 置信度 |",
            "|--------|------|------|----------|---------|--------|",
        ]
    )
    scale_ups = frame[frame["decision_tag"] == "scale_up"].head(20)
    if scale_ups.empty:
        report_lines.append("| — | — | 暂无 | — | — | — |")
    else:
        for _, row in scale_ups.iterrows():
            cvr_text = "" if pd.isna(row.get("30d_cvr")) else f"{float(row['30d_cvr']):.2%}"
            report_lines.append(
                f"| {row['search_term']} | {row['term_category']} | {row['decision_reason']} | "
                f"{int(row.get('30d_clicks') or 0)} | "
                f"{cvr_text} | {row['confidence_level']} |"
            )

    report_lines.extend(
        [
            "",
            "## 属性词 / 场景词洞察",
            "| 搜索词 | 分类 | 趋势 | 决策 | Listing对齐词 | 是否反馈Listing |",
            "|--------|------|------|------|---------------|------------------|",
        ]
    )
    insights = frame[frame["term_category"].isin(["attribute_term", "scenario_term"])].head(20)
    if insights.empty:
        report_lines.append("| — | — | — | 暂无 | — | — |")
    else:
        for _, row in insights.iterrows():
            report_lines.append(
                f"| {row['search_term']} | {row['term_category']} | {row['trend_flag']} | {row['decision_tag']} | {row.get('listing_alignment_tokens') or '—'} | {'是' if row['listing_feedback'] else '否'} |"
            )

    report_lines.extend(
        [
            "",
            "## 需继续观察 / 人工复核",
            "| 搜索词 | 原因 | 建议 |",
            "|--------|------|------|",
        ]
    )
    reviews = frame[frame["decision_tag"].isin(["observe", "manual_review"])].head(20)
    if reviews.empty:
        report_lines.append("| — | 暂无 | — |")
    else:
        for _, row in reviews.iterrows():
            report_lines.append(
                f"| {row['search_term']} | {row['decision_reason']} | {row['decision_tag']} |"
            )

    report_lines.extend(
        [
            "",
            "## 行动建议",
            "### 立即处理",
            f"- 优先复核否词候选 {negative_count} 个，先看高点击和高花费词。",
            f"- 对成本偏高词 {reduce_bid_count} 个，优先看 ACOS 明显高于目标 ACOS 的词。",
            "### 建议测试",
            f"- 放量候选 {scale_up_count} 个，可结合目标 ACOS 做小步测试。",
            "### 持续观察",
            f"- 观察 / 人工复核词 {observe_count} 个，避免在数据不足时下强结论。",
            "### 反馈到 Listing / 投放策略",
            f"- 属性词 / 场景词 {attribute_count} 个，建议同步回看 Listing 与投放方向。",
            "",
        ]
    )
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    summary = {
        "brand": brand_label,
        "asin": context.asin,
        "site": context.site_code,
        "report_type": context.report_type,
        "asin_baseline_cvr": asin_baseline_cvr,
        "asin_baseline_acos": asin_baseline_acos,
        "competitor_tokens": sorted(context.competitor_tokens),
        "listing_title": context.listing_title,
        "listing_source": context.listing_source,
        "negative_candidate_count": negative_count,
        "reduce_bid_count": reduce_bid_count,
        "scale_up_count": scale_up_count,
        "attribute_or_scenario_count": attribute_count,
        "listing_feedback_count": listing_feedback_count,
        "observe_or_manual_count": observe_count,
        "details_csv": str(details_path),
        "anomalies_csv": str(anomalies_path),
        "report_md": str(report_path),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="按单 ASIN 生成搜索词决策分析结果")
    parser.add_argument("input_file", help="原始搜索词报告路径（csv/xlsx）")
    parser.add_argument("--output-dir", help="输出目录，默认写入 outputs/search-term-report-analyzer/<brand>/")
    parser.add_argument("--brand", help="显式指定品牌，覆盖自动识别")
    parser.add_argument("--asin", help="显式指定分析的 ASIN")
    parser.add_argument("--site", default="US", help="显式指定站点代码（US/UK/DE...），默认 US")
    parser.add_argument("--report-type", help="显式指定报告类型（SP/SB/SD）")
    parser.add_argument(
        "--listing-context-file",
        help="可选：额外的 listing 上下文文件（txt/md/json），用于增强词义相关性判断",
    )
    parser.add_argument(
        "--skip-live-listing-fetch",
        action="store_true",
        help="跳过按 ASIN 访问亚马逊前台抓取 Listing 上下文",
    )
    parser.add_argument(
        "--target-acos",
        type=float,
        help="显式指定目标 ACOS（如 0.20 表示 20%%）。不传则使用报表自身 ACOS 基准作参考",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input_file).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    normalized_df, metadata = build_normalized_frame(input_path, brand=args.brand)
    if metadata["missing_core_fields"]:
        raise ValueError(
            "缺少核心字段，无法继续分析："
            + ", ".join(metadata["missing_core_fields"])
        )

    selected_asin = select_asin(normalized_df, metadata, args.asin)
    filtered_df = normalized_df[normalized_df["asin"].astype(str).str.upper() == selected_asin].copy()
    if filtered_df.empty:
        raise ValueError(f"选定 ASIN {selected_asin} 在报表中没有可用数据。")

    brand = args.brand or (metadata["brand_candidates"][0]["brand"] if metadata["brand_candidates"] else None)
    brand_label = brand or "unknown"
    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else Path.cwd() / "outputs" / "search-term-report-analyzer" / brand_label
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    site_code = args.site or "US"
    report_type = args.report_type or metadata["report_type"]
    target_acos = args.target_acos
    core_tokens = infer_core_tokens(filtered_df)
    brand_tokens = {normalize_token(token) for token in tokenize(brand) if len(token) > 1} if brand else set()
    listing_title = None
    listing_source = None
    live_listing_title = None
    live_listing_context = None
    live_listing_source = None
    if not args.skip_live_listing_fetch:
        live_listing_title, live_listing_context, live_listing_source = load_listing_context_live(selected_asin, site_code)
    if not listing_title and live_listing_title:
        listing_title = live_listing_title
    combined_source_parts = [part for part in [listing_source, live_listing_source] if part]
    listing_source = "; ".join(combined_source_parts) if combined_source_parts else None
    external_listing_context = None
    if args.listing_context_file:
        context_path = Path(args.listing_context_file).expanduser().resolve()
        context_label = args.listing_context_file
        external_listing_context = load_text_file(context_path)
        if external_listing_context:
            listing_title = listing_title or infer_title_from_context(external_listing_context)
            listing_source = (
                f"{listing_source}; external:{context_label}"
                if listing_source
                else f"external:{context_label}"
            )
    combined_listing_context = "\n\n".join(
        part for part in [live_listing_context, external_listing_context] if part
    ) or None
    listing_tokens = extract_listing_tokens(listing_title, combined_listing_context, brand_tokens)
    competitor_tokens = infer_competitor_tokens(
        filtered_df,
        own_brand_tokens=brand_tokens,
        known_brands=load_known_brands(brand),
        core_tokens=core_tokens,
        threshold=DEFAULT_THRESHOLDS["brand_similarity_threshold"],
        min_frequency=int(DEFAULT_THRESHOLDS["competitor_frequency_min"]),
    )
    context = AnalysisContext(
        brand=brand,
        asin=selected_asin,
        site_code=site_code,
        report_type=report_type,
        target_acos=target_acos,
        core_tokens=core_tokens,
        brand_tokens=brand_tokens,
        competitor_tokens=competitor_tokens,
        listing_title=listing_title,
        listing_context_text=combined_listing_context,
        listing_tokens=listing_tokens,
        listing_source=listing_source,
    )

    frame, asin_baseline_cvr, asin_baseline_acos = build_analysis_frame(filtered_df, context, DEFAULT_THRESHOLDS)
    frame = add_decision_columns(frame, context, asin_baseline_cvr, asin_baseline_acos, DEFAULT_THRESHOLDS)
    summary = export_outputs(frame, context, asin_baseline_cvr, asin_baseline_acos, output_dir, "7-14-30天")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
