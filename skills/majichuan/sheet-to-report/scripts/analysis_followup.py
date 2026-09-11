"""Bounded, declarative follow-up aggregation over an already loaded table."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any

import pandas as pd

from analysis_engine import execute_readonly_aggregation, required_source_fields, validate_metric_contract
from analysis_questions import infer_question_depth
from analysis_depth import aggregate_covers, assess_depth
from analysis_scope import ScopeRegistry
from analysis_periods import resolve_comparison_scopes

ALLOWED_TOOLS = {"period_comparison", "dimension_breakdown", "cross_breakdown", "concentration", "quality_impact"}
TRACE_FIELDS = {"round", "path_hash", "tool", "evidence_ids", "information_gain", "result_hash", "stop_reason"}
PATH_FIELDS = {"tool", "metric", "fields", "dimensions", "filters", "comparison_scope", "quality_filter"}
_ORDER_INSENSITIVE_PATH_FIELDS = {"fields", "dimensions", "filters", "values", "baseline", "current", "periods"}


@dataclass(frozen=True)
class FollowupBudget:
    max_rounds: int = 4
    max_total_paths: int = 12
    max_paths_per_question: int = 3

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} 必须是正整数")


def _canonicalize(value: Any, *, parent_key: str | None = None) -> Any:
    if isinstance(value, dict):
        return {str(key): _canonicalize(item, parent_key=str(key)) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        normalized = [_canonicalize(item, parent_key=parent_key) for item in value]
        if parent_key in _ORDER_INSENSITIVE_PATH_FIELDS:
            return sorted(normalized, key=lambda item: json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return normalized
    return value


def canonical_path_hash(path: dict) -> str:
    if not isinstance(path, dict):
        raise ValueError("followup path 必须是对象")
    unknown = set(path) - PATH_FIELDS
    if unknown:
        raise ValueError("unknown_path_field:" + ",".join(sorted(str(key) for key in unknown)))
    raw = json.dumps(_canonicalize(path), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _result_hash(result: dict[str, Any]) -> str:
    raw = json.dumps(_canonicalize(result), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _sanitize_trace(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, (list, tuple)):
        return []
    cleaned: list[dict[str, Any]] = []
    for entry in value:
        if not isinstance(entry, dict):
            continue
        if set(entry) - TRACE_FIELDS:
            continue
        if set(entry) != TRACE_FIELDS:
            continue
        if isinstance(entry["round"], bool) or not isinstance(entry["round"], int) or entry["round"] < 1:
            continue
        if not all(isinstance(entry[field], str) for field in ("path_hash", "tool", "result_hash", "stop_reason")):
            continue
        if entry["tool"] not in ALLOWED_TOOLS or not isinstance(entry["evidence_ids"], (list, tuple)) or not all(isinstance(item, str) for item in entry["evidence_ids"]):
            continue
        if not isinstance(entry["information_gain"], bool):
            continue
        cleaned.append({
            "round": entry["round"], "path_hash": entry["path_hash"], "tool": entry["tool"],
            "evidence_ids": list(entry["evidence_ids"]), "information_gain": entry["information_gain"],
            "result_hash": entry["result_hash"], "stop_reason": entry["stop_reason"],
        })
    return cleaned


def _contract_by_reference(metric_contracts: list[dict[str, Any]], reference: Any) -> dict[str, Any] | None:
    for contract in metric_contracts:
        if not isinstance(contract, dict):
            continue
        if str(reference) in {str(contract.get("name")), str(contract.get("metric_id"))}:
            return contract
    return None


def _structured_stop(questions: Any, reason: str) -> dict[str, Any]:
    items = questions if isinstance(questions, (list, tuple)) else []
    updated = []
    for index, raw in enumerate(items, start=1):
        question = dict(raw) if isinstance(raw, dict) else {"question_id": str(index)}
        question["followup_trace"] = _sanitize_trace(question.get("followup_trace"))
        question["stop_reason"] = reason
        updated.append(question)
    return {"questions": updated, "budget": {}, "executed_path_count": 0, "stop_reason": reason, "question_stop_reasons": {str(item.get("question_id") or index): reason for index, item in enumerate(updated, start=1)}, "evidence_index": {}}


def _question_confirmed_fields(question: dict[str, Any], contract: dict[str, Any]) -> set[str]:
    confirmed = set(str(value) for value in question.get("confirmed_fields", []))
    confirmed.update(str(value) for value in question.get("required_fields", []))
    confirmed.update(str(value) for value in question.get("dimensions", []))
    confirmed.update(required_source_fields(contract))
    return confirmed


def _predicate_fields(predicate: Any) -> tuple[set[str], str | None]:
    if not isinstance(predicate, dict):
        return set(), "invalid_filter"
    field = str(predicate.get("field") or "")
    if not field or str(predicate.get("operator") or "") not in {"eq", "in"}:
        return set(), "invalid_filter"
    return {field}, None


def _validate_path(*, question: dict[str, Any], path: dict[str, Any], frame: pd.DataFrame, metric_contracts: list[dict[str, Any]], comparison_scopes=None) -> tuple[dict[str, Any] | None, str | None]:
    if "approval_callback" in path:
        return None, "invalid_path"
    try:
        canonical_path_hash(path)
    except (TypeError, ValueError):
        return None, "invalid_path"
    tool = str(path.get("tool") or "")
    allowed = {
        *[str(value) for value in question.get("allowed_tools", [])],
        *[str(value) for value in question.get("allowed_followup_generators", [])],
    }
    if tool not in ALLOWED_TOOLS or tool not in allowed:
        return None, "unsupported_tool"
    contract = _contract_by_reference(metric_contracts, path.get("metric"))
    if contract is None:
        return None, "missing_required_field"
    required_metrics = {str(metric) for metric in question.get("required_metrics", [])}
    if required_metrics and "any_primary_metric" not in required_metrics and str(contract.get("name")) not in required_metrics and str(contract.get("metric_id")) not in required_metrics:
        return None, "missing_required_field"
    confirmed = _question_confirmed_fields(question, contract)
    if tool == "period_comparison" and isinstance(question.get("comparison_scope"), str) and comparison_scopes:
        # Only the resolver may authorize the engine-generated period axis.
        confirmed.add("__period")
    fields = {str(value) for value in path.get("fields", [])}
    dimensions = [str(value) for value in path.get("dimensions", [])]
    fields.update(dimensions)
    for predicate in list(path.get("filters", [])) + ([path["quality_filter"]] if "quality_filter" in path else []):
        predicate_fields, error = _predicate_fields(predicate)
        if error:
            return None, error
        fields.update(predicate_fields)
    scope = path.get("comparison_scope")
    if scope is not None:
        if not isinstance(scope, dict):
            return None, "invalid_comparison_scope"
        fields.add(str(scope.get("period_field") or ""))
    declared_scopes = comparison_scopes if comparison_scopes is not None else [question.get("comparison_scope")]
    if tool == "period_comparison" and (scope is None or not any(_canonicalize(scope) == _canonicalize(item) for item in declared_scopes)):
        return None, "invalid_comparison_scope"
    if tool == "quality_impact" and "quality_filter" not in path:
        return None, "invalid_quality_filter"
    if not fields.issubset(confirmed) or not fields.issubset(set(frame.columns)):
        return None, "missing_required_field"
    return contract, None


def _trace_entry(*, round_number: int, path_hash: str, tool: str, evidence_ids: list[str], information_gain: int, result_hash: str, stop_reason: str | None) -> dict[str, Any]:
    return {"round": round_number, "path_hash": path_hash, "tool": tool, "evidence_ids": evidence_ids, "information_gain": information_gain, "result_hash": result_hash, "stop_reason": stop_reason}


def generate_followup_paths(
    question: dict[str, Any],
    metric_contracts: list[dict[str, Any]],
    *, comparison_scopes=None,
) -> list[dict[str, Any]]:
    """Generate only whitelist paths backed by confirmed question fields."""

    allowed = list(dict.fromkeys([
        *[str(value) for value in question.get("allowed_followup_generators", [])],
        *[str(value) for value in question.get("allowed_tools", [])],
    ]))
    required_metrics = [
        str(value) for value in question.get("required_metrics", [])
        if str(value) != "any_primary_metric"
    ]
    if not required_metrics:
        required_metrics = [
            str(item.get("name") or item.get("metric_id"))
            for item in metric_contracts if isinstance(item, dict) and (item.get("name") or item.get("metric_id"))
        ][:1]
    dimensions = [str(value) for value in question.get("dimensions", [])]
    paths: list[dict[str, Any]] = []
    for metric in required_metrics:
        for tool in allowed:
            path: dict[str, Any] | None = None
            if tool == "period_comparison":
                scopes = comparison_scopes if comparison_scopes is not None else (
                    [question["comparison_scope"]] if isinstance(question.get("comparison_scope"), dict) else [])
                for scope in scopes:
                    comparison_path = {"tool": tool, "metric": metric, "comparison_scope": scope}
                    if comparison_path not in paths:
                        paths.append(comparison_path)
            elif tool == "dimension_breakdown" and dimensions:
                path = {"tool": tool, "metric": metric, "dimensions": dimensions[:1], "filters": []}
            elif tool == "cross_breakdown" and len(dimensions) >= 2:
                path = {"tool": tool, "metric": metric, "dimensions": dimensions[:2], "filters": []}
            elif tool == "concentration" and dimensions:
                path = {"tool": tool, "metric": metric, "dimensions": dimensions[:1], "filters": []}
            elif tool == "quality_impact" and isinstance(question.get("quality_filter"), dict):
                path = {"tool": tool, "metric": metric, "quality_filter": question["quality_filter"]}
            if path is not None and path not in paths:
                paths.append(path)
    return paths


def _has_decision_information_gain(tool: str, result: dict[str, Any]) -> bool:
    """Reject non-empty aggregates that do not add a decision-relevant distinction."""

    if tool == "period_comparison":
        return isinstance(result.get("delta"), (int, float)) and float(result["delta"]) != 0.0
    if tool in {"dimension_breakdown", "cross_breakdown"}:
        groups = result.get("groups", [])
        values = [float(item["metric"]) for item in groups if isinstance(item, dict) and isinstance(item.get("metric"), (int, float))]
        return len(values) >= 2 and max(values) != min(values)
    if tool == "concentration":
        return int(result.get("group_count") or 0) >= 2 and isinstance(result.get("top_share"), (int, float))
    if tool == "quality_impact":
        share = result.get("affected_share")
        return isinstance(share, (int, float)) and 0.0 < float(share) < 1.0
    return False


def run_controlled_followups(frame: pd.DataFrame, questions: list[dict], metric_contracts: list[dict], budget: FollowupBudget | None = None, *, scope_registry=None, scope_parent_id: str = "source_rows", existing_evidence_index=None, insights=()) -> dict:
    """Execute a finite whitelist of aggregate-only paths and index new evidence."""
    if not isinstance(budget, (FollowupBudget, type(None))):
        return _structured_stop(questions, "invalid_budget")
    if not isinstance(frame, pd.DataFrame) or not isinstance(questions, (list, tuple)) or not isinstance(metric_contracts, (list, tuple)):
        return _structured_stop(questions, "invalid_input")
    try:
        for contract in metric_contracts:
            validate_metric_contract(contract)
    except (TypeError, ValueError):
        return _structured_stop(questions, "invalid_metric_contract")
    active_budget = budget or FollowupBudget()
    initial_evidence = dict(existing_evidence_index or {})
    if scope_registry is None and not frame.index.is_unique:
        frame = frame.reset_index(drop=True)
    calculation_registry = scope_registry or ScopeRegistry(frame)
    executed_hashes: set[str] = set()
    known_result_hashes: set[str] = {_result_hash(item["result"]) for item in initial_evidence.values() if isinstance(item.get("result"), dict)}
    total_paths = 0
    updated_questions: list[dict[str, Any]] = []
    evidence_index: dict[str, dict[str, Any]] = {}
    global_stop_reason = "all_questions_stopped"
    for raw_question in questions:
        question = dict(raw_question) if isinstance(raw_question, dict) else {"question_id": "invalid"}
        trace = _sanitize_trace(question.get("followup_trace"))
        question["followup_trace"] = trace
        known_result_hashes.update(str(item["result_hash"]) for item in trace if isinstance(item.get("result_hash"), str))
        existing_evidence = list(dict.fromkeys(str(item) for item in question.get("evidence_ids", []) if isinstance(item, str) and item))
        question["evidence_ids"] = existing_evidence
        depth_aware = "required_depth" in question or "achieved_depth" in question
        raw_required_depth = question.get("required_depth", 1)
        if depth_aware and (
            isinstance(raw_required_depth, bool)
            or not isinstance(raw_required_depth, int)
            or not 0 <= raw_required_depth <= 5
        ):
            question["stop_reason"] = "invalid_required_depth"
            updated_questions.append(question)
            continue
        required_depth = int(raw_required_depth)
        achieved_depth = infer_question_depth(
            question,
            evidence_ids=existing_evidence,
            followup_tools=[str(item.get("tool")) for item in trace],
            evidence_index={**initial_evidence, **evidence_index}, insights=insights, scope_catalog=calculation_registry.export(),
        ) if depth_aware else 0
        if depth_aware:
            question["achieved_depth"] = achieved_depth
            if achieved_depth < required_depth:
                question["answer_status"] = "followup_needed"
            question["depth_gaps"] = assess_depth(question, evidence_index={**initial_evidence, **evidence_index},
                insights=insights, scope_catalog=calculation_registry.export())["depth_gaps"]
        try:
            raw_minimum = question.get("minimum_evidence", 1)
            minimum = int(raw_minimum)
            if minimum < 1 or isinstance(raw_minimum, bool):
                raise ValueError
        except (TypeError, ValueError):
            question["stop_reason"] = "invalid_minimum_evidence"
            updated_questions.append(question)
            continue
        if (not {str(value) for value in question.get("required_fields", [])}.issubset(set(frame.columns))
                or question.get("selection_status") == "rejected"
                or question.get("status") in {"rejected", "unavailable", "skipped"}):
            question["stop_reason"] = "missing_required_field"
            question["answer_status"] = "unanswerable"
            updated_questions.append(question)
            continue
        try:
            comparison_scopes = resolve_comparison_scopes(question, frame, calculation_registry, scope_parent_id)
        except (KeyError, TypeError, ValueError) as error:
            reason = str(error)
            question["stop_reason"] = reason if reason in {"invalid_comparison_scope", "missing_scope_data", "missing_required_field"} else "invalid_comparison_scope"
            updated_questions.append(question)
            continue
        if len(existing_evidence) >= minimum and (not depth_aware or achieved_depth >= required_depth):
            question["stop_reason"] = "required_depth_met" if depth_aware else "evidence_sufficient"
            updated_questions.append(question)
            continue
        paths = question.get("followup_paths", [])
        if depth_aware and (not isinstance(paths, (list, tuple)) or not paths):
            paths = generate_followup_paths(question, list(metric_contracts), comparison_scopes=comparison_scopes)
        if not isinstance(paths, (list, tuple)) or not paths:
            question["stop_reason"] = "missing_required_field" if depth_aware else "no_followup_path"
            updated_questions.append(question)
            continue
        for index, path in enumerate(paths, start=1):
            if total_paths >= active_budget.max_total_paths or index > active_budget.max_rounds or index > active_budget.max_paths_per_question:
                question["stop_reason"] = "budget_exhausted"
                global_stop_reason = "budget_exhausted"
                break
            if not isinstance(path, dict):
                question["stop_reason"] = "invalid_path"
                break
            try:
                path_hash = canonical_path_hash(path)
                if scope_registry is not None:
                    from canonical_json import canonical_sha256
                    path_hash = canonical_sha256({"path": path_hash, "scope_id": scope_parent_id})
            except (TypeError, ValueError):
                question["stop_reason"] = "invalid_path"
                break
            if path_hash in executed_hashes:
                question["stop_reason"] = "no_new_information" if trace else "duplicate_path"
                break
            try:
                contract, path_error = _validate_path(question=question, path=path, frame=frame, metric_contracts=list(metric_contracts), comparison_scopes=comparison_scopes)
            except (KeyError, TypeError, ValueError):
                contract, path_error = None, "invalid_path"
            if path_error:
                question["stop_reason"] = path_error
                break
            total_paths += 1
            executed_hashes.add(path_hash)
            try:
                result = execute_readonly_aggregation(frame, contract, tool=str(path["tool"]), dimensions=list(path.get("dimensions", [])), filters=list(path.get("filters", [])), comparison_scope=path.get("comparison_scope"), quality_filter=path.get("quality_filter"), scope_registry=calculation_registry, scope_parent_id=scope_parent_id)
            except (KeyError, TypeError, ValueError) as error:
                reason = str(error)
                question["stop_reason"] = reason if reason in {"missing_scope_data", "evidence_insufficient", "invalid_quality_filter", "invalid_comparison_scope", "unsupported_metric_for_tool"} else "insufficient_evidence"
                break
            result_hash = _result_hash(result)
            evidence_id = "followup:" + path_hash[:16]
            dimensions = list(path.get("dimensions", []))
            candidate = {"evidence_id": evidence_id, "kind": str(path["tool"]), "tool": str(path["tool"]),
                         "metric": str(contract.get("name")), "dimension": dimensions[0] if len(dimensions) == 1 else "", "dimensions": dimensions,
                         "calculation": str(contract.get("formula") or contract.get("aggregation")), "result": result, "result_hash": result_hash,
                         **{key: result[key] for key in ("scope_id", "scope_bindings", "sample_count")}}
            catalog = calculation_registry.export()
            known_records = {**initial_evidence, **evidence_index}
            matched_ids = [key for key, record in known_records.items()
                           if aggregate_covers(record, candidate, catalog)
                           or isinstance(record.get("result"), dict) and _result_hash(record["result"]) == result_hash]
            gain = bool(
                result_hash not in known_result_hashes
                and evidence_id not in existing_evidence
                and _has_decision_information_gain(str(path["tool"]), result)
                and not matched_ids
            )
            trace_evidence_ids = [evidence_id] if gain else []
            trace.append(_trace_entry(round_number=index, path_hash=path_hash, tool=str(path["tool"]), evidence_ids=trace_evidence_ids, information_gain=gain, result_hash=result_hash, stop_reason="" if gain else "no_new_information"))
            if not gain:
                # Reuse known proof without claiming a new analysis result.
                for known_id in matched_ids[:1]:
                    if known_id not in existing_evidence:
                        existing_evidence.append(known_id)
                if depth_aware:
                    assessment = assess_depth(question, evidence_index=known_records, insights=insights, scope_catalog=catalog)
                    achieved_depth = assessment["achieved_depth"]
                    question.update({key: assessment[key] for key in ("achieved_depth", "depth_gaps")})
                question["stop_reason"] = "no_new_information"
                continue
            known_result_hashes.add(result_hash)
            dimensions = list(path.get("dimensions", []))
            evidence_index[evidence_id] = candidate
            existing_evidence.append(evidence_id)
            if depth_aware:
                achieved_depth = infer_question_depth(
                    question,
                    evidence_ids=existing_evidence,
                    followup_tools=[
                        *[str(item.get("tool")) for item in trace],
                    ],
                    evidence_index={**initial_evidence, **evidence_index}, insights=insights, scope_catalog=calculation_registry.export(),
                )
                question["achieved_depth"] = achieved_depth
                question["depth_gaps"] = assess_depth(question, evidence_index={**initial_evidence, **evidence_index}, insights=insights, scope_catalog=calculation_registry.export())["depth_gaps"]
            if len(existing_evidence) >= minimum and (not depth_aware or achieved_depth >= required_depth):
                question["answer_status"] = "answered"
                question["status"] = "selected"
                question["missing_requirements"] = [item for item in question.get("missing_requirements", []) if item not in {"minimum_evidence", "required_depth"}]
                question["stop_reason"] = "required_depth_met" if depth_aware else "evidence_sufficient"
                if depth_aware:
                    break
            else:
                question["answer_status"] = "followup_needed" if depth_aware else "partial"
                if depth_aware and "required_depth" not in question.get("missing_requirements", []):
                    question["missing_requirements"] = [*question.get("missing_requirements", []), "required_depth"]
        else:
            if depth_aware:
                question["stop_reason"] = "required_depth_met" if achieved_depth >= required_depth and len(existing_evidence) >= minimum else "no_new_information"
            else:
                question["stop_reason"] = "evidence_sufficient" if len(existing_evidence) >= minimum else "no_new_information"
        updated_questions.append(question)
    return {"questions": updated_questions, "budget": asdict(active_budget), "executed_path_count": total_paths, "stop_reason": global_stop_reason, "question_stop_reasons": {str(question.get("question_id") or index): str(question.get("stop_reason")) for index, question in enumerate(updated_questions, start=1)}, "evidence_index": evidence_index}
