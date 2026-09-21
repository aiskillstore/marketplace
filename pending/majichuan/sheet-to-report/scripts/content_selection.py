"""Deterministically rank evidence-backed findings by business value."""
from __future__ import annotations

from typing import Any


VALUE_DIMENSIONS = (
    "impact",
    "abnormality",
    "actionability",
    "credibility",
    "urgency",
    "uniqueness",
)
HARD_GATES = (
    "evidence_valid",
    "business_question",
    "information_gain",
    "decision_impact",
)
RESOLUTION_STATUSES = {"direct_conclusion", "limited_with_next_step", "deferred_to_user"}


def _is_present(value: Any) -> bool:
    return bool(value.strip()) if isinstance(value, str) else bool(value)


def _hard_gate_reasons(finding: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if not str(finding.get("insight_id") or "").strip():
        reasons.append("insight_id_missing")
    if finding.get("evidence_valid") is not True:
        reasons.append("evidence_invalid")
    if str(finding.get("evidence_strength") or "").lower() == "low":
        reasons.append("evidence_strength_low")
    if str(finding.get("claim_type") or finding.get("kind") or "fact").lower() == "hypothesis" and len(finding.get("evidence_ids") or []) < 2:
        reasons.append("hypothesis_without_cross_evidence")
    if not _is_present(finding.get("business_question")):
        reasons.append("business_question_missing")
    if not _is_present(finding.get("information_gain")):
        reasons.append("information_gain_missing")
    if not _is_present(finding.get("decision_impact")):
        reasons.append("decision_impact_missing")
    return reasons


def _dimension_scores(finding: dict[str, Any]) -> tuple[dict[str, int], list[str]]:
    scores: dict[str, int] = {}
    reasons: list[str] = []
    for dimension in VALUE_DIMENSIONS:
        value = finding.get(dimension, 0)
        if isinstance(value, bool) or not isinstance(value, int) or value not in {0, 1, 2}:
            reasons.append(f"invalid_{dimension}")
            scores[dimension] = 0
        else:
            scores[dimension] = value
    return scores, reasons


def _classification(score: int) -> str:
    if score >= 8:
        return "featured"
    if score >= 5:
        return "appendix"
    return "dropped"


def is_supporting_finding(finding: dict[str, Any]) -> bool:
    """Return whether an item is explicitly supporting, not a main-story finding."""

    role = str(finding.get("presentation_role") or "").strip().lower()
    display_priority = str(finding.get("display_priority") or "").strip().lower()
    return role == "supporting" or (not role and display_priority == "supporting")


def evidence_safe_classification(
    finding: dict[str, Any], classification: str
) -> tuple[str, str | None]:
    if classification != "featured":
        return classification, None
    if str(finding.get("claim_type") or finding.get("kind") or "fact").lower() == "hypothesis":
        return "appendix", "hypothesis_max_appendix"
    if is_supporting_finding(finding):
        return "appendix", "supporting_max_appendix"
    return classification, None


def build_analysis_chapters(prepared: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group findings by decision question and select whole business chapters."""

    featured_signals_by_question: dict[str, set[str]] = {}
    for item in prepared:
        question_id = str(item.get("question_id") or item.get("insight_id") or "").strip()
        signal_type = str(item.get("signal_type") or "").strip().lower()
        if (
            question_id and signal_type
            and item.get("classification") == "featured"
            and not is_supporting_finding(item)
        ):
            featured_signals_by_question.setdefault(question_id, set()).add(signal_type)

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    order: list[tuple[str, str]] = []
    for item in prepared:
        question_id = str(item.get("question_id") or item.get("insight_id") or "").strip()
        if not question_id:
            continue
        signal_type = str(item.get("signal_type") or "").strip().lower()
        split_signal = signal_type if len(featured_signals_by_question.get(question_id, set())) > 1 else ""
        group_key = (question_id, split_signal)
        if group_key not in grouped:
            grouped[group_key] = []
            order.append(group_key)
        grouped[group_key].append(item)

    chapters: list[dict[str, Any]] = []
    selected_signatures: set[str] = set()
    for question_id, chapter_signal in order:
        items = grouped[(question_id, chapter_signal)]
        ranked = sorted(
            items,
            key=lambda item: (-int(item.get("score") or 0), int(item.get("source_index") or 0), str(item.get("insight_id") or "")),
        )
        representative = ranked[0]
        visible = [item for item in ranked if item.get("classification") != "dropped"]
        featured = [
            item for item in visible
            if item.get("classification") == "featured" and not is_supporting_finding(item)
        ]
        required_values = [
            item.get("required_depth") for item in visible
            if isinstance(item.get("required_depth"), int) and not isinstance(item.get("required_depth"), bool)
        ]
        required_depth = max(required_values, default=0)
        qualified_judgements = [item for item in featured if isinstance(item.get("achieved_depth"), int)
                                and item["achieved_depth"] >= max(4, required_depth) and item.get("answer_status") == "answered"]
        if qualified_judgements:
            representative = qualified_judgements[0]
        achieved_depth = int(representative.get("achieved_depth") or 0)
        depth_met = achieved_depth >= max(4, required_depth)
        signatures = {
            str(item.get("duplicate_signature") or "").strip()
            for item in featured if str(item.get("duplicate_signature") or "").strip()
        }
        adds_information = bool(featured) and not (signatures and signatures <= selected_signatures)
        selection_status = (
            "selected" if featured and depth_met and adds_information
            else "appendix" if visible else "dropped"
        )
        if selection_status == "selected":
            selected_signatures.update(signatures)
        evidence_ids = list(dict.fromkeys(
            str(value)
            for item in visible
            for value in item.get("evidence_ids", [])
            if str(value)
        ))
        driver_evidence_ids = list(dict.fromkeys(
            str(value)
            for item in visible
            for value in item.get("driver_evidence_ids", [])
            if str(value)
        ))
        segment_evidence_ids = list(dict.fromkeys(
            str(value)
            for item in visible
            for value in item.get("segment_evidence_ids", [])
            if str(value)
        ))
        judgement = str(
            representative.get("statement")
            or representative.get("resolved_answer")
            or representative.get("answer_text")
            or representative.get("headline")
            or representative.get("business_question")
            or ""
        ).strip()
        limitations = list(dict.fromkeys(
            str(value)
            for item in visible
            for value in item.get("limitations", [])
            if str(value).strip()
        ))
        chapters.append({
            "chapter_id": f"chapter:{question_id}{':' + chapter_signal if chapter_signal else ''}",
            "question_id": question_id,
            "signal_type": chapter_signal or str(representative.get("signal_type") or ""),
            "decision_question": str(representative.get("business_question") or "").strip(),
            "judgement": judgement,
            "judgement_insight_id": str(representative.get("insight_id") or ""),
            "answer_status": str(representative.get("answer_status") or ("answered" if featured else "partial")),
            "required_depth": required_depth,
            "achieved_depth": achieved_depth,
            "fact_evidence_ids": evidence_ids,
            "driver_evidence_ids": driver_evidence_ids,
            "segment_evidence_ids": segment_evidence_ids,
            "operating_implication": str(representative.get("decision_impact") or "").strip(),
            "report_language": judgement,
            "action_ids": list(dict.fromkeys(
                str(value) for item in visible for value in item.get("action_ids", []) if str(value)
            )),
            "chart_ids": list(dict.fromkeys(
                str(value) for item in visible for value in item.get("chart_ids", []) if str(value)
            )),
            "limitations": limitations,
            "insight_ids": [str(item.get("insight_id") or "") for item in visible if item.get("insight_id")],
            "selection_status": selection_status,
            "selection_score": max((int(item.get("score") or 0) for item in visible), default=0),
            "selection_reason": (
                "章节达到证据、深度与独立决策价值门槛。"
                if selection_status == "selected"
                else "章节未达到正文深度或独立信息增量门槛。"
            ),
        })
    return sorted(
        chapters,
        key=lambda item: (
            {"selected": 0, "appendix": 1, "dropped": 2}.get(str(item.get("selection_status")), 3),
            -int(item.get("selection_score") or 0),
            str(item.get("chapter_id") or ""),
        ),
    )


def score_and_select_findings(findings: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply hard evidence gates, six value dimensions, and exact de-duplication."""
    prepared: list[dict[str, Any]] = []
    for index, raw in enumerate(findings):
        finding = dict(raw)
        dimension_scores, invalid_dimensions = _dimension_scores(finding)
        drop_reasons = [*_hard_gate_reasons(finding), *invalid_dimensions]
        score = sum(dimension_scores.values())
        classification = "dropped" if drop_reasons else _classification(score)
        classification, safety_reason = evidence_safe_classification(finding, classification)
        if classification == "dropped" and not drop_reasons:
            drop_reasons.append("score_below_appendix_threshold")
        selection_reasons = [] if drop_reasons else [
            "hard_gates_passed",
            f"score_{score}",
            f"classified_{classification}",
        ]
        if safety_reason:
            selection_reasons.append(safety_reason)
        prepared.append({
            **finding,
            "insight_id": str(finding.get("insight_id") or ""),
            "score": score,
            "dimension_scores": dimension_scores,
            "classification": classification,
            "selection_reasons": selection_reasons,
            "drop_reasons": drop_reasons,
            "duplicate_of": None,
            "source_index": index,
        })

    winners: dict[str, dict[str, Any]] = {}
    for item in sorted(prepared, key=lambda candidate: (-candidate["score"], candidate["source_index"], candidate["insight_id"])):
        if item["classification"] == "dropped":
            continue
        signature = str(item.get("duplicate_signature") or "").strip()
        if not signature:
            continue
        winner = winners.get(signature)
        if winner is None:
            winners[signature] = item
            continue
        item["classification"] = "dropped"
        item["selection_reasons"] = []
        item["drop_reasons"] = [*item["drop_reasons"], "exact_duplicate"]
        item["duplicate_of"] = winner["insight_id"]

    result: dict[str, Any] = {
        "selection_unit": "analysis_chapter",
        "analysis_chapters": build_analysis_chapters(prepared),
        "featured": [],
        "appendix": [],
        "dropped": [],
        "selection_policy": {
            "featured_min_score": 8,
            "appendix_min_score": 5,
            "hard_gates": list(HARD_GATES),
            "tie_break": "source_index_then_insight_id",
        },
    }
    for item in prepared:
        result[item["classification"]].append(item)
    for group in ("featured", "appendix", "dropped"):
        result[group].sort(key=lambda item: (-item["score"], item["source_index"], item["insight_id"]))
    return result
