from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from datetime import date, timedelta
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import numpy as np
import pandas as pd


def generate_business_sample(seed: int = 20260829, days: int = 84) -> pd.DataFrame:
    rng = random.Random(seed)
    start = date(2026, 5, 4)
    channels = ("自然", "内容", "付费", "转介绍")
    regions = ("华东", "华南", "华北", "西南")
    rows: list[dict] = []
    for index in range(days):
        current = start + timedelta(days=index)
        channel = channels[index % len(channels)]
        region = regions[(index // 3) % len(regions)]
        visits = 700 + index * 5 + rng.randint(-80, 100)
        if index == 48:
            visits *= 3
        leads = max(1, round(visits * (0.07 + rng.uniform(-0.012, 0.012))))
        orders = max(1, round(leads * (0.28 + rng.uniform(-0.05, 0.05))))
        revenue = round(orders * (260 + rng.uniform(-35, 45)), 2)
        cost = round(visits * (1.15 + rng.uniform(-0.15, 0.2)), 2)
        rows.append(
            {
                "日期": current.isoformat(),
                "渠道": channel,
                "区域": region,
                "访问量": visits,
                "线索数": leads,
                "订单数": orders,
                "收入": revenue,
                "成本": cost,
            }
        )
    rows[11]["收入"] = None
    rows.append(dict(rows[20]))
    return pd.DataFrame(rows)


def generate_personal_sample(seed: int = 20260829, days: int = 42) -> pd.DataFrame:
    rng = random.Random(seed)
    start = date(2026, 7, 6)
    projects = ("求职准备", "AI学习", "作品打磨")
    return pd.DataFrame(
        [
            {
                "日期": (start + timedelta(days=index)).isoformat(),
                "项目": projects[index % len(projects)],
                "专注分钟": 45 + rng.randint(0, 75),
                "完成任务数": 1 + rng.randint(0, 4),
            }
            for index in range(days)
        ]
    )


def generate_retail_main_case(
    seed: int = 20260829, rows: int = 100_000
) -> pd.DataFrame:
    if rows < 548:
        raise ValueError("主案例至少需要 548 行，才能完整覆盖 18 个月日期范围")
    rng = np.random.default_rng(seed)
    calendar = pd.date_range("2024-01-01", "2025-06-30", freq="D")
    dates = calendar[np.arange(rows) % len(calendar)]
    order = rng.permutation(rows)
    dates = dates[order]

    channels = rng.choice(
        np.array(["自然搜索", "内容种草", "付费广告", "转介绍"]),
        rows,
        p=[0.30, 0.25, 0.30, 0.15],
    )
    regions = rng.choice(
        np.array(["华东", "华南", "华北", "西南"]),
        rows,
        p=[0.34, 0.28, 0.22, 0.16],
    )
    categories = rng.choice(
        np.array(["数码", "家居", "办公", "服饰", "食品"]),
        rows,
        p=[0.20, 0.22, 0.18, 0.23, 0.17],
    )
    segments = rng.choice(
        np.array(["新客", "活跃客", "高价值客", "沉睡唤醒"]),
        rows,
        p=[0.36, 0.35, 0.16, 0.13],
    )

    day_index = (dates - calendar[0]).days.to_numpy()
    month = dates.month.to_numpy()
    q2_2025 = (dates >= pd.Timestamp("2025-04-01")) & (
        dates <= pd.Timestamp("2025-06-30")
    )
    year_end = np.isin(month, [11, 12])
    trend = 1.0 + day_index * 0.00055
    seasonality = np.where(year_end, 1.45, np.where(np.isin(month, [6, 9]), 1.10, 1.0))
    channel_traffic = np.select(
        [channels == "自然搜索", channels == "内容种草", channels == "付费广告"],
        [1.10, 0.95, 1.28],
        default=0.72,
    )
    content_boost = np.where((channels == "内容种草") & q2_2025, 1.32, 1.0)
    visit_mean = 62 * trend * seasonality * channel_traffic * content_boost
    visits = np.maximum(5, rng.poisson(visit_mean)).astype(int)

    channel_conversion = np.select(
        [channels == "自然搜索", channels == "内容种草", channels == "付费广告"],
        [1.12, 1.02, 0.94],
        default=1.34,
    )
    segment_conversion = np.select(
        [segments == "新客", segments == "高价值客", segments == "沉睡唤醒"],
        [0.78, 1.55, 0.62],
        default=1.12,
    )
    paid_decline = np.where((channels == "付费广告") & q2_2025, 0.68, 1.0)
    content_conversion_lift = np.where((channels == "内容种草") & q2_2025, 1.16, 1.0)
    conversion = np.clip(
        0.046
        * channel_conversion
        * segment_conversion
        * paid_decline
        * content_conversion_lift,
        0.006,
        0.16,
    )
    orders = rng.binomial(visits, conversion).astype(int)

    category_aov = np.select(
        [categories == "数码", categories == "家居", categories == "办公", categories == "服饰"],
        [720.0, 390.0, 260.0, 310.0],
        default=145.0,
    )
    segment_aov = np.select(
        [segments == "新客", segments == "高价值客", segments == "沉睡唤醒"],
        [0.86, 1.42, 0.80],
        default=1.04,
    )
    aov = category_aov * segment_aov * rng.lognormal(mean=0.0, sigma=0.13, size=rows)
    revenue = np.round(orders * aov, 2)

    base_refund_probability = np.select(
        [categories == "服饰", categories == "数码", categories == "家居"],
        [0.115, 0.055, 0.048],
        default=0.032,
    )
    apparel_risk = np.where((categories == "服饰") & q2_2025, 0.095, 0.0)
    refund_probability = np.clip(base_refund_probability + apparel_risk, 0.0, 0.35)
    refund_orders = rng.binomial(orders, refund_probability).astype(int)
    refund_severity = rng.uniform(0.72, 1.0, rows)
    refund_amount = np.round(
        np.where(orders > 0, revenue * refund_orders / np.maximum(orders, 1) * refund_severity, 0),
        2,
    )

    cpc = np.select(
        [channels == "付费广告", channels == "内容种草", channels == "自然搜索"],
        [2.85, 1.05, 0.42],
        default=0.58,
    )
    paid_cost_pressure = np.where((channels == "付费广告") & q2_2025, 1.38, 1.0)
    marketing_cost = np.round(
        visits * cpc * paid_cost_pressure * rng.uniform(0.92, 1.08, rows), 2
    )

    return pd.DataFrame(
        {
            "日期": pd.Series(dates).dt.strftime("%Y-%m-%d"),
            "渠道": channels,
            "区域": regions,
            "品类": categories,
            "用户层级": segments,
            "访问量": visits,
            "订单数": orders,
            "收入": revenue,
            "退款订单数": refund_orders,
            "退款金额": refund_amount,
            "营销成本": marketing_cost,
        }
    )


def _synthetic_provenance(*, seed: int, row_count: int) -> dict:
    return {
        "kind": "synthetic",
        "generator": "scripts/generate_sample.py",
        "seed": int(seed),
        "row_count": int(row_count),
    }


def build_retail_known_answers(frame: pd.DataFrame, *, seed: int = 20260829) -> dict:
    work = frame.copy()
    work["日期"] = pd.to_datetime(work["日期"])

    def period_slice(start: str, end: str) -> pd.DataFrame:
        return work[(work["日期"] >= start) & (work["日期"] <= end)]

    def ratio(data: pd.DataFrame, numerator: str, denominator: str) -> float:
        denominator_value = float(data[denominator].sum())
        return 0.0 if denominator_value == 0 else float(data[numerator].sum()) / denominator_value

    q2_2024 = period_slice("2024-04-01", "2024-06-30")
    q2_2025 = period_slice("2025-04-01", "2025-06-30")
    paid_2024 = q2_2024[q2_2024["渠道"] == "付费广告"]
    paid_2025 = q2_2025[q2_2025["渠道"] == "付费广告"]
    content_2024 = q2_2024[q2_2024["渠道"] == "内容种草"]
    content_2025 = q2_2025[q2_2025["渠道"] == "内容种草"]
    apparel_2024 = q2_2024[q2_2024["品类"] == "服饰"]
    apparel_2025 = q2_2025[q2_2025["品类"] == "服饰"]
    monthly_revenue = work.assign(月份=work["日期"].dt.to_period("M").astype(str)).groupby("月份")["收入"].sum()
    q4_2024 = monthly_revenue.loc["2024-10":"2024-12"]
    h1_2024 = monthly_revenue.loc["2024-01":"2024-06"]

    scenarios = {
        "paid_efficiency_decline": {
            "q2_2024_roas": round(ratio(paid_2024, "收入", "营销成本"), 4),
            "q2_2025_roas": round(ratio(paid_2025, "收入", "营销成本"), 4),
            "q2_2024_conversion": round(ratio(paid_2024, "订单数", "访问量"), 4),
            "q2_2025_conversion": round(ratio(paid_2025, "订单数", "访问量"), 4),
        },
        "content_growth_opportunity": {
            "q2_2024_revenue": round(float(content_2024["收入"].sum()), 2),
            "q2_2025_revenue": round(float(content_2025["收入"].sum()), 2),
            "q2_2024_roas": round(ratio(content_2024, "收入", "营销成本"), 4),
            "q2_2025_roas": round(ratio(content_2025, "收入", "营销成本"), 4),
        },
        "apparel_refund_risk": {
            "q2_2024_refund_rate": round(ratio(apparel_2024, "退款金额", "收入"), 4),
            "q2_2025_refund_rate": round(ratio(apparel_2025, "退款金额", "收入"), 4),
        },
        "year_end_seasonality": {
            "q4_2024_monthly_revenue_mean": round(float(q4_2024.mean()), 2),
            "h1_2024_monthly_revenue_mean": round(float(h1_2024.mean()), 2),
        },
    }
    paid = scenarios["paid_efficiency_decline"]
    content = scenarios["content_growth_opportunity"]
    apparel = scenarios["apparel_refund_risk"]
    seasonality_answer = scenarios["year_end_seasonality"]
    checks = {
        "paid_roas_drop_at_least_35pct": paid["q2_2025_roas"]
        <= paid["q2_2024_roas"] * 0.65,
        "paid_conversion_drop_at_least_20pct": paid["q2_2025_conversion"]
        <= paid["q2_2024_conversion"] * 0.80,
        "content_revenue_growth_at_least_50pct": content["q2_2025_revenue"]
        >= content["q2_2024_revenue"] * 1.50,
        "apparel_refund_rate_rises_at_least_5pp": apparel["q2_2025_refund_rate"]
        >= apparel["q2_2024_refund_rate"] + 0.05,
        "q4_monthly_revenue_at_least_25pct_above_h1": seasonality_answer[
            "q4_2024_monthly_revenue_mean"
        ]
        >= seasonality_answer["h1_2024_monthly_revenue_mean"] * 1.25,
    }
    return {
        "row_count": int(len(frame)),
        "seed": int(seed),
        "provenance": _synthetic_provenance(seed=seed, row_count=len(frame)),
        "date_range": ["2024-01-01", "2025-06-30"],
        "scenarios": scenarios,
        "validation": {
            "status": "passed" if all(checks.values()) else "failed",
            "checks": checks,
        },
    }


def _retail_main_request(source_path: str = "retail-omnichannel-main.csv") -> dict:
    return {
        "source_path": source_path,
        "mode": "professional",
        "period_type": "monthly",
        "audience": "经营管理层与业务负责人",
        "objective": "复盘全渠道经营表现，定位增长机会、效率风险与下一周期行动",
        "analysis_intent": "business_review",
        "analysis_profile": "retail_growth",
        "report_subject": "全渠道零售经营分析简报",
        "report_subtitle": "2024年1月至2025年6月经营复盘",
        "date_column": "日期",
        "primary_metrics": ["收入", "订单数", "转化率", "退款率", "营销成本", "ROAS"],
        "dimensions": ["渠道", "区域", "品类", "用户层级"],
        "metric_contracts": [
            {"name": "收入", "aggregation": "sum", "unit": "元"},
            {"name": "订单数", "aggregation": "sum", "unit": "单"},
            {"name": "转化率", "aggregation": "ratio", "numerator": "订单数", "denominator": "访问量", "unit": "%", "scale": 100},
            {"name": "退款率", "aggregation": "ratio", "numerator": "退款金额", "denominator": "收入", "unit": "%", "scale": 100},
            {"name": "营销成本", "aggregation": "sum", "unit": "元"},
            {"name": "ROAS", "aggregation": "ratio", "numerator": "收入", "denominator": "营销成本", "unit": "x", "scale": 1},
        ],
        "comparisons": ["period_over_period", "year_over_year"],
        "incomplete_period_policy": "exclude",
        "theme": "corporate",
        "ppt_refinement": "offer_slideviber",
        "output_mode": "report+pptx",
    }


def _write_case_artifacts(
    output_dir: Path,
    *,
    file_stem: str,
    frame: pd.DataFrame,
    request: dict,
    known_answers: dict,
) -> tuple[Path, Path, dict]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"{file_stem}.csv"
    frame.to_csv(csv_path, index=False, encoding="utf-8")
    xlsx_path = csv_path.with_suffix(".xlsx")
    frame.to_excel(xlsx_path, index=False)
    _normalize_xlsx_archive(xlsx_path)
    request_path = output_dir / "request.json"
    request_path.write_text(json.dumps(request, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "known_answers.json").write_text(
        json.dumps(known_answers, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return csv_path, request_path, known_answers


def _normalize_xlsx_archive(path: Path) -> None:
    """Remove writer clock metadata so fixed-seed case artifacts hash identically."""

    with ZipFile(path, "r") as source:
        entries = sorted(
            ((entry, source.read(entry.filename)) for entry in source.infolist()),
            key=lambda item: item[0].filename,
        )
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as target:
        for original, content in entries:
            if original.filename == "docProps/core.xml":
                content = re.sub(
                    rb"(<dcterms:(created|modified)[^>]*>)[^<]*(</dcterms:\2>)",
                    lambda match: match.group(1) + b"2000-01-01T00:00:00Z" + match.group(3),
                    content,
                )
            entry = ZipInfo(original.filename, date_time=(2000, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = original.external_attr
            target.writestr(entry, content)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _ranked_dimension_answer(frame: pd.DataFrame, dimension: str, metric: str) -> dict:
    totals = frame.groupby(dimension, sort=True)[metric].sum().sort_values(ascending=False)
    return {
        "dimension": dimension,
        "metric": metric,
        "top_value": str(totals.index[0]),
        "top_metric": round(float(totals.iloc[0]), 2),
    }


def build_content_operations_known_answers(
    frame: pd.DataFrame, *, seed: int = 20260901
) -> dict:
    return {
        "row_count": int(len(frame)),
        "seed": int(seed),
        "provenance": _synthetic_provenance(seed=seed, row_count=len(frame)),
        "metric_totals": {
            metric: round(float(frame[metric].sum()), 2)
            for metric in ("impressions", "clicks", "leads", "conversions", "cost")
        },
        "dimension_answers": [
            _ranked_dimension_answer(frame, "channel", "conversions"),
            _ranked_dimension_answer(frame, "content_type", "conversions"),
        ],
        "quality_tradeoff": {
            "highest_reach_channel": _ranked_dimension_answer(frame, "channel", "impressions")["top_value"],
            "highest_conversion_channel": _ranked_dimension_answer(frame, "channel", "conversions")["top_value"],
            "conversion_rate_by_channel": {
                str(channel): round(float(group["conversions"].sum() / group["clicks"].sum()), 4)
                for channel, group in frame.groupby("channel", sort=True)
            },
        },
    }


def generate_content_operations_case(
    output_dir: Path, rows: int = 20_000, seed: int = 20260901
) -> tuple[Path, Path, dict]:
    if rows < 365:
        raise ValueError("内容运营案例至少需要 365 行，才能覆盖完整年度周期")
    rng = np.random.default_rng(seed)
    calendar = pd.date_range("2024-01-01", "2025-06-30", freq="D")
    dates = calendar[rng.permutation(rows) % len(calendar)]
    channels = rng.choice(np.array(["organic", "community", "paid", "partner"]), rows, p=[0.30, 0.30, 0.25, 0.15])
    content_types = rng.choice(np.array(["article", "short_video", "live_session"]), rows, p=[0.35, 0.45, 0.20])
    date_index = (dates - calendar[0]).days.to_numpy()
    reach_multiplier = np.select(
        [channels == "organic", channels == "community", channels == "paid"],
        [1.0, 1.18, 1.62],
        default=0.76,
    )
    type_reach_multiplier = np.select(
        [content_types == "short_video", content_types == "live_session"], [1.22, 0.90], default=1.0
    )
    impressions = np.maximum(
        100, rng.poisson(1_100 * (1 + date_index * 0.00045) * reach_multiplier * type_reach_multiplier)
    ).astype(int)
    click_rate = np.clip(
        0.065
        * np.select([content_types == "short_video", content_types == "live_session"], [1.30, 0.82], default=0.95)
        * np.select([channels == "community", channels == "paid"], [1.10, 0.78], default=1.0),
        0.01,
        0.25,
    )
    clicks = rng.binomial(impressions, click_rate).astype(int)
    lead_rate = np.clip(
        0.115
        * np.select([content_types == "article", content_types == "live_session"], [1.35, 1.25], default=0.82)
        * np.select([channels == "community", channels == "paid"], [1.22, 0.70], default=1.0),
        0.02,
        0.40,
    )
    leads = rng.binomial(clicks, lead_rate).astype(int)
    conversion_rate = np.clip(
        0.205
        * np.select([content_types == "article", content_types == "live_session"], [1.28, 1.18], default=0.76)
        * np.select([channels == "organic", channels == "community", channels == "paid"], [1.12, 1.25, 0.68], default=0.92),
        0.03,
        0.55,
    )
    conversions = rng.binomial(leads, conversion_rate).astype(int)
    cost_per_thousand = np.select(
        [channels == "organic", channels == "community", channels == "paid"], [1.8, 3.6, 11.8], default=4.8
    )
    cost = np.round(impressions / 1_000 * cost_per_thousand * rng.uniform(0.92, 1.08, rows), 2)
    frame = pd.DataFrame(
        {
            "date": pd.Series(dates).dt.strftime("%Y-%m-%d"),
            "content_id": [f"content-{value:05d}" for value in rng.integers(1, 2_001, rows)],
            "content_type": content_types,
            "channel": channels,
            "impressions": impressions,
            "clicks": clicks,
            "leads": leads,
            "conversions": conversions,
            "cost": cost,
        }
    )
    known_answers = build_content_operations_known_answers(frame, seed=seed)
    request = {
        "source_path": "content-operations.csv",
        "mode": "professional",
        "period_type": "monthly",
        "audience": "content operations lead",
        "objective": "identify delivery performance, quality tradeoffs, and next-cycle actions",
        "analysis_intent": "business_review",
        "analysis_profile": "content_operations",
        "semantic_contract": {
            "domain": "content_operations",
            "adapter_id": "content_operations",
            "adapter_maturity": "experimental",
            "execution_profile": "general",
            "confirmation_status": "confirmed",
            "field_mappings": {},
        },
        "date_column": "date",
        "primary_metrics": ["impressions", "clicks", "leads", "conversions", "cost", "conversion_rate"],
        "dimensions": ["channel", "content_type"],
        "metric_contracts": [
            {"name": metric, "aggregation": "sum", "unit": "count" if metric != "cost" else "currency"}
            for metric in ("impressions", "clicks", "leads", "conversions", "cost")
        ] + [{
            "name": "conversion_rate",
            "aggregation": "ratio",
            "numerator": "conversions",
            "denominator": "clicks",
            "unit": "%",
            "scale": 100,
            "role": "quality",
            "direction": "higher_is_better",
        }],
        "comparisons": ["period_over_period", "year_over_year"],
        "output_mode": "report",
    }
    return _write_case_artifacts(
        output_dir,
        file_stem="content-operations",
        frame=frame,
        request=request,
        known_answers=known_answers,
    )


def build_project_operations_known_answers(
    frame: pd.DataFrame, *, seed: int = 20260901
) -> dict:
    status_quality = frame.groupby("status", sort=True)["quality_score"].mean()
    status_delay = frame.groupby("status", sort=True).apply(
        lambda group: float((group["actual_days"] - group["planned_days"]).mean()), include_groups=False
    )
    return {
        "row_count": int(len(frame)),
        "seed": int(seed),
        "provenance": _synthetic_provenance(seed=seed, row_count=len(frame)),
        "metric_totals": {
            metric: round(float(frame[metric].sum()), 2)
            for metric in ("planned_days", "actual_days", "actual_cost")
        },
        "dimension_answers": [
            _ranked_dimension_answer(frame, "team", "actual_cost"),
            _ranked_dimension_answer(frame, "stage", "actual_days"),
        ],
        "delivery_tradeoff": {
            "mean_delay_by_status": {str(status): round(float(delay), 4) for status, delay in status_delay.items()},
            "mean_quality_by_status": {str(status): round(float(score), 4) for status, score in status_quality.items()},
        },
    }


def generate_project_operations_case(
    output_dir: Path, rows: int = 15_000, seed: int = 20260901
) -> tuple[Path, Path, dict]:
    if rows < 365:
        raise ValueError("项目运营案例至少需要 365 行，才能覆盖完整年度周期")
    rng = np.random.default_rng(seed)
    calendar = pd.date_range("2024-01-01", "2025-06-30", freq="D")
    dates = calendar[rng.permutation(rows) % len(calendar)]
    teams = rng.choice(np.array(["platform", "growth", "delivery", "service_ops"]), rows, p=[0.25, 0.28, 0.30, 0.17])
    stages = rng.choice(np.array(["discovery", "build", "launch", "stabilize"]), rows, p=[0.20, 0.40, 0.25, 0.15])
    planned_days = rng.integers(8, 46, rows)
    delay = np.maximum(
        0,
        rng.normal(3.2, 2.4, rows)
        + np.where(teams == "delivery", 5.0, 0.0)
        + np.where(stages == "launch", 2.2, 0.0),
    ).round().astype(int)
    actual_days = planned_days + delay
    budget = np.round(planned_days * rng.uniform(950, 1_650, rows), 2)
    actual_cost = np.round(budget * (1 + delay * 0.028 + rng.uniform(-0.04, 0.08, rows)), 2)
    cost_overrun = np.round(actual_cost - budget, 2)
    quality_score = np.clip(
        92 - delay * 1.55 - np.where(teams == "delivery", 4.0, 0.0) + rng.normal(0, 3.0, rows),
        45,
        99,
    ).round(2)
    status = np.where(delay >= 7, "delayed", np.where(quality_score < 76, "at_risk", "on_track"))
    frame = pd.DataFrame(
        {
            "date": pd.Series(dates).dt.strftime("%Y-%m-%d"),
            "project_id": [f"project-{value:05d}" for value in rng.integers(1, 3_001, rows)],
            "team": teams,
            "stage": stages,
            "planned_days": planned_days,
            "actual_days": actual_days,
            "budget": budget,
            "actual_cost": actual_cost,
            "delay_days": delay,
            "cost_overrun": cost_overrun,
            "quality_score": quality_score,
            "status": status,
        }
    )
    known_answers = build_project_operations_known_answers(frame, seed=seed)
    request = {
        "source_path": "project-operations.csv",
        "mode": "professional",
        "period_type": "monthly",
        "audience": "project operations lead",
        "objective": "identify delivery delays, cost pressure, quality risks, and next-cycle actions",
        "analysis_intent": "business_review",
        "analysis_profile": "project_operations",
        "semantic_contract": {
            "domain": "project_operations",
            "adapter_id": "project_operations",
            "adapter_maturity": "experimental",
            "execution_profile": "general",
            "confirmation_status": "confirmed",
            "field_mappings": {},
        },
        "date_column": "date",
        "primary_metrics": ["actual_days", "budget", "actual_cost", "delay_days", "cost_overrun", "quality_score"],
        "dimensions": ["team", "stage", "status"],
        "metric_contracts": [
            {"name": "actual_days", "aggregation": "sum", "unit": "days"},
            {"name": "budget", "aggregation": "sum", "unit": "currency"},
            {"name": "actual_cost", "aggregation": "sum", "unit": "currency"},
            {"name": "delay_days", "aggregation": "average", "unit": "days", "role": "quality", "direction": "lower_is_better"},
            {"name": "cost_overrun", "aggregation": "sum", "unit": "currency", "role": "quality", "direction": "lower_is_better"},
            {"name": "quality_score", "aggregation": "average", "unit": "score", "role": "quality", "direction": "higher_is_better"},
        ],
        "comparisons": ["period_over_period", "year_over_year"],
        "output_mode": "report",
    }
    return _write_case_artifacts(
        output_dir,
        file_stem="project-operations",
        frame=frame,
        request=request,
        known_answers=known_answers,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate synthetic demo data.")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=20260829)
    parser.add_argument("--main-case", action="store_true")
    parser.add_argument("--rows", type=int, default=100_000)
    parser.add_argument("--write-xlsx", action="store_true")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.main_case:
        main_case = generate_retail_main_case(seed=args.seed, rows=args.rows)
        csv_path = args.output_dir / "retail-omnichannel-main.csv"
        main_case.to_csv(csv_path, index=False, encoding="utf-8-sig")
        experience_source = csv_path.name
        xlsx_path: Path | None = None
        if args.write_xlsx:
            xlsx_path = args.output_dir / "retail-omnichannel-main.xlsx"
            main_case.to_excel(xlsx_path, index=False)
            _normalize_xlsx_archive(xlsx_path)
            experience_source = xlsx_path.name
        request = _retail_main_request(experience_source)
        (args.output_dir / "retail-main-request.json").write_text(
            json.dumps(request, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        answers = build_retail_known_answers(main_case, seed=args.seed)
        (args.output_dir / "retail-main-known-answers.json").write_text(
            json.dumps(answers, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        dataset_artifacts = {
            "canonical_source": {
                "path": experience_source,
                "role": "canonical_source",
                "sha256": _file_sha256(args.output_dir / experience_source),
            }
        }
        if xlsx_path is not None:
            dataset_artifacts["csv_mirror"] = {
                "path": csv_path.name,
                "role": "csv_mirror",
                "sha256": _file_sha256(csv_path),
            }
        receipt = {
            "provenance": _synthetic_provenance(seed=args.seed, row_count=len(main_case)),
            "artifacts": {
                "dataset": csv_path.name,
                "dataset_files": dataset_artifacts,
                "request": "retail-main-request.json",
                "known_answers": "retail-main-known-answers.json",
            },
        }
        (args.output_dir / "retail-main-generation-receipt.json").write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(
            json.dumps(
                {
                    "output_dir": str(args.output_dir.resolve()),
                    "rows": len(main_case),
                    "provenance": receipt["provenance"],
                },
                ensure_ascii=False,
            )
        )
        return 0

    business = generate_business_sample(seed=args.seed)
    business_csv = args.output_dir / "synthetic-business.csv"
    business_xlsx = args.output_dir / "synthetic-business.xlsx"
    business.to_csv(business_csv, index=False, encoding="utf-8-sig")
    business.to_excel(business_xlsx, index=False)

    request = {
        "source_path": business_csv.name,
        "period_type": "weekly",
        "audience": "manager",
        "objective": "识别周期趋势、异常与需要复核的重点",
        "analysis_intent": "business_review",
        "date_column": "日期",
        "primary_metrics": ["访问量", "订单数", "收入", "成本"],
        "dimensions": ["渠道", "区域"],
        "analysis_profile": "general",
        "report_subject": "业务周度经营分析简报",
        "output_mode": "report+pptx",
    }
    (args.output_dir / "sample-request.json").write_text(
        json.dumps(request, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"output_dir": str(args.output_dir.resolve())}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
