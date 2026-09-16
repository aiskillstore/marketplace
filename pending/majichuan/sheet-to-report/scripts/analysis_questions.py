"""Deterministic selection of useful business questions from confirmed inputs."""
from __future__ import annotations

from typing import Any

from analysis_periods import validate_comparison_scope


ALLOWED_QUESTION_TOOLS = {
    "period_comparison",
    "dimension_breakdown",
    "cross_breakdown",
    "concentration",
    "quality_impact",
}
ANSWER_STATUSES = {
    "answered",
    "followup_needed",
    "partial",
    "unanswerable",
}
QUESTION_TYPE_BY_LENS = {
    "overview": "result",
    "trend": "trend",
    "geography": "contribution",
    "product": "contribution",
    "customer": "structure_breakdown",
    "concentration": "concentration",
    "quality": "anomaly_quality",
    "growth_driver": "opportunity_risk",
    "user_lifecycle": "structure_breakdown",
    "content_performance": "cross_segment",
    "project_delivery": "opportunity_risk",
    "content_efficiency": "cross_segment",
    "delivery_efficiency": "opportunity_risk",
}
EVIDENCE_ROLES_BY_QUESTION_TYPE = {
    "result": ["metric_total"],
    "trend": ["period_comparison"],
    "contribution": ["group_contribution"],
    "concentration": ["ranked_contribution", "concentration_ratio"],
    "structure_breakdown": ["group_comparison"],
    "cross_segment": ["cross_breakdown"],
    "anomaly_quality": ["quality_impact"],
    "opportunity_risk": ["period_comparison", "driver_or_segment"],
}
_FOLLOWUP_TRACE_FIELDS = {
    "round",
    "path_hash",
    "tool",
    "evidence_ids",
    "information_gain",
    "result_hash",
    "stop_reason",
}


def canonical_available_objects(
    *,
    primary_metrics: tuple[str, ...] | list[str] | set[str],
    dimensions: tuple[str, ...] | list[str] | set[str],
    semantic_contract: dict[str, Any] | None,
    available_fields: set[str],
) -> set[str]:
    """Derive question-planning objects from root inputs, never from a persisted seed."""

    fields = {str(value) for value in available_fields}
    objects = {"dataset"} if any(str(value).strip() for value in primary_metrics) else set()
    contract = semantic_contract if isinstance(semantic_contract, dict) else {}
    mappings = contract.get("field_mappings", {})
    mapped_roles: set[str] = set()
    if isinstance(mappings, dict):
        for role, mapping in mappings.items():
            if isinstance(mapping, dict) and str(mapping.get("source_field") or "") in fields:
                mapped_roles.add(str(role))
                objects.add(str(role))
    domain = str(contract.get("domain") or contract.get("profile") or "").strip()
    if domain == "transactional_commerce" and {"order", "quantity", "unit_price"} <= objects:
        objects.add("sales")
    for dimension in dimensions:
        lowered = str(dimension).lower()
        if any(marker in lowered for marker in ("区域", "地域", "region", "geo", "country", "market")):
            objects.add("geography")
        if any(marker in lowered for marker in ("品类", "商品", "产品", "sku", "product")):
            objects.add("product")
        if any(marker in lowered for marker in ("客户", "用户", "customer", "user")):
            objects.add("user" if "user" in mapped_roles and "customer" not in mapped_roles else "customer")
    return objects


def _as_list(value: Any, field: str) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{field} 必须是列表")
    return list(value)


def _normalize_followup_trace(value: Any) -> list[dict[str, Any]]:
    trace = _as_list(value, "followup_trace")
    normalized: list[dict[str, Any]] = []
    for entry in trace:
        if not isinstance(entry, dict):
            raise ValueError("followup_trace 每项必须是摘要对象")
        unknown = set(entry) - _FOLLOWUP_TRACE_FIELDS
        if unknown:
            raise ValueError("followup_trace 包含不允许的字段：" + ", ".join(sorted(unknown)))
        if set(entry) != _FOLLOWUP_TRACE_FIELDS:
            raise ValueError("followup_trace 每项必须包含完整摘要字段")
        summary = dict(entry)
        if "round" in summary and (
            isinstance(summary["round"], bool) or not isinstance(summary["round"], int) or summary["round"] < 1
        ):
            raise ValueError("followup_trace.round 必须是正整数")
        for field in ("path_hash", "result_hash", "stop_reason"):
            if not isinstance(summary[field], str):
                raise ValueError(f"followup_trace.{field} 必须是字符串")
        tool = summary["tool"]
        if not isinstance(tool, str) or tool not in ALLOWED_QUESTION_TOOLS:
            raise ValueError("followup_trace.tool 必须是白名单工具")
        evidence_ids = summary["evidence_ids"]
        if not isinstance(evidence_ids, (list, tuple)) or not all(
            isinstance(item, str) and item.strip() for item in evidence_ids
        ):
            raise ValueError("followup_trace.evidence_ids 必须是证据 ID 列表")
        summary["evidence_ids"] = list(evidence_ids)
        if not isinstance(summary["information_gain"], bool):
            raise ValueError("followup_trace.information_gain 必须是布尔值")
        normalized.append(summary)
    return normalized


def _normalize_followup_paths(value: Any) -> list[dict[str, Any]]:
    paths = _as_list(value, "followup_paths")
    normalized: list[dict[str, Any]] = []
    for path in paths:
        if not isinstance(path, dict):
            raise ValueError("followup_paths 每项必须是对象")
        if "approval_callback" in path:
            raise ValueError("followup_paths 不接受 approval_callback")
        normalized.append(dict(path))
    return normalized


def _default_allowed_tools(*, lens: str, dimensions: list[Any], comparison_scope: Any) -> list[str]:
    tools: list[str] = []
    if comparison_scope:
        tools.append("period_comparison")
    if dimensions:
        tools.append("dimension_breakdown")
    if lens == "concentration":
        tools.append("concentration")
    if lens == "quality":
        tools.append("quality_impact")
    if lens == "growth_driver" and "period_comparison" not in tools:
        tools.append("period_comparison")
    return tools


def normalize_question_contract(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize a declarative analysis question into an executable contract."""
    if not isinstance(raw, dict):
        raise ValueError("analysis question 必须是对象")

    business_question = str(raw.get("business_question") or raw.get("question") or "").strip()
    if not business_question:
        raise ValueError("business_question 不能为空")
    lens = str(raw.get("lens") or "overview").strip()
    if not lens:
        raise ValueError("lens 不能为空")
    dimensions = _as_list(raw.get("dimensions"), "dimensions")
    confirmed_fields = _as_list(raw.get("confirmed_fields"), "confirmed_fields")
    comparison_scope = raw.get("comparison_scope")
    validate_comparison_scope(comparison_scope)
    provided_tools = raw.get("allowed_tools")
    allowed_tools = (
        _default_allowed_tools(lens=lens, dimensions=dimensions, comparison_scope=comparison_scope)
        if provided_tools is None else _as_list(provided_tools, "allowed_tools")
    )
    unknown_tools = [tool for tool in allowed_tools if tool not in ALLOWED_QUESTION_TOOLS]
    if unknown_tools:
        raise ValueError("unknown question tool: " + ", ".join(str(tool) for tool in unknown_tools))
    answer_status = str(raw.get("answer_status") or "").strip()
    if not answer_status:
        answer_status = {"hypothesis": "partial", "unavailable": "unanswerable"}.get(
            str(raw.get("status") or ""), "followup_needed"
        )
    if answer_status not in ANSWER_STATUSES:
        raise ValueError("answer_status 不受支持：" + answer_status)
    followup_trace = _normalize_followup_trace(raw.get("followup_trace"))

    normalized = {
        **raw,
        "question_id": str(raw.get("question_id") or f"q_{lens}").strip(),
        "lens": lens,
        "business_question": business_question,
        "decision_impact": str(raw.get("decision_impact") or "支持当前分析目标的决策").strip(),
        "priority": raw.get("priority", "medium"),
        "required_objects": _as_list(raw.get("required_objects"), "required_objects"),
        "required_fields": _as_list(raw.get("required_fields"), "required_fields"),
        "required_metrics": _as_list(raw.get("required_metrics"), "required_metrics"),
        "dimensions": dimensions,
        "confirmed_fields": confirmed_fields or list(dict.fromkeys([
            *[str(value) for value in raw.get("required_fields", [])],
            *[str(value) for value in dimensions],
        ])),
        "comparison_scope": comparison_scope,
        "allowed_tools": allowed_tools,
        "minimum_evidence": raw.get("minimum_evidence", 1),
        "followup_paths": _normalize_followup_paths(raw.get("followup_paths")),
        "expected_information_gain": raw.get("expected_information_gain", ""),
        "stop_conditions": _as_list(raw.get("stop_conditions"), "stop_conditions"),
        "answer_status": answer_status,
        "evidence_ids": _as_list(raw.get("evidence_ids"), "evidence_ids"),
        "followup_trace": followup_trace,
        "stop_reason": raw.get("stop_reason"),
        "missing_requirements": _as_list(raw.get("missing_requirements"), "missing_requirements"),
        "selection_reasons": _as_list(raw.get("selection_reasons"), "selection_reasons"),
    }
    if not normalized["question_id"]:
        raise ValueError("question_id 不能为空")
    return normalized


QUESTION_LIBRARY: tuple[dict[str, Any], ...] = (
    {"lens": "overview", "business_question": "当前整体经营规模与范围是什么？", "priority": "high", "required_objects": ("dataset", "sales"), "any_of_objects": True, "required_metrics": ("any_primary_metric",), "chart_requirement": "kpi", "minimum_evidence": 1},
    {"lens": "trend", "business_question": "核心指标相对上一完整周期如何变化？", "priority": "high", "required_objects": ("dataset", "sales"), "any_of_objects": True, "required_metrics": ("any_primary_metric",), "chart_requirement": "trend", "minimum_evidence": 2, "requires_multiple_periods": True},
    {"lens": "geography", "business_question": "不同地域的贡献或表现差异在哪里？", "priority": "medium", "required_objects": ("geography",), "required_metrics": ("any_primary_metric",), "chart_requirement": "ranking", "minimum_evidence": 1},
    {"lens": "product", "business_question": "哪些产品或品类贡献主要结果？", "priority": "medium", "required_objects": ("product",), "required_metrics": ("any_primary_metric",), "chart_requirement": "ranking", "minimum_evidence": 1},
    {"lens": "customer", "business_question": "客户结构是否集中或存在差异？", "priority": "medium", "required_objects": ("customer",), "required_metrics": ("any_primary_metric",), "chart_requirement": "ranking", "minimum_evidence": 1},
    {"lens": "concentration", "business_question": "主要贡献是否过度集中于少数对象？", "priority": "medium", "required_objects": ("product",), "required_metrics": ("any_primary_metric",), "chart_requirement": "concentration", "minimum_evidence": 1},
    {"lens": "quality", "business_question": "数据或经营质量风险是否影响结论？", "priority": "high", "required_objects": (), "required_metrics": (), "chart_requirement": "quality", "minimum_evidence": 1},
    {"lens": "growth_driver", "business_question": "增长变化有哪些可验证的结构线索？", "priority": "medium", "required_objects": ("dataset", "sales"), "any_of_objects": True, "required_metrics": ("any_primary_metric",), "chart_requirement": "comparison", "minimum_evidence": 2, "requires_multiple_periods": True},
)


# Experimental non-retail profiles intentionally use the general execution
# layer.  Their questions are therefore field-backed contracts, rather than
# aliases of the commerce-oriented object defaults above.
NON_RETAIL_QUESTION_LIBRARY: dict[str, tuple[dict[str, Any], ...]] = {
    "content_operations": (
        {"lens": "overview", "business_question": "当前内容交付规模与覆盖范围是什么？", "priority": "high", "required_objects": ("dataset",), "required_metrics": ("any_primary_metric",), "chart_requirement": "kpi", "minimum_evidence": 1},
        {"lens": "trend", "business_question": "内容交付指标相对上一完整周期如何变化？", "priority": "high", "required_objects": ("dataset",), "required_metrics": ("any_primary_metric",), "chart_requirement": "trend", "minimum_evidence": 2, "requires_multiple_periods": True},
        {
            "lens": "content_efficiency",
            "business_question": "各内容渠道的转化效率与投入是否存在可验证的取舍？",
            "priority": "high",
            "required_objects": ("dataset",),
            "required_fields": ("channel", "conversions", "clicks", "cost"),
            "required_metrics": ("conversion_rate", "cost"),
            "dimensions": ("channel",),
            "chart_requirement": "ranking",
            "minimum_evidence": 2,
            "allowed_tools": ("dimension_breakdown",),
            "followup_paths": (
                {"tool": "dimension_breakdown", "metric": "conversion_rate", "fields": ["channel"], "dimensions": ["channel"]},
                {"tool": "dimension_breakdown", "metric": "cost", "fields": ["channel"], "dimensions": ["channel"]},
            ),
            "expected_information_gain": "确认渠道转化效率与投入规模的取舍。",
        },
    ),
    "project_operations": (
        {"lens": "overview", "business_question": "当前项目交付规模与覆盖范围是什么？", "priority": "high", "required_objects": ("dataset",), "required_metrics": ("any_primary_metric",), "chart_requirement": "kpi", "minimum_evidence": 1},
        {"lens": "trend", "business_question": "项目交付指标相对上一完整周期如何变化？", "priority": "high", "required_objects": ("dataset",), "required_metrics": ("any_primary_metric",), "chart_requirement": "trend", "minimum_evidence": 2, "requires_multiple_periods": True},
        {
            "lens": "delivery_efficiency",
            "business_question": "各团队的延期、超支与质量是否存在可验证的交付取舍？",
            "priority": "high",
            "required_objects": ("dataset",),
            "required_fields": ("team", "delay_days", "cost_overrun", "quality_score"),
            "required_metrics": ("delay_days", "cost_overrun", "quality_score"),
            "dimensions": ("team",),
            "chart_requirement": "ranking",
            "minimum_evidence": 3,
            "allowed_tools": ("dimension_breakdown",),
            "followup_paths": (
                {"tool": "dimension_breakdown", "metric": "delay_days", "fields": ["team"], "dimensions": ["team"]},
                {"tool": "dimension_breakdown", "metric": "cost_overrun", "fields": ["team"], "dimensions": ["team"]},
                {"tool": "dimension_breakdown", "metric": "quality_score", "fields": ["team"], "dimensions": ["team"]},
            ),
            "expected_information_gain": "确认团队交付时效、预算和质量的取舍。",
        },
    ),
}

GRAIN_QUESTION_LIBRARY: dict[str, tuple[dict[str, Any], ...]] = {
    "user_snapshot": ({
        "lens": "user_lifecycle",
        "business_question": "不同用户生命周期或获客结构中，结果差异集中在哪里？",
        "priority": "high",
        "required_objects": ("user",),
        "required_metrics": ("any_primary_metric",),
        "chart_requirement": "ranking",
        "minimum_evidence": 2,
    },),
    "user_event": ({
        "lens": "user_lifecycle",
        "business_question": "用户事件路径中，转化或留存差异集中在哪里？",
        "priority": "high",
        "required_objects": ("user",),
        "required_metrics": ("any_primary_metric",),
        "chart_requirement": "ranking",
        "minimum_evidence": 2,
    },),
    "content_record": ({
        "lens": "content_performance",
        "business_question": "哪些内容对象或类型形成了结果、效率或质量差异？",
        "priority": "high",
        "required_objects": ("content",),
        "required_metrics": ("any_primary_metric",),
        "chart_requirement": "ranking",
        "minimum_evidence": 2,
    },),
    "project_task": ({
        "lens": "project_delivery",
        "business_question": "哪些项目、任务或团队形成了交付效率与质量风险？",
        "priority": "high",
        "required_objects": ("project", "task"),
        "any_of_objects": True,
        "required_metrics": ("any_primary_metric",),
        "chart_requirement": "ranking",
        "minimum_evidence": 2,
    },),
}


def _priority_score(priority: Any) -> int:
    if isinstance(priority, (int, float)) and not isinstance(priority, bool):
        return max(1, min(3, int(priority)))
    return {"high": 3, "medium": 2, "low": 1}.get(str(priority).lower(), 2)


def _question_planning_fields(
    item: dict[str, Any],
    *,
    missing_requirements: list[str],
    selection_status: str,
) -> dict[str, Any]:
    question_type = str(
        item.get("question_type")
        or QUESTION_TYPE_BY_LENS.get(str(item.get("lens") or ""), "structure_breakdown")
    )
    rejected = selection_status == "rejected"
    supported = not rejected
    importance = _priority_score(item.get("priority"))
    leverage = 3 if question_type in {"opportunity_risk", "anomaly_quality", "cross_segment"} else 2
    evidence_completeness = 2 if supported else 0
    story_coverage = 2 if question_type not in {"result", "trend"} else 1
    total = importance + leverage + evidence_completeness + story_coverage
    prerequisites = [
        *[f"object:{value}" for value in item.get("required_objects", ())],
        *[f"field:{value}" for value in item.get("required_fields", ())],
        *[f"metric:{value}" for value in item.get("required_metrics", ())],
    ]
    if item.get("requires_multiple_periods"):
        prerequisites.append("periods:at_least_2")
    if rejected:
        reason = "拒绝进入执行：" + "；".join(missing_requirements)
    elif missing_requirements:
        reason = "基础字段支持，但需补齐：" + "；".join(missing_requirements)
    else:
        reason = f"字段、对象与口径支持；以{question_type}补足决策故事。"
    provided_tools = item.get("allowed_tools")
    allowed_followup_generators = (
        _default_allowed_tools(
            lens=str(item.get("lens") or "overview"),
            dimensions=list(item.get("dimensions", ())),
            comparison_scope=item.get("comparison_scope"),
        )
        if provided_tools is None else list(provided_tools)
    )
    default_required_depth = 1 if question_type == "result" else 4 if importance >= 3 else 3
    return {
        "question_type": question_type,
        "decision_supported": str(
            item.get("decision_supported")
            or item.get("decision_impact")
            or "决定下一周期的资源、风险或验证优先级"
        ),
        "prerequisites": prerequisites,
        "required_depth": item.get("required_depth", default_required_depth),
        "required_evidence_roles": list(
            item.get("required_evidence_roles")
            or EVIDENCE_ROLES_BY_QUESTION_TYPE.get(question_type, ["group_comparison"])
        ),
        "allowed_followup_generators": allowed_followup_generators,
        "estimated_cost": {
            "class": "low" if len(prerequisites) <= 3 else "medium",
            "deterministic_aggregations": max(1, len(item.get("required_metrics", ()))),
        },
        "supportability": {
            "status": "supported" if supported and not missing_requirements else "partial" if supported else "unsupported",
            "missing_requirements": list(missing_requirements),
        },
        "preliminary_signals": [{
            "signal_id": "support_scan",
            "signal_type": "supportability",
            "value": 1 if supported else 0,
            "evidence_ids": [],
        }],
        "selection_scores": {
            "importance": importance,
            "abnormality": 0,
            "decision_leverage": leverage,
            "evidence_completeness": evidence_completeness,
            "action_value": leverage,
            "redundancy_penalty": 0,
            "story_coverage": story_coverage,
            "total": total + leverage,
        },
        "selection_status": selection_status,
        "selection_reason": reason,
    }


def _semantic_followup_dimensions(
    lens: str,
    semantic_contract: dict[str, Any],
) -> list[str]:
    """Choose decision-safe display dimensions from confirmed semantic roles."""

    role_preferences = {
        "geography": ("geography", "region", "market"),
        "product": ("product", "category"),
        "customer": ("customer_segment", "customer", "user_segment"),
        "concentration": ("product", "category", "customer_segment", "customer"),
        "growth_driver": (
            "channel", "acquisition_channel", "geography", "product", "category",
            "customer_segment", "lifecycle_stage", "content_type", "team", "phase",
        ),
        "user_lifecycle": ("acquisition_channel", "lifecycle_stage", "user_segment"),
        "content_performance": ("content_type", "channel"),
        "project_delivery": ("team", "phase"),
    }
    mappings = semantic_contract.get("field_mappings", {})
    if not isinstance(mappings, dict):
        return []
    for role in role_preferences.get(lens, ()):
        mapping = mappings.get(role)
        if not isinstance(mapping, dict):
            continue
        if str(mapping.get("confidence") or "high").lower() not in {"high", "confirmed"}:
            continue
        field = mapping.get("display_field") or mapping.get("source_field")
        if field:
            return [str(field)]
    return []


def infer_question_depth(
    question: dict[str, Any],
    *,
    evidence_ids: list[str] | tuple[str, ...] | None = None,
    followup_tools: list[str] | tuple[str, ...] = (),
    evidence_index: dict[str, Any] | None = None,
    insights=(), actions=(), scope_catalog=(),
) -> int:
    """Only computed evidence and its actual interpretation may grant depth."""
    from analysis_depth import assess_depth
    return assess_depth(question, evidence_index=evidence_index or {}, evidence_ids=evidence_ids,
                        insights=insights, actions=actions, scope_catalog=scope_catalog)["achieved_depth"]


def build_analysis_brief(
    *,
    audience: str,
    report_mode: str,
    objective: str,
    semantic_contract: dict[str, Any] | None,
    primary_metrics: list[str] | tuple[str, ...],
    periods: dict[str, Any] | None,
    quality_decisions: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
) -> dict[str, Any]:
    contract = semantic_contract if isinstance(semantic_contract, dict) else {}
    grain = str(contract.get("table_grain") or "other_confirmed")
    domain = str(contract.get("domain") or contract.get("profile") or "general")
    archetype = {
        "transaction": "transactional_commerce",
        "order": "transactional_commerce",
        "order_line": "transactional_commerce",
        "user_snapshot": "user_lifecycle",
        "user_event": "user_lifecycle",
        "content_record": "content_performance",
        "project_task": "project_delivery",
    }.get(grain, "growth_operations" if domain == "retail_growth" else "general_performance")
    bindings = contract.get("object_bindings", [])
    primary_objects = [
        str(item.get("object_id"))
        for item in bindings
        if isinstance(item, dict) and item.get("object_id")
    ]
    coverage = contract.get("semantic_coverage", {})
    required_confirmations = [
        {
            "kind": key,
            "field_id": str(item.get("field_id") or ""),
            "reason": str(item.get("reason") or ""),
        }
        for key in ("needs_confirmation", "material_unmapped")
        for item in coverage.get(key, [])
        if isinstance(item, dict)
    ]
    for decision in quality_decisions:
        if decision.get("severity") in {"block", "confirm"}:
            required_confirmations.append({
                "kind": "quality_policy",
                "issue_id": str(decision.get("issue_id") or ""),
                "reason": str(decision.get("decision_impact") or ""),
            })
    assumptions: list[str] = []
    if not contract:
        assumptions.append("未提供业务语义合同，按已确认请求字段执行通用分析。")
    if report_mode == "quick":
        assumptions.append("Quick 使用业务负责人视角的通用经营复盘框架。")
    time_scope = dict(periods or {})
    confidence = "low" if required_confirmations else "medium" if assumptions else "high"
    return {
        "audience": audience or "业务负责人",
        "report_mode": report_mode,
        "business_archetype": archetype,
        "objective": objective,
        "decision_frame": (
            "本期表现、变化驱动、风险与机会、下一步行动"
            if report_mode == "quick"
            else "按已确认问题优先级形成可审计的经营判断与行动验证"
        ),
        "time_scope": time_scope,
        "primary_metrics": [str(value) for value in primary_metrics],
        "primary_objects": list(dict.fromkeys(primary_objects)),
        "quality_policy_ids": [
            str(item.get("issue_id") or item.get("selected_policy") or "")
            for item in quality_decisions
            if item.get("issue_id") or item.get("selected_policy")
        ],
        "assumptions": assumptions,
        "required_confirmations": required_confirmations,
        "confidence": confidence,
    }


def select_analysis_questions(*, analysis_intent: str, audience: str, objective: str,
                              semantic_contract: dict[str, Any] | None,
                              available_fields: set[str], available_objects: set[str],
                              available_metrics: set[str], period_count: int | None = None) -> dict[str, Any]:
    """Return only supportable lenses; time-dependent gaps become hypotheses."""
    semantic_contract = semantic_contract or {}
    context = f"{audience} {objective}".lower()
    domain = str(semantic_contract.get("domain") or semantic_contract.get("profile") or "general")
    confirmed_roles = {
        str(role) for role, mapping in semantic_contract.get("field_mappings", {}).items()
        if isinstance(mapping, dict) and str(mapping.get("confidence") or "").lower() == "high"
    }
    if analysis_intent == "engineering_regression":
        raw = {"lens": "quality", "business_question": "数据质量与计算合同是否通过？", "priority": "high", "required_objects": [], "required_metrics": [], "chart_requirement": "quality", "minimum_evidence": 1, "status": "selected", "missing_requirements": []}
        raw.update(_question_planning_fields(raw, missing_requirements=[], selection_status="selected"))
        questions = [normalize_question_contract(raw)]
        return {
            "questions": questions,
            "candidate_questions": [dict(item) for item in questions],
            "rejected_questions": [],
            "missing_requirements": [],
            "available_objects": sorted(available_objects),
        }

    selected: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    domain_library = NON_RETAIL_QUESTION_LIBRARY.get(domain)
    domain_quality = domain_library[-1] if domain_library else None
    has_profile_contract = bool(domain_quality) and set(
        str(field) for field in domain_quality.get("required_fields", ())
    ).issubset(available_fields) and set(
        str(metric) for metric in domain_quality.get("required_metrics", ())
    ).issubset(available_metrics)
    question_library = domain_library if has_profile_contract else QUESTION_LIBRARY
    if not domain_library:
        grain = str(semantic_contract.get("table_grain") or "")
        question_library = (*question_library, *GRAIN_QUESTION_LIBRARY.get(grain, ()))
    for blueprint in question_library:
        required_objects = set(blueprint["required_objects"])
        available_objects = set(available_objects)
        absent = ([] if required_objects & available_objects else ["any_of:" + ",".join(sorted(required_objects))]) if blueprint.get("any_of_objects") else sorted(required_objects - available_objects)
        missing_metric = bool(blueprint["required_metrics"]) and not available_metrics
        missing_fields = not available_fields and blueprint["lens"] != "quality"
        reasons = [f"intent:{analysis_intent}", f"semantic_domain:{domain}"]
        keywords = {
            "geography": ("区域", "地域", "region"), "product": ("商品", "产品", "品类", "sku"),
            "customer": ("客户", "用户", "留存", "复购"), "quality": ("质量", "异常", "风险", "回归"),
            "growth_driver": ("增长", "驱动", "机会"), "trend": ("趋势", "周期", "同比", "环比"),
        }
        matched = [word for word in keywords.get(blueprint["lens"], ()) if word in context]
        if matched:
            reasons.extend(f"audience:{word}" if word in str(audience).lower() else f"objective:{word}" for word in matched)
        if required_objects & confirmed_roles:
            reasons.append("confirmed_mapping")
        item = {**blueprint, "required_objects": list(blueprint["required_objects"]), "required_metrics": list(blueprint["required_metrics"]), "missing_requirements": [], "selection_reasons": reasons}
        if not item.get("dimensions"):
            item["dimensions"] = _semantic_followup_dimensions(
                str(blueprint.get("lens") or ""), semantic_contract,
            )
        unsupported_requirements: list[str] = []
        if absent:
            requirement = "objects:" + ",".join(absent)
            missing.append({"lens": blueprint["lens"], "missing_requirement": requirement})
            unsupported_requirements.append(requirement)
        if missing_metric:
            requirement = "metrics:any_primary_metric"
            missing.append({"lens": blueprint["lens"], "missing_requirement": requirement})
            unsupported_requirements.append(requirement)
        if missing_fields:
            requirement = "fields:source_columns"
            missing.append({"lens": blueprint["lens"], "missing_requirement": requirement})
            unsupported_requirements.append(requirement)
        if unsupported_requirements:
            item.update({
                "status": "rejected",
                "answer_status": "unanswerable",
                "missing_requirements": unsupported_requirements,
                "selection_reasons": [*reasons, "unsupported_prerequisites"],
            })
            item.update(_question_planning_fields(
                item,
                missing_requirements=unsupported_requirements,
                selection_status="rejected",
            ))
            normalized_rejected = normalize_question_contract(item)
            candidates.append(normalized_rejected)
            rejected.append(normalized_rejected)
            continue
        if blueprint.get("requires_multiple_periods") and period_count is not None and period_count < 2:
            item["status"] = "hypothesis"
            item["answer_status"] = "partial"
            item["missing_requirements"] = ["multiple_periods"]
            missing.append({"lens": blueprint["lens"], "missing_requirement": "multiple_periods"})
        else:
            item["status"] = "selected"
        if matched or (required_objects & confirmed_roles):
            item["priority"] = "high"
        item.update(_question_planning_fields(
            item,
            missing_requirements=list(item.get("missing_requirements", [])),
            selection_status="hypothesis" if item["status"] == "hypothesis" else "selected",
        ))
        normalized = normalize_question_contract(item)
        selected.append(normalized)
        candidates.append(dict(normalized))
    return {
        "questions": selected,
        "candidate_questions": candidates,
        "rejected_questions": rejected,
        "missing_requirements": missing,
        "available_objects": sorted(available_objects),
        "selection_policy": {
            "steps": ["supportability_filter", "deterministic_preliminary_scan"],
            "retain_rejected_reasons": True,
        },
    }


def canonical_analysis_question_contract(
    *, analysis_intent: str, audience: str, objective: str,
    semantic_contract: dict[str, Any] | None, available_fields: set[str],
    available_objects: set[str], available_metrics: set[str], period_count: int | None,
    custom_questions: tuple[dict[str, Any], ...] | list[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Canonical static question contract shared by production and artifacts.

    Runtime fields (answer/evidence/followup) are intentionally reconciled
    later; this function owns only deterministic inference and caller overlay.
    """
    plan = select_analysis_questions(
        analysis_intent=analysis_intent, audience=audience, objective=objective,
        semantic_contract=semantic_contract, available_fields=available_fields,
        available_objects=available_objects, available_metrics=available_metrics,
        period_count=period_count,
    )
    normalized_custom = [normalize_question_contract(item) for item in custom_questions]
    for question in normalized_custom:
        question.setdefault("status", "selected")
        absent_fields = sorted((set(question["required_fields"]) | set(question["dimensions"])) - available_fields)
        metric_references = available_metrics | {f"metric:{name}" for name in available_metrics}
        absent_metrics = sorted(set(question["required_metrics"]) - metric_references - {"any_primary_metric"})
        absent_objects = sorted(set(question["required_objects"]) - available_objects)
        if question.get("any_of_objects") and set(question["required_objects"]) & available_objects:
            absent_objects = []
        unsupported = [f"{kind}:" + ",".join(values) for kind, values in (
            ("fields", absent_fields), ("metrics", absent_metrics), ("objects", absent_objects),
        ) if values]
        if "any_primary_metric" in question["required_metrics"] and not available_metrics:
            unsupported.append("metrics:any_primary_metric")
        if unsupported:
            question.update(status="rejected", answer_status="unanswerable")
        if question.get("requires_multiple_periods") and period_count is not None and period_count < 2:
            unsupported.append("multiple_periods")
            if question["status"] != "rejected":
                question.update(status="hypothesis", answer_status="partial")
        question["missing_requirements"] = list(dict.fromkeys([*question["missing_requirements"], *unsupported]))
        question.update(_question_planning_fields(
            question, missing_requirements=list(question.get("missing_requirements", [])),
            selection_status="hypothesis" if question["status"] == "hypothesis" else
                             "rejected" if question["status"] in {"rejected", "unavailable", "skipped"} else "selected",
        ))
    ids = [str(item["question_id"]) for item in normalized_custom]
    if len(ids) != len(set(ids)):
        raise ValueError("analysis_questions 包含重复 question_id")
    merged = list(plan["questions"])
    positions = {str(item["question_id"]): index for index, item in enumerate(merged)}
    for question in normalized_custom:
        question_id = str(question["question_id"])
        if question_id in positions:
            merged[positions[question_id]] = question
        else:
            positions[question_id] = len(merged)
            merged.append(question)
    candidate_by_id = {
        str(item.get("question_id") or ""): dict(item)
        for item in plan.get("candidate_questions", [])
        if isinstance(item, dict)
    }
    for question in normalized_custom:
        candidate_by_id[str(question["question_id"])] = dict(question)
    return {
        **plan,
        "questions": merged,
        "candidate_questions": list(candidate_by_id.values()),
        "rejected_questions": [item for item in candidate_by_id.values() if item.get("selection_status") == "rejected"],
        "missing_requirements": [*plan["missing_requirements"], *[
            {"lens": item["lens"], "missing_requirement": requirement}
            for item in normalized_custom for requirement in item["missing_requirements"]
        ]],
    }


def reconcile_questions_with_evidence(
    plan: dict[str, Any], *, evidence_ids_by_lens: dict[str, list[str]], evidence_index=None, insights=(), actions=(), scope_catalog=(),
    execution_stop_reasons: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Update only evidence-dependent fields of already-normalized questions."""

    questions = [dict(item) for item in plan.get("questions", [])]
    missing = [dict(item) for item in plan.get("missing_requirements", [])]
    for item in questions:
        lens = str(item.get("lens") or "")
        # Only a fresh executor result, not caller-supplied question metadata,
        # can close the current follow-up run.
        executed_stop = (execution_stop_reasons or {}).get(str(item.get("question_id")))
        evidence_ids = list(evidence_ids_by_lens.get(str(item.get("question_id")), evidence_ids_by_lens.get(lens, ())))
        depth_aware = "required_depth" in item or "achieved_depth" in item
        if evidence_ids:
            item["evidence_ids"] = evidence_ids
            if len(evidence_ids) >= int(item.get("minimum_evidence") or 1):
                item["missing_requirements"] = [value for value in item.get("missing_requirements", []) if value != "minimum_evidence"]
            if depth_aware:
                achieved_depth = infer_question_depth(item, evidence_ids=evidence_ids, evidence_index=evidence_index, insights=insights, actions=actions, scope_catalog=scope_catalog)
                from analysis_depth import assess_depth
                item["depth_gaps"] = assess_depth(item, evidence_index=evidence_index or {}, evidence_ids=evidence_ids, insights=insights, actions=actions, scope_catalog=scope_catalog)["depth_gaps"]
                item["achieved_depth"] = achieved_depth
                raw_required_depth = item.get("required_depth", 1)
                required_depth = (
                    int(raw_required_depth)
                    if isinstance(raw_required_depth, int) and not isinstance(raw_required_depth, bool)
                    else 5
                )
                requirements = list(item.get("missing_requirements", []))
                if achieved_depth < required_depth and "required_depth" not in requirements:
                    requirements.append("required_depth")
                if achieved_depth >= required_depth:
                    requirements = [value for value in requirements if value != "required_depth"]
                item["missing_requirements"] = requirements
                if achieved_depth < required_depth:
                    has_followup = bool(
                        item.get("followup_paths")
                        or item.get("allowed_followup_generators")
                        or item.get("allowed_tools")
                    )
                    item["answer_status"] = "followup_needed" if has_followup and not executed_stop else "partial"
                    item["stop_reason"] = executed_stop or (None if has_followup else "missing_required_field")
                    marker = {"lens": lens, "missing_requirement": "required_depth"}
                    if marker not in missing:
                        missing.append(marker)
                    continue
            if not item.get("missing_requirements", []):
                item["answer_status"] = "answered"
                item["stop_reason"] = None
            else:
                item["answer_status"] = "partial"
                item["stop_reason"] = executed_stop or "missing_requirements_unmet"
            continue
        requirements = list(item.get("missing_requirements", []))
        if depth_aware:
            item["achieved_depth"] = infer_question_depth(item, evidence_ids=[], evidence_index=evidence_index)
            if "required_depth" not in requirements:
                requirements.append("required_depth")
        if "minimum_evidence" not in requirements:
            requirements.append("minimum_evidence")
        item["missing_requirements"] = requirements
        item["answer_status"] = "partial" if item.get("evidence_ids", []) else "unanswerable"
        item["stop_reason"] = executed_stop or "minimum_evidence_unmet"
        marker = {"lens": lens, "missing_requirement": "minimum_evidence"}
        if marker not in missing:
            missing.append(marker)
    return {**plan, "questions": questions, "missing_requirements": missing}
