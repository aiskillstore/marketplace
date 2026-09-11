from __future__ import annotations

import unicodedata
from typing import Any


LAYOUT_REGISTRY: dict[str, dict[str, Any]] = {
    "cover": {
        "required_slots": ("claim",),
        "max_title_units": 48,
        "chart_aspect_ratio": None,
        "fallback_layout": None,
        "native_chart": False,
        "required_visual_roles": ("eyebrow", "title", "scope", "judgement"),
        "max_items": 1,
        "max_body_units": 160,
    },
    "executive-summary": {
        "required_slots": ("claim", "evidence_ids"),
        "max_title_units": 58,
        "chart_aspect_ratio": None,
        "fallback_layout": "data-appendix",
        "native_chart": False,
        "required_visual_roles": ("eyebrow", "title", "numbered-judgement", "action-band"),
        "max_items": 3,
        "max_body_units": 360,
    },
    "kpi-spotlight": {
        "required_slots": ("claim", "evidence_ids"),
        "max_title_units": 58,
        "chart_aspect_ratio": None,
        "fallback_layout": "executive-summary",
        "native_chart": False,
        "required_visual_roles": ("eyebrow", "title", "primary-kpi", "supporting-kpi"),
        "max_items": 6,
        "max_body_units": 240,
    },
    "trend-wide": {
        "required_slots": ("claim", "chart_ids"),
        "max_title_units": 58,
        "chart_aspect_ratio": 2.55,
        "fallback_layout": "chart-insight-action",
        "native_chart": True,
        "required_visual_roles": ("eyebrow", "title", "native-chart", "focus-callout"),
        "max_items": 2,
        "max_body_units": 220,
    },
    "chart-insight-action": {
        "required_slots": ("claim", "chart_ids", "evidence_ids"),
        "max_title_units": 58,
        "chart_aspect_ratio": 1.9,
        "fallback_layout": "trend-wide",
        "native_chart": True,
        "required_visual_roles": ("eyebrow", "title", "native-chart", "focus-callout"),
        "max_items": 3,
        "max_body_units": 260,
    },
    "chart-side-kpi": {
        "required_slots": ("claim", "chart_ids", "evidence_ids"),
        "max_title_units": 58,
        "chart_aspect_ratio": 1.65,
        "fallback_layout": "chart-insight-action",
        "native_chart": True,
        "required_visual_roles": ("eyebrow", "title", "native-chart", "focus-callout"),
        "max_items": 3,
        "max_body_units": 260,
    },
    "driver-levers": {
        "required_slots": ("claim", "evidence_ids"),
        "max_title_units": 58,
        "chart_aspect_ratio": None,
        "fallback_layout": "executive-summary",
        "native_chart": False,
        "required_visual_roles": ("eyebrow", "title", "lever-axis", "lever-node"),
        "max_items": 4,
        "max_body_units": 360,
    },
    "risk-opportunity": {
        "required_slots": ("claim", "evidence_ids"),
        "max_title_units": 58,
        "chart_aspect_ratio": None,
        "fallback_layout": "executive-summary",
        "native_chart": False,
        "required_visual_roles": ("eyebrow", "title", "opportunity-column", "risk-column"),
        "max_items": 4,
        "max_body_units": 360,
    },
    "action-roadmap": {
        "required_slots": ("claim", "evidence_ids"),
        "max_title_units": 58,
        "chart_aspect_ratio": None,
        "fallback_layout": "data-appendix",
        "native_chart": False,
        "required_visual_roles": ("eyebrow", "title", "priority-row", "success-signal"),
        "max_items": 3,
        "max_body_units": 420,
    },
    "data-appendix": {
        "required_slots": ("claim",),
        "max_title_units": 58,
        "chart_aspect_ratio": None,
        "fallback_layout": None,
        "native_chart": False,
        "required_visual_roles": ("eyebrow", "title", "data-scope", "formula-grid"),
        "max_items": 6,
        "max_body_units": 560,
    },
}


FONT_MINIMUMS = {
    "cover_title": 50,
    "slide_title": 35,
    "subheading": 24,
    "body": 16,
    "footnote": 10,
}


def display_units(text: str) -> int:
    return sum(
        2 if unicodedata.east_asian_width(character) in {"W", "F", "A"} else 1
        for character in str(text)
    )


def validate_layout_capacity(model: dict[str, Any]) -> None:
    for slide in model.get("slide_plan", []):
        layout_id = slide.get("layout_id")
        contract = LAYOUT_REGISTRY.get(layout_id)
        if contract is None:
            raise ValueError(f"未知 layout：{layout_id}")
        required_slots = contract["required_slots"]
        if slide.get("content_exemption") == "selection_meta":
            required_slots = tuple(slot for slot in required_slots if slot != "evidence_ids")
        missing = [slot for slot in required_slots if not slide.get(slot)]
        engineering_qa = (
            str(model.get("request", {}).get("analysis_intent") or "")
            == "engineering_regression"
            and slide.get("content_exemption") == "qa"
        )
        legacy_qa = (
            slide.get("content_exemption") == "qa"
            and not any(
                "content_refs" in page or "role" in page
                for page in model.get("slide_plan", [])
            )
        )
        if (
            missing
            and layout_id != "cover"
            and not engineering_qa
            and not legacy_qa
        ):
            raise ValueError(
                f"layout {layout_id} 缺少内容槽位：{', '.join(missing)}"
            )
        title_units = display_units(str(slide.get("claim", "")))
        density = str(slide.get("visual_spec", {}).get("density", "standard"))
        title_capacity = contract["max_title_units"]
        if density == "compact":
            # Compact is an explicit layout variant: it gains horizontal title
            # room without lowering the role's font minimum.
            title_capacity = max(title_capacity + 1, int(title_capacity * 1.5))
        if title_units > title_capacity:
            raise ValueError(
                f"页面 {slide.get('slide_id')} 标题过长，超过 layout 容量 capacity："
                f"{title_units}/{title_capacity}"
            )

    for insight in model.get("insights", []):
        if display_units(str(insight.get("statement", ""))) > 150:
            raise ValueError("洞察文本过长，超过页面容量")
    for action in model.get("actions", []):
        if display_units(str(action.get("text", ""))) > 180:
            raise ValueError("行动建议过长，超过页面容量")
