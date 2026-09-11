from __future__ import annotations

import argparse
import copy
import ctypes
import json
import math
import os
import re
import shutil
import sys
import tempfile
import time
from dataclasses import MISSING, asdict, dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pandas as pd

from analysis_engine import _aggregate_total, analyse_frame, enrich_question_graph_with_preliminary_scan, file_sha256, normalize_metric_contracts, period_labels, prepare_analysis_frame, required_source_fields, numeric_source_fields
from analysis_profiles import resolve_analysis_profile
from canonical_json import canonical_sha256
from analysis_followup import run_controlled_followups
from analysis_scope import ScopeRegistry, SCOPE_VERSION, record_evidence_ids, scope_lock_projection
from analysis_depth import assess_depth
from analysis_questions import build_analysis_brief, canonical_analysis_question_contract, canonical_available_objects, reconcile_questions_with_evidence
from build_pptx import build_pptx as build_pptx_v2
from content_qa import _validate_value_selection, validate_content_value
from content_selection import HARD_GATES, build_analysis_chapters, is_supporting_finding, score_and_select_findings
from content_resolver import project_legacy_content_refs
from evidence_catalog import (
    enrich_analysis_content,
    scope_content_to_lenses,
)
from html_renderer import render_html as render_html_v2
from html_qa import qa_html
from question_evidence import bind_custom_question_evidence
from decision_proposals import compile_decision_proposals, prepare_decision_context
from input_preflight import (
    PreflightNeedsInput,
    inspect_source,
    load_source_table,
    resolve_quick_payload,
)
from semantic_contract import resolve_request_semantic_contract, validate_analysis_questions
from transactional_commerce import prepare_transactional_commerce
from transactional_story import build_transactional_business_content, semantic_dimension_lenses
from layout_registry import LAYOUT_REGISTRY, display_units
from model_validation import validate_report_model, validate_story_topology, validate_scope_contract, validate_depth_evidence_contract
from report_model_projection import build_non_retail_projection, content_validation_lock_value, renderer_content_lock_projection
from narrative_planner import build_narrative_validation
from ppt_qa import qa_pptx
from slide_planner import build_slide_plan
from slideviber_handoff import render_slideviber_handoff as render_slideviber_handoff_v2
from story_topology import management_presentation_order


LOCKED_ADAPTIVE_KEYS = {
    "scope_contract",
    "analysis_lenses",
    "content_validation",
    "featured_insight_ids",
    "appendix_insight_ids",
    "non_retail_projection",
    "renderer_content",
}

LOCKED_SLIDE_KEYS = {
    "slide_id",
    "layout_id",
    "story_role",
    "evidence_ids",
    "chart_ids",
    "content_refs",
    "content_ref_bindings",
    "visual_spec",
}


@dataclass(frozen=True)
class ReportRequest:
    source_path: Path
    period_type: str
    audience: str
    objective: str
    date_column: str
    primary_metrics: tuple[str, ...]
    dimensions: tuple[str, ...] = ()
    output_mode: str = "report"
    mode: str = "quick"
    sheet_name: str | None = None
    metric_contracts: tuple[dict, ...] = ()
    comparisons: tuple[str, ...] = ("period_over_period", "year_over_year")
    week_start: str = "monday"
    timezone: str = "Asia/Shanghai"
    incomplete_period_policy: str = "exclude"
    theme: str = "clean"
    ppt_refinement: str = "offer_slideviber"
    analysis_profile: str = "auto"
    report_subject: str | None = None
    report_subtitle: str | None = None
    duplicate_policy: str = "keep"
    numeric_error_policy: str = "fail"
    allow_sensitive_fields: bool = False
    preflight: dict | None = None
    analysis_intent: str = "business_review"
    semantic_contract: dict | None = None
    analysis_questions: tuple[dict, ...] = ()


_ROOT_REQUEST_EXTENSION_FIELDS = frozenset({"source_path", "metric_contracts"})
_SEED_REQUEST_FIELD_ALIASES = {"preflight": "input_resolution"}
_SEED_REQUEST_LIST_FIELDS = frozenset(
    {"primary_metrics", "dimensions", "comparisons", "analysis_questions"}
)
_REPORT_REQUEST_SCHEMA = {field.name: field for field in fields(ReportRequest)}


def _request_schema_value(request: object, name: str) -> object:
    """Read a request-like value or its authoritative ReportRequest default."""

    if hasattr(request, name):
        return getattr(request, name)
    field = _REPORT_REQUEST_SCHEMA[name]
    if field.default is not MISSING:
        return copy.deepcopy(field.default)
    if field.default_factory is not MISSING:
        return field.default_factory()
    raise ValueError(f"request 缺少必填字段：{name}")


def _canonical_seed_request_contract(
    request: ReportRequest,
    *,
    resolved_sheet_name: str | None,
    resolved_semantic_contract: dict | None,
) -> dict:
    """Project every report-affecting request field into the finalized model."""

    resolved_values = {
        "sheet_name": resolved_sheet_name,
        "semantic_contract": resolved_semantic_contract,
        "analysis_intent": str(
            _request_schema_value(request, "analysis_intent") or "business_review"
        ),
    }
    payload: dict = {}
    for field in _REPORT_REQUEST_SCHEMA.values():
        name = field.name
        if name in _ROOT_REQUEST_EXTENSION_FIELDS:
            continue
        value = (
            resolved_values[name]
            if name in resolved_values
            else _request_schema_value(request, name)
        )
        if name == "analysis_questions":
            value = validate_analysis_questions(value)
        if name in _SEED_REQUEST_LIST_FIELDS:
            value = list(value)
        payload[_SEED_REQUEST_FIELD_ALIASES.get(name, name)] = copy.deepcopy(value)
    return payload


def _canonical_analysis_request_contract(
    request: ReportRequest,
    *,
    resolved_source_path: str | Path,
    resolved_sheet_name: str | None,
    resolved_semantic_contract: dict | None,
) -> dict:
    """Extend the shared seed contract with analysis-stage-only root inputs."""

    return {
        **_canonical_seed_request_contract(
            request,
            resolved_sheet_name=resolved_sheet_name,
            resolved_semantic_contract=resolved_semantic_contract,
        ),
        "source_path": str(Path(resolved_source_path).resolve()),
        "metric_contracts": [
            copy.deepcopy(contract)
            for contract in _request_schema_value(request, "metric_contracts")
        ],
    }


@dataclass(frozen=True)
class TableProfile:
    row_count: int
    column_count: int
    columns: tuple[str, ...]
    missing_by_column: dict[str, int]
    duplicate_rows: int
    date_min: str
    date_max: str
    sensitive_columns: tuple[str, ...]
    sheet_name: str | None
    source_encoding: str | None
    date_parse_rate: float
    date_invalid_count: int
    numeric_quality: dict[str, dict]
    ratio_denominator_zero: dict[str, int]
    high_cardinality_dimensions: dict[str, int]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class PipelineArtifacts:
    model_path: Path
    html_path: Path
    html_qa_path: Path | None
    manifest_path: Path
    pptx_path: Path | None = None
    pptx_qa_path: Path | None = None
    slideviber_handoff_path: Path | None = None


@dataclass(frozen=True)
class AnalysisArtifacts:
    """Deterministic output of the analysis stage, before any report rendering."""

    evidence_path: Path
    manifest_path: Path


class InsufficientEvidenceError(ValueError):
    """A business report cannot invent answers when no question is evidenced."""

    def __init__(self, intent: str, unanswered_questions: list[str] | None = None) -> None:
        self.result = {
            "status": "needs_input",
            "reason": "insufficient_evidence",
            "analysis_intent": intent,
            "unanswered_questions": list(unanswered_questions or []),
            "questions": [
                "当前没有已回答或部分回答且具备证据的业务问题；请补充可验证的分析维度、周期或口径。"
            ],
        }
        super().__init__(self.result["questions"][0])


class StructuredPipelineError(ValueError):
    """A pipeline failure with a stable caller-facing error contract."""

    def __init__(self, error_code: str, message: str, *, details: dict | None = None) -> None:
        self.error_code = error_code
        self.details = dict(details or {})
        super().__init__(message)


USER_INTERACTION_CHOICES = ("直接分析", "确认分析计划")


def user_interaction_choices() -> list[str]:
    """Return the only user-facing choices; orchestration modes stay internal."""
    return list(USER_INTERACTION_CHOICES)


def _user_observable_payload(payload: dict) -> dict:
    """Expose stable actions while keeping orchestration mode names internal."""
    # Payload values include file paths, business content, and real failures.
    # They are machine-observable facts, not mode-label presentation copy.
    visible = copy.deepcopy(payload)
    visible["user_actions"] = user_interaction_choices()
    return visible


def _followup_groups(evidence: dict) -> dict[str, float]:
    if isinstance(evidence, dict) and evidence.get("kind") == "dimension_contribution":
        rows = evidence.get("rows", [])
        if any(row.get("is_other") for row in rows):
            return {}  # A truncated ranking cannot prove an all-object claim.
        return {str(row["value"]): float(row["metric"]) for row in rows
                if row.get("value") is not None and type(row.get("metric")) in (int, float)}
    result = evidence.get("result") if isinstance(evidence, dict) else {}
    groups = result.get("groups") if isinstance(result, dict) else []
    return {
        str(group["dimensions"][0]): float(group["metric"])
        for group in groups
        if isinstance(group, dict)
        and isinstance(group.get("dimensions"), list)
        and group["dimensions"]
        and isinstance(group.get("metric"), (int, float))
    }


def _non_retail_followup_content(
    questions: list[dict], evidence_index: dict[str, dict], analysis_contract: dict | None = None,
    *, allow_unanswered_candidates: bool = False,
) -> tuple[list[dict], list[dict]]:
    """Turn executed non-retail aggregate paths into evidence-linked decisions."""

    semantic_contract = (analysis_contract or {}).get("semantic_contract", {})
    if not (
        (analysis_contract or {}).get("adapter_id") in {"content_operations", "project_operations"}
        and (analysis_contract or {}).get("adapter_maturity") == "experimental"
        and isinstance(semantic_contract, dict)
        and semantic_contract.get("adapter_selection_reason") == "confirmed_experimental"
        and semantic_contract.get("confirmation_status") == "confirmed"
    ):
        return [], []

    questions_by_lens = {str(item.get("lens")): item for item in questions}

    def evidence_for(lens: str, metric: str) -> tuple[str, dict] | None:
        question = questions_by_lens.get(lens, {})
        if question.get("status") in {"skipped", "unavailable"}:
            return None
        if not allow_unanswered_candidates and (question.get("status") != "selected" or question.get("answer_status") != "answered"):
            return None
        if allow_unanswered_candidates and question.get("selection_status") != "selected":
            return None
        for evidence_id in question.get("evidence_ids", []):
            evidence = evidence_index.get(str(evidence_id), {})
            if (str(evidence.get("metric")) == metric and _followup_groups(evidence)
                    and evidence.get("dimension") in question.get("dimensions", [])):
                return str(evidence_id), evidence
        return None

    insights: list[dict] = []
    actions: list[dict] = []
    content_rate = evidence_for("content_efficiency", "conversion_rate")
    content_cost = evidence_for("content_efficiency", "cost")
    if content_rate and content_cost:
        rate_id, rate_evidence = content_rate
        cost_id, cost_evidence = content_cost
        rate_by_channel = _followup_groups(rate_evidence)
        cost_by_channel = _followup_groups(cost_evidence)
        if rate_by_channel and cost_by_channel:
            best_channel = max(rate_by_channel, key=rate_by_channel.get)
            rate = rate_by_channel[best_channel]
            spend = cost_by_channel.get(best_channel, 0.0)
            spend_rank = sorted(cost_by_channel, key=lambda key: (-cost_by_channel[key], key)).index(best_channel) + 1
            claim_binding = {
                "lens": "content_efficiency",
                "claims": [
                    {"evidence_id": rate_id, "dimension": "channel", "subject_value": best_channel, "metric": "conversion_rate", "actual_value": rate, "relation": "max"},
                    {"evidence_id": cost_id, "dimension": "channel", "subject_value": best_channel, "metric": "cost", "actual_value": spend, "relation": "rank_desc", "rank": spend_rank},
                ],
            }
            insight_id = "insight-content-efficiency"
            statement = f"{best_channel} channel：conversion_rate {rate:.2f}% 最高；cost {spend:.2f} 第{spend_rank}高，效率投入有取舍。"
            insights.append({
                "insight_id": insight_id,
                "lens": "content_efficiency",
                "kind": "diagnostic",
                "headline": statement,
                "statement": statement,
                "resolved_answer": f"{best_channel} 的 conversion_rate 最高，且已与渠道投入交叉核验。",
                "business_question": "各内容渠道的转化效率与投入是否存在可验证的取舍？",
                "decision_impact": "支持下一周期内容资源分配。",
                "signal_type": "opportunity",
                "actionable": True,
                "evidence_ids": [rate_id, cost_id],
                "claim_binding": claim_binding,
            })
            actions.append({
                "action_id": "action-content-efficiency",
                "lens": "content_efficiency",
                "headline": f"优先验证 {best_channel} channel 的效率—投入取舍",
                "text": f"优先验证 {best_channel} channel：conversion_rate {rate:.2f}% 为最高，cost {spend:.2f} 在 {len(cost_by_channel)} 个渠道中第{spend_rank}高。",
                "target": f"{best_channel} channel（conversion_rate {rate:.2f}%，cost {spend:.2f}）",
                "basis": statement,
                "rationale": "待验证假设：在可比内容组合内小范围增配资源，能增加转化且不损伤转化效率或单位转化成本；当前排序不证明增配的因果效果。",
                "evidence_ids": [rate_id, cost_id],
                "source_insight_ids": [insight_id],
                "verification_signal": f"下一完整周期在可比内容组合内，{best_channel} channel 的 conversion_rate 不低于基期 {rate:.2f}%，转化量增加且单位转化成本不高于试验前；不能只比较渠道排名。",
                "action_type": "controlled_test",
                "steps": [
                    f"在 {best_channel} channel 选择可比内容组合，记录试验前转化量、转化率和单位转化成本。",
                    "仅对小范围内容增配制作资源，保留可比未调整内容，在下一完整周期复核。",
                ],
                "guardrails": ["转化率低于基期或单位转化成本上升则暂停扩展；内容组合不可比时不作效果归因。"],
                "limitations": ["渠道效率排序不证明资源增配会带来增量；总投入不能代替单位效率。"],
                "claim_binding": claim_binding,
            })

    project_metrics = {
        metric: evidence_for("delivery_efficiency", metric)
        for metric in ("delay_days", "cost_overrun", "quality_score")
    }
    if all(project_metrics.values()):
        delay_id, delay_evidence = project_metrics["delay_days"]
        overrun_id, overrun_evidence = project_metrics["cost_overrun"]
        quality_id, quality_evidence = project_metrics["quality_score"]
        delay_by_team = _followup_groups(delay_evidence)
        overrun_by_team = _followup_groups(overrun_evidence)
        quality_by_team = _followup_groups(quality_evidence)
        if delay_by_team and overrun_by_team and quality_by_team:
            delay_team = max(delay_by_team, key=delay_by_team.get)
            overrun_team = max(overrun_by_team, key=overrun_by_team.get)
            quality_team = min(quality_by_team, key=quality_by_team.get)
            insight_id = "insight-delivery-efficiency"
            evidence_ids = [delay_id, overrun_id, quality_id]
            claim_binding = {
                "lens": "delivery_efficiency",
                "claims": [
                    {"evidence_id": delay_id, "dimension": "team", "subject_value": delay_team, "metric": "delay_days", "display_metric": "延期", "actual_value": delay_by_team[delay_team], "display_precision": 1, "relation": "max"},
                    {"evidence_id": overrun_id, "dimension": "team", "subject_value": overrun_team, "metric": "cost_overrun", "display_metric": "超支", "actual_value": overrun_by_team[overrun_team], "display_precision": 1, "relation": "max"},
                    {"evidence_id": quality_id, "dimension": "team", "subject_value": quality_team, "metric": "quality_score", "display_metric": "质量", "actual_value": quality_by_team[quality_team], "display_precision": 1, "relation": "min"},
                ],
            }
            if len({delay_team, overrun_team, quality_team}) == 1:
                statement = f"{delay_team}：三项同差，延期 {delay_by_team[delay_team]:.1f}最高；超支 {overrun_by_team[overrun_team]:.1f}最高；质量 {quality_by_team[quality_team]:.1f}最低。"
            else:
                statement = f"不同队各最差：{delay_team} 延期 {delay_by_team[delay_team]:.1f}最高；{overrun_team} 超支 {overrun_by_team[overrun_team]:.1f}最高；{quality_team} 质量 {quality_by_team[quality_team]:.1f}最低。"
            insights.append({
                "insight_id": insight_id,
                "lens": "delivery_efficiency",
                "kind": "diagnostic",
                "headline": statement,
                "statement": statement,
                "resolved_answer": statement,
                "business_question": "各团队的延期、超支与质量是否存在可验证的交付取舍？",
                "decision_impact": "将有限的交付治理资源优先放到延期与质量风险切面；超支总额仍需按可比任务规模复核，不能用于人员评价。",
                "limitations": ["团队聚合差异不证明执行机制或个人表现；超支总额受任务规模影响。"],
                "signal_type": "risk",
                "actionable": True,
                "evidence_ids": evidence_ids,
                "claim_binding": claim_binding,
            })
            actions.append({
                "action_id": "action-delivery-efficiency",
                "lens": "delivery_efficiency",
                "headline": "按团队最差项建立交付纠偏复核",
                "text": statement,
                "target": f"{delay_team}/{overrun_team}/{quality_team} team：delay_days {delay_by_team[delay_team]:.2f}、cost_overrun {overrun_by_team[overrun_team]:.2f}、quality_score {quality_by_team[quality_team]:.2f}",
                "basis": statement,
                "rationale": "待验证假设：排期校准与阶段检查能减少延期而不牺牲质量或抬高单任务超支；当前聚合差异不证明因果。",
                "evidence_ids": evidence_ids,
                "source_insight_ids": [insight_id],
                "verification_signal": "下一完整周期同阶段可比任务的平均延期低于试验前，平均质量不低于试验前，单任务超支不高于试验前；任务规模不同时不直接比较超支总额。",
                "action_type": "controlled_test",
                "steps": [
                    f"在 {delay_team}、{overrun_team}、{quality_team} 的相应风险切面，按阶段选择可比任务并记录试验前延期、质量及单任务超支。",
                    "小范围试点排期校准和阶段检查，保留同阶段可比任务作为对照，下一完整周期复核。",
                ],
                "guardrails": ["质量下降或单任务超支上升则暂停扩展；任务阶段不可比时不作效果归因。"],
                "limitations": ["仅验证交付流程，不据此评价人员；聚合差异不能证明纠偏措施的效果。"],
                "claim_binding": claim_binding,
            })
    return insights, actions


def _raise_semantic_contract_error(semantic_result: dict, request: ReportRequest) -> None:
    """Expose explicit semantic conflicts without collapsing them into pipeline_failed."""

    contract = semantic_result.get("contract")
    conflicts = contract.get("conflicts", []) if isinstance(contract, dict) else []
    prefix = (
        "transactional_commerce 语义合同需要确认："
        if getattr(request, "analysis_profile", "auto") == "transactional_commerce"
        else "semantic_contract 需要确认："
    )
    message = prefix + "；".join(semantic_result.get("questions", []))
    if conflicts:
        raise StructuredPipelineError(
            "semantic_ambiguity",
            message,
            details={"field": "semantic_contract.conflicts", "conflicts": list(conflicts)},
        )
    raise ValueError(message)


def _has_answered_or_partial_evidence(model: dict) -> bool:
    """Check all legal question answers, independently from page value selection."""

    evidence_index = set(model.get("evidence_index", {}))
    candidates = list(model.get("analysis_lenses", []))
    return any(
        str(item.get("answer_status") or "") in {"answered", "partial"}
        and bool(item.get("evidence_ids"))
        and all(evidence_id in evidence_index for evidence_id in item.get("evidence_ids", []))
        for item in candidates
    )


def validate_analysis_evidence_model(model: dict) -> None:
    """Validate analysis-stage evidence without requiring a narrative or slides."""

    validate_scope_contract(model)
    validate_depth_evidence_contract(model)
    source = model.get("source")
    request = model.get("request")
    evidence_index = model.get("evidence_index")
    lenses = model.get("analysis_lenses")
    selection = model.get("value_selection")
    if not isinstance(source, dict) or not str(source.get("sha256") or "").strip():
        raise ValueError("analysis_evidence source 指纹无效")
    if not isinstance(request, dict) or not str(request.get("objective") or "").strip():
        raise ValueError("analysis_evidence request 合同无效")
    if not isinstance(evidence_index, dict):
        raise ValueError("analysis_evidence evidence_index 必须是对象")
    if not isinstance(lenses, list):
        raise ValueError("analysis_evidence analysis_lenses 必须是列表")
    for question in lenses:
        if not isinstance(question, dict) or not all(
            str(question.get(field) or "").strip()
            for field in ("question_id", "lens", "business_question", "answer_status")
        ):
            raise ValueError("analysis_evidence 问题合同不完整")
        question_evidence = question.get("evidence_ids", [])
        if not isinstance(question_evidence, list) or not set(question_evidence) <= set(evidence_index):
            raise ValueError("analysis_evidence 问题引用了无效 evidence")
    selection_required = {"featured", "appendix", "dropped", "selection_policy"}
    selection_allowed = {*selection_required, "selection_unit", "analysis_chapters"}
    if (
        not isinstance(selection, dict)
        or not selection_required <= set(selection)
        or set(selection) - selection_allowed
    ):
        raise ValueError("analysis_evidence value_selection 无效")
    if "selection_unit" in selection and selection.get("selection_unit") != "analysis_chapter":
        raise ValueError("analysis_evidence value_selection 选择单位无效")
    if selection.get("analysis_chapters") != model.get("analysis_chapters"):
        raise ValueError("analysis_evidence analysis_chapters 镜像不一致")
    policy = selection.get("selection_policy")
    if not isinstance(policy, dict) or policy.get("hard_gates") != list(HARD_GATES):
        raise ValueError("analysis_evidence value_selection 策略无效")
    if _validate_value_selection(model):
        raise ValueError("analysis_evidence value_selection 未通过完整硬门槛校验")
    seen_ids: set[str] = set()
    for classification in ("featured", "appendix", "dropped"):
        records = selection.get(classification)
        if not isinstance(records, list):
            raise ValueError("analysis_evidence value_selection 分组无效")
        for record in records:
            if not isinstance(record, dict) or not str(record.get("insight_id") or "").strip():
                raise ValueError("analysis_evidence value_selection 记录无效")
            insight_id = str(record["insight_id"])
            if insight_id in seen_ids or str(record.get("classification") or "") != classification:
                raise ValueError("analysis_evidence value_selection 分类无效")
            seen_ids.add(insight_id)
            if not set(record.get("evidence_ids", [])) <= set(evidence_index):
                raise ValueError("analysis_evidence value_selection evidence 无效")


def validate_analysis_evidence_artifact(evidence: dict) -> None:
    """Validate immutable analysis artifact bindings before planning or finalizing."""

    if not isinstance(evidence, dict):
        raise ValueError("analysis_evidence 必须是对象")
    source_sha = str(evidence.get("source_sha256") or "")
    request = evidence.get("analysis_request")
    seed = evidence.get("finalize_seed")
    if not source_sha or not isinstance(request, dict) or not isinstance(seed, dict):
        raise ValueError("analysis_evidence 缺少 source、request 或 seed")
    if _request_fingerprint(request) != evidence.get("request_fingerprint"):
        raise ValueError("analysis_evidence request_fingerprint 无效")
    if _artifact_sha256(seed) != evidence.get("finalize_seed_sha256"):
        raise ValueError("analysis_evidence finalize_seed 无效")
    if seed.get("source", {}).get("sha256") != source_sha:
        raise ValueError("analysis_evidence source_sha256 绑定无效")
    _validate_root_request_binding(request, seed)
    validate_analysis_evidence_model(seed)
    for key in ("scope_contract_version", "scope_catalog", "quality_decisions"):
        if evidence.get(key) != seed.get(key):
            raise ValueError(f"analysis_evidence {key} 与 seed 不一致")
    projection = build_non_retail_projection(seed)
    report_seed = evidence.get("report_seed")
    if not isinstance(report_seed, dict) or report_seed != seed:
        raise ValueError("analysis_evidence report_seed 与 finalize_seed 不一致")
    if evidence.get("analysis_lenses") != seed.get("analysis_lenses"):
        raise ValueError("analysis_evidence analysis_lenses 与 finalize_seed 不一致")
    if evidence.get("value_selection") != seed.get("value_selection"):
        raise ValueError("analysis_evidence value_selection 与 finalize_seed 不一致")
    if evidence.get("evidence_catalog") != seed.get("evidence_index"):
        raise ValueError("analysis_evidence evidence_catalog 与 seed 不一致")
    if evidence.get("non_retail_projection") != projection:
        raise ValueError("analysis_evidence non_retail_projection 与 seed 不一致")
    if evidence.get("content_lock") != _build_content_lock(seed):
        raise ValueError("analysis_evidence content_lock 无效")


def _value_selection_candidates(
    insights: list[dict], *, evidence_index: dict[str, dict], questions_by_lens: dict[str, dict],
    objective: str, available_dimensions: set[str], scope_catalog=(), actions=(),
) -> list[dict]:
    """Attach deterministic business-value inputs without changing narrative claims."""
    candidates: list[dict] = []
    for raw in insights:
        item = dict(raw)
        # Prefer the immutable question identity.  A lens is not unique: two
        # decision questions can intentionally share it with different
        # priorities and answer metadata.
        question_id = str(item.get("question_id") or "").strip()
        lens_question = (
            questions_by_lens.get(question_id, {})
            if question_id else {}
        ) or questions_by_lens.get(str(item.get("lens") or ""), {})
        evidence_ids = [str(value) for value in item.get("evidence_ids", [])]
        evidence_valid = bool(evidence_ids) and all(value in evidence_index for value in evidence_ids)
        resolved_answer = str(
            item.get("resolved_answer")
            or item.get("answer_text")
            or lens_question.get("resolved_answer")
            or lens_question.get("answer_text")
            or ""
        ).strip()
        statement = str(item.get("statement") or "").strip()
        claim_type = str(item.get("claim_type") or item.get("kind") or "fact")
        strength = str(item.get("evidence_strength") or "")
        value_score = int(item.get("value_score") or 0)
        signal_type = str(item.get("signal_type") or "")
        # A story item can deliberately narrow a broad question answer (for
        # example an ID-only contribution).  Never overwrite that boundary
        # with the question's optimistic status.
        answer_status = str(item.get("answer_status") or lens_question.get("answer_status") or ("answered" if evidence_valid else "evidence_insufficient"))
        evidence_gaps = [str(value) for value in item.get("evidence_gaps", []) if str(value).strip()]
        if answer_status == "partial" and not evidence_gaps:
            evidence_gaps.append("business_object_display_field")
        if not evidence_valid:
            evidence_gaps.append("valid_evidence")
        if strength == "low":
            evidence_gaps.append("evidence_strength")
        if claim_type == "hypothesis" and len(evidence_ids) < 2:
            evidence_gaps.append("cross_evidence")
        if not resolved_answer:
            evidence_gaps.append("resolved_answer")
        evidence_gaps = list(dict.fromkeys(evidence_gaps))
        limitations = [
            str(value) for value in item.get("limitations", []) if str(value).strip()
        ]
        if evidence_gaps and not limitations:
            limitations.append("缺少可验证的结构化答案或必要证据。")
        if evidence_gaps and answer_status == "answered":
            answer_status = "evidence_insufficient"
        confirmed_dimensions = sorted(str(value) for value in available_dimensions)
        if answer_status == "answered" and not evidence_gaps:
            resolution_status = "direct_conclusion"
            next_step = ""
        elif answer_status == "partial" and not evidence_gaps:
            resolution_status = "limited_with_next_step"
            next_step = str(
                item.get("next_step")
                or lens_question.get("expected_information_gain")
                or "补充必要范围后再复核结论"
            ).strip()
        elif evidence_gaps:
            resolution_status = "limited_with_next_step"
            next_step = str(item.get("next_step") or lens_question.get("expected_information_gain") or "补充缺失证据后再复核结论").strip()
        else:
            resolution_status = "deferred_to_user"
            next_step = str(item.get("next_step") or "").strip()
        presentation_role = str(item.get("presentation_role") or "")
        bound_id = str(item.get("question_id") or lens_question.get("question_id") or "").strip()
        depth_assessment = assess_depth({**lens_question, "question_id": bound_id}, evidence_index=evidence_index,
            evidence_ids=evidence_ids, insights=[{**item, "question_id": bound_id}], scope_catalog=scope_catalog, actions=actions)
        dimensions = {
            "impact": (
                0
                if presentation_role == "supporting"
                else (
                    2 if (
                        value_score >= 4
                        or (
                            lens_question.get("priority") == "high"
                            and bool(resolved_answer)
                        )
                    ) else (1 if value_score > 0 else 0)
                )
            ),
            "abnormality": 2 if signal_type == "risk" else (1 if claim_type in {"diagnostic", "inference"} or signal_type == "opportunity" else 0),
            "actionability": 2 if item.get("actionable") else (1 if claim_type in {"diagnostic", "inference"} else 0),
            "credibility": 2 if strength == "high" else (1 if strength == "medium" else 0),
            "urgency": 2 if signal_type == "risk" else 1,
            "uniqueness": 1,
        }
        for name, fallback in dimensions.items():
            supplied = item.get(name)
            dimensions[name] = supplied if isinstance(supplied, int) and not isinstance(supplied, bool) and supplied in {0, 1, 2} else fallback
        if lens_question.get("priority") == "high" and resolved_answer:
            # A verified answer to an explicitly high-priority decision
            # question is legitimate business impact; it does not lower any
            # evidence or score threshold.
            dimensions["impact"] = 2
        candidates.append({
            **item,
            "question_id": str(item.get("question_id") or lens_question.get("question_id") or "").strip(),
            "question_priority": str(lens_question.get("priority") or "").strip(),
            "evidence_valid": item.get("evidence_valid", evidence_valid) is True,
            "information_gain": bool(
                resolution_status in {"direct_conclusion", "limited_with_next_step"}
                and resolved_answer
            ),
            "business_question": str(item.get("business_question") or lens_question.get("business_question") or objective).strip(),
            "decision_impact": str(item.get("implication") or item.get("decision_impact") or "").strip(),
            "duplicate_signature": str(item.get("duplicate_signature") or statement).strip(),
            "answer_status": answer_status,
            "required_depth": lens_question.get("required_depth"),
            "achieved_depth": depth_assessment["achieved_depth"],
            "action_ids": depth_assessment["action_ids"],
            "driver_evidence_ids": depth_assessment["driver_evidence_ids"],
            "segment_evidence_ids": depth_assessment["segment_evidence_ids"],
            "confirmed_dimensions": confirmed_dimensions,
            "evidence_gaps": evidence_gaps,
            "limitations": limitations,
            "resolution_status": resolution_status,
            "next_step": next_step,
            "resolved_answer": resolved_answer,
            "answer_text": resolved_answer,
            **dimensions,
        })
    return candidates


def _finalize_analysis_chapters(
    selection: dict,
    *,
    questions: list[dict],
    charts: list[dict],
    evidence_index=None, insights=(), scope_catalog=(), actions=(),
) -> list[dict]:
    """Bind selected chapter candidates to question depth and proving charts."""

    question_by_id = {
        str(item.get("question_id") or ""): item
        for item in questions if isinstance(item, dict) and item.get("question_id")
    }
    charts_by_id = {
        str(item.get("chart_id") or ""): item
        for item in charts if isinstance(item, dict) and item.get("chart_id")
    }
    finalized: list[dict] = []
    for raw in selection.get("analysis_chapters", []):
        chapter = dict(raw)
        question = question_by_id.get(str(chapter.get("question_id") or ""), {})
        required = question.get("required_depth", chapter.get("required_depth", 0))
        achieved = question.get("achieved_depth", chapter.get("achieved_depth", 0))
        required = required if isinstance(required, int) and not isinstance(required, bool) else 0
        achieved = achieved if isinstance(achieved, int) and not isinstance(achieved, bool) else 0
        answer_status = str(question.get("answer_status") or chapter.get("answer_status") or "partial")
        evidence_ids = list(dict.fromkeys([
            *[str(value) for value in chapter.get("fact_evidence_ids", []) if str(value)],
            *[str(value) for value in chapter.get("driver_evidence_ids", []) if str(value)],
            *[str(value) for value in chapter.get("segment_evidence_ids", []) if str(value)],
        ]))
        question_evidence_ids = [
            str(value) for value in question.get("evidence_ids", []) if str(value)
        ]
        # A selected question can be answered by controlled follow-up evidence
        # even when no legacy finding survived the old item-level portfolio.
        # Preserve that real question evidence instead of inventing a chapter
        # or a depth level later merely to keep an action alive.
        evidence_ids = list(dict.fromkeys([*evidence_ids, *question_evidence_ids]))
        if evidence_index is not None:
            chapter_insights = [item for item in insights if item.get("insight_id") == chapter.get("judgement_insight_id")]
            assessment = assess_depth(question, evidence_index=evidence_index, evidence_ids=evidence_ids, insights=chapter_insights,
                scope_catalog=scope_catalog, actions=actions)
            achieved = assessment["achieved_depth"]
            for field in ("fact_evidence_ids", "driver_evidence_ids", "segment_evidence_ids"):
                chapter[field] = assessment[field]
            evidence_ids = list(chapter["fact_evidence_ids"])
        elif not record_evidence_ids(chapter):
            chapter["fact_evidence_ids"] = evidence_ids
        explicit_chart_ids = [
            str(value) for value in chapter.get("chart_ids", [])
            if str(value) in charts_by_id
        ]
        if not explicit_chart_ids:
            lens = str(question.get("lens") or "")
            explicit_chart_ids = [
                str(chart.get("chart_id"))
                for chart in charts
                if isinstance(chart, dict)
                and chart.get("chart_id")
                and (not lens or str(chart.get("lens") or "") == lens)
                and set(str(value) for value in chart.get("evidence_ids", [])) & set(evidence_ids)
            ][:1]
        chart_evidence = {
            str(value)
            for chart_id in explicit_chart_ids
            for value in charts_by_id[chart_id].get("evidence_ids", [])
        }
        alignment_status = (
            "passed" if explicit_chart_ids and bool(chart_evidence & set(evidence_ids))
            else "not_required" if not explicit_chart_ids
            else "failed"
        )
        depth_met = achieved >= max(4, required)
        if chapter.get("selection_status") == "selected" and (
            answer_status != "answered" or not depth_met or alignment_status == "failed"
        ):
            chapter["selection_status"] = "appendix"
            chapter["selection_reason"] = "问题未达到回答深度或图表证明合同，降级为附录。"
        chapter.update({
            "answer_status": answer_status,
            "required_depth": required,
            "achieved_depth": achieved,
            "chart_ids": explicit_chart_ids,
            "claim_chart_alignment": {
                "status": alignment_status,
                "chapter_evidence_ids": evidence_ids,
                "chart_evidence_ids": sorted(chart_evidence),
            },
        })
        finalized.append(chapter)
    return finalized


def _prepare_formal_action(action: dict) -> dict:
    """Normalize actual action content before depth selection, without assigning owners."""
    action = dict(action)
    text = action.get("headline") or action.get("text") or ""
    limitations = action.get("limitations", [])
    action_type = action.get("action_type")
    if "action_type" not in action:
        lens = str(action.get("lens") or "")
        action_language = " ".join(str(action.get(key) or "") for key in (
            "headline", "text", "rationale", "verification_signal",
        )).lower()
        validation_action = any(
            marker in action_language
            for marker in ("验证", "复核", "test", "validate")
        )
        action_type = (
            "data_governance" if lens == "quality"
            else "controlled_test" if limitations or validation_action
            else "act_now"
        )
    # Only omitted legacy fields have defaults. Explicit malformed or empty
    # content remains malformed so that neither grading nor QA can launder it.
    steps = action.get("steps", [text] if isinstance(text, str) and text.strip() else [])
    guardrails = action.get("guardrails", ["仅在现有证据范围内执行；未验证机制不扩大投入。"])
    action.update({
        "action_type": action_type,
        "steps": steps,
        "success_signal": action.get("success_signal", action.get("verification_signal", "")),
        "guardrails": guardrails,
        "limitations": limitations,
    })
    return action


def _select_action_closed_story(analysis: dict, question_plan: dict, *, request, scope_catalog,
                                execution_stop_reasons: dict, management_order: bool) -> tuple[dict, list[dict]]:
    """Reach a bounded fixed point on retained actions; never requery or lower depth."""
    analysis["actions"] = [_prepare_formal_action(item) for item in analysis["actions"] if item.get("formal") is True]
    # Each changing pass removes actions or binds their final owners. No new
    # evidence/actions can enter this loop, so it cannot consume follow-up budget.
    for _ in range(len(analysis["actions"]) + 2):
        previous_actions = copy.deepcopy(analysis["actions"])
        question_plan = reconcile_questions_with_evidence(
            question_plan, evidence_ids_by_lens={str(q["question_id"]): q.get("evidence_ids", []) for q in question_plan["questions"]},
            evidence_index=analysis["evidence_index"], scope_catalog=scope_catalog,
            insights=_bind_canonical_question_ids(analysis["insights"], questions=question_plan["questions"]),
            actions=analysis["actions"], execution_stop_reasons=execution_stop_reasons,
        )
        for question in question_plan["questions"]:
            if question.get("answer_status") == "answered":
                question["status"] = "selected"
        questions_by_lens: dict[str, dict] = {
            str(question.get("question_id")): question
            for question in question_plan["questions"]
            if question.get("question_id")
        }
        lens_groups: dict[str, list[dict]] = {}
        for question in question_plan["questions"]:
            lens = str(question.get("lens") or "").strip()
            if lens:
                lens_groups.setdefault(lens, []).append(question)
        # Legacy insights without question_id may use a lens only when that lens
        # has one unambiguous question.  Mixed-priority same-lens questions fail
        # closed instead of inheriting whichever item happened to be last.
        for lens, grouped_questions in lens_groups.items():
            if len(grouped_questions) == 1:
                questions_by_lens[lens] = grouped_questions[0]
        selection_insights = _bind_canonical_question_ids(
            analysis["insights"], questions=list(question_plan["questions"]),
        )
        value_selection = _promote_answered_high_priority_representatives(
            score_and_select_findings(
            _value_selection_candidates(
                selection_insights,
                evidence_index=analysis["evidence_index"],
                questions_by_lens=questions_by_lens,
                objective=request.objective,
                available_dimensions=set(str(value) for value in request.dimensions),
                scope_catalog=scope_catalog, actions=analysis["actions"],
            )),
            questions=list(question_plan["questions"]),
        )
        _require_same_lens_question_coverage(
            value_selection, questions=list(question_plan["questions"]),
        )
        value_selection["analysis_chapters"] = build_analysis_chapters([
            item
            for group in ("featured", "appendix", "dropped")
            for item in value_selection.get(group, [])
            if isinstance(item, dict)
        ])
        value_selection["analysis_chapters"] = _finalize_analysis_chapters(
            value_selection,
            questions=list(question_plan["questions"]),
            charts=list(analysis["charts"]),
            evidence_index=analysis["evidence_index"], insights=selection_insights,
            scope_catalog=scope_catalog, actions=analysis["actions"],
        )
        analysis["value_selection"] = value_selection
        analysis["analysis_chapters"] = value_selection["analysis_chapters"]
        analysis["featured_insight_ids"] = [
            str(item["insight_id"])
            for item in analysis["value_selection"]["featured"]
            if item["insight_id"]
        ]
        analysis["appendix_insight_ids"] = [
            str(item["insight_id"])
            for item in analysis["value_selection"]["appendix"]
            if item["insight_id"]
        ]
        presentation_featured = list(analysis["value_selection"]["featured"])
        if management_order:
            presentation_featured = management_presentation_order(presentation_featured)
        presentation_order = {
            str(item.get("insight_id") or ""): index
            for index, item in enumerate(presentation_featured)
            if isinstance(item, dict) and item.get("insight_id")
        }
        analysis["analysis_chapters"].sort(key=lambda chapter: (
            0 if chapter.get("selection_status") == "selected" else 1,
            min(
                (presentation_order.get(str(value), len(presentation_order)) for value in chapter.get("insight_ids", [])),
                default=len(presentation_order),
            ),
            -int(chapter.get("selection_score") or 0),
            str(chapter.get("chapter_id") or ""),
        ))
        featured_ids = set(analysis["featured_insight_ids"])
        # Formal recommendations must close a featured diagnostic when such a
        # link is available.  Generic supporting tasks do not crowd out a named
        # opportunity or risk in the decision section.
        formal_actions = [
            action for action in analysis["actions"] if action.get("formal") is True
        ]
        linked_actions = [
            action for action in formal_actions
            if featured_ids & set(action.get("source_insight_ids", []))
        ]
        if linked_actions:
            featured_order = {
                insight_id: index
                for index, insight_id in enumerate(
                    str(item.get("insight_id") or "") for item in presentation_featured
                )
            }
            linked_actions.sort(key=lambda action: min(
                (featured_order.get(str(insight_id), len(featured_order))
                 for insight_id in action.get("source_insight_ids", [])),
                default=len(featured_order),
            ))
            independent_actions = [
                action for action in formal_actions
                if not action.get("source_insight_ids")
            ]
            analysis["actions"] = [
                *linked_actions,
                *independent_actions[: max(0, 3 - len(linked_actions))],
            ][:5]
        else:
            analysis["actions"] = [
                action for action in formal_actions
                if not action.get("source_insight_ids")
            ][:5]
        analysis["actions"] = _close_formal_actions_with_chapters(
            analysis["actions"],
            chapters=analysis["analysis_chapters"],
        )
        for priority, action in enumerate(analysis["actions"], start=1):
            action["priority"] = priority

        if analysis["actions"] == previous_actions:
            return question_plan, presentation_featured
        if not {a["action_id"] for a in analysis["actions"]} <= {a["action_id"] for a in previous_actions}:
            raise ValueError("action closure may only retain existing actions")
    raise ValueError("action closure selection did not converge")


def _close_formal_actions_with_chapters(
    actions: list[dict],
    *,
    chapters: list[dict],
) -> list[dict]:
    """Keep formal actions only when they close a selected chapter."""

    def eligible_for_action_closure(chapter: dict) -> bool:
        required = chapter.get("required_depth")
        achieved = chapter.get("achieved_depth")
        return bool(
            chapter.get("answer_status") == "answered"
            and isinstance(required, int) and not isinstance(required, bool)
            and isinstance(achieved, int) and not isinstance(achieved, bool)
            and achieved >= max(4, required)
            and chapter.get("claim_chart_alignment", {}).get("status") != "failed"
            and str(chapter.get("decision_question") or "").strip()
            and str(chapter.get("report_language") or chapter.get("judgement") or "").strip()
        )

    eligible = [item for item in chapters if eligible_for_action_closure(item)]
    chapter_by_insight = {
        str(insight_id): chapter
        for chapter in eligible
        for insight_id in chapter.get("insight_ids", [])
        if str(insight_id)
    }
    closed: list[dict] = []
    for raw in actions:
        if raw.get("formal") is not True:
            continue
        action = dict(raw)
        source_chapter_ids = list(dict.fromkeys(
            str(chapter_by_insight[str(insight_id)].get("chapter_id"))
            for insight_id in action.get("source_insight_ids", [])
            if str(insight_id) in chapter_by_insight
        ))
        if not source_chapter_ids and not action.get("source_insight_ids"):
            action_evidence = {str(value) for value in action.get("evidence_ids", [])}
            source_chapter_ids = [
                str(chapter.get("chapter_id"))
                for chapter in eligible
                if action_evidence & set(
                    str(value)
                    for key in ("fact_evidence_ids", "driver_evidence_ids", "segment_evidence_ids")
                    for value in chapter.get(key, [])
                )
            ][:1]
        if not source_chapter_ids:
            continue
        for chapter in eligible:
            if str(chapter.get("chapter_id") or "") in source_chapter_ids:
                chapter["selection_status"] = "selected"
                chapter["selection_reason"] = "章节达到深度，且正式行动证据形成决策闭环。"
        action = _prepare_formal_action(action)
        action["source_chapter_ids"] = source_chapter_ids
        closed.append(action)
    action_ids_by_chapter: dict[str, list[str]] = {}
    for action in closed:
        for chapter_id in action.get("source_chapter_ids", []):
            action_ids_by_chapter.setdefault(str(chapter_id), []).append(str(action.get("action_id") or ""))
    for chapter in chapters:
        chapter["action_ids"] = [
            value for value in dict.fromkeys(action_ids_by_chapter.get(str(chapter.get("chapter_id") or ""), []))
            if value
        ]
    return closed


def _bind_canonical_question_ids(
    insights: list[dict], *, questions: list[dict],
) -> list[dict]:
    """Bind generic producers only to their deterministic canonical question.

    A lens is not a question identity.  Custom questions that share a lens
    therefore remain unbound until their producer names the question_id.
    """

    question_index = {
        str(question.get("question_id") or "").strip(): question
        for question in questions
        if isinstance(question, dict) and str(question.get("question_id") or "").strip()
    }
    bound: list[dict] = []
    for raw in insights:
        item = dict(raw)
        if not str(item.get("question_id") or "").strip():
            lens = str(item.get("lens") or "").strip()
            canonical_id = f"q_{lens}" if lens else ""
            canonical = question_index.get(canonical_id)
            if canonical and str(canonical.get("lens") or "").strip() == lens:
                item["question_id"] = canonical_id
        bound.append(item)
    return bound


def _require_same_lens_question_coverage(
    selection: dict[str, list[dict]], *, questions: list[dict],
) -> None:
    """Fail closed when an ambiguous lens hides an answered priority question."""

    lens_groups: dict[str, list[dict]] = {}
    for question in questions:
        if not isinstance(question, dict):
            continue
        if question.get("status") != "selected" or question.get("answer_status") != "answered":
            continue
        lens = str(question.get("lens") or "").strip()
        if lens:
            lens_groups.setdefault(lens, []).append(question)
    records = [
        item
        for group in ("featured", "appendix", "dropped")
        for item in selection.get(group, [])
        if isinstance(item, dict)
    ]
    for lens, grouped in lens_groups.items():
        high_priority = [
            question for question in grouped if question.get("priority") == "high"
        ]
        if len(high_priority) < 2:
            continue
        for question in high_priority:
            question_id = str(question.get("question_id") or "").strip()
            representatives = [
                item for item in records
                if str(item.get("question_id") or "").strip() == question_id
                and item.get("classification") == "featured"
            ]
            if len(representatives) != 1:
                raise ValueError(
                    "同一分析镜头存在多个问题时，高优先问题必须由 producer 显式绑定 question_id；"
                    f"未形成唯一主线代表：{question_id} ({lens})"
                )


def _promote_answered_high_priority_representatives(
    selection: dict[str, list[dict]], *, questions: list[dict],
) -> dict[str, list[dict]]:
    """Guarantee one bounded main-story representative per answered priority question."""

    records = [
        item for group in ("featured", "appendix", "dropped")
        for item in selection.get(group, []) if isinstance(item, dict)
    ]
    by_question: dict[str, list[dict]] = {}
    for item in records:
        question_id = str(item.get("question_id") or "").strip()
        if question_id:
            by_question.setdefault(question_id, []).append(item)
    question_index = {
        str(question.get("question_id") or "").strip(): question
        for question in questions
        if isinstance(question, dict) and str(question.get("question_id") or "").strip()
    }
    high_priority_count_by_lens: dict[str, int] = {}
    for question in question_index.values():
        if question.get("priority") == "high" and question.get("answer_status") == "answered":
            lens = str(question.get("lens") or "").strip()
            if lens:
                high_priority_count_by_lens[lens] = high_priority_count_by_lens.get(lens, 0) + 1
    for question_id, question in question_index.items():
        if not (question.get("priority") == "high" and question.get("answer_status") == "answered"):
            continue
        eligible = [
            item for item in by_question.get(question_id, [])
            if item.get("evidence_valid") is True
            and item.get("answer_status") == "answered"
            and item.get("resolution_status") == "direct_conclusion"
            and item.get("classification") != "dropped"
            and not is_supporting_finding(item)
        ]
        if not eligible:
            continue
        natural_featured = [
            item for item in eligible if item.get("classification") == "featured"
        ]
        lens = str(question.get("lens") or "").strip()
        requires_unique_representative = high_priority_count_by_lens.get(lens, 0) > 1
        if natural_featured and not requires_unique_representative:
            # One decision question can yield complementary main-story risks
            # and opportunities. Coverage must not demote already-qualified
            # findings merely because they share the same question identity.
            continue
        representative = min(
            natural_featured or eligible,
            key=lambda item: (-int(item.get("score") or 0), int(item.get("source_index") or 0), str(item.get("insight_id") or "")),
        )
        representative["classification"] = "featured"
        representative["portfolio_override"] = "answered_high_priority_representative"
        representative["selection_reasons"] = [
            *list(representative.get("selection_reasons") or []),
            "promoted_answered_high_priority_representative",
        ]
        # Only a management-grade direct answer can fill a missing high-
        # priority question slot. Supporting KPI facts never do. Same-lens
        # custom questions retain the stricter identity boundary.
        for sibling in eligible:
            if sibling is representative:
                continue
            if sibling.get("classification") == "featured":
                sibling["classification"] = "appendix"
            sibling["portfolio_override"] = "sibling_of_answered_high_priority_representative"
            sibling["selection_reasons"] = [
                *list(sibling.get("selection_reasons") or []),
                "bounded_to_one_representative_per_question",
            ]
    rebuilt = {"featured": [], "appendix": [], "dropped": []}
    for item in records:
        rebuilt[str(item.get("classification") or "dropped")].append(item)
    for group in rebuilt:
        rebuilt[group].sort(key=lambda item: (-int(item.get("score") or 0), int(item.get("source_index") or 0), str(item.get("insight_id") or "")))
    return {**selection, **rebuilt}


def _canonical_transactional_story_input(
    transactional_result: dict[str, object], *, analysis: dict[str, object], request: ReportRequest,
) -> dict[str, object]:
    """Give transactional narrative the identical retained-period window as KPI analysis."""

    prepared = transactional_result.get("prepared_frame")
    mappings = transactional_result.get("analysis_contract", {})
    fields = mappings.get("field_mappings", {}) if isinstance(mappings, dict) else {}
    time_field = str(fields.get("time") or "") if isinstance(fields, dict) else ""
    period_state = analysis.get("periods", {})
    retained = [str(value) for value in period_state.get("labels", [])] if isinstance(period_state, dict) else []
    excluded = [str(value) for value in period_state.get("excluded_incomplete_periods", [])] if isinstance(period_state, dict) else []
    if not isinstance(prepared, pd.DataFrame) or not time_field or time_field not in prepared.columns:
        return {**transactional_result, "story_period_scope": {"retained_periods": retained, "excluded_periods": excluded}}
    canonical, _, _, _ = prepare_analysis_frame(prepared, request, retained_periods=retained)
    return {
        **transactional_result,
        "prepared_frame": canonical,
        "story_period_scope": {
            "retained_periods": retained,
            "excluded_periods": excluded,
            "analysis_window": str(period_state.get("analysis_label") or "") if isinstance(period_state, dict) else "",
        },
    }


def _reconcile_executive_summary_with_value_selection(
    analysis: dict,
    *,
    engineering_regression: bool,
    presentation_featured: list[dict] | None = None,
) -> None:
    """Make every business-summary conclusion traceable to a featured finding."""
    if engineering_regression:
        return
    selection = analysis.get("value_selection", {})
    if presentation_featured is not None:
        featured = list(presentation_featured)
    else:
        featured = selection.get("featured", []) if isinstance(selection, dict) else []
    summary = analysis.get("executive_summary", {})
    priority_actions = [
        str(item.get("headline") or item.get("text") or "").rstrip("。")
        for item in analysis.get("actions", [])[:2]
        if str(item.get("headline") or item.get("text") or "").strip()
    ]
    if not priority_actions and isinstance(summary, dict):
        priority_actions = list(summary.get("priority_actions", []))
    selected_chapters = [
        item for item in analysis.get("analysis_chapters", [])
        if isinstance(item, dict) and item.get("selection_status") == "selected"
    ]
    if selected_chapters:
        source_chapters = selected_chapters[:3]
        conclusions = [
            str(item.get("report_language") or item.get("judgement") or "").rstrip("。")
            for item in source_chapters
        ]
        analysis["executive_summary"] = {
            "key_conclusions": conclusions,
            "key_conclusion_evidence_ids": [
                list(dict.fromkeys([
                    *item.get("fact_evidence_ids", []),
                    *item.get("driver_evidence_ids", []),
                    *item.get("segment_evidence_ids", []),
                ]))
                for item in source_chapters
            ],
            "key_conclusion_insight_ids": [
                str(item.get("insight_ids", [""])[0]) if item.get("insight_ids") else ""
                for item in source_chapters
            ],
            "key_conclusion_chapter_ids": [str(item["chapter_id"]) for item in source_chapters],
            "summary_status": "selected_chapter_conclusions",
            "priority_actions": priority_actions,
        }
        analysis["report_summary"] = "；".join(conclusions)
        if priority_actions:
            analysis["report_summary"] += f"。下一周期优先：{'；'.join(priority_actions)}"
        elif analysis["report_summary"]:
            analysis["report_summary"] += "。"
        return
    source_items: list[dict] = []
    used_ids: set[str] = set()
    used_slots: set[tuple[str, str]] = set()
    management_grade = [
        item for item in featured
        if isinstance(item, dict)
        and not is_supporting_finding(item)
        and (
            item.get("actionable")
            or str(item.get("claim_type") or item.get("kind") or "")
            in {"diagnostic", "inference"}
        )
    ]
    ordered_items = [
        *management_grade,
        *[item for item in featured if item not in management_grade],
    ]
    for item in ordered_items:
        if not isinstance(item, dict):
            continue
        insight_id = str(item.get("insight_id") or "")
        if not insight_id or insight_id in used_ids:
            continue
        lens = str(item.get("lens") or "")
        signal = str(item.get("signal_type") or "").strip().lower()
        if not signal:
            signal = str(item.get("claim_type") or item.get("kind") or "default").strip().lower()
        slot = (lens, signal)
        if slot in used_slots:
            continue
        source_items.append(item)
        used_ids.add(insight_id)
        used_slots.add(slot)
        if len(source_items) == 3:
            break
    if source_items:
        conclusions = [
            str(item.get("resolved_answer") or item.get("answer_text") or "").rstrip("。")
            for item in source_items
        ]
        analysis["executive_summary"] = {
            "key_conclusions": conclusions,
            "key_conclusion_evidence_ids": [list(item.get("evidence_ids", [])) for item in source_items],
            "key_conclusion_insight_ids": [str(item["insight_id"]) for item in source_items],
            "key_conclusion_chapter_ids": [],
            "summary_status": "direct_featured_conclusions",
            "priority_actions": priority_actions,
        }
        analysis["report_summary"] = "；".join(conclusions)
    else:
        analysis["executive_summary"] = {
            "key_conclusions": [],
            "key_conclusion_evidence_ids": [],
            "key_conclusion_insight_ids": [],
            "key_conclusion_chapter_ids": [],
            "summary_status": "limited_no_featured_insights",
            "priority_actions": priority_actions,
        }
        analysis["report_summary"] = "未形成满足证据门槛的关键经营结论。"
    if priority_actions:
        analysis["report_summary"] += f"。下一周期优先：{'；'.join(priority_actions)}"
    elif analysis["report_summary"]:
        analysis["report_summary"] += "。"


def default_report_title(source_path: Path, request: ReportRequest) -> str:
    """Build a concise business-facing title when the user did not supply one."""

    source_name = source_path.stem.replace("_", " ").strip()
    subject = re.sub(
        r"(?i)(?:19|20)\d{2}\s*(?:-|—|–|至|~)\s*(?:(?:19|20)\d{2}|\d{2})",
        "",
        source_name,
    )
    removable_suffixes = (
        "公开数据",
        "原始数据",
        "年度经营数据",
        "经营数据",
        "年度数据",
        "数据明细",
        "数据导出",
        "数据集",
        "数据",
    )
    changed = True
    while changed:
        changed = False
        for suffix in removable_suffixes:
            updated = re.sub(
                rf"[\s\-|—–_｜]*{re.escape(suffix)}[\s\-|—–_｜]*$",
                "",
                subject,
                flags=re.IGNORECASE,
            ).strip()
            if updated != subject:
                subject = updated
                changed = True
    subject = re.sub(r"[\s\-|—–_｜]+", " ", subject).strip()
    if subject.endswith("年度"):
        subject = subject[:-2].strip()

    business_words = ("经营", "零售", "销售", "订单", "收入", "营销", "业务")
    suffix = "经营分析简报" if any(word in source_name for word in business_words) else "数据分析简报"
    candidate = subject if subject.endswith(("简报", "报告", "复盘")) else f"{subject}{suffix}"
    cover_capacity = int(LAYOUT_REGISTRY["cover"]["max_title_units"])
    if subject and display_units(candidate) <= cover_capacity:
        return candidate

    period_label = "周度" if request.period_type == "weekly" else "月度"
    return f"{period_label}{suffix}"


MANAGED_OUTPUTS = {
    "report_model.json",
    "report.html",
    "html_qa.json",
    "report.pptx",
    "ppt_qa.json",
    "slideviber_handoff.md",
    "run_result.json",
}


SUPPORTED_REQUEST_VALUES = {
    "mode": {"quick", "professional"},
    "period_type": {"weekly", "monthly"},
    "output_mode": {"report", "report+pptx"},
    "week_start": {"monday", "sunday"},
    "incomplete_period_policy": {"exclude", "keep"},
    "theme": {"corporate", "clean", "warm"},
    "ppt_refinement": {"standard", "offer_slideviber"},
    "duplicate_policy": {"keep", "drop_exact"},
    "numeric_error_policy": {"fail", "coerce_and_warn"},
    "analysis_intent": {"business_review", "exploration", "engineering_regression"},
}
REQUEST_DEFAULTS = {
    "duplicate_policy": "keep",
    "numeric_error_policy": "fail",
}
SUPPORTED_COMPARISONS = {"period_over_period", "year_over_year"}


def validate_request(request: ReportRequest) -> None:
    for field, allowed in SUPPORTED_REQUEST_VALUES.items():
        raw_value = getattr(request, field, REQUEST_DEFAULTS.get(field))
        if raw_value is None and field == "analysis_intent":
            raw_value = "business_review"
        value = str(raw_value)
        if value not in allowed:
            choices = ", ".join(sorted(allowed))
            raise ValueError(f"{field} 不支持“{value}”；可选值：{choices}")
    unknown_comparisons = sorted(set(request.comparisons) - SUPPORTED_COMPARISONS)
    if unknown_comparisons:
        raise ValueError(
            f"comparisons 包含不支持的值：{', '.join(unknown_comparisons)}"
        )
    validate_analysis_questions(getattr(request, "analysis_questions", ()))
    if not request.primary_metrics:
        raise ValueError("primary_metrics 至少需要一个指标")
    if len(request.primary_metrics) > 6:
        raise ValueError("primary_metrics 首版最多支持 6 个指标")
    try:
        ZoneInfo(request.timezone)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"timezone 无法识别：{request.timezone}") from exc


def _load_table(source_path: Path, sheet_name: str | None = None) -> pd.DataFrame:
    frame, source_meta = load_source_table(source_path, sheet_name)
    if source_meta.get("needs_sheet_choice"):
        raise ValueError(
            "检测到多个 Sheet，请指定 sheet_name："
            + ", ".join(source_meta["sheet_names"])
        )
    return frame


def profile_table(
    request: ReportRequest,
    *,
    frame: pd.DataFrame | None = None,
    source_meta: dict | None = None,
) -> TableProfile:
    source_path = Path(request.source_path)
    if frame is None:
        frame, source_meta = load_source_table(source_path, request.sheet_name)
        if source_meta.get("needs_sheet_choice"):
            raise ValueError(
                "检测到多个 Sheet，请指定 sheet_name："
                + ", ".join(source_meta["sheet_names"])
            )
    source_meta = dict(source_meta or {})
    semantic_result = resolve_request_semantic_contract(
        request,
        source_columns=frame.columns,
        metric_dependencies={contract["name"]: required_source_fields(contract)
                             for contract in normalize_metric_contracts(request)},
    )
    if semantic_result["status"] != "ready":
        _raise_semantic_contract_error(semantic_result, request)
    contracts = normalize_metric_contracts(request)
    metric_fields = [field for contract in contracts for field in required_source_fields(contract)]
    numeric_fields = [field for contract in contracts for field in numeric_source_fields(contract)]
    required = (request.date_column, *metric_fields, *request.dimensions)
    missing_fields = [field for field in required if field not in frame.columns]
    if missing_fields:
        raise ValueError(f"缺少字段：{', '.join(missing_fields)}")

    raw_dates = frame[request.date_column]
    nonblank_dates = raw_dates[raw_dates.notna() & raw_dates.astype(str).str.strip().ne("")]
    dates = pd.to_datetime(raw_dates, errors="coerce")
    valid_dates = dates.dropna()
    if valid_dates.empty:
        raise ValueError(f"日期字段无法解析：{request.date_column}")
    invalid_date_mask = nonblank_dates.index[~dates.loc[nonblank_dates.index].notna()]
    date_invalid_count = int(len(invalid_date_mask))
    date_parse_rate = round(
        float((len(nonblank_dates) - date_invalid_count) / len(nonblank_dates)), 4
    ) if len(nonblank_dates) else 0.0

    numeric_quality: dict[str, dict] = {}
    for field in dict.fromkeys(numeric_fields):
        raw = frame[field]
        nonblank = raw[raw.notna() & raw.astype(str).str.strip().ne("")]
        parsed = pd.to_numeric(nonblank, errors="coerce")
        invalid = nonblank[parsed.isna()]
        numeric_quality[field] = {
            "nonblank_count": int(len(nonblank)),
            "valid_count": int(parsed.notna().sum()),
            "invalid_count": int(parsed.isna().sum()),
            "parse_rate": round(float(parsed.notna().mean()), 4) if len(nonblank) else 0.0,
            "invalid_examples": list(dict.fromkeys(str(value) for value in invalid.head(3))),
        }

    ratio_denominator_zero: dict[str, int] = {}
    for contract in contracts:
        if contract["aggregation"] != "ratio":
            continue
        denominator = str(contract["denominator"])
        numeric_denominator = pd.to_numeric(frame[denominator], errors="coerce")
        ratio_denominator_zero[str(contract["name"])] = int(
            numeric_denominator.eq(0).sum()
        )

    high_cardinality_dimensions: dict[str, int] = {}
    for dimension in request.dimensions:
        unique_count = int(frame[dimension].nunique(dropna=True))
        unique_ratio = unique_count / max(len(frame), 1)
        if unique_count >= 50 or (
            len(frame) <= 100 and unique_count >= 4 and unique_ratio >= 0.8
        ):
            high_cardinality_dimensions[str(dimension)] = unique_count

    profile_warnings: list[str] = []
    if date_invalid_count:
        profile_warnings.append(
            f"日期字段“{request.date_column}”有 {date_invalid_count} 个非空值无法解析。"
        )
    for field, quality in numeric_quality.items():
        if quality["invalid_count"]:
            profile_warnings.append(
                f"数值字段“{field}”有 {quality['invalid_count']} 个非空值无法解析。"
            )
    for metric_name, count in ratio_denominator_zero.items():
        if count:
            contract = next(c for c in contracts if c["name"] == metric_name)
            treatment = ("保留进入合计，汇总分母为 0 时不可计算"
                         if contract.get("zero_denominator_policy") == "include_in_totals"
                         else "计算时将排除")
            profile_warnings.append(
                f"比率指标“{metric_name}”存在 {count} 行分母为 0，{treatment}。"
            )
    for dimension, unique_count in high_cardinality_dimensions.items():
        profile_warnings.append(
            f"维度“{dimension}”包含 {unique_count} 个不同值，展示时使用 Top-N＋其他。"
        )

    sensitive_markers = (
        "姓名",
        "名字",
        "手机号",
        "电话",
        "身份证",
        "证件号",
        "邮箱",
        "email",
        "e-mail",
        "地址",
    )
    sensitive_columns = tuple(
        str(column)
        for column in frame.columns
        if any(marker in str(column).lower() for marker in sensitive_markers)
    )

    return TableProfile(
        row_count=int(len(frame)),
        column_count=int(len(frame.columns)),
        columns=tuple(str(column) for column in frame.columns),
        missing_by_column={
            str(column): int(frame[column].isna().sum()) for column in frame.columns
        },
        duplicate_rows=int(frame.duplicated().sum()),
        date_min=valid_dates.min().date().isoformat(),
        date_max=valid_dates.max().date().isoformat(),
        sensitive_columns=sensitive_columns,
        sheet_name=source_meta.get("sheet_name"),
        source_encoding=source_meta.get("encoding"),
        date_parse_rate=date_parse_rate,
        date_invalid_count=date_invalid_count,
        numeric_quality=numeric_quality,
        ratio_denominator_zero=ratio_denominator_zero,
        high_cardinality_dimensions=high_cardinality_dimensions,
        warnings=tuple(profile_warnings),
    )


def _period_labels(dates: pd.Series, period_type: str) -> pd.Series:
    if period_type == "monthly":
        return dates.dt.to_period("M").astype(str)
    if period_type == "weekly":
        return dates.dt.to_period("W-SUN").map(
            lambda period: period.start_time.date().isoformat()
        )
    return dates.dt.date.astype(str)


def _engineering_regression_analysis(analysis: dict) -> dict:
    """Keep engineering regression output to deterministic QA contracts only."""
    qa_title = "工程回归：交易数据质量与计算合同核验"
    sanitized = dict(analysis)
    sanitized.update(
        {
            "kpis": [],
            "dimensions": {},
            "findings": [],
            "insights": [],
            "actions": [],
            "levers": [],
            "charts": [],
            "evidence_index": {},
            "report_title": qa_title,
            "judgement_headline": qa_title,
            "executive_summary": {
                "key_conclusions": [],
                "key_conclusion_evidence_ids": [],
                "priority_actions": [],
            },
            "report_summary": "已生成交易准备、聚合与数据质量的工程核验合同。",
        }
    )
    sanitized["period_overview"] = {
        **sanitized["period_overview"], "kpis": []
    }
    sanitized["latest_snapshot"] = {
        **sanitized["latest_snapshot"], "kpis": []
    }
    return sanitized


def _engineering_metric_reconciliation(
    frame: pd.DataFrame,
    analysis: dict,
    request: ReportRequest,
) -> dict:
    """Recompute every locked metric contract and expose exact reconciliation evidence."""

    scoped_frame = frame.copy()
    if str(getattr(request, "duplicate_policy", "keep")) == "drop_exact":
        scoped_frame = scoped_frame.drop_duplicates().copy()
    scoped_frame[request.date_column] = pd.to_datetime(
        scoped_frame[request.date_column], errors="coerce"
    )
    scoped_frame = scoped_frame.dropna(subset=[request.date_column]).copy()
    scoped_frame["__period"] = period_labels(
        scoped_frame[request.date_column], request.period_type, request.week_start
    )
    excluded_periods = {
        str(value)
        for value in analysis.get("periods", {}).get("excluded_incomplete_periods", [])
    }
    if excluded_periods:
        scoped_frame = scoped_frame[
            ~scoped_frame["__period"].astype(str).isin(excluded_periods)
        ].copy()
    items: list[dict] = []
    for contract in analysis.get("metric_contracts", []):
        name = str(contract["name"])
        expected = analysis.get("metrics", {}).get(name, {}).get("total")
        recomputed = _aggregate_total(scoped_frame, contract)
        matched = (
            expected is None
            and recomputed is None
            or expected is not None
            and recomputed is not None
            and math.isclose(float(expected), float(recomputed), rel_tol=1e-9, abs_tol=1e-9)
        )
        difference = (
            None
            if expected is None or recomputed is None
            else float(recomputed) - float(expected)
        )
        items.append(
            {
                "metric_name": name,
                "aggregation": str(contract.get("aggregation") or ""),
                "sample_count": int(len(scoped_frame)),
                "expected_total": expected,
                "recomputed_total": recomputed,
                "difference": difference,
                "status": "passed" if matched else "failed",
            }
        )
    return {
        "status": "passed" if all(item["status"] == "passed" for item in items) else "failed",
        "items": items,
    }


def _qa_slide_copy(model: dict) -> None:
    """Replace planner fallbacks that imply business conclusions in QA mode."""
    copies = {
        "S01": ("工程回归：交易合同核验", "说明工程核验的范围与输入合同", "工程核验"),
        "S02": ("仅输出数据质量与计算核验结果", "确认本次不生成经营判断", "QA 摘要"),
        "S03": ("核心指标仅作为聚合合同核验输入", "核对计算路径与字段完整性", "聚合合同"),
        "S04": ("未生成经营趋势判断", "工程回归不输出经营趋势解读", "趋势核验"),
        "S05": ("未生成经营结构判断", "工程回归不输出结构归因", "结构核验"),
        "S06": ("未生成驱动归因", "工程回归不输出驱动归因", "质量核验"),
        "S07": ("仅记录 QA 风险与限制", "工程回归不输出机会或经营风险判断", "风险登记"),
        "S08": ("不生成经营行动", "工程回归只保留后续 QA 复核边界", "复核边界"),
        "S09": ("输入数据与合同可回溯", "说明数据范围、合同和质量限制", "数据合同"),
    }
    for slide in model["slide_plan"]:
        claim, purpose, eyebrow = copies[str(slide["slide_id"])]
        slide["claim"] = claim
        slide["purpose"] = purpose
        visual_spec = slide.get("visual_spec") or {}
        visual_spec["eyebrow"] = eyebrow
        if "display_claim" in visual_spec:
            visual_spec["display_claim"] = claim
        slide["content_exemption"] = "qa"


def bind_direct_dimension_evidence(
    *,
    evidence_index: dict[str, Any],
    dimension_lenses: dict[str, str],
) -> dict[str, list[str]]:
    """Bind deterministic dimension evidence to its semantic business lens."""

    bound: dict[str, list[str]] = {}
    for evidence_id, evidence in evidence_index.items():
        if not isinstance(evidence, dict):
            continue
        lens = dimension_lenses.get(str(evidence.get("dimension") or ""))
        if lens and isinstance(evidence_id, str) and evidence_id:
            bound.setdefault(lens, []).append(evidence_id)
    return bound


def build_report_model(
    request: ReportRequest,
    *,
    enforce_narrative: bool = True,
    execute_followups: bool = True,
) -> dict:
    validate_request(request)
    source_path = Path(request.source_path)
    frame, source_meta = load_source_table(source_path, request.sheet_name)
    scope_registry = ScopeRegistry(frame)
    source_columns = [str(column) for column in frame.columns]
    if source_meta.get("needs_sheet_choice"):
        raise ValueError(
            "检测到多个 Sheet，请指定 sheet_name："
            + ", ".join(source_meta["sheet_names"])
        )
    engineering_regression = str(
        getattr(request, "analysis_intent", "business_review")
    ) == "engineering_regression"
    source_profile = (
        profile_table(request, frame=frame, source_meta=source_meta)
        if engineering_regression
        else None
    )
    transactional_result = None
    semantic_result = resolve_request_semantic_contract(
        request,
        source_columns=frame.columns,
        metric_dependencies={contract["name"]: required_source_fields(contract)
                             for contract in normalize_metric_contracts(request)},
    )
    if semantic_result["status"] != "ready":
        _raise_semantic_contract_error(semantic_result, request)
    semantic_contract = semantic_result["contract"]
    # Analysis and replay must resolve adapters from the same normalized
    # semantics, including automatically bound business display fields.
    request = ReportRequest(**{
        name: semantic_contract if name == "semantic_contract" else _request_schema_value(request, name)
        for name in _REPORT_REQUEST_SCHEMA
    })
    if isinstance(semantic_contract, dict) and str(
        semantic_contract.get("domain") or semantic_contract.get("profile") or ""
    ) == "transactional_commerce":
        transactional_result = prepare_transactional_commerce(
            frame,
            semantic_contract,
            analysis_intent=str(getattr(request, "analysis_intent", "business_review")),
            mode=str(getattr(request, "mode", "professional")),
        )
        if transactional_result["status"] != "ready":
            raise ValueError("transactional_commerce 语义合同需要确认：" + "；".join(transactional_result["questions"]))
        frame = transactional_result["prepared_frame"]
    engineered_profile = profile_table(request, frame=frame, source_meta=source_meta)
    profile = source_profile or engineered_profile
    analysis = analyse_frame(frame, request, scope_registry=scope_registry)
    final_profile = analysis.get("analysis_profile", {})
    if (
        isinstance(semantic_contract, dict)
        and semantic_contract.get("adapter_selection_reason")
        in {"explicit_verified", "confirmed_experimental"}
        and semantic_contract.get("adapter_id")
        != final_profile.get("adapter_id")
    ):
        raise ValueError(
            "semantic_contract 适配器与最终 analysis_profile 不一致："
            f"{semantic_contract.get('adapter_id')} != {final_profile.get('adapter_id')}"
        )
    if engineering_regression:
        analysis = _engineering_regression_analysis(analysis)
    available_objects = canonical_available_objects(
        primary_metrics=request.primary_metrics,
        dimensions=request.dimensions,
        semantic_contract=semantic_contract,
        available_fields={str(value) for value in frame.columns},
    )
    custom_questions = list(validate_analysis_questions(getattr(request, "analysis_questions", ())))
    question_plan = canonical_analysis_question_contract(
        analysis_intent=str(getattr(request, "analysis_intent", "business_review")), audience=request.audience,
        objective=request.objective, semantic_contract=semantic_contract, available_fields=set(str(value) for value in frame.columns),
        available_objects=available_objects, available_metrics={
            *[str(value) for value in request.primary_metrics],
            *[str(item["metric_id"]) for item in request.metric_contracts
              if item.get("metric_id") and item.get("name") in request.primary_metrics],
        },
        period_count=len(analysis["periods"].get("labels", [])), custom_questions=custom_questions,
    )
    question_plan = enrich_question_graph_with_preliminary_scan(
        question_plan,
        analysis={
            **analysis,
            "warnings": list(dict.fromkeys([*analysis["warnings"], *profile.warnings])),
        },
    )
    candidate_question_graph = copy.deepcopy(question_plan)
    dimension_lenses = semantic_dimension_lenses(semantic_contract, request.dimensions)
    metric_lenses = {
        str(item.get("name")): "quality"
        for item in analysis.get("metric_contracts", [])
        if item.get("name") and item.get("role") == "quality"
    }
    metric_directions = {
        str(item.get("name")): str(item.get("direction") or "neutral")
        for item in analysis.get("metric_contracts", []) if item.get("name")
    }
    transactional_story = None
    if transactional_result is not None and not engineering_regression:
        story_transactional_result = _canonical_transactional_story_input(
            transactional_result, analysis=analysis, request=request,
        )
        transactional_story = build_transactional_business_content(
            analysis=analysis,
            transactional_result=story_transactional_result,
            semantic_contract=semantic_contract or {},
            scope_registry=scope_registry,
            scope_parent_id=analysis["analysis_window_scope_id"],
        )
        analysis["evidence_index"].update(transactional_story["evidence_index"])
        analysis["insights"] = [*transactional_story["insights"], *analysis["insights"]]
        analysis["actions"] = [*transactional_story["actions"], *analysis["actions"]]
        # Transactional levers are restricted to the calculated sales bridge;
        # geography/product/customer contributions have their own evidence-led
        # insight/chart rather than being repeated as pseudo-drivers.
        analysis["levers"] = list(transactional_story.get("levers", []))
        analysis["charts"] = [*transactional_story["charts"], *analysis["charts"]]
    enriched_content = enrich_analysis_content(
        evidence_index=analysis["evidence_index"], insights=analysis["insights"], actions=analysis["actions"],
        row_count=int(len(frame)), business_objects=available_objects,
        filter_scope="confirmed semantic filters" if semantic_contract else "loaded source table",
    )
    analysis.update(enriched_content)
    selected_lenses = {str(item["lens"]) for item in question_plan["questions"] if item.get("status") == "selected"}
    analysis.update(scope_content_to_lenses(
        evidence_index=analysis["evidence_index"], insights=analysis["insights"], actions=analysis["actions"], charts=analysis["charts"],
        selected_lenses=selected_lenses, dimension_lenses=dimension_lenses,
        metric_lenses=metric_lenses,
        metric_directions=metric_directions,
    ))
    evidence_ids_by_lens: dict[str, list[str]] = {}

    def bind_evidence(lens: Any, evidence_ids: Any) -> None:
        if not lens or not isinstance(evidence_ids, (list, tuple)):
            return
        bound = evidence_ids_by_lens.setdefault(str(lens), [])
        for evidence_id in evidence_ids:
            if isinstance(evidence_id, str) and evidence_id and evidence_id not in bound:
                bound.append(evidence_id)

    for item in analysis.get("insights", []):
        if item.get("lens") and item.get("evidence_ids") and (
            item.get("lens") != "quality"
            or item.get("signal_type") in {"risk", "opportunity"}
            or item.get("claim_type") in {"diagnostic", "inference"}
        ):
            bind_evidence(item.get("lens"), item.get("evidence_ids"))
    for item in analysis.get("charts", []):
        bind_evidence(item.get("lens"), item.get("evidence_ids"))
    for item in analysis.get("kpis", []):
        bind_evidence("overview", item.get("evidence_ids"))
    # Dimension summaries and YoY records are already deterministic answers to
    # their corresponding business lenses.  Do not downgrade an available
    # geography/product/customer lens merely because no diagnostic prose used
    # that evidence yet.
    for lens, evidence_ids in bind_direct_dimension_evidence(
        evidence_index=analysis.get("evidence_index", {}),
        dimension_lenses=dimension_lenses,
    ).items():
        bind_evidence(lens, evidence_ids)
    evidence_ids_by_lens = bind_custom_question_evidence(
        questions=question_plan["questions"], custom_questions=request.analysis_questions,
        evidence_index=analysis["evidence_index"], metric_contracts=analysis["metric_contracts"],
        scope_catalog=scope_registry.export(), legacy_bindings=evidence_ids_by_lens,
    )
    question_plan = reconcile_questions_with_evidence(
        question_plan, evidence_ids_by_lens=evidence_ids_by_lens,
        scope_catalog=scope_registry.export(),
        evidence_index=analysis["evidence_index"],
        insights=_bind_canonical_question_ids(analysis["insights"], questions=question_plan["questions"]),
    )
    question_plan = {
        **question_plan,
        "questions": [
            {
                **question,
                    "status": (
                        "selected"
                        if question.get("answer_status") in {"answered", "partial"}
                        and bool(question.get("evidence_ids"))
                        else "hypothesis"
                    ),
            }
            for question in question_plan["questions"]
        ],
    }
    if execute_followups:
        followup_frame, _, _, _ = prepare_analysis_frame(
            frame, request, retained_periods=list(analysis["periods"]["labels"]),
        )
        followup_result = run_controlled_followups(
            frame=followup_frame,
            questions=question_plan["questions"],
            metric_contracts=analysis["metric_contracts"],
            scope_registry=scope_registry,
            scope_parent_id=analysis["analysis_window_scope_id"],
            existing_evidence_index=analysis["evidence_index"],
            insights=_bind_canonical_question_ids(analysis["insights"], questions=question_plan["questions"]),
        )
        question_plan["questions"] = followup_result["questions"]
        analysis["evidence_index"].update(followup_result["evidence_index"])
        followup_insights, followup_actions = _non_retail_followup_content(
            question_plan["questions"],
            analysis["evidence_index"],
            {
                "adapter_id": final_profile.get("adapter_id"),
                "adapter_maturity": final_profile.get("adapter_maturity"),
                "semantic_contract": semantic_contract,
            },
            allow_unanswered_candidates=True,
        )
        if followup_insights or followup_actions:
            analysis["insights"] = [*analysis["insights"], *followup_insights]
            analysis["actions"] = [*analysis["actions"], *followup_actions]
            analysis.update(enrich_analysis_content(
                evidence_index=analysis["evidence_index"],
                insights=analysis["insights"],
                actions=analysis["actions"],
                row_count=int(len(frame)),
                business_objects=available_objects,
                filter_scope="confirmed semantic filters" if semantic_contract else "loaded source table",
            ))
    else:
        followup_result = {
            "budget": {"max_rounds": 4, "max_total_paths": 12, "max_paths_per_question": 3},
            "executed_path_count": 0,
            "stop_reason": "not_executed_in_finalize",
            "question_stop_reasons": {},
        }
    # Preserve a genuinely action-closed candidate across lens scoping. Final
    # selection below still regrades against only the actions it actually keeps.
    analysis["actions"] = [_prepare_formal_action(item) for item in analysis["actions"]]
    question_plan = reconcile_questions_with_evidence(
        question_plan, evidence_ids_by_lens={str(item["question_id"]): item.get("evidence_ids", []) for item in question_plan["questions"]},
        execution_stop_reasons=followup_result["question_stop_reasons"],
        scope_catalog=scope_registry.export(),
        evidence_index=analysis["evidence_index"],
        insights=_bind_canonical_question_ids(analysis["insights"], questions=question_plan["questions"]),
        actions=analysis["actions"],
    )
    for question in question_plan["questions"]:
        if question.get("answer_status") == "answered":
            question["status"] = "selected"
    final_selected_lenses = {
        str(item["lens"]) for item in question_plan["questions"]
        if item.get("status") == "selected"
    }
    if final_selected_lenses != selected_lenses:
        analysis.update(scope_content_to_lenses(
            evidence_index=analysis["evidence_index"],
            insights=analysis["insights"],
            actions=analysis["actions"],
            charts=analysis["charts"],
            selected_lenses=final_selected_lenses,
            dimension_lenses=dimension_lenses,
            metric_lenses=metric_lenses,
            metric_directions=metric_directions,
        ))
    question_plan, presentation_featured = _select_action_closed_story(
        analysis, question_plan, request=request, scope_catalog=scope_registry.export(),
        execution_stop_reasons=followup_result["question_stop_reasons"],
        management_order=transactional_result is not None and request.analysis_intent == "business_review",
    )

    current_summary = analysis.get("executive_summary", {})
    summary_actions = [
        str(item.get("headline") or item.get("text") or "").rstrip("。")
        for item in analysis["actions"][:2]
    ]
    if current_summary and not engineering_regression:
        analysis["executive_summary"] = {
            **current_summary,
            "priority_actions": summary_actions,
        }
    if transactional_story:
        story_insights = [
            item for item in analysis["insights"]
            if str(item.get("insight_id") or "").startswith("transaction-")
        ][:3]
        story_actions = [
            item for item in analysis["actions"]
            if str(item.get("action_id") or "").startswith("transaction-")
        ][:2]
        if story_insights:
            analysis["judgement_headline"] = str(
                story_insights[0].get("headline") or story_insights[0].get("statement")
            )
            analysis["executive_summary"] = {
                "key_conclusions": [str(item.get("statement") or item.get("headline")) for item in story_insights],
                "key_conclusion_evidence_ids": [list(item.get("evidence_ids", [])) for item in story_insights],
                "priority_actions": [str(item.get("headline") or item.get("text")) for item in story_actions],
            }
            analysis["report_summary"] = "；".join(
                str(item.get("statement") or item.get("headline")).rstrip("。")
                for item in story_insights
            ) + "。"
    _reconcile_executive_summary_with_value_selection(
        analysis,
        engineering_regression=engineering_regression,
        presentation_featured=presentation_featured,
    )
    if transactional_story and presentation_featured:
        primary_finding = presentation_featured[0]
        analysis["judgement_headline"] = str(
            primary_finding.get("headline")
            or primary_finding.get("resolved_answer")
            or primary_finding.get("statement")
            or analysis["judgement_headline"]
        )
    resolved_sheet_name = source_meta.get("sheet_name")
    request_payload = _canonical_seed_request_contract(
        request,
        resolved_sheet_name=resolved_sheet_name,
        resolved_semantic_contract=semantic_contract,
    )
    report_title = str(
        request.report_subject
        or default_report_title(source_path, request)
    )
    if engineering_regression:
        report_title = str(analysis["report_title"])
    report_subtitle = str(
        request.report_subtitle or f"{profile.date_min} 至 {profile.date_max}"
    )
    engineering_qa = None
    if engineering_regression:
        metric_reconciliation = _engineering_metric_reconciliation(
            frame, analysis, request
        )
        if metric_reconciliation["status"] != "passed":
            raise ValueError("工程回归指标复算不一致，停止生成验收材料")
        engineering_qa = {
            "generation_status": "model_ready",
            "acceptance_status": "pending",
            "acceptance_reasons": [
                "尚未建立可比较的历史性能基线",
                "尚未完成独立重复运行稳定性验证",
            ],
            "metric_reconciliation": metric_reconciliation,
            "performance": {
                "baseline_status": "not_established",
                "acceptance_status": "pending",
                "reason": "当前仅记录本次运行观测值，不能据此声明相对性能通过",
            },
            "stability": {
                "status": "not_run",
                "acceptance_status": "pending",
                "reason": "需要在相同输入与环境下完成至少两次独立运行并比对确定性产物",
            },
        }
    quality_decision_records = (
        list(transactional_result.get("quality_decisions", []))
        if isinstance(transactional_result, dict)
        else []
    )
    for record in analysis["evidence_index"].values():
        record["scope_disclosure"] = scope_registry.record(record["scope_id"])["definition"]
    for collection in ("insights", "analysis_chapters", "charts", "actions"):
        for record in analysis.get(collection, []):
            if record_evidence_ids(record):
                scope_registry.bind(record, analysis["evidence_index"])
            elif collection == "analysis_chapters" and record.get("selection_status") != "selected":
                record["scope_id"] = None
                record["scope_disclosure"] = "未获得证据，未作范围内业务判断。"
            else:
                raise ValueError(f"{collection} 记录无证据，不可登记业务范围")
    decision_context = prepare_decision_context(question_plan["questions"], analysis["evidence_index"], scope_registry)
    analysis_brief = build_analysis_brief(
        audience=request.audience,
        report_mode=str(getattr(request, "mode", "professional")),
        objective=request.objective,
        semantic_contract=semantic_contract,
        primary_metrics=request.primary_metrics,
        periods=analysis.get("periods"),
        quality_decisions=quality_decision_records,
    )
    analysis["insights"] = _bind_canonical_question_ids(analysis["insights"], questions=question_plan["questions"])
    model = {
        "schema_version": "2.0",
        "scope_contract_version": SCOPE_VERSION,
        "decision_context": decision_context,
        "scope_catalog": [*scope_registry.export(), *(transactional_result.get("scope_catalog", []) if transactional_result else [])],
        "product_name": "数据分析&汇报小助手",
        "title": report_title,
        "report_title": report_title,
        "report_subtitle": report_subtitle,
        "judgement_headline": analysis["judgement_headline"],
        "executive_summary": analysis["executive_summary"],
        "report_summary": analysis["report_summary"],
        "source": {
            "file_name": source_path.name,
            "source_path": str(source_path.resolve()),
            "sha256": file_sha256(source_path),
            "loaded_row_count": scope_registry.record("source_rows")["included_rows"],
            "file_type": source_path.suffix.lower(),
            "sheet_name": resolved_sheet_name,
        },
        "request": request_payload,
        "data_profile": {**asdict(profile), "source_columns": source_columns},
        "profile": {**asdict(profile), "source_columns": source_columns},
        **(
            {
                "engineered_profile": asdict(engineered_profile),
                "engineering_qa": engineering_qa,
            }
            if engineering_regression
            else {}
        ),
        "metric_contracts": analysis["metric_contracts"],
        "analysis_profile": analysis["analysis_profile"],
        "analysis_contract": {
            "analysis_intent": str(getattr(request, "analysis_intent", "business_review")),
            "semantic_contract": semantic_contract,
            "adapter_id": final_profile.get("adapter_id"),
            "adapter_maturity": final_profile.get("adapter_maturity"),
            "execution_profile": final_profile.get("resolved"),
            "adapter_selection_reason": final_profile.get("adapter_selection_reason"),
            "available_objects": sorted(available_objects),
            "followup_policy": {
                "budget": followup_result["budget"],
                "executed_path_count": followup_result["executed_path_count"],
                "stop_reason": followup_result["stop_reason"],
                "question_stop_reasons": followup_result["question_stop_reasons"],
            },
        },
        "analysis_brief": analysis_brief,
        "candidate_question_graph": candidate_question_graph,
        "quality_decisions": quality_decision_records,
        "question_selection_decision": {
            "missing_requirements": candidate_question_graph["missing_requirements"],
            "selected_question_ids": candidate_question_graph.get("selected_question_ids", []),
            "rejected_question_ids": candidate_question_graph.get("rejected_question_ids", []),
        },
        "analysis_lenses": question_plan["questions"],
        "analysis_chapters": analysis.get("analysis_chapters", []),
        **({"transactional_commerce": {
            key: value for key, value in transactional_result.items() if key != "prepared_frame"
        }} if transactional_result else {}),
        "periods": analysis["periods"],
        "kpis": analysis["kpis"],
        "period_overview": analysis["period_overview"],
        "latest_snapshot": analysis["latest_snapshot"],
        "metrics": analysis["metrics"],
        "dimensions": analysis["dimensions"],
        "findings": analysis["findings"],
        "insights": analysis["insights"],
        "featured_insight_ids": analysis.get("featured_insight_ids", []),
        "appendix_insight_ids": analysis.get("appendix_insight_ids", []),
        "actions": analysis["actions"],
        "levers": analysis["levers"],
        "charts": analysis["charts"],
        "evidence_index": analysis["evidence_index"],
        "value_selection": analysis["value_selection"],
        "slide_plan": [],
        "slide_outline": [],
        "validation": {
            "model": {"status": "pending"},
            "warnings": list(dict.fromkeys([*analysis["warnings"], *profile.warnings])),
            "html": {"status": "pending", "self_contained": True},
            "pptx": {
                "status": "pending",
                "visual_review": {
                    "status": "not_run",
                    "required_for_public_demo": True,
                    "method": "逐页渲染或在 PowerPoint 中逐页检查",
                },
                "font_gate": {
                    "cover_title_min_pt": 50,
                    "slide_title_min_pt": 35,
                    "subheading_min_pt": 24,
                    "body_min_pt": 16,
                    "footnote_min_pt": 10,
                    "status": "pending",
                },
            },
            "slideviber": {"status": "not_requested"},
        },
    }
    model["slide_plan"] = build_slide_plan(model)
    model["slide_outline"] = model["slide_plan"]
    if (
        enforce_narrative
        and not engineering_regression
        and not _has_answered_or_partial_evidence(model)
    ):
        raise InsufficientEvidenceError(
            intent=str(getattr(request, "analysis_intent", "business_review")),
        )
    if engineering_regression:
        _qa_slide_copy(model)
        model["content_validation"] = {
            "status": "passed", "blocking": [], "warnings": [],
            "narrative_validation": {"status": "not_applicable"},
        }
        validate_report_model(model, enforce_narrative=False)
    elif not enforce_narrative:
        # Analyse-only validates source/request/evidence/question/value gates,
        # but intentionally leaves narrative coverage to finalization.
        validate_analysis_evidence_model(model)
        model["content_validation"] = {
            "status": "passed", "blocking": [], "warnings": [],
            "validation_scope": "analysis_evidence_only",
            "narrative_validation": {"status": "not_finalized"},
        }
    else:
        narrative_validation = build_narrative_validation(model["slide_plan"], model)
        # Content QA consumes this deterministic disposition before producing the
        # persisted validation result; it does not infer coverage from statements.
        model["content_validation"] = {"narrative_validation": narrative_validation}
        model["content_validation"] = validate_content_value(model)
        model["content_validation"]["narrative_validation"] = narrative_validation
        if not any(page.get("story_role") in {"action", "decision"} for page in model["slide_plan"]):
            raise InsufficientEvidenceError(intent=str(getattr(request, "analysis_intent", "business_review")))
        validate_report_model(model, enforce_narrative=True)
    model["validation"]["model"] = {"status": "passed"}
    return model


def _request_fingerprint(request_payload: dict) -> str:
    """Hash the resolved request so a story cannot cross analysis inputs."""

    return canonical_sha256(request_payload)


def _artifact_sha256(payload: dict) -> str:
    return canonical_sha256(payload)


def _locked_adaptive_content(model: dict) -> dict:
    """Return the analysis-stage objects that finalization must not rewrite."""

    selection = model.get("value_selection", {})
    return {
        "scope_contract": scope_lock_projection(model),
        "analysis_lenses": copy.deepcopy(model.get("analysis_lenses", [])),
        "analysis_chapters": copy.deepcopy(model.get("analysis_chapters", [])),
        "content_validation": copy.deepcopy(content_validation_lock_value(model.get("content_validation"))),
        "featured_insight_ids": [
            str(item.get("insight_id") or "")
            for item in selection.get("featured", [])
            if isinstance(item, dict)
        ],
        "appendix_insight_ids": [
            str(item.get("insight_id") or "")
            for item in selection.get("appendix", [])
            if isinstance(item, dict)
        ],
        "non_retail_projection": copy.deepcopy(build_non_retail_projection(model)),
        "renderer_content": copy.deepcopy(renderer_content_lock_projection(model)),
    }


def _locked_slide_content(page: dict) -> dict:
    """Project a page's immutable semantic object without its presentation order."""

    return {
        key: copy.deepcopy(page.get(key))
        for key in sorted(LOCKED_SLIDE_KEYS)
    }


def _build_content_lock(model: dict) -> dict:
    """Hash analysis content once; page order deliberately remains outside the lock."""

    adaptive = _locked_adaptive_content(model)
    slides = {
        str(page.get("slide_id") or ""): _locked_slide_content(page)
        for page in model.get("slide_plan", [])
    }
    adaptive_hashes = {
        key: _artifact_sha256(value) for key, value in adaptive.items()
    }
    slide_hashes = {
        slide_id: _artifact_sha256(value) for slide_id, value in slides.items()
    }
    return {
        "adaptive_hashes": adaptive_hashes,
        "slide_hashes": slide_hashes,
        "content_hash": _artifact_sha256(
            {"adaptive_hashes": adaptive_hashes, "slide_hashes": slide_hashes}
        ),
    }


def _content_lock_violation(field: str) -> StructuredPipelineError:
    return StructuredPipelineError(
        "content_lock_violation",
        f"content_lock_violation: {field} 不可脱离 analysis_evidence 重写",
        details={"field": field},
    )


def _validate_story_content_lock(evidence: dict, story_plan: dict, seed: dict) -> None:
    """Reject any semantic drift while allowing only a legal page ordering change."""

    content_lock = evidence.get("content_lock")
    if not isinstance(content_lock, dict) or content_lock != _build_content_lock(seed):
        raise ValueError("analysis_evidence content_lock 无效")
    if story_plan.get("content_lock") != content_lock:
        raise _content_lock_violation("content_lock")
    expected_adaptive = _locked_adaptive_content(seed)
    for key in sorted(LOCKED_ADAPTIVE_KEYS):
        if story_plan.get(key) != expected_adaptive[key]:
            raise _content_lock_violation(key)
    planned_pages = story_plan.get("pages")
    if not isinstance(planned_pages, list):
        raise ValueError("story_plan_invalid: pages 必须是列表")
    canonical_pages = {
        str(page.get("slide_id") or ""): page for page in seed.get("slide_plan", [])
    }
    planned_ids = [
        str(page.get("slide_id") or "") if isinstance(page, dict) else ""
        for page in planned_pages
    ]
    if (
        len(planned_ids) != len(set(planned_ids))
        or not planned_ids
        or set(planned_ids) != set(canonical_pages)
    ):
        raise _content_lock_violation("slide_id")
    for page in planned_pages:
        if not isinstance(page, dict):
            raise ValueError("story_plan_invalid: page 必须是对象")
        slide_id = str(page.get("slide_id") or "")
        canonical = canonical_pages[slide_id]
        for key in sorted(LOCKED_SLIDE_KEYS):
            if page.get(key) != canonical.get(key):
                raise _content_lock_violation(f"{slide_id}.{key}")
        if content_lock["slide_hashes"].get(slide_id) != _artifact_sha256(
            _locked_slide_content(page)
        ):
            raise _content_lock_violation(f"{slide_id}.hash")


def structured_failure_payload(exc: Exception, *, finalizing: bool = False) -> dict:
    """Return stable, machine-readable failures for CLI and pipeline callers."""

    message = str(exc)
    if isinstance(exc, StructuredPipelineError):
        return {
            "status": "failed",
            "error_code": exc.error_code,
            "message": message,
            "details": exc.details,
            "recoverable": False,
        }
    if isinstance(exc, InsufficientEvidenceError):
        return {
            "status": "failed",
            "error_code": "evidence_insufficient",
            "message": message,
            "details": {"analysis_intent": exc.result.get("analysis_intent")},
            "recoverable": False,
        }
    if "semantic_ambiguity" in message:
        error_code = "semantic_ambiguity"
    elif "adapter" in message and "unavailable" in message:
        error_code = "adapter_unavailable"
    elif "content_lock_violation" in message:
        error_code = "content_lock_violation"
    elif finalizing or "story_plan_invalid" in message:
        error_code = "story_plan_invalid"
    else:
        error_code = "pipeline_failed"
    return {
        "status": "failed",
        "error_code": error_code,
        "message": message,
        "details": {},
        "recoverable": False,
    }


def build_analysis_evidence(request: ReportRequest) -> dict:
    """Build deterministic evidence without creating report artifacts."""

    # Analysis must be deterministic and available even when the evidence is
    # too sparse to authorize a business narrative.  Finalization enforces
    # the narrative page gate before any rendering starts.
    model = build_report_model(request, enforce_narrative=False)
    analysis_request = _canonical_analysis_request_contract(
        request,
        resolved_source_path=model["source"]["source_path"],
        resolved_sheet_name=model["request"].get("sheet_name"),
        resolved_semantic_contract=model["request"].get("semantic_contract"),
    )
    evidence = {
        "schema_version": "2.0",
        "analysis_evidence_version": "0.2",
        "scope_contract_version": model["scope_contract_version"],
        "scope_catalog": copy.deepcopy(model["scope_catalog"]),
        "source_sha256": model["source"]["sha256"],
        "request_fingerprint": _request_fingerprint(analysis_request),
        # Finalization consumes this analysis artifact only; it never touches
        # source rows or recomputes analysis after analyse-only completes.
        "analysis_request": analysis_request,
        "analysis_contract": copy.deepcopy(model["analysis_contract"]),
        "analysis_brief": copy.deepcopy(model["analysis_brief"]),
        "candidate_question_graph": copy.deepcopy(model["candidate_question_graph"]),
        "quality_decisions": copy.deepcopy(model["quality_decisions"]),
        "analysis_lenses": copy.deepcopy(model["analysis_lenses"]),
        "analysis_chapters": copy.deepcopy(model["analysis_chapters"]),
        "value_selection": copy.deepcopy(model["value_selection"]),
        "evidence_catalog": copy.deepcopy(model["evidence_index"]),
        "non_retail_projection": copy.deepcopy(build_non_retail_projection(model)),
        # This seed is internal deterministic analysis state, not a second
        # narrative truth. Finalization may only select its IDs and order.
        "report_seed": copy.deepcopy(model),
        "finalize_seed": copy.deepcopy(model),
        "finalize_seed_sha256": _artifact_sha256(model),
        "content_lock": _build_content_lock(model),
    }
    validate_analysis_evidence_artifact(evidence)
    return evidence


def _compile_decision_story(evidence: dict, proposals: list) -> dict:
    """Compose a derived story; immutable input evidence remains the authority."""
    from analysis_scope import bind_existing_scope

    seed = copy.deepcopy(evidence["finalize_seed"])
    insights, actions = compile_decision_proposals(seed, proposals)
    seed.pop("content_lock", None)
    seed["decision_proposals"] = copy.deepcopy(proposals)
    seed["insights"].extend(insights)
    seed["actions"].extend(actions)
    request = _request_from_analysis_snapshot(evidence["analysis_request"])
    plan = {"questions": seed["analysis_lenses"]}
    plan, featured = _select_action_closed_story(seed, plan, request=request, scope_catalog=seed["scope_catalog"],
        execution_stop_reasons=seed["analysis_contract"].get("followup_policy", {}).get("question_stop_reasons", {}),
        management_order=bool(seed.get("transactional_commerce")))
    seed["analysis_lenses"] = plan["questions"]
    for collection in ("insights", "analysis_chapters", "charts", "actions"):
        for record in seed.get(collection, []):
            if record_evidence_ids(record):
                bind_existing_scope(record, seed["evidence_index"], seed["scope_catalog"])
            elif collection != "analysis_chapters" or record.get("selection_status") == "selected":
                raise ValueError("decision_proposal: business content lacks evidence")
    _reconcile_executive_summary_with_value_selection(seed, engineering_regression=False, presentation_featured=featured)
    if featured:
        seed["judgement_headline"] = str(featured[0].get("headline") or featured[0].get("resolved_answer") or featured[0]["statement"])
    seed["slide_plan"] = build_slide_plan(seed)
    seed["slide_outline"] = seed["slide_plan"]
    narrative = build_narrative_validation(seed["slide_plan"], seed)
    seed["content_validation"] = {"narrative_validation": narrative}
    seed["content_validation"] = validate_content_value(seed)
    seed["content_validation"]["narrative_validation"] = narrative
    validate_report_model(seed)
    return seed


def build_story_plan(evidence: dict, *, decision_proposals: list | None = None) -> dict:
    """Return the deterministic default story plan as reference-only pages."""

    validate_analysis_evidence_artifact(evidence)
    seed = evidence.get("finalize_seed")
    if not isinstance(seed, dict):
        raise ValueError("analysis_evidence 缺少 finalize_seed")
    if decision_proposals is not None:
        seed = _compile_decision_story(evidence, decision_proposals)
    adaptive = _locked_adaptive_content(seed)
    return {
        "schema_version": "2.0",
        "source_sha256": evidence.get("source_sha256"),
        "request_fingerprint": evidence.get("request_fingerprint"),
        **copy.deepcopy(adaptive),
        "content_lock": _build_content_lock(seed) if decision_proposals is not None else copy.deepcopy(evidence.get("content_lock")),
        **({"decision_proposals": copy.deepcopy(decision_proposals),
            "base_content_hash": evidence["content_lock"]["content_hash"]} if decision_proposals is not None else {}),
        "pages": [
            _locked_slide_content(page)
            for page in seed.get("slide_plan", [])
        ],
    }


def finalize_model_from_story_plan(evidence: dict, story_plan: dict) -> dict:
    """Strictly bind a story plan to its analysis evidence before rendering."""

    if evidence.get("contract_version") == "html-chapters/1":
        from html_analysis import compose, check_binding
        check_binding(evidence, story_plan)
        model = compose(evidence, story_plan["proposal"])
        if model["sha256"] != story_plan["model_sha256"]:
            raise ValueError("HTML 章节内容锁不匹配")
        return model

    if not isinstance(story_plan, dict):
        raise ValueError("story_plan 必须是对象")
    for key in ("source_sha256", "request_fingerprint", "pages", "content_lock", *LOCKED_ADAPTIVE_KEYS):
        if key not in story_plan:
            raise ValueError(f"story_plan 缺少 {key}")
    if story_plan["source_sha256"] != evidence.get("source_sha256"):
        raise ValueError("story_plan source_sha256 与 analysis_evidence 不一致")
    if story_plan["request_fingerprint"] != evidence.get("request_fingerprint"):
        raise ValueError("story_plan request_fingerprint 与 analysis_evidence 不一致")
    validate_analysis_evidence_artifact(evidence)
    seed = evidence.get("finalize_seed")
    if not isinstance(seed, dict) or _artifact_sha256(seed) != evidence.get("finalize_seed_sha256"):
        raise ValueError("analysis_evidence finalize_seed 无效")
    if seed.get("source", {}).get("sha256") != evidence.get("source_sha256"):
        raise ValueError("analysis_evidence source_sha256 绑定无效")
    seed = copy.deepcopy(seed)
    if "decision_proposals" in story_plan:
        if story_plan.get("base_content_hash") != evidence["content_lock"]["content_hash"]:
            raise _content_lock_violation("base_content_hash")
        seed = _compile_decision_story(evidence, story_plan["decision_proposals"])
        # Only this local derived view receives a new lock. The supplied base
        # artifact has already been validated and is never rewritten.
        evidence = {**evidence, "content_lock": _build_content_lock(seed)}
    _validate_story_content_lock(evidence, story_plan, seed)
    planned_pages = story_plan["pages"]
    canonical_pages = {page["slide_id"]: page for page in seed.get("slide_plan", [])}
    planned_ids = [page.get("slide_id") for page in planned_pages]
    engineering_dossier = str(seed.get("request", {}).get("analysis_intent") or "") == "engineering_regression"
    if not engineering_dossier and not _has_answered_or_partial_evidence(seed):
        raise InsufficientEvidenceError(intent=str(seed.get("request", {}).get("analysis_intent") or "business_review"))
    if not engineering_dossier and not canonical_pages:
        raise InsufficientEvidenceError(intent=str(seed.get("request", {}).get("analysis_intent") or "business_review"))
    if (
        not engineering_dossier
        and str(seed.get("request", {}).get("analysis_intent") or "business_review") == "business_review"
        and "analysis_chapters" in seed
        and not any(chapter.get("selection_status") == "selected" for chapter in seed["analysis_chapters"])
    ):
        raise InsufficientEvidenceError(intent="business_review")
    if not engineering_dossier:
        validate_story_topology(planned_pages)
    canonical_layouts = {
        str(page.get("layout_id") or "")
        for page in canonical_pages.values()
    }
    if engineering_dossier:
        required_layouts = {"cover", "executive-summary", "data-appendix"}
    else:
        required_layouts = {"cover"}
        for layout in ("executive-summary", "action-roadmap"):
            if layout in canonical_layouts:
                required_layouts.add(layout)
    planned_layouts = {canonical_pages[slide_id]["layout_id"] for slide_id in planned_ids}
    if not required_layouts <= planned_layouts:
        raise ValueError("story_plan 缺少必需页面角色")
    if not engineering_dossier and not any(canonical_pages[slide_id].get("evidence_ids") for slide_id in planned_ids):
        raise ValueError("story_plan 至少需要一页有证据的分析页面")
    ordered_pages = [copy.deepcopy(canonical_pages[page["slide_id"]]) for page in planned_pages]
    model = copy.deepcopy(seed)
    model["slide_plan"] = ordered_pages
    model["slide_outline"] = ordered_pages
    model["content_lock"] = copy.deepcopy(evidence["content_lock"])
    if not engineering_dossier:
        # Final-only narrative validation is derived after the analysis lock
        # has already been verified. Its diagnostic details stay out of the
        # content-validation lock projection, so legal ordering does not alter
        # the analysis-stage content hash.
        narrative_validation = build_narrative_validation(ordered_pages, model)
        model["content_validation"] = {"narrative_validation": narrative_validation}
        model["content_validation"] = validate_content_value(model)
        model["content_validation"]["narrative_validation"] = narrative_validation
        if not _has_answered_or_partial_evidence(model) or not any(
            page.get("story_role") in {"action", "decision"} for page in ordered_pages
        ):
            raise InsufficientEvidenceError(intent=str(model.get("request", {}).get("analysis_intent") or "business_review"))
    validate_report_model(model)
    return model


def _request_from_analysis_snapshot(payload: dict) -> ReportRequest:
    """Rebuild a resolved request without rerunning interactive preflight."""

    required = (
        "source_path", "period_type", "audience", "objective", "date_column",
        "primary_metrics",
    )
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise ValueError("analysis_request 缺少：" + ", ".join(missing))
    request = ReportRequest(
        source_path=Path(str(payload["source_path"])).resolve(),
        period_type=str(payload["period_type"]),
        audience=str(payload["audience"]),
        objective=str(payload["objective"]),
        date_column=str(payload["date_column"]),
        primary_metrics=tuple(payload["primary_metrics"]),
        dimensions=tuple(payload.get("dimensions", [])),
        output_mode=str(payload.get("output_mode", "report")),
        mode=str(payload.get("mode", "professional")),
        sheet_name=payload.get("sheet_name"),
        metric_contracts=tuple(copy.deepcopy(payload.get("metric_contracts", []))),
        comparisons=tuple(payload.get("comparisons", ["period_over_period", "year_over_year"])),
        week_start=str(payload.get("week_start", "monday")),
        timezone=str(payload.get("timezone", "Asia/Shanghai")),
        incomplete_period_policy=str(payload.get("incomplete_period_policy", "exclude")),
        theme=str(payload.get("theme", "clean")),
        ppt_refinement=str(payload.get("ppt_refinement", "offer_slideviber")),
        analysis_profile=str(payload.get("analysis_profile", "auto")),
        report_subject=payload.get("report_subject"),
        report_subtitle=payload.get("report_subtitle"),
        duplicate_policy=str(payload.get("duplicate_policy", "keep")),
        numeric_error_policy=str(payload.get("numeric_error_policy", "fail")),
        allow_sensitive_fields=bool(payload.get("allow_sensitive_fields", False)),
        preflight=copy.deepcopy(payload.get("input_resolution")),
        analysis_intent=str(payload.get("analysis_intent", "business_review")),
        semantic_contract=copy.deepcopy(payload.get("semantic_contract")),
        analysis_questions=validate_analysis_questions(payload.get("analysis_questions")),
    )
    validate_request(request)
    return request


def _validate_root_request_binding(request_payload: dict, seed: dict) -> None:
    """Rebuild the production request contract before accepting an artifact seed."""

    seed_request = seed.get("request")
    if not isinstance(seed_request, dict):
        raise ValueError("analysis_evidence finalize_seed request 无效")
    request = _request_from_analysis_snapshot(request_payload)
    columns = seed.get("data_profile", {}).get("columns", [])
    source_columns = seed.get("data_profile", {}).get("source_columns", columns)
    semantic_result = resolve_request_semantic_contract(
        request, source_columns=source_columns,
        metric_dependencies={contract["name"]: required_source_fields(contract)
                             for contract in normalize_metric_contracts(request)},
    )
    if semantic_result.get("status") != "ready":
        raise ValueError("analysis_evidence root semantic_contract 无法按生产规则解析")
    semantic_contract = semantic_result.get("contract")
    if semantic_contract is not None and not isinstance(semantic_contract, dict):
        raise ValueError("analysis_evidence root semantic_contract 无效")

    expected_seed_request = _canonical_seed_request_contract(
        request,
        resolved_sheet_name=request.sheet_name,
        resolved_semantic_contract=semantic_contract,
    )
    expected_root_request = _canonical_analysis_request_contract(
        request,
        resolved_source_path=request.source_path,
        resolved_sheet_name=request.sheet_name,
        resolved_semantic_contract=semantic_contract,
    )
    if _artifact_sha256(request_payload) != _artifact_sha256(expected_root_request):
        raise ValueError("analysis_evidence root request canonical contract 无效")
    if _artifact_sha256(seed_request) != _artifact_sha256(expected_seed_request):
        raise ValueError(
            "analysis_evidence root request canonical contract 与 finalize_seed.request 不一致"
        )

    source = seed.get("source")
    if not isinstance(source, dict):
        raise ValueError("analysis_evidence finalize_seed source 无效")
    source_path = Path(request.source_path).resolve()
    expected_source_binding = {
        "source_path": str(source_path),
        "file_name": source_path.name,
        "file_type": source_path.suffix.lower(),
        "sheet_name": request.sheet_name,
    }
    for key, value in expected_source_binding.items():
        if source.get(key) != value:
            raise ValueError(
                f"analysis_evidence root request canonical contract source.{key} 不一致"
            )

    expected_metric_contracts = normalize_metric_contracts(
        request, {str(value) for value in columns}
    )
    seed_metric_contracts = seed.get("metric_contracts")
    if (
        not isinstance(seed_metric_contracts, list)
        or _artifact_sha256(seed_metric_contracts)
        != _artifact_sha256(expected_metric_contracts)
    ):
        raise ValueError(
            "analysis_evidence root request canonical contract metric_contracts 不一致"
        )

    profile = resolve_analysis_profile(request, expected_metric_contracts)
    if seed.get("analysis_profile") != profile:
        raise ValueError("analysis_evidence root request analysis_profile 与生产解析不一致")
    contract = seed.get("analysis_contract")
    if not isinstance(contract, dict):
        raise ValueError("analysis_evidence finalize_seed analysis_contract 无效")
    expected_contract = {
        "adapter_id": profile.get("adapter_id"),
        "adapter_maturity": profile.get("adapter_maturity"),
        "execution_profile": profile.get("resolved"),
        "adapter_selection_reason": profile.get("adapter_selection_reason"),
        "semantic_contract": semantic_contract,
    }
    expected_objects = canonical_available_objects(
        primary_metrics=request.primary_metrics,
        dimensions=request.dimensions,
        semantic_contract=semantic_contract,
        available_fields={str(value) for value in columns},
    )
    expected_contract["available_objects"] = sorted(expected_objects)
    for key, value in expected_contract.items():
        if contract.get(key) != value:
            raise ValueError(
                f"analysis_evidence root request analysis_contract.{key} 与生产解析不一致"
            )
    lenses = seed.get("analysis_lenses")
    if not isinstance(lenses, list):
        raise ValueError("analysis_evidence finalize_seed analysis_lenses 无效")
    by_question_id = {str(item.get("question_id") or ""): item for item in lenses if isinstance(item, dict)}
    static_plan = canonical_analysis_question_contract(
        analysis_intent=str(getattr(request, "analysis_intent", "business_review")),
        audience=request.audience,
        objective=request.objective,
        semantic_contract=semantic_contract,
        available_fields={str(value) for value in columns},
        available_objects=expected_objects,
        available_metrics={
            *[str(value) for value in request.primary_metrics],
            *[str(item["metric_id"]) for item in request.metric_contracts
              if item.get("metric_id") and item.get("name") in request.primary_metrics],
        },
        period_count=len(seed.get("periods", {}).get("labels", [])),
        custom_questions=list(request.analysis_questions),
    )
    static_plan = enrich_question_graph_with_preliminary_scan(
        static_plan,
        analysis=seed,
    )
    runtime_fields = {
        "status", "answer_status", "answer_text", "resolved_answer", "evidence_ids",
        "followup_trace", "stop_reason", "missing_requirements", "selection_reasons",
        "achieved_depth", "depth_gaps",
    }
    expected_static = [
        {key: value for key, value in question.items() if key not in runtime_fields}
        for question in static_plan["questions"]
    ]
    actual_static = [
        {key: value for key, value in question.items() if key not in runtime_fields}
        for question in lenses
    ]
    if actual_static != expected_static:
        raise ValueError("analysis_evidence root analysis_lenses 静态合同与生产解析不一致")
    for question in request.analysis_questions:
        question_id = str(question.get("question_id") or "")
        actual = by_question_id.get(question_id)
        if not isinstance(actual, dict):
            raise ValueError("analysis_evidence root custom analysis_questions 未生成实际 lens")
        for key in ("question_id", "lens", "business_question", "required_objects", "required_metrics", "required_fields", "dimensions"):
            if key in question and actual.get(key) != question.get(key):
                raise ValueError("analysis_evidence root custom analysis_questions 与实际 lens 不一致")


def write_analysis_evidence(evidence: dict, output_dir: Path) -> AnalysisArtifacts:
    """Persist the analysis-stage output without touching report artifacts."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = output_dir / "analysis_evidence.json"
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest_path = output_dir / "analysis_result.json"
    manifest_path.write_text(
        json.dumps({
            "status": "passed", "source_sha256": evidence["source_sha256"],
            "request_fingerprint": evidence["request_fingerprint"], "artifacts": ["analysis_evidence.json"],
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return AnalysisArtifacts(evidence_path=evidence_path, manifest_path=manifest_path)


def run_analysis_only(request: ReportRequest, output_dir: Path) -> AnalysisArtifacts:
    return write_analysis_evidence(build_analysis_evidence(request), output_dir)


def compose_story_from_decisions(output_dir: Path, proposals_path: Path) -> Path:
    """Write a validated derived plan only; never render or overwrite a plan."""
    output_dir = Path(output_dir)
    destination = output_dir / "story_plan.json"
    if destination.exists():
        raise ValueError("decision_proposal: story_plan.json already exists; preserve it and choose a new output directory")
    evidence = json.loads((output_dir / "analysis_evidence.json").read_text(encoding="utf-8"))
    proposals = json.loads(Path(proposals_path).read_text(encoding="utf-8"))
    story = build_story_plan(evidence, decision_proposals=proposals)
    payload = json.dumps(story, ensure_ascii=False, indent=2)
    # Exclusive creation preserves an existing plan even if another writer
    # creates it during validation.
    with destination.open("x", encoding="utf-8") as stream:
        stream.write(payload)
    return destination


def finalize_from_story_plan(output_dir: Path, story_plan_path: Path) -> PipelineArtifacts:
    output_dir = Path(output_dir)
    evidence_path = output_dir / "analysis_evidence.json"
    if not evidence_path.exists():
        raise ValueError("--finalize 需要 output/analysis_evidence.json")
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    story_plan = json.loads(Path(story_plan_path).read_text(encoding="utf-8"))
    return run_model_pipeline(finalize_model_from_story_plan(evidence, story_plan), output_dir)


def render_html(model: dict, output_path: Path) -> None:
    render_html_v2(model, output_path)


def render_pptx(model: dict, output_path: Path) -> None:
    # The native builder validates first.  Project marked legacy models here
    # so PPT follows the same legacy-to-content-refs boundary as HTML/handoff.
    projected = project_legacy_content_refs(model)
    if model.get("legacy_content_refs_fixture") is True:
        role_by_layout = {
            "cover": "cover", "executive-summary": "executive_summary",
            "kpi-spotlight": "baseline", "trend-wide": "driver",
            "chart-insight-action": "driver", "chart-side-kpi": "driver",
            "driver-levers": "driver", "risk-opportunity": "risk",
            "action-roadmap": "action", "data-appendix": "appendix",
        }
        for page in projected.get("slide_plan", []):
            page.setdefault("role", str(page.get("layout_id") or ""))
            page.setdefault("page_reason", "legacy content refs projection")
            page.setdefault("selection_score", 0)
            page.setdefault("story_role", role_by_layout.get(str(page.get("layout_id")), "driver"))
    build_pptx_v2(projected, output_path)


def render_slideviber_handoff(model: dict, output_path: Path) -> None:
    render_slideviber_handoff_v2(model, output_path)


def run_pipeline(request: ReportRequest, output_dir: Path) -> PipelineArtifacts:
    """Run the one-click path through the same locked two-stage contract."""

    performance_started_at = time.perf_counter()
    evidence = build_analysis_evidence(request)
    story_plan = build_story_plan(evidence)
    model = finalize_model_from_story_plan(evidence, story_plan)
    return run_model_pipeline(
        model,
        output_dir,
        _performance_started_at=performance_started_at,
    )


def _process_memory_observation() -> dict:
    """Read Windows process working-set counters without tracing every allocation."""

    if os.name != "nt":
        return {
            "working_set_bytes": 0,
            "peak_process_working_set_bytes": 0,
            "memory_scope": "not_available_on_platform",
        }

    from ctypes import wintypes

    class ProcessMemoryCounters(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    counters = ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    get_current_process = ctypes.windll.kernel32.GetCurrentProcess
    get_current_process.restype = wintypes.HANDLE
    get_process_memory_info = ctypes.windll.psapi.GetProcessMemoryInfo
    get_process_memory_info.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(ProcessMemoryCounters),
        wintypes.DWORD,
    ]
    get_process_memory_info.restype = wintypes.BOOL
    process = get_current_process()
    success = get_process_memory_info(
        process, ctypes.byref(counters), counters.cb
    )
    if not success:
        return {
            "working_set_bytes": 0,
            "peak_process_working_set_bytes": 0,
            "memory_scope": "windows_process_counters_unavailable",
        }
    return {
        "working_set_bytes": int(counters.WorkingSetSize),
        "peak_process_working_set_bytes": int(counters.PeakWorkingSetSize),
        "memory_scope": "windows_process_working_set",
    }


def _promote_outputs_transactionally(
    staging_dir: Path, output_dir: Path, current_names: set[str]
) -> None:
    """Promote a complete managed bundle or restore the previous bundle."""

    output_dir.mkdir(parents=True, exist_ok=True)
    backup_dir = Path(
        tempfile.mkdtemp(prefix=f".{output_dir.name}.backup-", dir=output_dir.parent)
    )
    existing_names = {
        name for name in MANAGED_OUTPUTS if (output_dir / name).is_file()
    }
    try:
        # Finish a complete backup before the first externally visible write.
        for name in sorted(existing_names):
            shutil.copy2(output_dir / name, backup_dir / name)
        for name in sorted(current_names):
            os.replace(staging_dir / name, output_dir / name)
        for name in sorted(MANAGED_OUTPUTS - current_names):
            stale_path = output_dir / name
            if stale_path.exists():
                stale_path.unlink()
    except Exception:
        rollback_errors: list[str] = []
        for name in sorted(MANAGED_OUTPUTS):
            target = output_dir / name
            try:
                if target.exists():
                    target.unlink()
            except OSError as exc:
                rollback_errors.append(f"remove {name}: {exc}")
        for name in sorted(existing_names):
            try:
                os.replace(backup_dir / name, output_dir / name)
            except OSError as exc:
                rollback_errors.append(f"restore {name}: {exc}")
        if rollback_errors:
            raise RuntimeError("输出提升失败且回滚不完整：" + "; ".join(rollback_errors))
        raise
    finally:
        shutil.rmtree(backup_dir, ignore_errors=True)


def run_model_pipeline(
    model: dict,
    output_dir: Path,
    *,
    _performance_started_at: float | None = None,
) -> PipelineArtifacts:
    performance_started_at = _performance_started_at or time.perf_counter()
    output_dir = Path(output_dir)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging_dir = Path(
        tempfile.mkdtemp(prefix=f".{output_dir.name}.staging-", dir=output_dir.parent)
    )
    current_stage = "render_html"
    previous_success_manifest = False
    previous_manifest_path = output_dir / "run_result.json"
    if previous_manifest_path.is_file():
        try:
            previous_success_manifest = (
                json.loads(previous_manifest_path.read_text(encoding="utf-8")).get("status")
                == "passed"
            )
        except (OSError, ValueError, TypeError):
            previous_success_manifest = False
    try:
        model_path = staging_dir / "report_model.json"
        html_path = staging_dir / "report.html"
        current_stage = "render_html"
        render_html(model, html_path)
        current_stage = "qa_html"
        html_qa_result = qa_html(html_path, model)
        html_qa_path = staging_dir / "html_qa.json"
        html_qa_path.write_text(
            json.dumps(html_qa_result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        if html_qa_result["status"] != "passed":
            raise ValueError(
                f"HTML QA 未通过：{json.dumps(html_qa_result, ensure_ascii=False)}"
            )
        model["validation"]["html"] = html_qa_result
        artifact_names = ["report_model.json", "report.html", "html_qa.json"]
        pptx_path = None
        pptx_qa_path = None
        slideviber_handoff_path = None
        if "pptx" in str(model["request"].get("output_mode", "report")):
            current_stage = "render_pptx"
            pptx_path = staging_dir / "report.pptx"
            render_pptx(model, pptx_path)
            current_stage = "qa_pptx"
            qa = qa_pptx(pptx_path, model)
            pptx_qa_path = staging_dir / "ppt_qa.json"
            pptx_qa_path.write_text(
                json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            if qa["status"] != "passed":
                raise ValueError(f"PPT QA 未通过：{json.dumps(qa, ensure_ascii=False)}")
            model["validation"]["pptx"]["status"] = "passed"
            model["validation"]["pptx"]["font_gate"]["status"] = "passed"
            artifact_names.extend(["report.pptx", "ppt_qa.json"])
            if model["request"].get("ppt_refinement") == "offer_slideviber":
                current_stage = "render_slideviber_handoff"
                slideviber_handoff_path = staging_dir / "slideviber_handoff.md"
                model["validation"]["slideviber"] = {
                    "status": "handoff_ready",
                    "qa_required": True,
                    "checker": "scripts/slideviber_consistency.py",
                    "polished_output": "report-polished.pptx",
                    "qa_output": "slideviber_qa.json",
                }
                render_slideviber_handoff(model, slideviber_handoff_path)
                artifact_names.append("slideviber_handoff.md")

        model_path.write_text(
            json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        performance_observation = {
            "duration_seconds": round(time.perf_counter() - performance_started_at, 6),
            **_process_memory_observation(),
        }
        manifest = {
            "status": "passed",
            "status_scope": "artifact_generation_and_machine_render_qa",
            "generation_status": "passed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "source_sha256": model["source"]["sha256"],
            "mode": model["request"].get("mode"),
            "output_mode": model["request"].get("output_mode"),
            "artifacts": artifact_names,
            "validation": model["validation"],
            "performance_observation": performance_observation,
            **(
                {
                    "engineering_acceptance": {
                        "status": model.get("engineering_qa", {}).get(
                            "acceptance_status", "pending"
                        ),
                        "reasons": model.get("engineering_qa", {}).get(
                            "acceptance_reasons", []
                        ),
                    }
                }
                if str(model.get("request", {}).get("analysis_intent") or "")
                == "engineering_regression"
                else {}
            ),
        }
        (staging_dir / "run_result.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        current_stage = "promote_outputs"
        current_names = set(artifact_names) | {"run_result.json"}
        _promote_outputs_transactionally(staging_dir, output_dir, current_names)

        return PipelineArtifacts(
            model_path=output_dir / "report_model.json",
            html_path=output_dir / "report.html",
            html_qa_path=output_dir / "html_qa.json",
            manifest_path=output_dir / "run_result.json",
            pptx_path=(output_dir / "report.pptx") if pptx_path else None,
            pptx_qa_path=(output_dir / "ppt_qa.json") if pptx_qa_path else None,
            slideviber_handoff_path=(
                output_dir / "slideviber_handoff.md" if slideviber_handoff_path else None
            ),
        )
    except Exception as exc:
        output_dir.mkdir(parents=True, exist_ok=True)
        preserved = sorted(
            name for name in MANAGED_OUTPUTS - {"run_result.json"} if (output_dir / name).exists()
        )
        failure = {
            **structured_failure_payload(exc),
            "failed_at": datetime.now(timezone.utc).isoformat(),
            "stage": current_stage,
            "error_type": type(exc).__name__,
            "previous_artifacts_preserved": preserved,
        }
        # A promotion failure rolls the complete previous successful bundle
        # back, including its passed manifest. Pre-promotion failures still
        # receive a structured failure manifest for diagnosis.
        if not (current_stage == "promote_outputs" and previous_success_manifest):
            failure_temp = staging_dir / "run_result.json"
            failure_temp.write_text(
                json.dumps(failure, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            os.replace(failure_temp, output_dir / "run_result.json")
        raise
    finally:
        shutil.rmtree(staging_dir, ignore_errors=True)


def _request_from_json(path: Path) -> ReportRequest:
    payload = json.loads(path.read_text(encoding="utf-8"))
    source_path = Path(payload["source_path"])
    if not source_path.is_absolute():
        source_path = (path.parent / source_path).resolve()
    payload["source_path"] = str(source_path)
    mode = str(payload.get("mode", "quick"))
    preflight_result = None
    if "period_type" not in payload:
        raise ValueError("period_type 未提供；请明确选择 weekly 或 monthly")
    if mode == "quick":
        payload, preflight_result = resolve_quick_payload(payload)
    elif mode == "professional":
        missing = [
            field
            for field in ("date_column", "primary_metrics", "audience", "objective")
            if not payload.get(field)
        ]
        if missing:
            raise ValueError(
                "professional 模式需要显式提供：" + ", ".join(missing)
            )
    raw_contracts = payload.get("metric_contracts", [])
    if isinstance(raw_contracts, dict):
        metric_contracts = tuple(
            {"name": name, **(contract if isinstance(contract, dict) else {})}
            for name, contract in raw_contracts.items()
        )
    else:
        metric_contracts = tuple(dict(contract) for contract in raw_contracts)
    request = ReportRequest(
        source_path=source_path,
        period_type=payload["period_type"],
        audience=payload["audience"],
        objective=payload["objective"],
        date_column=payload["date_column"],
        primary_metrics=tuple(payload["primary_metrics"]),
        dimensions=tuple(payload.get("dimensions", [])),
        output_mode=payload.get("output_mode", "report"),
        mode=payload.get("mode", "quick"),
        sheet_name=payload.get("sheet_name"),
        metric_contracts=metric_contracts,
        comparisons=tuple(
            payload.get("comparisons", ["period_over_period", "year_over_year"])
        ),
        week_start=payload.get("week_start", "monday"),
        timezone=payload.get("timezone", "Asia/Shanghai"),
        incomplete_period_policy=payload.get("incomplete_period_policy", "exclude"),
        theme=payload.get("theme", "clean"),
        ppt_refinement=payload.get("ppt_refinement", "offer_slideviber"),
        analysis_profile=payload.get("analysis_profile", "auto"),
        report_subject=payload.get("report_subject"),
        report_subtitle=payload.get("report_subtitle"),
        duplicate_policy=payload.get("duplicate_policy", "keep"),
        numeric_error_policy=payload.get("numeric_error_policy", "fail"),
        allow_sensitive_fields=bool(payload.get("allow_sensitive_fields", False)),
        preflight=preflight_result,
        analysis_intent=payload.get("analysis_intent", "business_review"),
        semantic_contract=payload.get("semantic_contract"),
        analysis_questions=validate_analysis_questions(payload.get("analysis_questions")),
    )
    validate_request(request)
    return request


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Generate a traceable HTML report and optional editable PPTX from Excel/CSV."
    )
    parser.add_argument("--request", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--inspect", type=Path)
    parser.add_argument("--sheet-name")
    parser.add_argument("--analyse-only", action="store_true")
    parser.add_argument("--html-analysis", action="store_true", help="宿主驱动的版本化 HTML 分析合同")
    parser.add_argument("--followup", type=Path, help="同一 HTML 分析运行的补查批次")
    parser.add_argument("--finalize", type=Path, metavar="STORY_PLAN_PATH")
    parser.add_argument("--compose-decisions", type=Path, metavar="PROPOSALS_PATH")
    args = parser.parse_args()
    try:
        if args.html_analysis:
            from html_analysis import cli
            if args.output is None or sum(bool(x) for x in [args.analyse_only, args.followup, args.compose_decisions, args.finalize]) != 1:
                parser.error("HTML 分析需要 output 和唯一分析阶段操作")
            if args.analyse_only and args.request is None:
                parser.error("初扫需要 request")
            if args.request and not args.analyse_only:
                parser.error("补查/组织/最终化只读取已绑定请求")
            print(json.dumps(cli(args), ensure_ascii=False))
            return 0
        if args.followup:
            parser.error("补查需要 --html-analysis")
        if args.inspect:
            result = inspect_source(args.inspect.resolve(), sheet_name=args.sheet_name)
            print(json.dumps(_user_observable_payload(result), ensure_ascii=False, indent=2))
            return 0
        if args.output is None:
            parser.error("生成报告需要提供 --output")
        if args.analyse_only and args.finalize:
            parser.error("--analyse-only 与 --finalize 不能同时使用")
        if args.compose_decisions and (args.analyse_only or args.finalize or args.request):
            parser.error("--compose-decisions 只读取 output 中的证据，不能与 --request/--analyse-only/--finalize 同用")
        if args.compose_decisions:
            path = compose_story_from_decisions(args.output, args.compose_decisions)
            print(json.dumps({"status": "passed", "story_plan": str(path)}, ensure_ascii=False))
            return 0
        if args.analyse_only:
            if args.request is None:
                parser.error("--analyse-only 需要提供 --request")
            artifacts = run_analysis_only(_request_from_json(args.request), args.output)
            print(json.dumps(_user_observable_payload({"status": "passed", "analysis_evidence": str(artifacts.evidence_path), "manifest": str(artifacts.manifest_path)}), ensure_ascii=False))
            return 0
        if args.finalize:
            artifacts = finalize_from_story_plan(args.output, args.finalize)
        else:
            if args.request is None:
                parser.error("生成报告需要提供 --request，或改用 --finalize")
            artifacts = run_pipeline(_request_from_json(args.request), args.output)
        print(
            json.dumps(
                _user_observable_payload({
                    "status": "passed",
                    "model": str(artifacts.model_path),
                    "html": str(artifacts.html_path),
                    "pptx": str(artifacts.pptx_path) if artifacts.pptx_path else None,
                    "slideviber_handoff": (
                        str(artifacts.slideviber_handoff_path)
                        if artifacts.slideviber_handoff_path
                        else None
                    ),
                    "manifest": str(artifacts.manifest_path),
                }),
                ensure_ascii=False,
            )
        )
        return 0
    except PreflightNeedsInput as exc:
        payload = {
            "status": "needs_input",
            "message": str(exc),
            "questions": exc.result.get("questions", []),
            "preflight": exc.result,
        }
        print(
            json.dumps(_user_observable_payload(payload), ensure_ascii=False),
            file=sys.stderr,
        )
        return 2
    except InsufficientEvidenceError as exc:
        print(
            json.dumps(_user_observable_payload(structured_failure_payload(exc, finalizing=bool(args.finalize))), ensure_ascii=False),
            file=sys.stderr,
        )
        return 2
    except ValueError as exc:
        print(
            json.dumps(_user_observable_payload(structured_failure_payload(exc, finalizing=bool(args.finalize))), ensure_ascii=False),
            file=sys.stderr,
        )
        return 2 if args.finalize else 1
    except Exception as exc:
        print(
            json.dumps(
                _user_observable_payload({
                    "status": "failed",
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                }),
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
