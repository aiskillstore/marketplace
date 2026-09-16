from __future__ import annotations

"""Single, deterministic page-content resolver for every report renderer."""

import re
from typing import Any
import copy


REFERENCE_KEYS = ("kpi_ids", "insight_ids", "action_ids", "lever_ids", "chart_ids", "contract_ids")

MODERN_MODEL_MARKERS = frozenset({
    "analysis_contract", "analysis_lenses", "value_selection", "content_validation", "content_lock",
})
LEGACY_CONTENT_REFS_MARKER = "legacy_content_refs_fixture"

# This is the shared formal renderer schema. ``None`` is deliberate for a
# field a record kind does not use: omission and injection remain visible to
# the lock rather than silently falling outside a renderer payload.
FORMAL_INSIGHT_FIELDS = (
    "insight_id", "question_id", "lens", "headline", "statement", "implication", "display", "display_label",
    "signal_type", "kind", "claim_type", "confidence", "evidence_ids", "claim_binding",
    "business_question", "decision_impact", "value_score", "actionable", "answer_status",
    "answer_text", "evidence_strength", "limitations", "presentation_role", "resolved_answer",
    "display_priority", "no_action_reason", "metric_name", "title_clause",
    "scope_id", "scope_disclosure",
)
FORMAL_ACTION_FIELDS = (
    "action_id", "question_id", "lens", "priority", "formal", "headline", "text", "target", "basis",
    "rationale", "verification_signal", "evidence_ids", "source_insight_ids", "claim_binding",
    "analysis_dimensions", "action_type", "steps", "success_signal", "guardrails",
    "source_chapter_ids", "limitations",
    "scope_id", "scope_disclosure",
)
RENDERER_VISIBLE_FIELDS = {
    "insight_ids": FORMAL_INSIGHT_FIELDS,
    "action_ids": FORMAL_ACTION_FIELDS,
}


def is_modern_model(model: dict[str, Any]) -> bool:
    return any(marker in model for marker in MODERN_MODEL_MARKERS)


def has_formal_renderer_contract(model: dict[str, Any]) -> bool:
    return is_modern_model(model) and (
        model.get("content_lock") is not None
        or any(isinstance(page, dict) and isinstance(page.get("content_refs"), dict) for page in model.get("slide_plan", []))
    )


def canonical_formal_renderer_records(model: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Return every formal record in the exact schema consumed by renderers."""

    return {
        "insights": [
            {field: copy.deepcopy(item.get(field)) for field in FORMAL_INSIGHT_FIELDS}
            for item in model.get("insights", [])
            if isinstance(item, dict) and item.get("formal", True)
        ],
        "actions": [
            {field: copy.deepcopy(item.get(field)) for field in FORMAL_ACTION_FIELDS}
            for item in model.get("actions", [])
            if isinstance(item, dict) and item.get("formal", True)
        ],
    }


def validate_formal_renderer_records(model: dict[str, Any]) -> None:
    """Fail closed on duplicate/missing formal identities in modern models."""

    if not has_formal_renderer_contract(model):
        return
    schemas = (("insights", "insight_id", FORMAL_INSIGHT_FIELDS), ("actions", "action_id", FORMAL_ACTION_FIELDS))
    global_ids: set[str] = set()
    for collection, id_field, fields in schemas:
        seen: set[str] = set()
        allowed = set(fields)
        for record in model.get(collection, []):
            if not isinstance(record, dict):
                continue
            if record.get("formal") is False:
                raise ValueError("现代 locked report_model 不允许 formal=false 退出正式合同")
            unknown = set(record) - set(fields)
            if unknown:
                raise ValueError(
                    f"formal {collection} 包含未知字段：" + ", ".join(sorted(unknown))
                )
            record_id = record.get(id_field)
            if (
                not isinstance(record_id, str) or not record_id.strip()
                or record_id in seen or record_id in global_ids
            ):
                raise ValueError(f"formal {id_field} 必须非空且全局唯一")
            seen.add(record_id)
            global_ids.add(record_id)
            if collection == "actions" and (
                type(record.get("priority")) is not int or record["priority"] < 1
            ):
                raise ValueError("formal action priority 必须为正整数")


def normalize_claim_text(value: Any) -> str:
    """Normalize only presentation whitespace; never rewrite a business claim."""

    return re.sub(r"\s+", " ", str(value or "")).strip()


def canonical_claim(value: Any, fallback: str = "") -> str:
    """Return the sole canonical business-claim text for a finding or string."""

    if isinstance(value, dict):
        value = value.get("headline") or value.get("statement") or fallback
    return normalize_claim_text(value or fallback)


def _id_maps(model: dict[str, Any]) -> dict[str, dict[str, dict[str, Any]]]:
    return {
        "kpi_ids": {
            f"kpi:{index}": item
            for index, item in enumerate(
                model.get("period_overview", {}).get("kpis") or model.get("kpis", []), 1
            )
        },
        "insight_ids": {f"insight:{index}": item for index, item in enumerate(model.get("insights", []), 1)},
        "action_ids": {f"action:{index}": item for index, item in enumerate(model.get("actions", []), 1)},
        "lever_ids": {f"lever:{index}": item for index, item in enumerate(model.get("levers", []), 1)},
        "chart_ids": {str(item["chart_id"]): item for item in model.get("charts", [])},
        "contract_ids": {
            str(item.get("metric_id") or f"contract:{index}"): item
            for index, item in enumerate(model.get("metric_contracts", []), 1)
        },
    }


def _globally_selected_signal_present(
    model: dict[str, Any], maps: dict[str, dict[str, dict[str, Any]]], signals: set[str]
) -> bool:
    """Scope global signal checks to the selected story, never raw leftovers."""

    selection = model.get("value_selection")
    if isinstance(selection, dict):
        selected = {
            str(item.get("insight_id") or "")
            for item in selection.get("featured", [])
            if isinstance(item, dict)
        }
        return any(
            str(item.get("insight_id") or "") in selected
            and str(item.get("signal_type") or "") in signals
            for item in maps["insight_ids"].values()
        )
    return any(
        str(item.get("signal_type") or "") in signals
        for item in maps["insight_ids"].values()
    )


def canonical_content_ref_bindings(model: dict[str, Any], page: dict[str, Any]) -> list[dict[str, Any]]:
    """Resolve positional renderer refs once into stable identity plus visible payload."""
    refs = page.get("content_refs")
    if not isinstance(refs, dict):
        raise ValueError(f"页面 {page.get('slide_id')} 缺少 content_refs")
    maps = _id_maps(model)
    bindings: list[dict[str, Any]] = []
    stable_fields = {
        "kpi_ids": ("kpi_id", "name"), "insight_ids": ("insight_id",), "action_ids": ("action_id",),
        "lever_ids": ("lever_id", "name"), "chart_ids": ("chart_id",), "contract_ids": ("metric_id", "name"),
    }
    for key in REFERENCE_KEYS:
        for ref in refs.get(key, []):
            item = maps[key].get(str(ref))
            if not isinstance(item, dict):
                raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.{key} 无效")
            stable_id = next((str(item.get(field) or "") for field in stable_fields[key] if item.get(field)), "")
            if not stable_id:
                raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.{key} 缺少稳定 ID")
            visible = {field: copy.deepcopy(item.get(field)) for field in RENDERER_VISIBLE_FIELDS.get(key, ())}
            bindings.append({"key": key, "position_ref": str(ref), "stable_id": stable_id, "visible": visible})
    return bindings


def validate_canonical_content_ref_bindings(model: dict[str, Any], page: dict[str, Any]) -> None:
    # Editable in-memory plans retain positional refs until analysis evidence
    # creates a content lock. Persisted/finalized models must match exactly.
    if model.get("content_lock") is None:
        return
    locked = page.get("content_ref_bindings")
    if locked is None:
        raise ValueError(f"页面 {page.get('slide_id')} 缺少 content_ref_bindings")
    if locked != canonical_content_ref_bindings(model, page):
        raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs 位置与稳定内容映射不一致")


def canonical_claim_for_page(model: dict[str, Any], page: dict[str, Any]) -> str | None:
    """Resolve the canonical finding claim for a business appendix page only."""

    if str(page.get("layout_id") or "") != "data-appendix":
        return None
    finding_ids = [str(value) for value in page.get("finding_ids", [])]
    if not finding_ids:
        return None
    refs = page.get("content_refs")
    if not isinstance(refs, dict):
        return None
    claim_ref = str(refs.get("claim_ref") or "")
    finding = _id_maps(model)["insight_ids"].get(claim_ref)
    if not isinstance(finding, dict):
        return None
    if str(finding.get("insight_id") or "") not in finding_ids:
        return None
    return canonical_claim(finding)


def _matching_ids(items: dict[str, dict[str, Any]], evidence_ids: list[str]) -> list[str]:
    evidence = set(evidence_ids)
    return [
        item_id for item_id, item in items.items()
        if evidence & set(item.get("evidence_ids", []))
    ]


def _project_scope_kpis(
    model: dict[str, Any], selected: list[dict[str, Any]], scope: str
) -> list[dict[str, Any]]:
    """Project the selected KPI identities without replacing their time scope."""

    selected_keys = {
        str(item.get("kpi_id") or item.get("name") or "") for item in selected
    }
    source = list(model.get(scope, {}).get("kpis") or [])
    return [
        item
        for item in source
        if str(item.get("kpi_id") or item.get("name") or "") in selected_keys
    ]


def _prioritized_contract_ids(model: dict[str, Any], contracts: dict[str, dict[str, Any]]) -> list[str]:
    """Choose appendix contracts once: requested primary metrics, then source order."""

    primary_order = {
        str(name): index
        for index, name in enumerate(model.get("request", {}).get("primary_metrics", []))
    }
    return sorted(
        contracts,
        key=lambda contract_id: (
            0 if str(contracts[contract_id].get("name")) in primary_order else 1,
            primary_order.get(str(contracts[contract_id].get("name")), len(primary_order)),
            list(contracts).index(contract_id),
        ),
    )[:6]


def build_content_refs(model: dict[str, Any], page: dict[str, Any]) -> dict[str, Any]:
    """Build refs only; never copy narrative text or numeric values into a page."""

    maps = _id_maps(model)
    evidence_ids = list(page.get("evidence_ids", []))
    layout = str(page.get("layout_id", ""))
    matched_insight_ids = _matching_ids(maps["insight_ids"], evidence_ids)
    declared_finding_ids = {
        str(value) for value in page.get("finding_ids", []) if str(value)
    }
    if declared_finding_ids:
        matched_insight_ids = [
            item_id for item_id in matched_insight_ids
            if str(maps["insight_ids"][item_id].get("insight_id") or "")
            in declared_finding_ids
        ]
    refs = {
        "kpi_ids": [],
        "insight_ids": matched_insight_ids,
        "action_ids": [],
        "lever_ids": [],
        "chart_ids": list(page.get("chart_ids", [])),
        "contract_ids": [],
    }
    if layout == "kpi-spotlight":
        # Presentation density is selected once by the planner, then every
        # consumer receives those exact KPI IDs instead of a global fallback.
        refs["kpi_ids"] = list(maps["kpi_ids"])[:6]
        if page.get("story_role") == "baseline":
            refs["insight_ids"] = [ref for ref in refs["insight_ids"]
                if maps["insight_ids"][ref].get("presentation_role") == "supporting"
                and maps["insight_ids"][ref].get("claim_type") == "fact"]
        claim_ref = refs["kpi_ids"][0] if refs["kpi_ids"] else "meta:kpi_summary"
    elif layout == "driver-levers":
        refs["lever_ids"] = _matching_ids(maps["lever_ids"], evidence_ids)[:4]
        claim_ref = refs["insight_ids"][0] if refs["insight_ids"] else "meta:analysis_scope"
    elif layout == "risk-opportunity":
        opportunities = [
            item_id for item_id in refs["insight_ids"]
            if maps["insight_ids"][item_id].get("signal_type") in {"opportunity", "seasonality"}
        ][:2]
        risks = [
            item_id for item_id in refs["insight_ids"]
            if maps["insight_ids"][item_id].get("signal_type") == "risk"
        ][:2]
        refs["opportunity_insight_ids"] = opportunities
        refs["risk_insight_ids"] = risks
        refs["opportunity_globally_absent"] = not _globally_selected_signal_present(
            model, maps, {"opportunity", "seasonality"}
        )
        refs["risk_globally_absent"] = not _globally_selected_signal_present(
            model, maps, {"risk"}
        )
        refs["insight_ids"] = list(dict.fromkeys(opportunities + risks))
        claim_ref = (opportunities or risks or refs["insight_ids"])[0] if (opportunities or risks or refs["insight_ids"]) else "meta:analysis_scope"
    elif layout == "action-roadmap":
        if page.get("content_exemption") == "selection_meta":
            claim_ref = "meta:value_selection_status"
        else:
            refs["action_ids"] = _matching_ids(maps["action_ids"], evidence_ids)[:3]
            claim_ref = refs["action_ids"][0] if refs["action_ids"] else "meta:analysis_scope"
    elif layout == "cover":
        claim_ref = "meta:report_title"
    elif layout == "data-appendix":
        refs["contract_ids"] = _prioritized_contract_ids(model, maps["contract_ids"])
        selected = set(str(value) for value in page.get("finding_ids", []))
        if selected:
            refs["insight_ids"] = [
                ref for ref, item in maps["insight_ids"].items()
                if str(item.get("insight_id") or "") in selected
            ]
        claim_ref = refs["insight_ids"][0] if refs["insight_ids"] else "meta:data_profile"
    elif refs["insight_ids"]:
        claim_ref = refs["insight_ids"][0]
    elif refs["chart_ids"]:
        claim_ref = refs["chart_ids"][0]
    else:
        claim_ref = "meta:analysis_scope"
    if layout == "executive-summary":
        summary = model.get("executive_summary", {})
        refs["insight_ids"] = list(refs["insight_ids"][:3])
        refs["action_ids"] = _matching_ids(maps["action_ids"], evidence_ids)[:2]
        refs["summary_refs"] = {
            "insight_ids": list(refs["insight_ids"]),
            "action_ids": list(refs["action_ids"]),
            "conclusion_indexes": list(range(1, min(3, len(summary.get("key_conclusions", []))) + 1)),
            "priority_action_indexes": list(range(1, min(2, len(summary.get("priority_actions", []))) + 1)),
        }
    return {"claim_ref": claim_ref, **refs}


def resolve_page_content(model: dict[str, Any], page: dict[str, Any]) -> dict[str, Any]:
    """Resolve exactly one page's payload from refs, with no renderer selection."""

    refs = page.get("content_refs")
    if not isinstance(refs, dict):
        raise ValueError(f"页面 {page.get('slide_id')} 缺少 content_refs")
    maps = _id_maps(model)
    is_new_page = "role" in page
    if is_new_page:
        missing_reference_keys = set(REFERENCE_KEYS) - set(refs)
        if missing_reference_keys:
            raise ValueError(
                f"页面 {page.get('slide_id')} 的 content_refs 缺少："
                + ", ".join(sorted(missing_reference_keys))
            )
        allowed_reference_keys = set(REFERENCE_KEYS) | {
            "claim_ref", "summary_refs", "opportunity_insight_ids", "risk_insight_ids",
            "opportunity_globally_absent", "risk_globally_absent",
        }
        unknown_reference_keys = set(refs) - allowed_reference_keys
        if unknown_reference_keys:
            raise ValueError(
                f"页面 {page.get('slide_id')} 的 content_refs 包含未知引用："
                + ", ".join(sorted(unknown_reference_keys))
            )
    resolved: dict[str, list[dict[str, Any]]] = {}
    for key in REFERENCE_KEYS:
        values = refs.get(key, [])
        if not isinstance(values, list):
            raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.{key} 必须是列表")
        unknown = [value for value in values if value not in maps[key]]
        if unknown:
            raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.{key} 无效：{', '.join(unknown)}")
        payload_key = {
            "kpi_ids": "kpis",
            "insight_ids": "insights",
            "action_ids": "actions",
            "lever_ids": "levers",
            "chart_ids": "charts",
            "contract_ids": "metric_contracts",
        }[key]
        resolved[payload_key] = [maps[key][value] for value in values]
    if refs.get("chart_ids", []) != list(page.get("chart_ids", [])):
        raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.chart_ids 必须与 chart_ids 一致")
    claim_ref = str(refs.get("claim_ref") or "")
    allowed_claim_refs = {"meta:report_title", "meta:kpi_summary", "meta:data_profile", "meta:analysis_scope", "meta:value_selection_status"}
    known_refs = {reference for key in REFERENCE_KEYS for reference in maps[key]}
    if claim_ref not in allowed_claim_refs | known_refs:
        raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.claim_ref 无效：{claim_ref}")
    if claim_ref in known_refs and not any(claim_ref in refs[key] for key in REFERENCE_KEYS):
        raise ValueError(f"页面 {page.get('slide_id')} 的 claim_ref 必须属于本页 content_refs")
    finding_ids = [str(value) for value in page.get("finding_ids", [])]
    if page.get("content_exemption") == "data_contract" and finding_ids:
        raise ValueError(f"页面 {page.get('slide_id')} 承载业务 finding 时不得使用 data_contract 豁免")
    if finding_ids:
        referenced_finding_ids = [
            str(maps["insight_ids"][value].get("insight_id") or "")
            for value in refs.get("insight_ids", [])
        ]
        if set(referenced_finding_ids) != set(finding_ids):
            raise ValueError(
                f"页面 {page.get('slide_id')} 的 content_refs.insight_ids "
                "必须与 finding_ids 一致"
            )
    if (
        is_new_page
        and page.get("layout_id") in {"trend-wide", "chart-insight-action"}
        and not refs.get("insight_ids")
    ):
        raise ValueError(f"趋势页 {page.get('slide_id')} 的 content_refs.insight_ids 不得为空")
    summary_refs = refs.get("summary_refs")
    if is_new_page and page.get("layout_id") == "executive-summary" and summary_refs is None:
        raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.summary_refs 缺失")
    if summary_refs is not None:
        if page.get("layout_id") != "executive-summary" or not isinstance(summary_refs, dict):
            raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.summary_refs 无效")
        summary_keys = {"insight_ids", "action_ids", "conclusion_indexes", "priority_action_indexes"}
        if is_new_page and set(summary_refs) != summary_keys:
            raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.summary_refs 缺失或包含未知键")
        for key, values in summary_refs.items():
            if key not in summary_keys or not isinstance(values, list):
                raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.summary_refs 无效")
        if is_new_page and not summary_keys <= set(summary_refs):
            raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.summary_refs 缺失")
        if summary_refs.get("insight_ids", []) != refs["insight_ids"] or summary_refs.get("action_ids", []) != refs["action_ids"]:
            raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.summary_refs 必须与页面 refs 一致")
        summary = model.get("executive_summary", {})
        indexed_collections = (
            ("conclusion_indexes", list(summary.get("key_conclusions", [])), 3),
            ("priority_action_indexes", list(summary.get("priority_actions", [])), 2),
        )
        for key, collection, capacity in indexed_collections:
            indexes = summary_refs.get(key, [])
            if any(type(index) is not int or index < 1 for index in indexes):
                raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.summary_refs 索引无效")
            if len(indexes) != len(set(indexes)) or len(indexes) > capacity:
                raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.summary_refs 索引无效")
            if any(index > len(collection) for index in indexes):
                raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.summary_refs 索引超出范围")
            if any(not str(collection[index - 1]).strip() for index in indexes):
                raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.summary_refs 选择了空摘要")
        engineering_qa = (
            str(model.get("request", {}).get("analysis_intent") or "")
            == "engineering_regression"
            and page.get("content_exemption") == "qa"
        )
        requires_business_summary = is_new_page and not engineering_qa
        if requires_business_summary and not summary_refs["conclusion_indexes"]:
            raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.summary_refs 必须选择摘要结论")
        has_formal_actions = any(action.get("formal", True) for action in model.get("actions", []))
        if requires_business_summary and has_formal_actions and not summary_refs["priority_action_indexes"]:
            raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.summary_refs 必须选择优先行动")
    for group_key in ("opportunity_insight_ids", "risk_insight_ids"):
        values = refs.get(group_key)
        if is_new_page and page.get("layout_id") == "risk-opportunity" and values is None:
            raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.{group_key} 缺失")
        if values is None:
            continue
        if page.get("layout_id") != "risk-opportunity" or not isinstance(values, list):
            raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.{group_key} 无效")
        if len(values) > 2 or len(values) != len(set(values)) or any(value not in refs["insight_ids"] for value in values):
            raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.{group_key} 无效")
        expected_signal = {"opportunity", "seasonality"} if group_key.startswith("opportunity") else {"risk"}
        if any(maps["insight_ids"][value].get("signal_type") not in expected_signal for value in values):
            raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.{group_key} 信号类别无效")
    if page.get("layout_id") == "risk-opportunity":
        grouped = list(dict.fromkeys(refs.get("opportunity_insight_ids", []) + refs.get("risk_insight_ids", [])))
        if is_new_page and not grouped:
            raise ValueError(f"页面 {page.get('slide_id')} 的 risk-opportunity 至少需要一组证据")
        if grouped and refs["insight_ids"] != grouped:
            raise ValueError(f"页面 {page.get('slide_id')} 的 risk-opportunity insight_ids 必须等于分组并集")
    if page.get("layout_id") == "data-appendix" and finding_ids:
        expected_refs = [
            ref for ref, insight in maps["insight_ids"].items()
            if str(insight.get("insight_id") or "") in finding_ids
        ]
        if (
            len(finding_ids) != 1
            or len(set(finding_ids)) != 1
            or refs["insight_ids"] != expected_refs
            or claim_ref != expected_refs[0]
        ):
            raise ValueError(f"页面 {page.get('slide_id')} 的 appendix finding/content_refs 必须一对一")
        finding = maps["insight_ids"][expected_refs[0]]
        selected_finding = next(
            (
                item for item in (model.get("value_selection", {}).get("appendix", []))
                if isinstance(item, dict)
                and str(item.get("insight_id") or "") == finding_ids[0]
            ),
            finding,
        )
        expected_question = str(selected_finding.get("business_question") or finding.get("business_question") or "")
        expected_lens = str(selected_finding.get("lens") or finding.get("lens") or "")
        if (
            str(page.get("business_question") or "") != expected_question
        ):
            raise ValueError(f"页面 {page.get('slide_id')} 的 appendix finding 问题标识不一致")
        question = next(
            (
                candidate for candidate in model.get("analysis_lenses", [])
                if str(candidate.get("business_question") or "") == expected_question
                and (
                    not expected_lens
                    or str(candidate.get("lens") or "") == expected_lens
                )
            ),
            None,
        )
        if not isinstance(question, dict) or str(page.get("question_id") or "") != str(question.get("question_id") or ""):
            raise ValueError(f"页面 {page.get('slide_id')} 的 appendix finding 问题标识不一致")
        expected_evidence = list(question.get("evidence_ids", [])) if isinstance(question, dict) else list(selected_finding.get("evidence_ids", []))
        if set(page.get("evidence_ids", [])) != set(expected_evidence):
            raise ValueError(f"页面 {page.get('slide_id')} 的 appendix finding 证据范围不完整")
        expected_claim = canonical_claim_for_page(model, page)
        if not expected_claim or normalize_claim_text(page.get("claim")) != expected_claim:
            raise ValueError(f"页面 {page.get('slide_id')} 的 appendix canonical claim 必须等于引用 finding")
        visual_spec = page.get("visual_spec")
        if isinstance(visual_spec, dict) and "display_claim" in visual_spec and (
            normalize_claim_text(visual_spec.get("display_claim")) != expected_claim
        ):
            raise ValueError(f"页面 {page.get('slide_id')} 的 appendix canonical claim 必须等于 display_claim")
    contract_ids = refs.get("contract_ids")
    if is_new_page and page.get("layout_id") == "data-appendix" and contract_ids is None:
        raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.contract_ids 缺失")
    if contract_ids is not None:
        if not isinstance(contract_ids, list):
            raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.contract_ids 无效")
        if page.get("layout_id") != "data-appendix" and contract_ids:
            raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.contract_ids 无效")
        if len(contract_ids) > 6 or len(contract_ids) != len(set(contract_ids)):
            raise ValueError(f"页面 {page.get('slide_id')} 的 content_refs.contract_ids 无效")
    validate_canonical_content_ref_bindings(model, page)
    return {
        "slide_id": page["slide_id"],
        "claim": page.get("claim", ""),
        "purpose": page.get("purpose", ""),
        "evidence_ids": list(page.get("evidence_ids", [])),
        "chart_ids": list(page.get("chart_ids", [])),
        "content_refs": refs,
        "opportunity_insights": [maps["insight_ids"][item_id] for item_id in refs.get("opportunity_insight_ids", [])],
        "risk_insights": [maps["insight_ids"][item_id] for item_id in refs.get("risk_insight_ids", [])],
        "opportunity_globally_absent": bool(refs.get("opportunity_globally_absent", False)),
        "risk_globally_absent": bool(refs.get("risk_globally_absent", False)),
        **resolved,
    }


def validate_content_refs(model: dict[str, Any]) -> None:
    for page in model.get("slide_plan", []):
        resolve_page_content(model, page)


def validate_renderer_model(model: dict[str, Any]) -> None:
    """Recheck the whole modern model before any renderer consumes one page."""

    if is_modern_model(model):
        validate_formal_renderer_records(model)
        validate_content_refs(model)
    if model.get("content_lock") is not None:
        # Local import avoids the model-validation/content-resolver import
        # cycle while ensuring a locked formal artifact enforces its complete
        # projection. Unlocked partial models remain valid for internal
        # slide-contract construction, where no finalized content may leak.
        from model_validation import validate_report_model

        validate_report_model(model)


def project_legacy_content_refs(model: dict[str, Any]) -> dict[str, Any]:
    """Create an in-memory, one-time projection for persisted v2 models.

    New builders must persist refs and remain strict.  This adapter only lets
    legacy models reach the same resolver path without mutating the source.
    """

    pages = list(model.get("slide_plan", []))
    if not pages or all(isinstance(page.get("content_refs"), dict) for page in pages):
        return model
    if any("content_refs" in page for page in pages):
        raise ValueError("legacy projection requires either zero or complete content_refs")
    if is_modern_model(model):
        raise ValueError("modern report_model 不得降级为 legacy content_refs projection")
    if model.get(LEGACY_CONTENT_REFS_MARKER) is not True:
        raise ValueError("legacy content_refs projection 需要明确 legacy fixture marker")
    projected = copy.deepcopy(model)
    # Legacy v2 reports had only positional slide references and therefore no
    # business IDs for findings/actions.  This in-memory adapter gives those
    # old records deterministic projection identities; persisted, locked
    # models still have to provide their own stable IDs before rendering.
    for index, insight in enumerate(projected.get("insights", []), 1):
        if isinstance(insight, dict) and not str(insight.get("insight_id") or "").strip():
            insight["insight_id"] = f"legacy-insight:{index}"
    for index, action in enumerate(projected.get("actions", []), 1):
        if isinstance(action, dict) and not str(action.get("action_id") or "").strip():
            action["action_id"] = f"legacy-action:{index}"
    for page in projected["slide_plan"]:
        page["content_refs"] = build_content_refs(projected, page)
        page["content_ref_bindings"] = canonical_content_ref_bindings(projected, page)
    return projected


def resolve_model_for_page(model: dict[str, Any], page: dict[str, Any]) -> dict[str, Any]:
    """Return a renderer-facing model restricted to one page's approved refs."""

    # A renderer may be invoked for one page, but it must not validate only
    # that page and leak an invalid formal record elsewhere in the model.
    validate_renderer_model(model)
    payload = resolve_page_content(model, page)
    scoped = copy.copy(model)
    scoped["kpis"] = payload["kpis"]
    scoped["insights"] = payload["insights"]
    scoped["actions"] = payload["actions"]
    scoped["levers"] = payload["levers"]
    scoped["charts"] = payload["charts"]
    scoped["opportunity_insights"] = payload["opportunity_insights"]
    scoped["risk_insights"] = payload["risk_insights"]
    scoped["opportunity_globally_absent"] = payload["opportunity_globally_absent"]
    scoped["risk_globally_absent"] = payload["risk_globally_absent"]
    if page.get("layout_id") == "data-appendix":
        scoped["metric_contracts"] = payload["metric_contracts"]
    scoped["period_overview"] = {
        **model.get("period_overview", {}),
        "kpis": _project_scope_kpis(model, payload["kpis"], "period_overview"),
    }
    scoped["latest_snapshot"] = {
        **model.get("latest_snapshot", {}),
        "kpis": _project_scope_kpis(model, payload["kpis"], "latest_snapshot"),
    }
    summary = model.get("executive_summary", {})
    page_evidence = set(page.get("evidence_ids", []))
    summary_refs = page.get("content_refs", {}).get("summary_refs", {})
    conclusions = list(summary.get("key_conclusions", []))
    conclusion_evidence = list(summary.get("key_conclusion_evidence_ids", []))
    if summary_refs:
        conclusion_indexes = summary_refs.get("conclusion_indexes", [])
        action_indexes = summary_refs.get("priority_action_indexes", [])
        # resolve_page_content has already validated the exact declared
        # indexes.  Renderers consume them directly and never skip or replace
        # an out-of-range item.
        scoped_conclusions = [conclusions[index - 1] for index in conclusion_indexes]
        scoped_actions = [summary["priority_actions"][index - 1] for index in action_indexes]
    else:
        scoped_conclusions = [
            conclusion
            for conclusion, evidence_ids in zip(conclusions, conclusion_evidence)
            if set(evidence_ids) & page_evidence
        ]
        scoped_actions = []
    selected_actions = {
        str(item.get("text") or item.get("headline") or item.get("action") or "").rstrip("，。；： ")
        for item in payload["actions"]
    }
    if not summary_refs:
        scoped_actions = [
            action
            for action in summary.get("priority_actions", [])
            if str(action).rstrip("，。；： ") in selected_actions
        ]
    # Preserve the canonical summary strings.  A renderer may filter a page's
    # payload by approved refs, but it must not rewrite a selected conclusion.
    scoped["executive_summary"] = {
        **summary,
        "key_conclusions": scoped_conclusions,
        "key_conclusion_evidence_ids": [
            conclusion_evidence[index - 1]
            for index in summary_refs.get("conclusion_indexes", [])
            if index <= len(conclusion_evidence)
        ] if summary_refs else [
            evidence_ids
            for evidence_ids in conclusion_evidence
            if set(evidence_ids) & page_evidence
        ],
        "priority_actions": scoped_actions,
    }
    return scoped


def resolve_model_for_pages(model: dict[str, Any]) -> dict[str, Any]:
    """Union page payloads in plan order; used by non-page HTML sections."""

    validate_renderer_model(model)
    scoped = copy.copy(model)
    collections = {"kpis": [], "insights": [], "actions": [], "levers": [], "charts": []}
    for page in model.get("slide_plan", []):
        payload = resolve_page_content(model, page)
        for key in collections:
            for item in payload[key]:
                if item not in collections[key]:
                    collections[key].append(item)
    scoped.update(collections)
    scoped["period_overview"] = {
        **model.get("period_overview", {}),
        "kpis": _project_scope_kpis(model, collections["kpis"], "period_overview"),
    }
    scoped["latest_snapshot"] = {
        **model.get("latest_snapshot", {}),
        "kpis": _project_scope_kpis(model, collections["kpis"], "latest_snapshot"),
    }
    summary_page = next(
        (page for page in model.get("slide_plan", []) if page.get("layout_id") == "executive-summary"),
        None,
    )
    if summary_page is not None:
        scoped["executive_summary"] = resolve_model_for_page(
            model, summary_page
        )["executive_summary"]
    return scoped
