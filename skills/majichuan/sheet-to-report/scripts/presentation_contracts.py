from __future__ import annotations

import re
import unicodedata
from typing import Any


def compact_report_subtitle(value: Any) -> str:
    text = str(value or "").strip()
    range_match = re.fullmatch(
        r"(\d{4})年(\d{1,2})月至(\d{4})年(\d{1,2})月(.+)", text
    )
    if range_match:
        start_year, start_month, end_year, end_month, suffix = range_match.groups()
        return (
            f"{start_year}.{int(start_month):02d}—"
            f"{end_year}.{int(end_month):02d}｜{suffix}"
        )
    month_match = re.fullmatch(r"(\d{4})年(\d{1,2})月(.+)", text)
    if month_match:
        year, month, suffix = month_match.groups()
        return f"{year}.{int(month):02d}｜{suffix}"
    return text


ALLOWED_TONES = {"neutral", "accent", "positive", "negative", "data"}
ALLOWED_DENSITIES = {"standard", "compact"}
ALLOWED_COMPARISON_KINDS = {"yoy", "pop", "comparison"}
REQUIRED_THEME_TOKENS = {
    "background",
    "surface",
    "ink",
    "muted",
    "line",
    "accent",
    "accent_soft",
    "positive",
    "positive_soft",
    "negative",
    "negative_soft",
    "chart",
    "cover_background",
    "cover_ink",
    "cover_muted",
    "secondary",
    "secondary_soft",
    "chart_muted",
}

EYEBROW_BY_LAYOUT = {
    "cover": "经营复盘",
    "executive-summary": "管理摘要",
    "kpi-spotlight": "经营基线",
    "trend-wide": "关键趋势",
    "chart-insight-action": "关键趋势",
    "chart-side-kpi": "结构与效率",
    "driver-levers": "经营杠杆",
    "risk-opportunity": "机会与风险",
    "action-roadmap": "行动路线",
    "data-appendix": "数据与口径",
}

DEFAULT_TONE_BY_LAYOUT = {
    "cover": "accent",
    "executive-summary": "accent",
    "kpi-spotlight": "neutral",
    "trend-wide": "data",
    "chart-insight-action": "data",
    "chart-side-kpi": "data",
    "driver-levers": "accent",
    "risk-opportunity": "neutral",
    "action-roadmap": "accent",
    "data-appendix": "data",
}


def display_units(text: str) -> int:
    return sum(
        2 if unicodedata.east_asian_width(character) in {"W", "F", "A"} else 1
        for character in str(text)
    )


def _semantic_tone(insight: dict[str, Any] | None, fallback: str) -> str:
    if not insight:
        return fallback
    tokens = " ".join(
        str(insight.get(key, "")).lower()
        for key in ("signal_type", "classification", "kind", "headline", "statement")
    )
    if any(token in tokens for token in ("risk", "negative", "anomaly", "decline", "风险", "承压", "下降")):
        return "negative"
    if any(token in tokens for token in ("opportunity", "positive", "growth", "机会", "增长", "改善")):
        return "positive"
    return fallback


def _matching_insight(model: dict[str, Any], evidence_ids: list[str]) -> dict[str, Any] | None:
    target = set(evidence_ids)
    return next(
        (
            insight
            for insight in model.get("insights", [])
            if target & set(insight.get("evidence_ids", []))
        ),
        None,
    )


def _chart_focus(
    model: dict[str, Any], slide: dict[str, Any], focus_evidence_ids: list[str]
) -> dict[str, str | None] | None:
    if not slide.get("chart_ids"):
        return None
    charts_by_id = {chart.get("chart_id"): chart for chart in model.get("charts", [])}
    chart = charts_by_id.get(slide["chart_ids"][0])
    if not chart:
        return None
    evidence_index = model.get("evidence_index", {})
    chart_evidence = set(chart.get("evidence_ids", []))
    claim_evidence = set(slide.get("claim_evidence_ids", []))
    matched_ids = list(chart_evidence & (claim_evidence or set(focus_evidence_ids)))
    if not matched_ids:
        return None

    series_name: str | None = None
    category_name: str | None = None
    if len(chart.get("series", [])) == 1:
        series_name = str(chart["series"][0].get("name") or "") or None
    for evidence_id in matched_ids:
        evidence = evidence_index.get(evidence_id, {})
        if str(evidence.get("kind", "")).startswith("dimension"):
            rows = [row for row in evidence.get("rows", []) if not row.get("is_other")]
            if rows:
                candidate = str(rows[0].get("value") or "") or None
                if candidate in {str(value) for value in chart.get("categories", [])}:
                    category_name = candidate
                    break
    if not series_name and not category_name:
        return None
    return {"series_name": series_name, "category_name": category_name}


def _display_period(value: Any) -> str:
    text = str(value or "").strip()
    month = re.fullmatch(r"(\d{4})-(\d{1,2})", text)
    if month:
        return f"{month.group(1)}年{int(month.group(2))}月"
    day = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", text)
    if day:
        return f"{day.group(1)}年{int(day.group(2))}月{int(day.group(3))}日"
    week = re.fullmatch(r"(\d{4})-W(\d{1,2})", text, re.IGNORECASE)
    if week:
        return f"{week.group(1)}年第{int(week.group(2))}周"
    return text


def _comparison_kind(kind: str, current: str, baseline: str) -> tuple[str, str]:
    if "yoy" in kind.lower():
        return "yoy", "同比"
    current_month = re.fullmatch(r"(\d{4})-(\d{1,2})", current)
    baseline_month = re.fullmatch(r"(\d{4})-(\d{1,2})", baseline)
    if current_month and baseline_month:
        current_index = int(current_month.group(1)) * 12 + int(current_month.group(2))
        baseline_index = int(baseline_month.group(1)) * 12 + int(baseline_month.group(2))
        if current_index - baseline_index == 12:
            return "yoy", "同比"
        if current_index - baseline_index == 1:
            return "pop", "环比"
    return "comparison", "对比"


def _slide_copy_candidates(model: dict[str, Any], slide: dict[str, Any]) -> list[str]:
    layout_id = str(slide.get("layout_id", ""))
    values = [str(slide.get("claim", ""))]
    if layout_id == "executive-summary":
        summary = model.get("executive_summary", {})
        values.extend(str(value) for value in summary.get("key_conclusions", []))
        values.extend(str(value) for value in summary.get("priority_actions", []))
    elif layout_id in {"trend-wide", "chart-insight-action", "chart-side-kpi"}:
        evidence = set(slide.get("evidence_ids", []))
        values.extend(
            str(insight.get("headline") or insight.get("statement") or "")
            for insight in model.get("insights", [])
            if evidence & set(insight.get("evidence_ids", []))
        )
        values.extend(
            str(insight.get("statement") or "")
            for insight in model.get("insights", [])
            if evidence & set(insight.get("evidence_ids", []))
        )
    elif layout_id == "driver-levers":
        for lever in model.get("levers", []):
            values.extend(
                str(lever.get(field) or "") for field in ("headline", "takeaway")
            )
    elif layout_id == "risk-opportunity":
        visible = [
            insight
            for insight in model.get("insights", [])
            if insight.get("signal_type") in {"opportunity", "seasonality", "risk"}
        ]
        if not visible:
            visible = [
                insight
                for insight in model.get("insights", [])
                if insight.get("kind") == "inference"
            ]
        values.extend(str(insight.get("statement") or "") for insight in visible)
    elif layout_id == "action-roadmap":
        for action in model.get("actions", []):
            values.extend(
                str(action.get(field) or "")
                for field in ("headline", "text", "action", "verification_signal")
            )
    return [value for value in values if value]


def _comparison_contexts(
    model: dict[str, Any], slide: dict[str, Any]
) -> list[dict[str, str]]:
    candidates = _slide_copy_candidates(model, slide)
    raw_contexts: list[tuple[str, str, str]] = []
    evidence_index = model.get("evidence_index", {})
    for evidence_id in slide.get("evidence_ids", []):
        evidence = evidence_index.get(evidence_id, {})
        current = str(evidence.get("latest_period") or "")
        baseline = str(evidence.get("comparison_period") or "")
        if current and baseline:
            raw_contexts.append((str(evidence.get("kind") or ""), current, baseline))
    if slide.get("layout_id") == "driver-levers":
        snapshot = model.get("latest_snapshot", {})
        current = str(snapshot.get("period") or "")
        baseline = str(snapshot.get("comparison_period") or "")
        if current and baseline:
            raw_contexts.append(("period_over_period", current, baseline))

    contexts: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for evidence_kind, current, baseline in raw_contexts:
        current_label = _display_period(current)
        baseline_label = _display_period(baseline)
        pair = (current_label, baseline_label)
        if pair in seen:
            continue
        if not any(
            (current_label in value and baseline_label in value)
            or f"较{baseline_label}" in value
            or f"相比{baseline_label}" in value
            for value in candidates
        ):
            continue
        kind, label = _comparison_kind(evidence_kind, current, baseline)
        contexts.append(
            {
                "kind": kind,
                "label": label,
                "current_label": current_label,
                "baseline_label": baseline_label,
            }
        )
        seen.add(pair)
    return contexts[:2]


def compact_comparison_copy(
    text: Any, comparison_contexts: list[dict[str, str]] | None
) -> str:
    """Remove repeated period labels while retaining a short comparison mode tag."""
    result = str(text or "").strip()
    for context in comparison_contexts or []:
        current = re.escape(str(context.get("current_label") or ""))
        baseline = re.escape(str(context.get("baseline_label") or ""))
        label = str(context.get("label") or "对比")
        if not current or not baseline:
            continue
        result = re.sub(
            rf"^{current}(?P<body>.+?)较{baseline}(?P<change>增长|下降|上升|提升|减少|回落|扩大|收窄)",
            rf"\g<body>{label}\g<change>",
            result,
        )
        result = re.sub(
            rf"{current}(?:较|相比){baseline}[，,:：]\s*",
            f"{label}｜",
            result,
        )
        result = re.sub(rf"(?:较|相比){baseline}", label, result)
    return result


def comparison_context_text(contexts: list[dict[str, str]] | None) -> str:
    return "；".join(
        f"{context['label']}：{context['current_label']} vs {context['baseline_label']}"
        for context in contexts or []
    )


def build_visual_spec(model: dict[str, Any], slide: dict[str, Any]) -> dict[str, Any]:
    layout_id = str(slide.get("layout_id"))
    slide_evidence = list(dict.fromkeys(slide.get("evidence_ids", [])))
    claim_evidence = set(slide.get("claim_evidence_ids", []))
    focus_evidence_ids = [value for value in slide_evidence if value in claim_evidence]
    if not focus_evidence_ids and layout_id != "cover":
        focus_evidence_ids = slide_evidence[:1]

    insight = _matching_insight(model, focus_evidence_ids)
    default_tone = DEFAULT_TONE_BY_LAYOUT.get(layout_id, "neutral")
    tone = _semantic_tone(insight, default_tone)
    if layout_id in {"risk-opportunity", "data-appendix"}:
        tone = default_tone

    content_units = display_units(str(slide.get("claim", ""))) + display_units(
        str(slide.get("purpose", ""))
    )
    title_units = display_units(str(slide.get("claim", "")))
    density = (
        "compact"
        if content_units > 110 or title_units > 58 or len(slide_evidence) > 6
        else "standard"
    )
    spec: dict[str, Any] = {
        "eyebrow": EYEBROW_BY_LAYOUT.get(layout_id, "经营分析"),
        "tone": tone,
        "density": density,
        "focus_evidence_ids": focus_evidence_ids,
    }
    comparison_contexts = _comparison_contexts(model, slide)
    if comparison_contexts:
        spec["comparison_contexts"] = comparison_contexts
    spec["display_claim"] = compact_comparison_copy(
        slide.get("claim", ""), comparison_contexts
    )
    chart_focus = _chart_focus(model, slide, focus_evidence_ids)
    if chart_focus:
        spec["chart_focus"] = chart_focus
    return spec


def relative_luminance(hex_color: str) -> float:
    color = str(hex_color).strip().lstrip("#")
    if len(color) != 6:
        raise ValueError(f"无效颜色：{hex_color}")
    channels = []
    for offset in (0, 2, 4):
        value = int(color[offset : offset + 2], 16) / 255
        channels.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast_ratio(foreground: str, background: str) -> float:
    lighter = max(relative_luminance(foreground), relative_luminance(background))
    darker = min(relative_luminance(foreground), relative_luminance(background))
    return (lighter + 0.05) / (darker + 0.05)


def validate_visual_spec(spec: dict[str, Any]) -> None:
    """Reject unapproved visual semantics before any editable shape is emitted."""

    tone = str(spec.get("tone", "neutral"))
    if tone not in ALLOWED_TONES:
        raise ValueError(f"unknown tone: {tone}")
    density = str(spec.get("density", "standard"))
    if density not in ALLOWED_DENSITIES:
        raise ValueError(f"unknown density: {density}")


def validate_image_exception(exception: dict[str, Any]) -> None:
    """Allow only disclosed decorative images with no unique business evidence."""

    if not isinstance(exception, dict):
        raise ValueError("image exception must be an object")
    reason = str(exception.get("image_exception_reason") or "").strip()
    if not reason:
        raise ValueError("image exception requires image_exception_reason")
    if exception.get("unique_evidence") is not False:
        raise ValueError("image exception cannot contain unique evidence")
    if exception.get("editable_alternative") is not None:
        raise ValueError("image exception cannot replace an editable alternative")


def validate_theme(theme: dict[str, Any]) -> None:
    missing = REQUIRED_THEME_TOKENS - set(theme)
    if missing:
        raise ValueError(f"主题缺少 token：{', '.join(sorted(missing))}")
    if not isinstance(theme.get("chart"), list) or not theme["chart"]:
        raise ValueError("主题 chart token 必须是非空颜色列表")
    for token in REQUIRED_THEME_TOKENS - {"chart"}:
        relative_luminance(str(theme[token]))
    for color in theme["chart"]:
        relative_luminance(str(color))
    contrast_pairs = (
        ("ink", "background", 4.5),
        ("ink", "surface", 4.5),
        ("cover_ink", "cover_background", 4.5),
        ("cover_muted", "cover_background", 3.0),
    )
    for foreground, background, minimum in contrast_pairs:
        ratio = contrast_ratio(theme[foreground], theme[background])
        if ratio < minimum:
            raise ValueError(
                f"主题对比度不足：{foreground}/{background}={ratio:.2f}，最低 {minimum:.1f}"
            )
