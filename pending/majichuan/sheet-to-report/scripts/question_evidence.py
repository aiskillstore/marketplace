"""Attach existing calculated proof to a concrete, supported question contract."""
from __future__ import annotations

from analysis_engine import _year_over_year_label
from analysis_questions import QUESTION_TYPE_BY_LENS, normalize_question_contract


def _standard_metadata_overlay(raw):
    """Only an unconstrained canonical question can reuse its native lens proof.

    A caller's answer/depth/evidence fields never participate in this decision.
    New IDs, changed question types and explicit computation constraints retain
    the exact custom binding path below.
    """
    normalized = normalize_question_contract(raw)
    lens = normalized["lens"]
    if lens not in QUESTION_TYPE_BY_LENS or normalized["question_id"] != f"q_{lens}":
        return False
    if raw.get("question_type", QUESTION_TYPE_BY_LENS[lens]) != QUESTION_TYPE_BY_LENS[lens]:
        return False
    if any(raw.get(key) for key in (
        "comparison_scope", "dimensions", "required_metrics", "required_objects", "followup_paths",
        "filters", "quality_filter", "periods", "metric", "scope_id",
    )):
        return False
    defaults = normalize_question_contract({"lens": lens, "business_question": "标准问题"})
    return normalized["allowed_tools"] == defaults["allowed_tools"]


def bind_custom_question_evidence(*, questions, custom_questions, evidence_index, metric_contracts,
                                  scope_catalog, legacy_bindings):
    custom_by_id = {normalize_question_contract(raw)["question_id"]: raw for raw in custom_questions}
    scopes = {item["scope_id"]: item for item in scope_catalog}
    metrics = {str(c["name"]): c for c in metric_contracts}
    bound = dict(legacy_bindings)

    def in_requested_time(question, record):
        declared = question.get("comparison_scope")
        # Non-temporal paths already have a calculation/result-identity matcher
        # in the follow-up executor. A metric match alone does not answer e.g.
        # concentration or an efficiency trade-off.
        if declared is None:
            return False
        current_scope, seen, rules = record.get("scope_id"), set(), {}
        while current_scope in scopes and current_scope not in seen:
            seen.add(current_scope)
            scope = scopes[current_scope]
            if scope.get("rules", {}).get("stage") == "analysis_window":
                rules = scope["rules"]
                break
            current_scope = scope.get("parent_scope_id")
        window = rules.get("time_scope", {})
        labels = sorted(window.get("periods", []))
        if isinstance(declared, dict):
            # Calendar buckets are not raw date values, even when their labels
            # look alike. Exact source-field queries go through the executor.
            if declared["period_field"] != "__period" or not labels:
                return False
            pairs = [(set(declared["current"]), set(declared["baseline"]))]
        elif (len(labels) >= 2 and rules.get("incomplete_period_policy") in {"exclude", "exclude_and_note"}
              and window.get("period_type") in {"monthly", "weekly"}
              and window.get("field") in {*question.get("confirmed_fields", []), *question.get("required_fields", [])}):
            pairs = [({labels[-1]}, {labels[-2]})]
            if declared == "latest_complete_vs_previous_and_year_over_year":
                pairs.append(({labels[-1]}, {_year_over_year_label(labels[-1], window["period_type"], window["week_start"])}))
        else:
            return False
        # A full series is context for an explicit pair, not a structural
        # judgement. Depth continues to be calculated by analysis_depth.
        if record.get("kind") == "metric_trend":
            available = set(record.get("periods", []))
            return any(current | baseline <= available for current, baseline in pairs)
        if record.get("kind") == "dimension_contribution" and record.get("periods"):
            actual = scopes[record["scope_id"]].get("rules", {}).get("time_scope", {}).get("periods", [])
            return set(record["periods"]) == set(actual) and any(set(actual) == current for current, _ in pairs)
        if record.get("kind") in {"dimension_yoy", "dimension_slice_yoy"}:
            return any({record.get("latest_period")} == current and {record.get("comparison_period")} == baseline
                       for current, baseline in pairs)
        return False

    for question in questions:
        qid = question["question_id"]
        if qid not in custom_by_id:
            continue
        # An explicit empty binding prevents reconcile's legacy lens fallback.
        bound[qid] = []
        if (question.get("selection_status") != "selected"
                or question.get("supportability", {}).get("status") != "supported"):
            continue
        if _standard_metadata_overlay(custom_by_id[qid]):
            bound[qid] = list(dict.fromkeys(
                key for key in legacy_bindings.get(qid, legacy_bindings.get(question["lens"], []))
                if isinstance(evidence_index.get(key), dict)
                and evidence_index[key].get("scope_id") in scopes
            ))
            continue
        required = set(question.get("required_metrics", []))
        allowed_metrics = {name for name, contract in metrics.items()
                           if not required or "any_primary_metric" in required
                           or required & {name, str(contract.get("metric_id"))}}
        dimensions = set(question.get("dimensions", []))
        for key, record in evidence_index.items():
            if record.get("metric") not in allowed_metrics or record.get("scope_id") not in scopes:
                continue
            axes = set(record.get("dimensions") or [record.get("dimension")]) - {None, ""}
            axes.update(value for value in (record.get("primary_dimension"), record.get("secondary_dimension")) if value)
            if not axes <= dimensions or not in_requested_time(question, record):
                continue
            bound[qid].append(key)
    return bound
