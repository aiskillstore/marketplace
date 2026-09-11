from __future__ import annotations

from typing import Any

from content_resolver import canonical_claim, canonical_claim_for_page, build_content_refs, canonical_content_ref_bindings, normalize_claim_text
from presentation_contracts import build_visual_spec
from story_topology import (
    canonical_story_sort_key,
    management_presentation_order,
    story_topology_is_valid,
)


_LAYOUT_BY_STORY_ROLE = {
    "cover": ("cover", "cover"),
    "executive_summary": ("executive-summary", "narrative"),
    "baseline": ("kpi-spotlight", "spotlight"),
    "driver": ("chart-side-kpi", "chart-sidebar"),
    "opportunity": ("chart-insight-action", "wide-chart"),
    # A risk finding is not evidence that an opportunity is absent elsewhere
    # in the report.  Keep its page single-signal unless a planner explicitly
    # constructs a balanced comparison with both sides bound.
    "risk": ("chart-insight-action", "wide-chart"),
    "decision": ("action-roadmap", "roadmap"),
    "action": ("action-roadmap", "roadmap"),
    "appendix": ("data-appendix", "appendix"),
}


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values if value))


def _claim(item: dict[str, Any], fallback: str) -> str:
    return canonical_claim(item, fallback)


def claim_signature(claim: str, evidence_ids: list[str]) -> tuple[str, frozenset[str]]:
    """Return the one claim/evidence identity shared by story and content QA."""

    return normalize_claim_text(claim).replace(" ", ""), frozenset(_unique(evidence_ids))


def _selected_findings(model: dict[str, Any], classification: str) -> list[dict[str, Any]]:
    value_selection = model.get("value_selection")
    if not isinstance(value_selection, dict):
        return []
    evidence_index = set(model.get("evidence_index", {}))
    findings = [
        dict(item)
        for item in value_selection.get(classification, [])
        if str(item.get("classification") or classification) == classification
        and item.get("evidence_valid") is True
        and str(item.get("answer_status") or "") in {"answered", "partial"}
        and str(item.get("resolution_status") or "") != "deferred_to_user"
        and item.get("evidence_ids")
        and set(str(value) for value in item.get("evidence_ids", [])) <= evidence_index
    ]
    analysis_contract = model.get("analysis_contract", {})
    request = model.get("request", {})
    if (
        isinstance(analysis_contract, dict)
        and str(analysis_contract.get("adapter_id") or "") == "transactional_commerce"
        and isinstance(request, dict)
        and str(request.get("analysis_intent") or "business_review") == "business_review"
    ):
        return management_presentation_order(findings)
    return findings


def _story_role_for_finding(finding: dict[str, Any]) -> str:
    signal = str(finding.get("signal_type") or "").lower()
    if signal == "risk":
        return "risk"
    if signal in {"opportunity", "seasonality"}:
        return "opportunity"
    return "driver"


def _valid_kpi_evidence(model: dict[str, Any]) -> list[str]:
    evidence_index = set(model.get("evidence_index", {}))
    return _unique([
        evidence_id
        for kpi in model.get("kpis", [])
        for evidence_id in kpi.get("evidence_ids", [])
        if evidence_id in evidence_index
    ])


def _action_claim(action: dict[str, Any], evidence_index: dict[str, Any]) -> str:
    target = str(action.get("target") or "").strip()
    action_text = str(action.get("headline") or action.get("text") or action.get("action") or "行动建议").strip()
    for evidence_id in action.get("evidence_ids", []):
        evidence = evidence_index.get(evidence_id, {})
        metric = str(evidence.get("metric") or evidence.get("name") or "").strip()
        if metric:
            candidate = f"{target or action_text}：基于{metric}证据推进"
            units = 0
            compact: list[str] = []
            for character in candidate:
                width = 2 if ord(character) > 127 else 1
                if units + width > 52:
                    return "".join(compact).rstrip("，。；：") + "…"
                compact.append(character)
                units += width
            return candidate
    return action_text


def _finding_groups(findings: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Merge only genuinely identical question-and-evidence findings."""

    grouped: dict[tuple[str, tuple[str, ...], str, str], list[dict[str, Any]]] = {}
    order: list[tuple[str, tuple[str, ...], str, str]] = []
    for finding in findings:
        evidence_ids = tuple(_unique(list(finding.get("evidence_ids", []))))
        key = (
            str(finding.get("business_question") or finding.get("lens") or finding.get("insight_id") or ""),
            evidence_ids,
            _story_role_for_finding(finding),
            claim_signature(_claim(finding, ""), list(evidence_ids))[0],
        )
        if key not in grouped:
            grouped[key] = []
            order.append(key)
        grouped[key].append(finding)
    return [grouped[key] for key in order]


def _requires_decision(actions: list[dict[str, Any]], model: dict[str, Any]) -> bool:
    decision_fields = ("decision_request", "resource_request", "requires_approval", "approval_required")
    return any(
        bool(item.get(field))
        for item in [*actions, model.get("request", {}), model]
        for field in decision_fields
    )


def _page(
    model: dict[str, Any],
    *,
    story_role: str,
    claim: str,
    purpose: str,
    evidence_ids: list[str],
    chart_ids: list[str] | None = None,
    claim_evidence_ids: list[str] | None = None,
    selection_score: float = 0,
    lens: str | None = None,
    content_exemption: str | None = None,
    layout_id: str | None = None,
    silhouette: str | None = None,
    business_question: str | None = None,
    question_id: str | None = None,
    finding_ids: list[str] | None = None,
) -> dict[str, Any]:
    default_layout_id, default_silhouette = _LAYOUT_BY_STORY_ROLE[story_role]
    layout_id = layout_id or default_layout_id
    silhouette = silhouette or default_silhouette
    page: dict[str, Any] = {
        "layout_id": layout_id,
        "silhouette": silhouette,
        "story_role": story_role,
        "role": layout_id,
        "claim": claim,
        "purpose": purpose,
        "page_reason": purpose,
        "selection_score": selection_score,
        "evidence_ids": _unique(evidence_ids),
        "claim_evidence_ids": _unique(claim_evidence_ids or evidence_ids),
        "chart_ids": _unique(chart_ids or []),
        "finding_ids": _unique(finding_ids or []),
    }
    if lens:
        page["lens"] = lens
        page["covered_lenses"] = [lens]
    if business_question:
        page["business_question"] = business_question
    if question_id:
        page["question_id"] = question_id
    if content_exemption:
        page["content_exemption"] = content_exemption
    return page


def _add_projection_fields(model: dict[str, Any], pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for index, page in enumerate(pages, 1):
        page["slide_id"] = f"S{index:02d}"
        page["content_refs"] = build_content_refs(model, page)
        page["content_ref_bindings"] = canonical_content_ref_bindings(model, page)
        page["visual_spec"] = build_visual_spec(model, page)
        canonical = canonical_claim_for_page(model, page)
        if canonical:
            # A business appendix has no editorial rewrite budget: the renderer
            # must display the exact canonical finding selected by claim_ref.
            page["visual_spec"]["display_claim"] = canonical
    return pages


def _question_id_for_finding(model: dict[str, Any], finding: dict[str, Any]) -> str:
    """Resolve the stable question identity without deriving a business claim."""

    direct = str(finding.get("question_id") or "").strip()
    if direct:
        return direct
    question = str(finding.get("business_question") or "").strip()
    lens = str(finding.get("lens") or "").strip()
    for candidate in model.get("analysis_lenses", []):
        if (
            str(candidate.get("business_question") or "").strip() == question
            and (not lens or str(candidate.get("lens") or "").strip() == lens)
        ):
            return str(candidate.get("question_id") or "").strip()
    return ""


def _question_evidence_for_finding(model: dict[str, Any], finding: dict[str, Any]) -> list[str]:
    """Carry the complete required/used evidence scope for a covered question."""

    question_id = _question_id_for_finding(model, finding)
    question = str(finding.get("business_question") or "").strip()
    for candidate in model.get("analysis_lenses", []):
        if (
            (question_id and str(candidate.get("question_id") or "") == question_id)
            or (not question_id and str(candidate.get("business_question") or "").strip() == question)
        ):
            return _unique(list(finding.get("evidence_ids", [])) + list(candidate.get("evidence_ids", [])))
    return _unique(list(finding.get("evidence_ids", [])))


def _has_answered_question_evidence(model: dict[str, Any]) -> bool:
    evidence = set(model.get("evidence_index", {}))
    return any(
        str(question.get("answer_status") or "") in {"answered", "partial"}
        and bool(question.get("evidence_ids"))
        and set(str(value) for value in question.get("evidence_ids", [])) <= evidence
        for question in model.get("analysis_lenses", [])
    )


def unresolved_question_records(model: dict[str, Any], pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Canonical dispositions, distinct from answered business-page coverage."""
    known = set(model.get("evidence_index", {}))
    levels = {0: "尚无有效证据", 1: "事实与变化", 2: "驱动线索", 3: "细分结构", 4: "经营判断", 5: "行动闭环"}
    stop_labels = {"no_new_information": "已执行补查没有增加新的证据",
                   "budget_exhausted": "本次受控补查预算已用完",
                   "missing_required_field": "当前没有可执行的已确认补查路径"}
    records = []
    for question in model.get("analysis_lenses", []):
        if question.get("status") != "selected" and question.get("selection_status") != "selected":
            continue
        question_id = str(question.get("question_id") or "")
        text = str(question.get("business_question") or "").strip()
        evidence_ids = _unique(list(question.get("evidence_ids", [])))
        if not text or not set(evidence_ids) <= known:
            continue
        required, achieved = question.get("required_depth"), question.get("achieved_depth")
        shallow = type(required) is int and type(achieved) is int and achieved < required
        covered = not shallow and any(
            page.get("story_role") in {"driver", "opportunity", "risk", "appendix", "baseline"}
            and (page.get("story_role") != "baseline" or question.get("lens") == "overview")
            and str(page.get("business_question") or "") == text
            and (not question_id or str(page.get("question_id") or "") == question_id)
            and bool(evidence_ids) and set(evidence_ids) <= set(page.get("evidence_ids", []))
            and (page.get("story_role") != "appendix" or bool(page.get("finding_ids")))
            for page in pages
        )
        if covered:
            continue
        reason = (f"目前达到{levels.get(achieved, '已记录证据')}，尚未达到{levels.get(required, '所需深度')}；不将本问题作为核心判断。"
                  if shallow else "本问题未形成达到本次正文选择门槛的判断，不据此新增资源调整建议。")
        stop_reason = question.get("stop_reason")
        if stop_reason in stop_labels:
            reason += stop_labels[stop_reason] + "。"
        records.append({"question_id": question_id, "business_question": text, "evidence_ids": evidence_ids,
                        "answer_status": question.get("answer_status"), "required_depth": required, "achieved_depth": achieved,
                        "depth_gaps": list(question.get("depth_gaps", [])), "stop_reason": stop_reason, "reason": reason,
                        "next_step": ("补齐驱动、细分与经营含义的证据闭环后，再判断是否需要行动。" if shallow
                                      else "保留已有证据；出现新的决策相关信息时重新评估是否进入正文。")})
    return records


def _build_no_selection_closure(
    model: dict[str, Any], *, appendix: list[dict[str, Any]] | None = None
) -> list[dict[str, Any]]:
    """Report a selection outcome without exposing any dropped business claim."""

    reason = "当前没有达到决策展示阈值的发现；不据此调整资源，并建议补充决策目标后再复核。"
    model["narrative_selection"] = {
        "status": "no_findings_selected", "reason": reason, "selected_count": 0,
    }
    model["report_summary"] = reason
    pages = [_page(
        model, story_role="cover",
        claim=str(model.get("report_title") or model.get("title") or "数据分析简报"),
        purpose="建立本次经营复盘的范围、对象与决策目标",
        evidence_ids=[], claim_evidence_ids=[], content_exemption="cover", selection_score=100,
    )]
    kpi_evidence = _valid_kpi_evidence(model)
    if kpi_evidence:
        first_kpi = list(model.get("kpis", []))[0] if model.get("kpis") else {}
        pages.append(_page(
            model, story_role="baseline",
            claim=f"{first_kpi.get('display_name') or first_kpi.get('name') or '核心指标'}整体基线",
            purpose="保留可验证的经营基线，但本次不将低价值发现升级为决策结论",
            evidence_ids=kpi_evidence, claim_evidence_ids=list(first_kpi.get("evidence_ids", [])),
            selection_score=100, lens="overview",
        ))
    pages.append(_page(
        model, story_role="action", claim="本次不据低价值发现调整资源",
        purpose=reason, evidence_ids=[], claim_evidence_ids=[], selection_score=0,
        content_exemption="selection_meta", layout_id="action-roadmap", silhouette="roadmap",
    ))
    for item in appendix or []:
        pages.append(_page(
            model,
            story_role="appendix",
            claim=_claim(item, "补充证据"),
            purpose="承载已选择但不进入主决策链的补充证据",
            evidence_ids=_question_evidence_for_finding(model, item),
            claim_evidence_ids=[],
            selection_score=float(item.get("score") or 0),
            lens=str(item.get("lens") or ""),
            business_question=str(item.get("business_question") or "") or None,
            question_id=_question_id_for_finding(model, item) or None,
            finding_ids=[str(item.get("insight_id") or "")],
        ))
    pages.sort(key=canonical_story_sort_key)
    return _add_projection_fields(model, pages)


def build_decision_narrative(
    report_model: dict[str, Any], *, adapter_inputs: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Project selected, explicitly answered findings into an adaptive report story."""

    featured = _selected_findings(report_model, "featured")
    appendix = _selected_findings(report_model, "appendix")
    evidence_index = report_model.get("evidence_index", {})
    pages: list[dict[str, Any]] = []

    # A statement cannot re-enter the narrative merely because it has text.
    # The value-selection answer contract is the gate for every business page.
    selected = [*featured, *appendix]
    if not selected:
        return (
            _build_no_selection_closure(report_model)
            if _has_answered_question_evidence(report_model)
            else []
        )
    if not featured:
        return _build_no_selection_closure(report_model, appendix=appendix)

    if selected:
        summary = report_model.setdefault("executive_summary", {})
        # Appendix-only facts may support the evidence trail, but must never
        # flow back into the executive summary after value selection has
        # explicitly left the featured set empty.
        if featured and not summary.get("key_conclusions"):
            summary["key_conclusions"] = [_claim(featured[0], "经营结论待确认")]
            summary["key_conclusion_evidence_ids"] = [
                list(featured[0].get("evidence_ids", []))
            ]
            summary["key_conclusion_insight_ids"] = [
                str(featured[0].get("insight_id") or "")
            ]
        if "priority_actions" not in summary:
            summary["priority_actions"] = []
        pages.append(_page(
            report_model,
            story_role="cover",
            claim=str(report_model.get("report_title") or report_model.get("title") or "数据分析简报"),
            purpose="建立本次经营复盘的范围、对象与决策目标",
            evidence_ids=[],
            claim_evidence_ids=[],
            content_exemption="cover",
            selection_score=100,
        ))
        summary_evidence = _unique([
            evidence_id for item in selected[:3] for evidence_id in item.get("evidence_ids", [])
        ])
        pages.append(_page(
            report_model,
            story_role="executive_summary",
            claim=_claim(selected[0], "经营结论待确认"),
            purpose="汇总已回答业务问题，明确管理者需优先处理的判断",
            evidence_ids=summary_evidence,
            claim_evidence_ids=list(selected[0].get("evidence_ids", [])),
            selection_score=float(selected[0].get("score") or 0),
            lens=str(selected[0].get("lens") or "overview"),
        ))

    kpi_evidence = _valid_kpi_evidence(report_model)
    if kpi_evidence:
        kpis = list(report_model.get("kpis", []))
        first_kpi = kpis[0] if kpis else {}
        overview_question = next((
            question for question in report_model.get("analysis_lenses", [])
            if str(question.get("lens") or "") == "overview"
            and str(question.get("answer_status") or "") in {"answered", "partial"}
            and question.get("evidence_ids")
        ), None)
        baseline_evidence = _unique(
            kpi_evidence + (list(overview_question.get("evidence_ids", [])) if overview_question else [])
        )
        pages.append(_page(
            report_model,
            story_role="baseline",
            claim=f"{first_kpi.get('display_name') or first_kpi.get('name') or '核心指标'}整体基线",
            purpose="呈现有证据支撑的经营基线，作为后续判断的共同口径",
            evidence_ids=baseline_evidence,
            claim_evidence_ids=list(first_kpi.get("evidence_ids", [])),
            selection_score=100,
            lens="overview",
            business_question=(str(overview_question.get("business_question") or "") if overview_question else None),
            question_id=(str(overview_question.get("question_id") or "") if overview_question else None),
        ))

    used_chart_ids: set[str] = set()
    adapter_inputs = adapter_inputs or {}
    charts = list(adapter_inputs.get("charts", report_model.get("charts", [])))
    levers = list(adapter_inputs.get("levers", report_model.get("levers", [])))
    actions = list(adapter_inputs.get("actions", report_model.get("actions", [])))
    used_lever_layout = False
    finding_groups = _finding_groups(featured)
    global_opportunity_selected = any(
        _story_role_for_finding(item) == "opportunity" for item in featured
    )
    for group in finding_groups:
        finding = group[0]
        story_role = _story_role_for_finding(finding)
        claim_evidence_ids = _unique([
            evidence_id for item in group for evidence_id in item.get("evidence_ids", [])
        ])
        evidence_ids = _unique([
            evidence_id
            for item in group
            for evidence_id in _question_evidence_for_finding(report_model, item)
        ])
        chart_candidates = [
            item for item in charts
            if str(item.get("chart_id")) not in used_chart_ids
            and set(item.get("evidence_ids", [])) & set(claim_evidence_ids)
        ]
        evidence_order = {
            evidence_id: index for index, evidence_id in enumerate(claim_evidence_ids)
        }
        chart = min(
            chart_candidates,
            key=lambda item: (
                min(
                    evidence_order[evidence_id]
                    for evidence_id in item.get("evidence_ids", [])
                    if evidence_id in evidence_order
                ),
                -len(set(item.get("evidence_ids", [])) & set(claim_evidence_ids)),
                str(item.get("chart_id") or ""),
            ),
            default=None,
        )
        chart_ids = [str(chart["chart_id"])] if chart else []
        uses_levers = (
            not used_lever_layout
            and bool(levers)
            and len(finding_groups) > 1
            and str(finding.get("lens") or "") == "growth_driver"
        )
        if uses_levers:
            # The retail/transactional adapters have already produced a
            # bounded, evidence-backed business-lever view.  Prefer it for
            # the first selected growth-driver question so both HTML and PPT
            # consume the same semantic payload instead of silently dropping
            # it behind a generic chart card.
            chart_ids = []
            used_lever_layout = True
        used_chart_ids.update(chart_ids)
        if (
            story_role == "driver"
            and not chart_ids
            and not levers
            and report_model.get("analysis_lenses")
        ):
            # A driver-levers layout without declared levers would be a fake
            # content container; the high-priority coverage gate will surface
            # any resulting unanswered business question.
            continue
        has_bound_action = any(
            set(action.get("evidence_ids", [])) & set(claim_evidence_ids)
            for action in actions
        )
        if uses_levers:
            layout_id, silhouette = "driver-levers", "levers"
        elif chart_ids:
            layout_id, silhouette = _LAYOUT_BY_STORY_ROLE[story_role]
        elif story_role == "risk" and has_bound_action:
            # A risk claim without a chart still has a concrete, evidence-bound
            # management response.  Use the native single-sided action layout
            # rather than pretending this page contains a chart.
            layout_id, silhouette = "action-roadmap", "roadmap"
        elif story_role == "risk" and not global_opportunity_selected:
            # A two-sided risk/opportunity page may state that opportunity is
            # absent only when the selected story actually has none.
            layout_id, silhouette = "risk-opportunity", "risk-opportunity"
        else:
            layout_id, silhouette = "driver-levers", "levers"
        pages.append(_page(
            report_model,
            story_role=story_role,
            claim=_claim(finding, "已选择的经营判断"),
            purpose=f"回答业务问题：{finding.get('business_question') or finding.get('lens') or '当前经营判断'}",
            evidence_ids=evidence_ids,
            chart_ids=chart_ids,
            claim_evidence_ids=claim_evidence_ids,
            selection_score=float(finding.get("score") or finding.get("value_score") or 0),
            lens=str(finding.get("lens") or "overview"),
            business_question=str(finding.get("business_question") or ""),
            question_id=_question_id_for_finding(report_model, finding),
            finding_ids=[str(item.get("insight_id") or "") for item in group],
            layout_id=layout_id,
            silhouette=silhouette,
        ))

    if actions:
        action_evidence = _unique([
            evidence_id for action in actions for evidence_id in action.get("evidence_ids", [])
            if evidence_id in evidence_index
        ])
        action = actions[0]
        story_role = "decision" if _requires_decision(actions, report_model) else "action"
        pages.append(_page(
            report_model,
            story_role=story_role,
            claim=_action_claim(action, evidence_index),
            purpose="收口为可执行行动与验证信号" if story_role == "action" else "明确需要管理层批准或配置的资源",
            evidence_ids=action_evidence,
            claim_evidence_ids=list(action.get("evidence_ids", [])),
            selection_score=float(action.get("score") or 0),
            lens=str(action.get("lens") or "overview"),
        ))

    if appendix:
        # An appendix finding remains business content.  Give each selected
        # finding its own capacity-safe page instead of shrinking an unbounded
        # list into one decorative text box.
        for item in appendix:
            pages.append(_page(
                report_model,
                story_role="appendix",
                claim=_claim(item, "补充证据"),
                purpose="承载已选择但不进入主决策链的补充证据",
                evidence_ids=_question_evidence_for_finding(report_model, item),
                claim_evidence_ids=[],
                selection_score=float(item.get("score") or 0),
                lens=str(item.get("lens") or ""),
                business_question=str(item.get("business_question") or "") or None,
                question_id=_question_id_for_finding(report_model, item) or None,
                finding_ids=[str(item.get("insight_id") or "")],
            ))

    pending = unresolved_question_records(report_model, pages)
    if pending:
        report_model["narrative_selection"] = {
            "status": "partial_coverage", "selected_count": len(featured),
            "reason": "已入选章节的判断与行动保留；以下问题尚未形成核心判断，不能视为全部问题已回答。",
            "unresolved_questions": pending,
        }
        pages.append(_page(report_model, story_role="appendix", claim="尚未形成核心判断的问题",
            purpose=report_model["narrative_selection"]["reason"], evidence_ids=[], claim_evidence_ids=[],
            content_exemption="selection_meta", layout_id="action-roadmap", silhouette="roadmap"))
    elif report_model.get("narrative_selection", {}).get("status") == "partial_coverage":
        report_model.pop("narrative_selection")
    pages.sort(key=canonical_story_sort_key)
    return _add_projection_fields(report_model, pages)


def build_narrative_validation(
    pages: list[dict[str, Any]], report_model: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Persist a compact, consumer-neutral audit of the selected story."""

    main_pages = [page for page in pages if page.get("story_role") != "appendix"]
    question_coverage: dict[str, list[str]] = {}
    duplicate_claims: list[str] = []
    question_dispositions: list[dict[str, Any]] = []
    seen_claims: dict[tuple[str, frozenset[str]], str] = {}
    for page in pages:
        if page.get("story_role") in {"driver", "opportunity", "risk", "baseline"}:
            question = str(page.get("business_question") or "")
            if question:
                question_coverage.setdefault(question, []).append(str(page["slide_id"]))
        signature = claim_signature(str(page.get("claim") or ""), list(page.get("evidence_ids", [])))
        if signature in seen_claims:
            duplicate_claims.append(str(page["slide_id"]))
        else:
            seen_claims[signature] = str(page["slide_id"])
    selection = (report_model or {}).get("value_selection", {})
    if isinstance(selection, dict):
        for item in selection.get("appendix", []):
            question = str(item.get("business_question") or "").strip()
            evidence_ids = _question_evidence_for_finding(report_model or {}, item)
            target = next((
                page for page in pages
                if page.get("story_role") == "appendix"
                and set(evidence_ids) <= set(page.get("evidence_ids", []))
                and str(item.get("insight_id") or "") in set(page.get("finding_ids", []))
            ), None)
            if question and evidence_ids and target is not None:
                question_dispositions.append({
                    "kind": "appendix",
                    "reason": "价值选择将该问题的现有证据归入附录；是否达到回答深度另行记录。",
                    "evidence_ids": evidence_ids,
                    "target_slide_id": str(target["slide_id"]),
                    "content_refs": target.get("content_refs", {}),
                    "business_question": question,
                    "question_id": _question_id_for_finding(report_model or {}, item),
                    "finding_ids": [str(item.get("insight_id") or "")],
                })
        meta_page = next((page for page in pages if page.get("content_exemption") == "selection_meta"), None)
        if meta_page is not None:
            pending_by_id = {item["question_id"]: item for item in unresolved_question_records(report_model or {}, pages)}
            dropped_by_question: dict[str, list[dict[str, Any]]] = {}
            for item in selection.get("dropped", []):
                if isinstance(item, dict):
                    dropped_by_question.setdefault(str(item.get("business_question") or "").strip(), []).append(item)
            for question in (report_model or {}).get("analysis_lenses", []):
                pending = pending_by_id.get(str(question.get("question_id") or ""))
                if (report_model or {}).get("narrative_selection", {}).get("status") == "partial_coverage" and pending is None:
                    continue
                business_question = str(question.get("business_question") or "").strip()
                evidence_ids = [str(value) for value in question.get("evidence_ids", [])]
                if not business_question or not evidence_ids:
                    continue
                records = dropped_by_question.get(business_question, [])
                question_dispositions.append({
                    "kind": "not_selected", "reason": pending["reason"] if pending else "问题已有证据，但没有发现达到决策展示阈值。",
                    "evidence_ids": evidence_ids, "target_slide_id": str(meta_page["slide_id"]),
                    "content_refs": meta_page.get("content_refs", {}), "business_question": business_question,
                    "question_id": str(question.get("question_id") or ""), "finding_ids": [],
                    "drop_reasons": [reason for record in records for reason in record.get("drop_reasons", [])],
                    "value_scores": [record.get("score") for record in records],
                    "evidence_status": str(question.get("answer_status") or ""),
                })
    question_coverage = {
        question: _unique(slide_ids)
        for question, slide_ids in question_coverage.items()
    }
    return {
        "story_order_valid": story_topology_is_valid(pages),
        "main_page_count": len(main_pages),
        "appendix_page_count": len(pages) - len(main_pages),
        "last_main_story_role": main_pages[-1].get("story_role") if main_pages else None,
        "question_coverage": question_coverage,
        "question_dispositions": question_dispositions,
        "selection_status": (report_model or {}).get("narrative_selection", {}).get("status"),
        "duplicate_claims": duplicate_claims,
        "page_reasons": {str(page["slide_id"]): str(page["page_reason"]) for page in pages},
    }
