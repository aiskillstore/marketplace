from __future__ import annotations

from typing import Any

from content_resolver import build_content_refs, canonical_content_ref_bindings
from narrative_planner import build_decision_narrative
from presentation_contracts import build_visual_spec


def _build_engineering_dossier(model: dict[str, Any]) -> list[dict[str, Any]]:
    """Project the QA-only engineering dossier outside the business story contract."""

    pages = [
        ("cover", "cover", "工程回归：交易合同核验", "说明工程核验范围、输入数据与合同边界"),
        ("executive-summary", "qa-summary", "仅输出数据质量与计算核验结果", "确认本次不生成经营判断、归因或行动建议"),
        ("data-appendix", "qa-contract", "输入数据与合同可回溯", "记录字段映射、聚合口径与后续复核边界"),
    ]
    plan: list[dict[str, Any]] = []
    for index, (layout_id, silhouette, claim, purpose) in enumerate(pages, 1):
        page = {
            "slide_id": f"S{index:02d}", "layout_id": layout_id, "silhouette": silhouette,
            "role": layout_id, "claim": claim, "purpose": purpose,
            "page_reason": "工程 QA dossier 固定角色", "selection_score": 100,
            "content_exemption": "qa", "evidence_ids": [], "claim_evidence_ids": [], "chart_ids": [],
        }
        page["content_refs"] = build_content_refs(model, page)
        page["content_ref_bindings"] = canonical_content_ref_bindings(model, page)
        page["visual_spec"] = build_visual_spec(model, page)
        plan.append(page)
    return plan


def _profile_adapter_inputs(model: dict[str, Any]) -> dict[str, Any]:
    """Keep profile selection explicit while sharing one business narrative planner."""

    profile = model.get("analysis_profile", {})
    resolved = profile.get("resolved") if isinstance(profile, dict) else profile
    return {
        "profile": str(resolved or model.get("request", {}).get("analysis_profile") or "general"),
        "selected_lenses": [
            str(item.get("lens")) for item in model.get("analysis_lenses", [])
            if item.get("status") == "selected"
        ],
        "charts": list(model.get("charts", [])),
        "levers": list(model.get("levers", [])),
        "actions": list(model.get("actions", [])),
        "kpis": list(model.get("kpis", [])),
    }


def build_slide_plan(model: dict[str, Any]) -> list[dict[str, Any]]:
    """Choose a profile adapter, then delegate all business pages to one planner."""

    if str(model.get("request", {}).get("analysis_intent") or "") == "engineering_regression":
        return _build_engineering_dossier(model)
    return build_decision_narrative(model, adapter_inputs=_profile_adapter_inputs(model))
