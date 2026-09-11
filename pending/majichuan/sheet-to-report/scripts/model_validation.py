from __future__ import annotations

import math
import re
import warnings
from typing import Any, Iterable

from presentation_contracts import (
    ALLOWED_COMPARISON_KINDS,
    ALLOWED_DENSITIES,
    ALLOWED_TONES,
)
from content_qa import validate_content_value
from layout_registry import validate_layout_capacity
from canonical_json import canonical_sha256
from analysis_scope import SCOPE_VERSION, record_evidence_ids, scope_lock_projection
from content_resolver import (
    is_modern_model,
    validate_content_refs,
    validate_formal_renderer_records,
)
from story_topology import ALLOWED_STORY_ROLES, validate_story_topology
from report_model_projection import build_non_retail_projection, content_validation_lock_value, renderer_content_lock_projection


REQUIRED_MODEL_KEYS = {
    "schema_version",
    "source",
    "request",
    "data_profile",
    "metric_contracts",
    "analysis_profile",
    "report_title",
    "report_subtitle",
    "judgement_headline",
    "executive_summary",
    "periods",
    "kpis",
    "insights",
    "actions",
    "charts",
    "slide_plan",
    "evidence_index",
    "validation",
}

ALLOWED_LAYOUTS = {
    "cover",
    "executive-summary",
    "kpi-spotlight",
    "trend-wide",
    "chart-insight-action",
    "chart-side-kpi",
    "driver-levers",
    "risk-opportunity",
    "action-roadmap",
    "data-appendix",
}


def validate_question_depth_contract(questions: Any) -> None:
    """Fail closed when a depth-aware question overclaims its answer status."""

    if not isinstance(questions, list):
        raise ValueError("analysis_lenses 必须是列表")
    for question in questions:
        if not isinstance(question, dict):
            raise ValueError("analysis_lenses 每项必须是对象")
        if "required_depth" not in question:
            continue
        required = question.get("required_depth")
        achieved = question.get("achieved_depth")
        if (
            isinstance(required, bool) or not isinstance(required, int) or not 0 <= required <= 5
            or isinstance(achieved, bool) or not isinstance(achieved, int) or not 0 <= achieved <= 5
        ):
            raise ValueError("问题深度必须是 0-5 的整数")
        if question.get("answer_status") == "answered" and achieved < required:
            raise ValueError("问题未达到 required_depth，不得标记 answered")
        if question.get("stop_reason") == "evidence_sufficient":
            raise ValueError("深度问题不得以 evidence_sufficient 代替 required_depth_met")


def validate_depth_evidence_contract(model: dict) -> None:
    if "analysis_brief" not in model:
        return
    from analysis_depth import assess_depth, validate_action_chapter_links
    validate_action_chapter_links(model)
    questions = {item["question_id"]: item for item in model.get("analysis_lenses", [])}
    insights = []
    for raw in model.get("insights", []):
        item = dict(raw)
        canonical = "q_" + str(item.get("lens") or "")
        if not item.get("question_id") and canonical in questions:
            item["question_id"] = canonical
        insights.append(item)
    kwargs = {"evidence_index": model.get("evidence_index", {}), "scope_catalog": model.get("scope_catalog", [])}
    validate_question_depth_contract(list(questions.values()))
    for question in questions.values():
        if question.get("answer_status") == "answered":
            from question_coverage import requested_coverage_gaps
            request = model.get("request", {})
            gaps = requested_coverage_gaps(question, model.get("evidence_index", {}), model.get("metric_contracts", []),
                period_type=request.get("period_type", "monthly"), week_start=request.get("week_start", "monday"))
            if gaps:
                raise ValueError("requested comparison coverage 不完整：" + ";".join(gaps))
        owners = {chapter.get("chapter_id") for chapter in model.get("analysis_chapters", [])
                  if chapter.get("question_id") == question.get("question_id")}
        question_actions = [action for action in model.get("actions", [])
                            if owners & set(action.get("source_chapter_ids", []))]
        actual = assess_depth(question, insights=insights, actions=question_actions, **kwargs)
        if question.get("achieved_depth") != actual["achieved_depth"]:
            raise ValueError("analysis depth 与实际证据和经营判断不一致")
    for chapter in model.get("analysis_chapters", []):
        question = questions.get(chapter.get("question_id"), {})
        representative = next((item for item in insights if item.get("insight_id") == chapter.get("judgement_insight_id")), None)
        if representative is not None:
            judgement = str(representative.get("statement") or representative.get("resolved_answer")
                            or representative.get("answer_text") or representative.get("headline")
                            or representative.get("business_question") or "").strip()
            implication = str(representative.get("implication") or representative.get("decision_impact") or "").strip()
            if chapter.get("judgement") != judgement or chapter.get("operating_implication") != implication:
                raise ValueError("chapter judgement 必须投影自同一真实洞察")
        actual = assess_depth(question, evidence_ids=record_evidence_ids(chapter),
            actions=[item for item in model.get("actions", []) if item.get("action_id") in chapter.get("action_ids", [])],
            insights=[item for item in insights if item.get("insight_id") == chapter.get("judgement_insight_id")], **kwargs)
        if chapter.get("achieved_depth") != actual["achieved_depth"]:
            raise ValueError("chapter depth 与实际证据和经营判断不一致")
        for role in ("driver_evidence_ids", "segment_evidence_ids"):
            if chapter.get(role, []) != actual[role]:
                raise ValueError("chapter depth 证据角色与实际结构不一致")
        if chapter.get("selection_status") == "selected" and actual["achieved_depth"] < 4:
            raise ValueError("核心 chapter depth 不得低于4")
        if chapter.get("selection_status") == "selected" and chapter.get("judgement_insight_id") not in actual["judgement_insight_ids"]:
            raise ValueError("核心 chapter judgement 未绑定合格经营判断")


_GENERIC_EVIDENCE_SCOPES = {
    "",
    "loaded source table",
    "confirmed dataset scope",
    "confirmed semantic filters",
}


def validate_engine_evidence_provenance(evidence_index: dict[str, dict[str, Any]]) -> None:
    """Fail closed when deterministic engine evidence drops known provenance."""

    for evidence_id, evidence in evidence_index.items():
        if not isinstance(evidence, dict) or evidence.get("provenance_source") != "analysis_engine":
            continue
        scope = str(evidence.get("filter_scope") or "").strip().lower()
        sample_count = evidence.get("sample_count")
        if scope in _GENERIC_EVIDENCE_SCOPES:
            raise ValueError(f"evidence {evidence_id} 的 filter_scope 不能使用泛化范围")
        if isinstance(sample_count, bool) or not isinstance(sample_count, int) or sample_count < 0:
            raise ValueError(f"evidence {evidence_id} 的 sample_count 必须是已知源行数")

LOCKED_ADAPTIVE_KEYS = {
    "scope_contract",
    "analysis_lenses",
    "analysis_chapters",
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


def _content_hash(value: object) -> str:
    return canonical_sha256(value)


def validate_content_lock(model: dict[str, Any]) -> None:
    """Verify persisted analysis-stage content locks without reusing narrative text."""

    lock = model.get("content_lock")
    if lock is None:
        return
    if not isinstance(lock, dict):
        raise ValueError("content_lock 必须是对象")
    adaptive_hashes = lock.get("adaptive_hashes")
    slide_hashes = lock.get("slide_hashes")
    if not isinstance(adaptive_hashes, dict) or set(adaptive_hashes) != LOCKED_ADAPTIVE_KEYS:
        raise ValueError("content_lock adaptive_hashes 无效")
    if not isinstance(slide_hashes, dict):
        raise ValueError("content_lock slide_hashes 无效")
    selection = model.get("value_selection", {})
    adaptive_values = {
        "scope_contract": scope_lock_projection(model),
        "analysis_lenses": model.get("analysis_lenses", []),
        "analysis_chapters": model.get("analysis_chapters", []),
        # Keep this derived QA state inside the same lock as the analysis
        # lenses.  content_hash only hashes these leaves, never itself.
        "content_validation": content_validation_lock_value(model.get("content_validation")),
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
        "non_retail_projection": build_non_retail_projection(model),
        "renderer_content": renderer_content_lock_projection(model),
    }
    for key, value in adaptive_values.items():
        if adaptive_hashes.get(key) != _content_hash(value):
            raise ValueError(f"content_lock {key} 无效")
    slide_ids = {str(page.get("slide_id") or "") for page in model.get("slide_plan", [])}
    if not slide_ids or set(slide_hashes) != slide_ids:
        raise ValueError("content_lock slide_hashes 与 slide_plan 不一致")
    for page in model.get("slide_plan", []):
        locked = {key: page.get(key) for key in sorted(LOCKED_SLIDE_KEYS)}
        slide_id = str(page.get("slide_id") or "")
        if slide_hashes.get(slide_id) != _content_hash(locked):
            raise ValueError(f"content_lock 页面 {slide_id} 无效")
    if lock.get("content_hash") != _content_hash(
        {"adaptive_hashes": adaptive_hashes, "slide_hashes": slide_hashes}
    ):
        raise ValueError("content_lock content_hash 无效")

PLACEHOLDER_PATTERN = re.compile(r"\{[^{}]+\}")


def _string_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _string_values(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from _string_values(child)


def _evidence_references(model: dict[str, Any]) -> set[str]:
    references: set[str] = set()
    for collection in ("kpis", "insights", "actions", "levers", "charts", "analysis_chapters", "slide_plan"):
        for item in model.get(collection, []):
            references.update(str(value) for value in item.get("evidence_ids", []))
    return references


def _validate_scope_catalog(
    scope_catalog: Any,
    quality_decisions: Any,
    *,
    context: str,
) -> set[str]:
    if not isinstance(scope_catalog, list) or not scope_catalog:
        raise ValueError(f"{context} scope_catalog 必须是非空列表")
    required_scope = {
        "scope_id", "definition", "included_rows", "excluded_rows", "filters",
        "quality_policy_ids",
    }
    scope_ids: set[str] = set()
    for scope in scope_catalog:
        if not isinstance(scope, dict) or required_scope - set(scope):
            raise ValueError(f"{context} scope_catalog 记录字段不完整")
        scope_id = str(scope.get("scope_id") or "").strip()
        if not scope_id or scope_id in scope_ids:
            raise ValueError(f"{context} scope_id 为空或重复：{scope_id}")
        if any(
            isinstance(scope.get(field), bool)
            or not isinstance(scope.get(field), int)
            or scope[field] < 0
            for field in ("included_rows", "excluded_rows")
        ):
            raise ValueError(f"{context} scope {scope_id} 行数无效")
        if not isinstance(scope.get("filters"), list) or not isinstance(scope.get("quality_policy_ids"), list):
            raise ValueError(f"{context} scope {scope_id} filters 或 quality_policy_ids 无效")
        scope_ids.add(scope_id)

    required_decision = {
        "issue_id", "issue_type", "severity", "affected_rows",
        "affected_metric_value", "affected_fields", "decision_impact", "options",
        "selected_policy", "scope_ids", "status", "disclosure",
    }
    if not isinstance(quality_decisions, list):
        raise ValueError(f"{context} quality_decisions 必须是列表")
    for decision in quality_decisions:
        if not isinstance(decision, dict) or required_decision - set(decision):
            raise ValueError(f"{context} quality_decisions 记录字段不完整")
        decision_scopes = {str(value) for value in decision.get("scope_ids", [])}
        unknown = decision_scopes - scope_ids
        if not decision_scopes or unknown:
            raise ValueError(
                f"{context} quality decision scope 无效：{', '.join(sorted(unknown)) or '缺失'}"
            )
    return scope_ids


def validate_scope_contract(model: dict[str, Any]) -> None:
    """Kernel models require calculation-owned scopes; legacy fixtures stay explicit."""
    transactional = model.get("transactional_commerce")
    if isinstance(transactional, dict) and "scope_catalog" in transactional:
        _validate_scope_catalog(
            transactional.get("scope_catalog"),
            transactional.get("quality_decisions"),
            context="transactional_commerce",
        )

    if "scope_catalog" not in model:
        if "analysis_brief" in model or "scope_contract_version" in model:
            raise ValueError("分析内核模型缺少 scope_catalog")
        return
    scope_ids = _validate_scope_catalog(
        model.get("scope_catalog"), model.get("quality_decisions"), context="report_model"
    )
    catalog = {item["scope_id"]: item for item in model["scope_catalog"]}
    modern = "analysis_brief" in model or "scope_contract_version" in model
    if modern:
        if model.get("scope_contract_version") != SCOPE_VERSION:
            raise ValueError("scope_contract_version 无效")
        root = catalog.get("source_rows", {})
        if root.get("kind") != "source" or root.get("excluded_rows") != 0 or root.get("parent_scope_id") is not None:
            raise ValueError("scope_catalog 源范围无效")
        if root.get("included_rows") != model.get("source", {}).get("loaded_row_count"):
            raise ValueError("scope_catalog 源行数与 loaded_row_count 不一致")
        visiting, visited = set(), set()
        def visit(scope_id):
            if scope_id in visited:
                return
            if scope_id in visiting or scope_id not in catalog:
                raise ValueError("scope_catalog 依赖循环或引用未知范围")
            visiting.add(scope_id)
            scope = catalog[scope_id]
            kind = scope.get("kind")
            if kind in {"source", "atomic", "comparison"}:
                fingerprint = scope.get("population_sha256")
                if not isinstance(fingerprint, str) or len(fingerprint) != 64 or any(char not in "0123456789abcdef" for char in fingerprint):
                    raise ValueError("scope_catalog 缺少有效 population_sha256")
            if kind in {"atomic", "comparison"}:
                parent = scope.get("parent_scope_id")
                visit(parent)
                if scope["included_rows"] + scope["excluded_rows"] != catalog[parent]["included_rows"]:
                    raise ValueError("scope_catalog 子范围行数不守恒")
                if kind == "atomic":
                    identity = {"kind": kind, "parent_scope_id": parent, "rules": scope.get("rules")}
                else:
                    members = scope.get("member_scope_ids")
                    if not isinstance(members, list) or len(members) < 2 or members != sorted(set(members)):
                        raise ValueError("scope_catalog 比较范围成员无效")
                    for member in members:
                        visit(member)
                    counts = [catalog[member]["included_rows"] for member in members]
                    if not max(counts) <= scope["included_rows"] <= sum(counts):
                        raise ValueError("scope_catalog 比较范围并集计数无效")
                    identity = {"kind": kind, "member_scope_ids": members, "relationship": "separate_denominators"}
                    if scope.get("relationship") != "separate_denominators":
                        raise ValueError("scope_catalog 比较关系无效")
                if scope_id != "scope:" + canonical_sha256(identity)[:24]:
                    raise ValueError("scope_catalog 范围规则指纹不一致")
            elif scope_id.startswith("scope:"):
                raise ValueError("scope_catalog 计算范围类型无效")
            visiting.remove(scope_id)
            visited.add(scope_id)
        for scope_id in catalog:
            visit(scope_id)

    def validate_bindings(value):
        if isinstance(value, dict):
            for child in value.values():
                validate_bindings(child)
        elif not isinstance(value, str) or value not in scope_ids:
            raise ValueError("evidence scope_bindings 引用了未知范围")

    evidence_scopes: dict[str, str] = {}
    for evidence_id, evidence in model.get("evidence_index", {}).items():
        if not isinstance(evidence, dict):
            raise ValueError(f"evidence {evidence_id} 必须是对象")
        scope_id = str(evidence.get("scope_id") or "").strip()
        if scope_id not in scope_ids:
            raise ValueError(f"evidence {evidence_id} 缺少或引用未知 scope_id：{scope_id}")
        evidence_scopes[str(evidence_id)] = scope_id
        if modern:
            if evidence.get("sample_count") != catalog[scope_id]["included_rows"]:
                raise ValueError(f"evidence {evidence_id} 样本行数与 scope 不一致")
            if str(evidence_id).startswith("followup:") or "result" in evidence:
                from analysis_followup import _result_hash
                result = evidence.get("result")
                if not isinstance(result, dict) or any(
                    result.get(field) != evidence.get(field)
                    for field in ("scope_id", "scope_bindings", "sample_count")
                ):
                    raise ValueError(f"evidence {evidence_id} result scope 镜像不一致")
                if evidence.get("result_hash") != _result_hash(result):
                    raise ValueError(f"evidence {evidence_id} result_hash 无效")
            for field in ("scope_bindings", "metric_scope_bindings"):
                if field in evidence:
                    validate_bindings(evidence[field])

    for collection in ("insights", "analysis_chapters", "charts", "actions"):
        for item in model.get(collection, []):
            refs = record_evidence_ids(item)
            if modern and collection == "analysis_chapters" and item.get("selection_status") != "selected" and not refs:
                if item.get("scope_id") is not None or not item.get("scope_disclosure"):
                    raise ValueError("无证据章节不得声明数字范围")
                continue
            scope_id = str(item.get("scope_id") or "").strip()
            if scope_id not in scope_ids:
                raise ValueError(f"{collection} 记录缺少或引用未知 scope_id：{scope_id}")
            if any(ref not in evidence_scopes for ref in refs):
                raise ValueError(f"{collection} 范围引用未知 evidence")
            referenced_scopes = {evidence_scopes[ref] for ref in refs}
            if referenced_scopes and referenced_scopes != {scope_id}:
                comparison = catalog[scope_id]
                if comparison.get("kind") != "comparison" or set(comparison.get("member_scope_ids", [])) != referenced_scopes or not item.get("scope_disclosure"):
                    raise ValueError(f"{collection} 混用了不同数字范围且未显式拆分")
            if modern and (not refs or not item.get("scope_disclosure")):
                raise ValueError(f"{collection} 缺少 scope 证据或披露")


def _is_engineering_dossier(model: dict[str, Any]) -> bool:
    return str(model.get("request", {}).get("analysis_intent") or "") == "engineering_regression"


def _non_retail_binding_error(message: str) -> None:
    raise ValueError("non_retail_claim_binding: " + message)


def _followup_group_values(evidence: dict[str, Any], dimension: str) -> dict[str, float]:
    if str(evidence.get("dimension") or "") != dimension:
        _non_retail_binding_error("evidence dimension 不匹配")
    result = evidence.get("result")
    groups = result.get("groups") if isinstance(result, dict) else None
    if not isinstance(groups, list) or not groups:
        _non_retail_binding_error("evidence 缺少分组结果")
    values: dict[str, float] = {}
    for group in groups:
        dimensions = group.get("dimensions") if isinstance(group, dict) else None
        value = group.get("metric") if isinstance(group, dict) else None
        if not isinstance(dimensions, list) or len(dimensions) != 1 or not isinstance(value, (int, float)):
            _non_retail_binding_error("evidence 分组格式无效")
        values[str(dimensions[0])] = float(value)
    return values


def _validate_non_retail_binding_record(
    record: dict[str, Any], *, expected_lens: str, evidence_index: dict[str, Any], kind: str,
) -> None:
    binding = record.get("claim_binding")
    if not isinstance(binding, dict) or binding.get("lens") != expected_lens:
        _non_retail_binding_error(f"{kind} 缺少或错误的 lens binding")
    if record.get("lens") != expected_lens:
        _non_retail_binding_error(f"{kind} lens 与 binding 不一致")
    claims = binding.get("claims")
    if not isinstance(claims, list) or not claims:
        _non_retail_binding_error(f"{kind} claims 不能为空")
    evidence_ids = [str(value) for value in record.get("evidence_ids", [])]
    if {str(claim.get("evidence_id") or "") for claim in claims if isinstance(claim, dict)} != set(evidence_ids):
        _non_retail_binding_error(f"{kind} evidence_ids 与 binding 不一致")
    fields = ("evidence_id", "dimension", "subject_value", "metric", "actual_value", "relation")
    required_text = [str(record.get("statement") or record.get("headline") or "")]
    if kind == "action":
        required_text = [str(record.get("text") or ""), str(record.get("verification_signal") or "")]
    for claim in claims:
        if not isinstance(claim, dict) or any(field not in claim for field in fields):
            _non_retail_binding_error(f"{kind} claim 字段不完整")
        evidence_id = str(claim["evidence_id"])
        evidence = evidence_index.get(evidence_id)
        if not isinstance(evidence, dict) or str(evidence.get("metric") or "") != str(claim["metric"]):
            _non_retail_binding_error(f"{kind} metric evidence 不匹配")
        values = _followup_group_values(evidence, str(claim["dimension"]))
        subject = str(claim["subject_value"])
        if subject not in values or not isinstance(claim["actual_value"], (int, float)):
            _non_retail_binding_error(f"{kind} subject 或实际值无效")
        actual = float(claim["actual_value"])
        if not math.isclose(actual, values[subject], rel_tol=1e-9, abs_tol=1e-9):
            _non_retail_binding_error(f"{kind} 实际值未由 evidence 重算")
        relation = str(claim["relation"])
        relation_text = ""
        if relation == "max":
            if not math.isclose(actual, max(values.values()), rel_tol=1e-9, abs_tol=1e-9):
                _non_retail_binding_error(f"{kind} max 关系不成立")
            relation_text = "最高"
        elif relation == "min":
            if not math.isclose(actual, min(values.values()), rel_tol=1e-9, abs_tol=1e-9):
                _non_retail_binding_error(f"{kind} min 关系不成立")
            relation_text = "最低"
        elif relation == "rank_desc":
            rank = claim.get("rank")
            expected_rank = sorted(values, key=lambda key: (-values[key], key)).index(subject) + 1
            if rank != expected_rank:
                _non_retail_binding_error(f"{kind} 排名关系不成立")
            relation_text = f"第{expected_rank}高"
        else:
            _non_retail_binding_error(f"{kind} comparison relation 无效")
        allowed_display_metrics = {
            "delay_days": "延期",
            "cost_overrun": "超支",
            "quality_score": "质量",
        }
        display_metric = str(claim.get("display_metric") or claim["metric"])
        if str(claim["metric"]) in allowed_display_metrics and display_metric != allowed_display_metrics[str(claim["metric"])]:
            _non_retail_binding_error(f"{kind} display metric 无效")
        precision = claim.get("display_precision", 2)
        if precision not in {0, 1, 2}:
            _non_retail_binding_error(f"{kind} display precision 无效")
        expected_value = f"{actual:.{precision}f}"
        for text in required_text:
            if not all(token in text for token in (subject, display_metric, expected_value, relation_text)):
                _non_retail_binding_error(f"{kind} 文本未硬绑定对象、指标、数值或比较关系")


def _validate_non_retail_claim_bindings(model: dict[str, Any]) -> None:
    # One projection owns both generation-time and validator-time truth.  It
    # rejects duplicate same-lens records rather than silently selecting first.
    build_non_retail_projection(model)


def _validate_engineering_dossier(model: dict[str, Any], slides: list[dict[str, Any]]) -> None:
    """Validate the QA-only policy separately from business report narratives."""

    allowed_roles = {"cover", "executive-summary", "data-appendix"}
    required_roles = allowed_roles
    roles = {str(slide.get("role") or "") for slide in slides}
    if not 3 <= len(slides) <= 6:
        raise ValueError(f"engineering_regression dossier 必须为 3–6 页，当前 {len(slides)} 页")
    if not required_roles <= roles or not roles <= allowed_roles:
        raise ValueError("engineering_regression dossier 只能使用 cover、executive-summary、data-appendix 角色")
    if any(model.get(key) for key in ("insights", "actions", "levers", "charts")):
        raise ValueError("engineering_regression dossier 不得包含经营洞察、行动、杠杆或图表")
    for slide in slides:
        if slide.get("content_exemption") != "qa":
            raise ValueError("engineering_regression dossier 页面必须标记 content_exemption=qa")
        if not str(slide.get("claim") or "").strip() or not str(slide.get("purpose") or "").strip():
            raise ValueError("engineering_regression dossier 不得包含空页面")


def validate_report_model(model: dict[str, Any], *, enforce_narrative: bool = True) -> None:
    if model.get("contract_version") == "html-chapters/1":
        from html_analysis import verify, check_binding
        verify(model)
        verify(model["snapshot"])
        check_binding(model["snapshot"], model["binding"])
        from summary_contract import validate_summary
        validate_summary(model)
        if model.get('action_revision') or model['snapshot'].get('capabilities', {}).get('action_target_version'):
            from action_target_contract import validate_target
            for action in model['actions']:
                refs = {e for c in model['chapters'] if c['id'] in action['chapter_ids'] for e in c['evidence_ids']}
                validate_target(action, model['snapshot'], refs, require_binding=True)
        if model.get("ppt_supported") is not False or "slide_plan" in model:
            raise ValueError("新版 HTML 合同不得伪装成已支持 PPT")
        return
    missing = REQUIRED_MODEL_KEYS - set(model)
    if missing:
        raise ValueError(f"report_model v2 缺少字段：{', '.join(sorted(missing))}")
    if model.get("schema_version") != "2.0":
        raise ValueError("schema_version 必须为 2.0")
    validate_formal_renderer_records(model)
    validate_content_lock(model)
    validate_scope_contract(model)
    validate_depth_evidence_contract(model)

    slides = model.get("slide_plan", [])
    engineering_dossier = _is_engineering_dossier(model)
    if (
        slides
        and not engineering_dossier
        and any("content_refs" in slide for slide in slides)
        and not all("story_role" in slide for slide in slides)
    ):
        raise ValueError("自适应叙事的每页都必须提供 story_role")

    # v2.0 remains additive: legacy persisted models are accepted, while new
    # builders that opt into quality fields must satisfy the stronger contract.
    quality_keys = {"analysis_contract", "quality_decisions", "analysis_lenses", "content_validation"}
    present_quality_keys = quality_keys & set(model)
    if present_quality_keys and present_quality_keys != quality_keys:
        raise ValueError("分析质量字段必须完整提供：analysis_contract、quality_decisions、analysis_lenses、content_validation")
    if present_quality_keys:
        validate_question_depth_contract(model.get("analysis_lenses", []))
        for evidence_id, evidence in model.get("evidence_index", {}).items():
            if not evidence.get("quality_managed"):
                # Renderers and compatibility callers may attach transient
                # evidence annotations after the deterministic catalog is built.
                continue
            required = {"calculation", "filter_scope", "sample_count", "affected_rows", "affected_amount", "limitations", "business_objects"}
            absent = required - set(evidence)
            if absent:
                raise ValueError(f"evidence {evidence_id} 缺少质量字段：{', '.join(sorted(absent))}")
        validate_engine_evidence_provenance(model.get("evidence_index", {}))
        for insight in model.get("insights", []):
            required = {"claim_type", "evidence_strength", "limitations", "value_score"}
            absent = required - set(insight)
            if absent:
                raise ValueError("洞察缺少质量字段：" + ", ".join(sorted(absent)))
            if str(insight["claim_type"]) not in {"fact", "diagnostic", "inference", "hypothesis"}:
                raise ValueError("洞察 claim_type 无效")
            if str(insight["evidence_strength"]) not in {"high", "medium", "low"}:
                raise ValueError("洞察 evidence_strength 无效")
        for action in model.get("actions", []):
            required = {"target", "basis", "rationale", "evidence_ids", "verification_signal"}
            if any(not str(action.get(key) or "").strip() for key in required) or not action.get("formal", True):
                raise ValueError("行动缺少对象、依据、证据或验证信号")
        _validate_non_retail_claim_bindings(model)

    for slide in model.get("slide_plan", []):
        layout_id = slide.get("layout_id")
        if layout_id not in ALLOWED_LAYOUTS:
            raise ValueError(f"未知 layout_id：{layout_id}")
        visual_spec = slide.get("visual_spec")
        if visual_spec is not None:
            tone = visual_spec.get("tone")
            density = visual_spec.get("density")
            if tone not in ALLOWED_TONES:
                raise ValueError(f"未知 visual_spec tone：{tone}")
            if density not in ALLOWED_DENSITIES:
                raise ValueError(f"未知 visual_spec density：{density}")
            if not str(visual_spec.get("eyebrow", "")).strip():
                raise ValueError("visual_spec eyebrow 不能为空")
            if "display_claim" in visual_spec and not str(
                visual_spec.get("display_claim", "")
            ).strip():
                raise ValueError("visual_spec display_claim 不能为空")
            contexts = visual_spec.get("comparison_contexts", [])
            if not isinstance(contexts, list) or len(contexts) > 2:
                raise ValueError("visual_spec comparison_contexts 必须为最多两项的列表")
            for context in contexts:
                if context.get("kind") not in ALLOWED_COMPARISON_KINDS:
                    raise ValueError("visual_spec comparison context kind 无效")
                if not all(
                    str(context.get(field, "")).strip()
                    for field in ("label", "current_label", "baseline_label")
                ):
                    raise ValueError("visual_spec comparison context 字段不完整")

    for text in _string_values(model):
        if PLACEHOLDER_PATTERN.search(text):
            raise ValueError(f"存在未解析 placeholder 占位符：{text}")

    evidence_ids = set(model.get("evidence_index", {}))
    dangling = _evidence_references(model) - evidence_ids
    if dangling:
        raise ValueError(f"存在悬空 evidence ID：{', '.join(sorted(dangling))}")
    for slide in model.get("slide_plan", []):
        visual_spec = slide.get("visual_spec")
        if not visual_spec:
            continue
        focus_ids = {str(value) for value in visual_spec.get("focus_evidence_ids", [])}
        unknown_focus = focus_ids - evidence_ids
        if unknown_focus:
            raise ValueError(
                "visual_spec focus evidence 无效：" + ", ".join(sorted(unknown_focus))
            )
        outside_slide = focus_ids - set(slide.get("evidence_ids", []))
        if outside_slide:
            raise ValueError(
                f"页面 {slide.get('slide_id')} 的 focus evidence 不属于本页证据："
                + ", ".join(sorted(outside_slide))
            )
        chart_focus = visual_spec.get("chart_focus")
        if chart_focus is not None and not (
            chart_focus.get("series_name") or chart_focus.get("category_name")
        ):
            raise ValueError("visual_spec chart_focus 必须包含系列名或类目名")

    has_content_refs = any("content_refs" in slide for slide in slides)
    if is_modern_model(model) and slides and not has_content_refs:
        raise ValueError("现代 report_model 必须提供 content_refs，不能降级为 legacy 投影")
    if is_modern_model(model) and has_content_refs and not all(
        "content_ref_bindings" in slide for slide in slides
    ):
        raise ValueError("现代 report_model 的每页都必须提供 content_ref_bindings")
    new_projection = has_content_refs or any("role" in slide for slide in slides)
    if new_projection and not engineering_dossier and any(
        slide.get("content_exemption") == "qa" for slide in slides
    ):
        raise ValueError(
            "content_exemption=qa 仅允许 engineering_regression dossier 使用"
        )
    if has_content_refs and not all("content_refs" in slide for slide in slides):
        raise ValueError("新 report_model 的每页都必须提供 content_refs")
    if has_content_refs:
        validate_content_refs(model)
        for slide in slides:
            required_page_fields = {"role", "page_reason", "selection_score", "content_refs"}
            absent = required_page_fields - set(slide)
            if absent:
                raise ValueError("新页面缺少编排字段：" + ", ".join(sorted(absent)))
            if slide["role"] != slide.get("layout_id"):
                raise ValueError("页面 role 必须与 layout_id 一致")
            if not isinstance(slide["selection_score"], (int, float)):
                raise ValueError("页面 selection_score 必须为数值")
            if "story_role" in slide and slide["story_role"] not in ALLOWED_STORY_ROLES:
                raise ValueError("页面 story_role 无效")
            refs = slide["content_refs"]
            layout = slide["layout_id"]
            if layout == "executive-summary":
                summary_refs = refs.get("summary_refs", {})
                if len(summary_refs.get("conclusion_indexes", [])) > 3 or len(summary_refs.get("priority_action_indexes", [])) > 2:
                    raise ValueError("executive-summary 超出布局容量")
            if layout == "kpi-spotlight" and len(refs.get("kpi_ids", [])) > 6:
                raise ValueError("kpi-spotlight 超出布局容量")
            if layout == "driver-levers" and len(refs.get("lever_ids", [])) > 4:
                raise ValueError("driver-levers 超出布局容量")
            if layout == "risk-opportunity" and (
                len(refs.get("opportunity_insight_ids", [])) > 2
                or len(refs.get("risk_insight_ids", [])) > 2
            ):
                raise ValueError("risk-opportunity 超出布局容量")
            if layout == "action-roadmap" and len(refs.get("action_ids", [])) > 3:
                raise ValueError("action-roadmap 超出布局容量")
    elif slides:
        warnings.warn(
            "legacy projection warning: v2 report_model 缺少 content_refs，将按旧投影消费",
            UserWarning,
            stacklevel=2,
        )
    if has_content_refs and engineering_dossier:
        _validate_engineering_dossier(model, slides)
    story_pages = [slide for slide in slides if "story_role" in slide]
    if story_pages and enforce_narrative:
        validate_story_topology(story_pages)
        narrative_validation = model.get("content_validation", {}).get("narrative_validation", {})
        if isinstance(narrative_validation, dict) and narrative_validation.get("story_order_valid") is False:
            raise ValueError("自适应叙事故事顺序验证失败")
    if not has_content_refs and not 8 <= len(slides) <= 10:
        lens_constrained = bool(model.get("analysis_lenses")) and all(
            slide.get("layout_id") == "cover"
            or slide.get("content_exemption")
            or bool(slide.get("lens"))
            for slide in slides
        )
        if not lens_constrained:
            raise ValueError(f"slide_plan 必须为 8–10 页，当前 {len(slides)} 页")
    if not story_pages and len(slides) >= 5 and len({slide.get("silhouette") for slide in slides}) < 5:
        raise ValueError("slide_plan 至少需要 5 类页面轮廓")
    content_slides = [slide for slide in slides if slide.get("layout_id") != "cover"]
    if not story_pages:
        for previous, current in zip(content_slides, content_slides[1:]):
            if previous.get("silhouette") == current.get("silhouette"):
                raise ValueError(
                    f"相邻内容页轮廓重复：{previous.get('slide_id')} / {current.get('slide_id')}"
                )

    slide_ids = [slide.get("slide_id") for slide in slides]
    if len(slide_ids) != len(set(slide_ids)) or any(not value for value in slide_ids):
        raise ValueError("slide_id 必须非空且唯一")
    if engineering_dossier:
        return
    chart_ids = [chart.get("chart_id") for chart in model.get("charts", [])]
    if len(chart_ids) != len(set(chart_ids)) or any(not value for value in chart_ids):
        raise ValueError("chart_id 必须非空且唯一")
    known_chart_ids = set(chart_ids)
    missing_chart_ids = {
        str(chart_id)
        for slide in slides
        for chart_id in slide.get("chart_ids", [])
        if chart_id not in known_chart_ids
    }
    if missing_chart_ids:
        raise ValueError(
            "slide_plan 引用了不存在的 chart："
            + ", ".join(sorted(missing_chart_ids))
        )
    charts_by_id = {
        chart["chart_id"]: chart for chart in model.get("charts", [])
    }
    chart_contract_fields = {
        "unit",
        "display_unit",
        "display_scale",
        "number_format",
        "scope_label",
        "takeaway",
    }
    used_chart_ids = {
        chart_id for slide in slides for chart_id in slide.get("chart_ids", [])
    }
    for chart_id in used_chart_ids:
        chart = charts_by_id[chart_id]
        missing_contract = chart_contract_fields - set(chart)
        if missing_contract:
            raise ValueError(
                f"chart {chart_id} 缺少展示契约：{', '.join(sorted(missing_contract))}"
            )
        if float(chart.get("display_scale", 0)) <= 0:
            raise ValueError(f"chart {chart_id} 的 display_scale 必须大于 0")
    for slide in slides:
        referenced_charts = [
            charts_by_id[chart_id] for chart_id in slide.get("chart_ids", [])
        ]
        if not referenced_charts:
            continue
        chart_evidence = {
            evidence_id
            for chart in referenced_charts
            for evidence_id in chart.get("evidence_ids", [])
        }
        claim_evidence = set(slide.get("claim_evidence_ids", []))
        if not claim_evidence or not claim_evidence & chart_evidence:
            raise ValueError(
                f"图表页 {slide.get('slide_id')} 的标题 evidence 与 chart 不一致"
            )
    conclusion_evidence = model.get("executive_summary", {}).get(
        "key_conclusion_evidence_ids", []
    )
    visual_evidence = {
        evidence_id
        for chart_id in used_chart_ids
        for evidence_id in charts_by_id[chart_id].get("evidence_ids", [])
    }
    lens_constrained = bool(model.get("analysis_lenses"))
    for index, evidence_ids in enumerate(conclusion_evidence[:2], start=1):
        if (
            not story_pages
            and evidence_ids
            and not set(evidence_ids) & visual_evidence
            and not (lens_constrained and not visual_evidence)
        ):
            raise ValueError(f"第 {index} 条管理结论缺少直接图表证据")
    if not has_content_refs and slides and all(slide.get("content_exemption") for slide in slides):
        return
    # Capacity is a deterministic structural gate and should take precedence
    # over derived content-QA freshness when a caller has edited a title.
    validate_layout_capacity(model)
    if present_quality_keys and has_content_refs:
        computed_content = validate_content_value(model)
        declared_content = model.get("content_validation", {})
        if declared_content.get("status") != computed_content["status"]:
            raise ValueError("content_validation 与内容质量校验结果不一致")
        if computed_content["blocking"]:
            raise ValueError("内容质量阻断：" + ", ".join(item["code"] for item in computed_content["blocking"]))
