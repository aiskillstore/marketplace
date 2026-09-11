"""Canonical, evidence-recomputable projection for formal non-retail content."""
from __future__ import annotations

import math
from typing import Any

from canonical_json import canonical_sha256
from content_resolver import canonical_content_ref_bindings, canonical_formal_renderer_records


NON_RETAIL_SPECS = {
    "content_operations": {
        "lens": "content_efficiency",
        "insight_id": "insight-content-efficiency",
        "action_id": "action-content-efficiency",
        "claims": (("conversion_rate", "max", "conversion_rate", 2), ("cost", "rank_desc", "cost", 2)),
    },
    "project_operations": {
        "lens": "delivery_efficiency",
        "insight_id": "insight-delivery-efficiency",
        "action_id": "action-delivery-efficiency",
        "claims": (("delay_days", "max", "延期", 1), ("cost_overrun", "max", "超支", 1), ("quality_score", "min", "质量", 1)),
    },
}

RETAIL_ONLY_LENS_IDS = {"geography", "product", "customer", "concentration", "growth_driver"}
RETAIL_ONLY_OBJECTS = {"sales", "product", "customer", "geography", "retail_growth_table"}
RETAIL_TEMPLATE_SIGNATURES = {
    "不同地域的贡献或表现差异在哪里？", "哪些产品或品类贡献主要结果？",
    "客户结构是否集中或存在差异？", "主要贡献是否过度集中于少数对象？",
    "增长变化有哪些可验证的结构线索？",
}


def _fail(message: str) -> None:
    raise ValueError("non_retail_claim_binding: " + message)


def _canonical_hash(value: object) -> str:
    return canonical_sha256(value)


def content_validation_lock_value(value: Any) -> dict[str, Any]:
    """Lock analysis QA dispositions, not finalizer-only narrative diagnostics."""
    if not isinstance(value, dict):
        return {}
    # ``warnings`` and narrative diagnostics are page-order-dependent output
    # observations.  The analysis lock protects the stable pass/fail decision
    # and blockers; finalization may append warnings without rewriting truth.
    return {key: value[key] for key in ("status", "blocking") if key in value}


def renderer_content_lock_projection(model: dict[str, Any]) -> dict[str, Any]:
    """One complete, position-stable lock input for all renderer-visible content."""
    records = canonical_formal_renderer_records(model)
    pages = [
        {"slide_id": page.get("slide_id"), "content_refs": page.get("content_refs"), "bindings": canonical_content_ref_bindings(model, page)}
        for page in sorted(model.get("slide_plan", []), key=lambda item: str(item.get("slide_id") or ""))
        if isinstance(page, dict) and isinstance(page.get("content_refs"), dict)
    ]
    return {
        "value_selection": model.get("value_selection"), **records,
        "executive_summary": model.get("executive_summary"), "pages": pages,
        "charts": model.get("charts"), "narrative_selection": model.get("narrative_selection"),
    }


def _groups(evidence: dict[str, Any], dimension: str) -> dict[str, float]:
    if str(evidence.get("dimension") or "") != dimension:
        _fail("evidence dimension 不匹配")
    result = evidence.get("result")
    rows = result.get("groups") if isinstance(result, dict) else None
    if evidence.get("kind") == "dimension_contribution":
        source_rows = evidence.get("rows")
        if not isinstance(source_rows, list) or any(not isinstance(row, dict) or row.get("is_other") for row in source_rows):
            _fail("evidence 完整分组结果不可用")
        rows = [{"dimensions": [row.get("value")], "metric": row.get("metric")} for row in source_rows]
    if not isinstance(rows, list) or not rows:
        _fail("evidence 缺少分组结果")
    values: dict[str, float] = {}
    for row in rows:
        dimensions = row.get("dimensions") if isinstance(row, dict) else None
        value = row.get("metric") if isinstance(row, dict) else None
        if not isinstance(dimensions, list) or len(dimensions) != 1 or dimensions[0] is None or type(value) not in {int, float} or not math.isfinite(float(value)):
            _fail("evidence 分组格式无效")
        subject = str(dimensions[0])
        if subject in values:
            _fail("evidence 分组对象重复")
        values[subject] = float(value)
    return values


def _target_records(model: dict[str, Any], *, lens: str, kind: str) -> list[dict[str, Any]]:
    key = "insights" if kind == "insight" else "actions"
    records = [item for item in model.get(key, []) if isinstance(item, dict) and item.get("lens") == lens]
    if len(records) != 1:
        _fail(f"{lens} 必须且只能有一条正式 {kind}")
    return records


def _validate_claims(record: dict[str, Any], *, spec: dict[str, Any], evidence_index: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    lens = spec["lens"]
    binding = record.get("claim_binding")
    if not isinstance(binding, dict) or set(binding) != {"lens", "claims"} or binding.get("lens") != lens:
        _fail(f"{kind} 缺少或错误的 lens binding")
    claims = binding.get("claims")
    expected = spec["claims"]
    if not isinstance(claims, list) or len(claims) != len(expected):
        _fail(f"{kind} claim 数量无效")
    if record.get("lens") != lens:
        _fail(f"{kind} lens 与 binding 不一致")
    evidence_ids = record.get("evidence_ids")
    if not isinstance(evidence_ids, list) or len(evidence_ids) != len(expected) or len(evidence_ids) != len(set(evidence_ids)):
        _fail(f"{kind} evidence_ids 基数或重复无效")
    canonical_claims: list[dict[str, Any]] = []
    for claim, (metric, relation, display_metric, precision) in zip(claims, expected):
        allowed = {"evidence_id", "dimension", "subject_value", "metric", "actual_value", "relation"}
        if relation == "rank_desc":
            allowed.add("rank")
        # Internal metrics deliberately retain their contract names.  Only
        # project metrics carry the fixed human-facing aliases below.
        if display_metric != metric:
            allowed.update({"display_metric", "display_precision"})
        if not isinstance(claim, dict) or set(claim) != allowed:
            _fail(f"{kind} claim schema 无效")
        evidence_id = str(claim.get("evidence_id") or "")
        if evidence_id != str(evidence_ids[len(canonical_claims)]):
            _fail(f"{kind} evidence_ids 顺序必须与 claims 一致")
        if str(claim.get("metric") or "") != metric or str(claim.get("relation") or "") != relation:
            _fail(f"{kind} claim metric 或关系无效")
        actual_display = str(claim.get("display_metric") or metric)
        actual_precision = claim.get("display_precision", 2)
        if actual_display != display_metric or actual_precision != precision:
            _fail(f"{kind} display alias 或 precision 无效")
        evidence = evidence_index.get(evidence_id)
        if not isinstance(evidence, dict) or str(evidence.get("metric") or "") != metric:
            _fail(f"{kind} metric evidence 不匹配")
        values = _groups(evidence, str(claim.get("dimension") or ""))
        subject = str(claim.get("subject_value") or "")
        actual = claim.get("actual_value")
        if subject not in values or type(actual) not in {int, float} or not math.isfinite(float(actual)) or float(actual) != values[subject]:
            _fail(f"{kind} 对象或实际值未由 evidence 重算")
        if relation == "max" and float(actual) != max(values.values()):
            _fail(f"{kind} max 关系不成立")
        if relation == "min" and float(actual) != min(values.values()):
            _fail(f"{kind} min 关系不成立")
        if relation == "rank_desc":
            rank = sorted(values, key=lambda key: (-values[key], key)).index(subject) + 1
            if claim.get("rank") != rank:
                _fail(f"{kind} 排名关系不成立")
        canonical_claims.append({key: claim[key] for key in sorted(allowed)})
    return canonical_claims


def _expected_text(spec: dict[str, Any], claims: list[dict[str, Any]]) -> dict[str, str]:
    data = {str(item["metric"]): item for item in claims}
    if spec["lens"] == "content_efficiency":
        rate, cost = data["conversion_rate"], data["cost"]
        channel = str(rate["subject_value"])
        rate_value = float(rate["actual_value"])
        cost_value = float(cost["actual_value"])
        rank = int(cost["rank"])
        statement = f"{channel} channel：conversion_rate {rate_value:.2f}% 最高；cost {cost_value:.2f} 第{rank}高，效率投入有取舍。"
        return {
            "headline": statement, "statement": statement,
            "action_headline": f"优先验证 {channel} channel 的效率—投入取舍",
            "text": f"优先验证 {channel} channel：conversion_rate {rate_value:.2f}% 为最高，cost {cost_value:.2f} 在 {{channel_count}} 个渠道中第{rank}高。",
            "target": f"{channel} channel（conversion_rate {rate_value:.2f}%，cost {cost_value:.2f}）",
            "basis": statement,
            "rationale": "待验证假设：在可比内容组合内小范围增配资源，能增加转化且不损伤转化效率或单位转化成本；当前排序不证明增配的因果效果。",
            "verification_signal": f"下一完整周期在可比内容组合内，{channel} channel 的 conversion_rate 不低于基期 {rate_value:.2f}%，转化量增加且单位转化成本不高于试验前；不能只比较渠道排名。",
        }
    delay, overrun, quality = (data[name] for name in ("delay_days", "cost_overrun", "quality_score"))
    same_team = len({delay["subject_value"], overrun["subject_value"], quality["subject_value"]}) == 1
    if same_team:
        statement = f"{delay['subject_value']}：三项同差，延期 {float(delay['actual_value']):.1f}最高；超支 {float(overrun['actual_value']):.1f}最高；质量 {float(quality['actual_value']):.1f}最低。"
    else:
        statement = f"不同队各最差：{delay['subject_value']} 延期 {float(delay['actual_value']):.1f}最高；{overrun['subject_value']} 超支 {float(overrun['actual_value']):.1f}最高；{quality['subject_value']} 质量 {float(quality['actual_value']):.1f}最低。"
    return {
        "headline": statement, "statement": statement, "action_headline": "按团队最差项建立交付纠偏复核", "text": statement,
        "target": f"{delay['subject_value']}/{overrun['subject_value']}/{quality['subject_value']} team：delay_days {float(delay['actual_value']):.2f}、cost_overrun {float(overrun['actual_value']):.2f}、quality_score {float(quality['actual_value']):.2f}",
        "basis": statement,
        "rationale": "待验证假设：排期校准与阶段检查能减少延期而不牺牲质量或抬高单任务超支；当前聚合差异不证明因果。",
        "verification_signal": "下一完整周期同阶段可比任务的平均延期低于试验前，平均质量不低于试验前，单任务超支不高于试验前；任务规模不同时不直接比较超支总额。",
    }


def build_non_retail_projection(model: dict[str, Any]) -> dict[str, Any] | None:
    """Return the single canonical formal-content projection, or ``None`` for retail/general models."""
    contract = model.get("analysis_contract")
    if not isinstance(contract, dict):
        return None
    semantic = contract.get("semantic_contract")
    outer_adapter = str(contract.get("adapter_id") or "")
    inner_adapter = str(semantic.get("adapter_id") or "") if isinstance(semantic, dict) else ""
    target_lenses = {spec["lens"] for spec in NON_RETAIL_SPECS.values()}
    has_formal_target = any(
        isinstance(item, dict) and item.get("lens") in target_lenses
        for key in ("insights", "actions") for item in model.get(key, [])
    )
    if outer_adapter not in NON_RETAIL_SPECS:
        if inner_adapter in NON_RETAIL_SPECS or has_formal_target:
            _fail("非零售正式内容的内外 adapter 不一致")
        return None
    spec = NON_RETAIL_SPECS[outer_adapter]
    if not isinstance(semantic, dict) or not (
        inner_adapter == outer_adapter
        and contract.get("adapter_maturity") == "experimental"
        and semantic.get("adapter_maturity") == "experimental"
        and contract.get("execution_profile") == semantic.get("execution_profile") == "general"
        and semantic.get("adapter_selection_reason") == "confirmed_experimental"
        and semantic.get("confirmation_status") == "confirmed"
    ):
        _fail("experimental adapter 未满足确认门禁")
    if set(contract.get("available_objects", [])) & RETAIL_ONLY_OBJECTS:
        _fail("非零售 adapter 不得声明零售专属 available_objects")
    for question in model.get("analysis_lenses", []):
        if not isinstance(question, dict):
            continue
        if (
            question.get("lens") in RETAIL_ONLY_LENS_IDS
            or set(question.get("required_objects", [])) & RETAIL_ONLY_OBJECTS
            or str(question.get("business_question") or "") in RETAIL_TEMPLATE_SIGNATURES
        ):
            _fail("非零售 adapter 不得使用零售专属 lens 或模板")
    lenses = [item for item in model.get("analysis_lenses", []) if isinstance(item, dict) and item.get("lens") == spec["lens"]]
    if len(lenses) != 1 or lenses[0].get("status") != "selected" or lenses[0].get("answer_status") != "answered":
        _fail("未 answered 的 lens 不得生成正式内容")
    lens = lenses[0]
    lens_ids = lens.get("evidence_ids")
    if not isinstance(lens_ids, list) or len(lens_ids) != len(spec["claims"]) or len(lens_ids) != len(set(lens_ids)):
        _fail("目标 lens evidence 基数或重复无效")
    evidence_index = model.get("evidence_index")
    if not isinstance(evidence_index, dict):
        _fail("evidence_index 无效")
    insight = _target_records(model, lens=spec["lens"], kind="insight")[0]
    action = _target_records(model, lens=spec["lens"], kind="action")[0]
    if insight.get("insight_id") != spec["insight_id"] or action.get("action_id") != spec["action_id"]:
        _fail("正式内容稳定 ID 无效")
    insight_claims = _validate_claims(insight, spec=spec, evidence_index=evidence_index, kind="insight")
    action_claims = _validate_claims(action, spec=spec, evidence_index=evidence_index, kind="action")
    if insight_claims != action_claims or list(insight.get("evidence_ids", [])) != lens_ids or list(action.get("evidence_ids", [])) != lens_ids:
        _fail("lens、insight 与 action evidence 必须精确一致")
    expected = _expected_text(spec, insight_claims)
    if spec["lens"] == "content_efficiency":
        channel_count = len(_groups(evidence_index[lens_ids[1]], "channel"))
        expected["text"] = expected["text"].format(channel_count=channel_count)
    if any(str(insight.get(field) or "") != expected[field] for field in ("headline", "statement")):
        _fail("insight 可见文本偏离规范证据结论")
    if any(insight.get(field) not in (None, "") for field in ("implication", "display")):
        _fail("insight 不得携带投影外可见字段")
    visible_action_fields = ("headline", "text", "target", "basis", "rationale", "verification_signal")
    expected_action = {"headline": expected["action_headline"], **{field: expected[field] for field in visible_action_fields if field != "headline"}}
    if any(str(action.get(field) or "") != expected_action[field] for field in visible_action_fields):
        _fail("action 可见文本偏离规范证据结论")
    if action.get("source_insight_ids") != [spec["insight_id"]] or type(action.get("priority")) is not int:
        _fail("action source link 或 priority 无效")
    selection = model.get("value_selection")
    if not isinstance(selection, dict):
        _fail("value_selection 无效")
    selected = [record for group in ("featured", "appendix", "dropped") for record in selection.get(group, []) if isinstance(record, dict) and record.get("insight_id") == spec["insight_id"]]
    if len(selected) != 1 or selected[0].get("evidence_ids") != lens_ids:
        _fail("value_selection 必须精确引用正式 insight 与 evidence")
    summary = model.get("executive_summary")
    if not isinstance(summary, dict):
        _fail("executive_summary 无效")
    summary_payload = {
        "key_conclusions": list(summary.get("key_conclusions", [])),
        "key_conclusion_evidence_ids": list(summary.get("key_conclusion_evidence_ids", [])),
        "priority_actions": list(summary.get("priority_actions", [])),
    }
    pages = []
    for page in model.get("slide_plan", []):
        if not isinstance(page, dict):
            continue
        refs = page.get("content_refs")
        if isinstance(refs, dict):
            bindings = canonical_content_ref_bindings(model, page)
            referenced = {entry["stable_id"] for entry in bindings}
            if spec["insight_id"] in referenced or spec["action_id"] in referenced:
                if page.get("content_ref_bindings") != bindings:
                    _fail("页面 content refs 未锁定为稳定业务 ID")
                pages.append({"slide_id": page.get("slide_id"), "evidence_ids": page.get("evidence_ids"), "content_refs": refs, "bindings": bindings})
    evidence_digest = []
    for evidence_id in lens_ids:
        evidence = evidence_index.get(evidence_id)
        if not isinstance(evidence, dict):
            _fail("目标 lens 引用了未知 evidence")
        evidence_digest.append({
            "evidence_id": evidence_id, "metric": evidence.get("metric"), "dimension": evidence.get("dimension"),
            "result": evidence.get("result"), "result_hash": evidence.get("result_hash"),
            "kind": evidence.get("kind"), "rows": evidence.get("rows"),
            "scope_id": evidence.get("scope_id"), "scope_bindings": evidence.get("scope_bindings"),
        })
        if evidence.get("kind") == "dimension_contribution":
            _groups(evidence, str(evidence.get("dimension")))
        elif evidence.get("result_hash") != _canonical_hash(evidence.get("result")):
            _fail("evidence result_hash 与结果不一致")
    return {
        "schema_version": "non_retail_projection.v1",
        "contract": {key: contract.get(key) for key in ("adapter_id", "adapter_maturity", "execution_profile")},
        "semantic_contract": {key: semantic.get(key) for key in ("adapter_id", "adapter_maturity", "execution_profile", "adapter_selection_reason", "confirmation_status")},
        "lens": {key: lens.get(key) for key in ("question_id", "lens", "status", "answer_status", "evidence_ids")},
        "insight": {key: insight.get(key) for key in ("insight_id", "lens", "headline", "statement", "resolved_answer", "business_question", "decision_impact", "evidence_ids", "claim_binding")},
        "action": {key: action.get(key) for key in ("action_id", "lens", "priority", "headline", "text", "target", "basis", "rationale", "verification_signal", "evidence_ids", "source_insight_ids", "claim_binding")},
        "value_selection": selected[0], "executive_summary": summary_payload, "slide_content_refs": pages,
        "evidence_digest": evidence_digest, "evidence_digest_sha256": _canonical_hash(evidence_digest),
    }
