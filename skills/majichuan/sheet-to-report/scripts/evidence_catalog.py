"""Add auditable evidence and content contracts without recalculating metrics."""
from __future__ import annotations

import re
from typing import Any

from content_selection import score_and_select_findings


def _claim_type(item: dict[str, Any]) -> str:
    raw = str(item.get("claim_type") or item.get("kind") or "fact").lower()
    return raw if raw in {"fact", "diagnostic", "inference", "hypothesis"} else "fact"


def _target(text: str) -> str:
    quoted = re.search(r"[“\"]([^”\"]+)[”\"]", text)
    if quoted:
        return quoted.group(1).strip()
    for pattern in (r"(?:复核|检查|暂停|优化|建立|修复|提升|降低)([^：；，。]+)",):
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip(" 的，。；")
    return ""


def _lens_for_evidence(
    record: dict[str, Any], dimension_lenses: dict[str, str], metric_lenses: dict[str, str]
) -> str:
    kind = str(record.get("kind") or "")
    evidence_id = str(record.get("evidence_id") or "")
    dimension = str(record.get("dimension") or "")
    metric = str(record.get("metric") or record.get("name") or "")
    if metric in metric_lenses:
        return metric_lenses[metric]
    if dimension in dimension_lenses:
        return dimension_lenses[dimension]
    if kind in {"metric_trend", "metric_yoy"} or evidence_id.endswith(":trend"):
        return "trend"
    if "quality" in kind or "reconciliation" in kind:
        return "quality"
    if kind.startswith("dimension"):
        return "growth_driver"
    return "overview"


def _item_lens(
    evidence_ids: list[str], evidence: dict[str, dict[str, Any]],
    dimension_lenses: dict[str, str], metric_lenses: dict[str, str]
) -> str:
    lenses = [
        _lens_for_evidence(evidence[evidence_id], dimension_lenses, metric_lenses)
        for evidence_id in evidence_ids if evidence_id in evidence
    ]
    return lenses[0] if lenses and len(set(lenses)) == 1 else ("growth_driver" if lenses else "overview")


def scope_content_to_lenses(*, evidence_index: dict[str, dict[str, Any]], insights: list[dict[str, Any]],
                            actions: list[dict[str, Any]], charts: list[dict[str, Any]],
                            selected_lenses: set[str], dimension_lenses: dict[str, str],
                            metric_lenses: dict[str, str] | None = None,
                            metric_directions: dict[str, str] | None = None) -> dict[str, list[dict[str, Any]]]:
    """Attach deterministic lenses and remove content whose lens is unsupported."""
    scoped: dict[str, list[dict[str, Any]]] = {}
    metric_lenses = metric_lenses or {}
    metric_directions = metric_directions or {}
    for name, collection in (("insights", insights), ("actions", actions), ("charts", charts)):
        kept: list[dict[str, Any]] = []
        for raw in collection:
            item = dict(raw)
            inferred_lens = (
                "trend" if name == "charts" and item.get("chart_type") == "line"
                else _item_lens(
                    list(item.get("evidence_ids", [])), evidence_index,
                    dimension_lenses, metric_lenses,
                )
            )
            item["lens"] = str(item.get("lens") or inferred_lens)
            if name == "insights" and item["lens"] == "quality" and not item.get("signal_type"):
                for evidence_id in item.get("evidence_ids", []):
                    record = evidence_index.get(str(evidence_id), {})
                    metric = str(record.get("metric") or record.get("name") or "")
                    values = record.get("values")
                    if metric not in metric_directions or not isinstance(values, list) or len(values) < 2:
                        continue
                    previous, latest = values[-2], values[-1]
                    if not isinstance(previous, (int, float)) or not isinstance(latest, (int, float)) or latest == previous:
                        continue
                    improving_up = metric_directions[metric] != "lower_is_better"
                    improved = (latest > previous) == improving_up
                    item["signal_type"] = "opportunity" if improved else "risk"
                    break
            if item["lens"] in selected_lenses:
                kept.append(item)
        scoped[name] = kept
    return scoped


def enrich_analysis_content(*, evidence_index: dict[str, dict[str, Any]], insights: list[dict[str, Any]],
                            actions: list[dict[str, Any]], row_count: int,
                            business_objects: set[str], filter_scope: str = "confirmed dataset scope") -> dict[str, Any]:
    """Normalize engine outputs into evidence-first v0.2 quality fields."""
    enriched_evidence: dict[str, dict[str, Any]] = {}
    for evidence_id, raw in evidence_index.items():
        item = dict(raw)
        formula = str(item.get("calculation") or item.get("formula") or "deterministic aggregation")
        sample_count = item.get("sample_count")
        limitations = list(item.get("limitations") or [])
        if sample_count is None:
            limitations.append("样本范围未知，未用整表行数替代。")
        if item.get("affected_rows") is None:
            limitations.append("受影响行数未知。")
        if not item.get("business_objects"):
            limitations.append("业务对象范围未知。")
        item.update({
            "evidence_id": str(item.get("evidence_id") or evidence_id),
            "calculation": formula,
            "formula": formula,
            "filter_scope": item.get("filter_scope") or filter_scope,
            "sample_count": int(sample_count) if sample_count is not None else None,
            "affected_rows": int(item["affected_rows"]) if item.get("affected_rows") is not None else None,
            "affected_amount": item.get("affected_amount"),
            "limitations": list(dict.fromkeys(limitations)),
            "business_objects": list(item.get("business_objects") or []),
            "quality_managed": True,
        })
        enriched_evidence[str(evidence_id)] = item

    enriched_insights: list[dict[str, Any]] = []
    for raw in insights:
        item = dict(raw)
        original_kind = str(item.get("kind") or "fact").lower()
        claim_type = _claim_type(item)
        evidence_ids = [str(value) for value in item.get("evidence_ids", []) if str(value) in enriched_evidence]
        limitations = list(item.get("limitations") or [])
        from analysis_depth import has_bound_contribution_judgement
        bound_structure = has_bound_contribution_judgement(item, enriched_evidence)
        if claim_type in {"diagnostic", "inference"} and len(evidence_ids) < 2 and not bound_structure:
            claim_type = "hypothesis"
            limitations.append("缺少交叉证据，不能作为诊断或推断结论。")
        if claim_type == "hypothesis" and not limitations:
            limitations.append("当前证据不足，需补充验证。")
        strength = "high" if claim_type == "fact" and evidence_ids else ("medium" if len(evidence_ids) >= 2 or bound_structure else "low")
        presentation_role = str(
            item.get("presentation_role")
            or (
                "featured"
                if original_kind in {"diagnostic", "inference"}
                or item.get("display_priority") == "primary"
                else "supporting"
            )
        )
        default_score = (
            5 if original_kind == "diagnostic"
            else 4 if original_kind == "inference"
            else 1 if presentation_role == "supporting"
            else 3
        )
        item.update({
            "claim_type": claim_type,
            "evidence_strength": strength,
            "limitations": list(dict.fromkeys(limitations)),
            "value_score": int(item.get("value_score", default_score)),
            "presentation_role": presentation_role,
            "actionable": bool(
                item.get("actionable", original_kind == "diagnostic")
            ),
            "evidence_ids": evidence_ids,
        })
        enriched_insights.append(item)

    enriched_actions: list[dict[str, Any]] = []
    for raw in actions:
        item = dict(raw)
        evidence_ids = [str(value) for value in item.get("evidence_ids", []) if str(value) in enriched_evidence]
        text = str(item.get("text") or item.get("headline") or "")
        rationale = str(item.get("rationale") or "").strip()
        item.update({"target": str(item.get("target") or _target(text)), "basis": str(item.get("basis") or rationale), "rationale": rationale, "evidence_ids": evidence_ids, "verification_signal": str(item.get("verification_signal") or "").strip(), "analysis_dimensions": list(item.get("analysis_dimensions") or []), "source_insight_ids": list(item.get("source_insight_ids") or [])})
        item["formal"] = bool(item["target"] and item["basis"] and evidence_ids and item["verification_signal"])
        enriched_actions.append(item)
    return {"evidence_index": enriched_evidence, "insights": enriched_insights, "actions": enriched_actions}


def select_featured_insight_ids(
    insights: list[dict[str, Any]], *, maximum: int = 5
) -> list[str]:
    """Compatibility wrapper for callers that previously requested a fixed quota."""
    del maximum
    candidates: list[dict[str, Any]] = []
    for raw in insights:
        item = dict(raw)
        if item.get("presentation_role") != "featured":
            continue
        claim_type = str(item.get("claim_type") or item.get("kind") or "fact")
        evidence_ids = list(item.get("evidence_ids") or [])
        value_score = int(item.get("value_score") or 0)
        candidates.append({
            **item,
            "evidence_valid": bool(evidence_ids),
            "information_gain": bool(evidence_ids and str(item.get("statement") or item.get("headline") or "").strip()),
            "business_question": str(item.get("business_question") or "兼容洞察筛选"),
            "decision_impact": str(item.get("decision_impact") or "支持当前分析目标的决策"),
            "impact": min(2, max(0, value_score // 2)),
            "abnormality": 2 if claim_type in {"diagnostic", "inference"} else 1,
            "actionability": 2 if item.get("actionable") else (1 if claim_type in {"diagnostic", "inference"} else 0),
            "credibility": 0 if str(item.get("evidence_strength") or "").lower() == "low" else (2 if len(evidence_ids) >= 2 else 1),
            "urgency": 1,
            "uniqueness": 1,
            "duplicate_signature": str(item.get("duplicate_signature") or item.get("statement") or item.get("headline") or item.get("insight_id") or ""),
        })
    selection = score_and_select_findings(candidates)
    return [str(item["insight_id"]) for item in selection["featured"] if item["insight_id"]]
