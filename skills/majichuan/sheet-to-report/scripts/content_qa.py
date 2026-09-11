"""Machine gate for evidence-first, decision-useful report content."""
from __future__ import annotations

import re
from typing import Any

from content_selection import (
    HARD_GATES,
    RESOLUTION_STATUSES,
    VALUE_DIMENSIONS,
    evidence_safe_classification,
    is_supporting_finding,
)
from content_resolver import canonical_claim_for_page, canonical_content_ref_bindings, normalize_claim_text
from narrative_planner import claim_signature, unresolved_question_records
from report_model_projection import build_non_retail_projection


def _issue(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def visible_implication_violations(model: dict[str, Any]) -> list[dict[str, str]]:
    """Reject repeated boilerplate in the reader-facing key-insight surface."""

    selection = model.get("value_selection")
    if isinstance(selection, dict):
        visible_ids = {
            str(item.get("insight_id") or "")
            for item in selection.get("featured", [])
            if isinstance(item, dict)
        }
    else:
        visible_ids = {str(value) for value in model.get("featured_insight_ids", [])}
    implications: dict[str, int] = {}
    for insight in model.get("insights", []):
        if str(insight.get("insight_id") or "") not in visible_ids:
            continue
        text = re.sub(r"\s+", "", str(insight.get("implication") or ""))
        if text:
            implications[text] = implications.get(text, 0) + 1
    return [
        _issue("repeated_visible_implication", "关键洞察中重复出现无新增信息的套话。")
        for count in implications.values()
        if count > 1
    ]


def _contains_raw_field(text: str, raw_fields: set[str]) -> bool:
    for field in raw_fields:
        if not field:
            continue
        # ``\w`` treats Chinese characters as word characters.  A source
        # field such as “原始收入” must therefore still be visible to the gate
        # in a natural-language sentence (“原始收入需要复核”).
        if re.search(r"[^\x00-\x7f]", field):
            if field in text:
                return True
        elif re.search(rf"(?<!\w){re.escape(field)}(?!\w)", text, flags=re.IGNORECASE):
            return True
    return bool(re.search(r"\b(?:raw_field|source_field|__\w+)\b", text, flags=re.IGNORECASE))


def _is_numeric_restatement(claim: str, records: list[dict[str, Any]]) -> bool:
    """Reject a metric-plus-number label when it contains no comparison or decision."""
    compact = re.sub(r"\s+", "", claim)
    if re.fullmatch(r"[^，。；：]*[为是]\s*[-+]?\d+(?:\.\d+)?[%倍万元]*", compact):
        return True
    if re.search(r"较|同比|环比|变化|增长|下降|上升|下滑|异常|风险|建议|优先|需", compact):
        return False
    for record in records:
        metric = str(record.get("metric") or record.get("name") or "").strip()
        values = tuple(
            value for value in (record.get("value"), record.get("latest"), record.get("latest_value"))
            if isinstance(value, (int, float)) and not isinstance(value, bool)
            or isinstance(value, str) and re.fullmatch(r"[-+]?\d+(?:\.\d+)?", value.strip())
        )
        if metric and metric in compact and any(value is not None and str(value) in compact for value in values):
            return True
    return False


def _has_evidence_anchor(claim: str, records: list[dict[str, Any]]) -> bool:
    text = claim.lower()
    anchor_keys = ("metric", "name", "dimension", "value", "latest", "latest_value", "latest_period", "comparison_period")
    # A legacy v2.0 evidence record may only carry its identifier.  There is
    # no relationship metadata to evaluate in that shape, so retain its
    # compatibility path; all evidence created by v0.2 carries anchors.
    if records and not any(record.get(key) not in (None, "") for record in records for key in anchor_keys):
        return True
    for record in records:
        anchors = [record.get(key) for key in anchor_keys]
        anchors.extend(
            row.get("value")
            for row in record.get("rows", [])
            if isinstance(row, dict) and row.get("value") not in (None, "")
        )
        matched = [str(value).lower() for value in anchors if value is not None and str(value).strip() and str(value).lower() in text]
        kind = str(record.get("kind") or "")
        if (
            ("trend" in kind or "yoy" in kind)
            and re.search(r"较|同比|环比|变化|增长|下降|上升|下滑", claim)
            and re.search(r"20\d{2}年\d{1,2}月", claim)
        ):
            # Date-formatted comparison evidence may expose ISO periods while
            # the presentation renders business-readable Chinese dates.
            return True
        if not matched:
            continue
        if "trend" in kind or "yoy" in kind:
            if re.search(r"较|同比|环比|变化|增长|下降|上升|下滑", claim):
                return True
            # Action-roadmap claims may name the affected object and metric
            # while keeping the directional evidence in their declared basis.
            if len(matched) >= 2:
                return True
        if (
            str(record.get("metric") or record.get("name") or "").strip()
            and str(record.get("metric") or record.get("name") or "").lower() in text
            and re.search(r"累计|整体|概览|KPI", claim, flags=re.IGNORECASE)
        ):
            # A KPI spotlight is a scoped metric view; its cards carry the
            # numerical detail while the page title names that metric/scope.
            return True
        elif len(matched) >= 2 or any(str(record.get(key) or "").lower() in text for key in ("dimension", "value")):
            return True
    return False


def _has_claim_binding_anchor(text: str, binding: Any) -> bool:
    """Recognize compact display labels only when their structured binding is complete."""
    if not isinstance(binding, dict) or not isinstance(binding.get("claims"), list):
        return False
    relation_words = {"max": "最高", "min": "最低"}
    for claim in binding["claims"]:
        if not isinstance(claim, dict):
            return False
        relation = str(claim.get("relation") or "")
        if relation == "rank_desc":
            relation_word = f"第{claim.get('rank')}高"
        else:
            relation_word = relation_words.get(relation, "")
        precision = claim.get("display_precision", 2)
        value = claim.get("actual_value")
        if precision not in {0, 1, 2} or not isinstance(value, (int, float)):
            return False
        display_metric = str(claim.get("display_metric") or claim.get("metric") or "")
        if not all(token in text for token in (
            str(claim.get("subject_value") or ""), display_metric,
            f"{float(value):.{precision}f}", relation_word,
        )):
            return False
    return bool(binding["claims"])


def _validate_value_selection(model: dict[str, Any]) -> list[dict[str, str]]:
    declared_content = model.get("content_validation")
    nested_selection = (
        declared_content.get("value_selection")
        if isinstance(declared_content, dict)
        else None
    )
    selection = model.get("value_selection") or nested_selection
    selection_required = (
        "appendix_insight_ids" in model
        or "value_selection" in model
        or (isinstance(declared_content, dict) and "value_selection" in declared_content)
    )
    if not isinstance(selection, dict):
        return [_issue("missing_value_selection", "已启用价值选择的模型必须提供完整选择结果。")] if selection_required else []
    required_keys = {"featured", "appendix", "dropped", "selection_policy"}
    allowed_keys = {*required_keys, "selection_unit", "analysis_chapters"}
    if not required_keys <= set(selection) or set(selection) - allowed_keys:
        return [_issue("invalid_value_selection", "洞察价值选择必须包含且只包含固定分组与策略。")]
    if "selection_unit" in selection and selection.get("selection_unit") != "analysis_chapter":
        return [_issue("invalid_value_selection", "新版价值选择必须以 analysis_chapter 为选择单位。")]
    if not isinstance(selection.get("selection_policy"), dict):
        return [_issue("invalid_selection_policy", "洞察价值选择策略必须是对象。")]
    blocking: list[dict[str, str]] = []
    policy = selection["selection_policy"]
    if (
        policy.get("featured_min_score") != 8
        or policy.get("appendix_min_score") != 5
        or policy.get("hard_gates") != list(HARD_GATES)
        or policy.get("tie_break") != "source_index_then_insight_id"
    ):
        blocking.append(_issue("invalid_selection_policy", "洞察价值选择策略缺少固定门槛或确定性排序规则。"))
    records: list[dict[str, Any]] = []
    portfolio_records: dict[str, list[dict[str, Any]]] = {}
    insight_ids = {str(item.get("insight_id") or "") for item in model.get("insights", [])}
    expected_ids: dict[str, list[str]] = {"featured": [], "appendix": []}
    for classification in ("featured", "appendix", "dropped"):
        items = selection[classification]
        if not isinstance(items, list):
            blocking.append(_issue("invalid_value_selection", "洞察价值选择分组必须是列表。"))
            continue
        previous_key: tuple[int, int, str] | None = None
        for item in items:
            if not isinstance(item, dict):
                blocking.append(_issue("invalid_value_selection", "洞察价值选择记录必须是对象。"))
                continue
            records.append(item)
            insight_id = str(item.get("insight_id") or "")
            if not insight_id:
                blocking.append(_issue("missing_value_selection_id", "价值选择记录必须有稳定 insight_id。"))
            elif insight_ids and insight_id not in insight_ids:
                blocking.append(_issue("unknown_value_selection_id", "价值选择引用了不存在的洞察。"))
            if classification in expected_ids:
                expected_ids[classification].append(insight_id)
            if not isinstance(item.get("score"), int) or not isinstance(item.get("source_index"), int):
                blocking.append(_issue("invalid_value_selection_order", "价值选择记录必须提供整数分数和源序号。"))
            else:
                order_key = (-item["score"], item["source_index"], insight_id)
                if previous_key is not None and order_key < previous_key:
                    blocking.append(_issue("invalid_value_selection_order", "同组洞察必须按分数和稳定 tie-break 排序。"))
                previous_key = order_key
            dimensions = item.get("dimension_scores", {})
            gate_failed = (
                item.get("evidence_valid") is not True
                or not str(item.get("business_question") or "").strip()
                or not bool(item.get("information_gain"))
                or not str(item.get("decision_impact") or "").strip()
                or str(item.get("evidence_strength") or "").lower() == "low"
                or (str(item.get("claim_type") or item.get("kind") or "fact").lower() == "hypothesis" and len(item.get("evidence_ids") or []) < 2)
            )
            valid_dimensions = isinstance(dimensions, dict) and all(
                type(dimensions.get(name)) is int and dimensions[name] in {0, 1, 2}
                for name in VALUE_DIMENSIONS
            )
            if not valid_dimensions:
                blocking.append(_issue("invalid_value_dimension", "洞察价值维度只能取 0、1 或 2。"))
            else:
                expected_score = sum(dimensions[name] for name in VALUE_DIMENSIONS)
                expected = "dropped" if gate_failed or expected_score < 5 else ("featured" if expected_score >= 8 else "appendix")
                expected, _ = evidence_safe_classification(item, expected)
                if item.get("duplicate_of"):
                    expected = "dropped"
                override = str(item.get("portfolio_override") or "")
                if override:
                    question_id = str(item.get("question_id") or "").strip()
                    direct = (
                        item.get("evidence_valid") is True
                        and str(item.get("answer_status") or "") == "answered"
                        and str(item.get("resolution_status") or "") == "direct_conclusion"
                        and not item.get("evidence_gaps")
                        and str(item.get("evidence_strength") or "").lower() != "low"
                        and bool(item.get("evidence_ids"))
                        and question_id
                        and str(item.get("question_priority") or "") == "high"
                        and not is_supporting_finding(item)
                    )
                    valid_override = (
                        direct
                        and override in {
                            "answered_high_priority_representative",
                            "sibling_of_answered_high_priority_representative",
                        }
                        and (
                            (override == "answered_high_priority_representative" and classification == "featured")
                            or (override == "sibling_of_answered_high_priority_representative" and classification == "appendix")
                        )
                    )
                    if not valid_override:
                        blocking.append(_issue("invalid_portfolio_override", "组合呈现覆盖必须绑定已回答的直接结论、有效证据和完整问题身份。"))
                    else:
                        portfolio_records.setdefault(question_id, []).append(item)
                    if item.get("score") != expected_score or item.get("classification") != classification:
                        blocking.append(_issue("inconsistent_value_classification", "洞察价值分数、硬门槛与分类不一致。"))
                elif item.get("score") != expected_score or item.get("classification") != classification or classification != expected:
                    blocking.append(_issue("inconsistent_value_classification", "洞察价值分数、硬门槛与分类不一致。"))
            resolution = str(item.get("resolution_status") or "")
            answer_status = str(item.get("answer_status") or "")
            gaps = item.get("evidence_gaps")
            confirmed_dimensions = item.get("confirmed_dimensions")
            if resolution not in RESOLUTION_STATUSES or not isinstance(gaps, list) or not isinstance(confirmed_dimensions, list):
                blocking.append(_issue("invalid_resolution_state", "洞察必须声明结构化结论状态、证据缺口和已确认维度。"))
            elif answer_status == "answered" and confirmed_dimensions and resolution != "direct_conclusion":
                blocking.append(_issue("deferred_available_analysis", "字段充分且问题已回答时必须给出直接结论。"))
            elif resolution == "direct_conclusion" and (
                answer_status != "answered"
                or gaps
                or not str(item.get("resolved_answer") or item.get("answer_text") or "").strip()
                or item.get("evidence_valid") is not True
                or not isinstance(item.get("evidence_ids"), list)
                or not item["evidence_ids"]
            ):
                blocking.append(_issue("invalid_resolution_state", "直接结论必须对应已回答且无证据缺口的问题。"))
            elif resolution == "limited_with_next_step" and (not gaps or not str(item.get("next_step") or "").strip() or not item.get("limitations")):
                blocking.append(_issue("invalid_resolution_state", "证据不足时必须提供限制条件和下一步补数。"))
    for question_id, portfolio_items in portfolio_records.items():
        representatives = [
            item for item in portfolio_items
            if item.get("portfolio_override") == "answered_high_priority_representative"
        ]
        siblings = [
            item for item in portfolio_items
            if item.get("portfolio_override") == "sibling_of_answered_high_priority_representative"
        ]
        if len(representatives) != 1 or any(
            str(item.get("question_id") or "") != question_id for item in siblings
        ):
            blocking.append(_issue("invalid_portfolio_override", "同一已回答高优先问题必须恰有一个组合代表，其余同题结论仅可进入附录。"))
    ids = [str(item.get("insight_id") or "") for item in records]
    if len(ids) != len(set(ids)):
        blocking.append(_issue("duplicate_value_selection_record", "同一洞察不得重复进入价值选择结果。"))
    selected_signatures: set[str] = set()
    for item in records:
        signature = str(item.get("duplicate_signature") or "").strip()
        if not signature or item.get("classification") == "dropped":
            continue
        if signature in selected_signatures:
            blocking.append(_issue("duplicate_value_selection", "同一精确重复结论只能保留一条。"))
            break
        selected_signatures.add(signature)
    for group, model_key in (("featured", "featured_insight_ids"), ("appendix", "appendix_insight_ids")):
        declared = model.get(model_key)
        if not isinstance(declared, list) or [str(value) for value in declared] != expected_ids[group]:
            blocking.append(_issue("value_selection_id_drift", "洞察 ID 必须与价值分类结果精确一致。"))
        if isinstance(declared, list) and any(str(value) not in insight_ids for value in declared):
            blocking.append(_issue("unknown_value_selection_id", "洞察 ID 引用了不存在的洞察。"))
    return blocking


def validate_content_value(model: dict[str, Any]) -> dict[str, Any]:
    # QA and the model validator deliberately share the same evidence-derived
    # projection; a rehashed artifact cannot make formal non-retail prose true.
    build_non_retail_projection(model)
    blocking: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    blocking.extend(_validate_value_selection(model))
    blocking.extend(visible_implication_violations(model))
    evidence = set(model.get("evidence_index", {}))
    chapters_enabled = "analysis_chapters" in model
    chapters = model.get("analysis_chapters", []) if chapters_enabled else []
    if chapters_enabled and not isinstance(chapters, list):
        blocking.append(_issue("invalid_analysis_chapters", "analysis_chapters 必须是列表。"))
        chapters = []
    chapter_ids = [
        str(item.get("chapter_id") or "") for item in chapters if isinstance(item, dict)
    ]
    if chapters_enabled and (any(not value for value in chapter_ids) or len(chapter_ids) != len(set(chapter_ids))):
        blocking.append(_issue("invalid_analysis_chapters", "章节必须提供唯一稳定 chapter_id。"))
    selected_chapter_ids = {
        str(item.get("chapter_id") or "")
        for item in chapters
        if isinstance(item, dict) and item.get("selection_status") == "selected"
    }
    if chapters_enabled and "analysis_brief" in model:
        from analysis_depth import validate_action_chapter_links
        try:
            validate_action_chapter_links(model)
        except (ValueError, TypeError, KeyError):
            blocking.append(_issue("action_depth_closure_invalid", "行动与章节必须双向归属，深度5须由最终保留的本章判断行动证明。"))
    for chapter in chapters:
        if not isinstance(chapter, dict):
            blocking.append(_issue("invalid_analysis_chapters", "章节记录必须是对象。"))
            continue
        required = chapter.get("required_depth")
        achieved = chapter.get("achieved_depth")
        valid_depth = not (
            isinstance(required, bool) or not isinstance(required, int)
            or isinstance(achieved, bool) or not isinstance(achieved, int)
            or not 0 <= required <= 5 or not 0 <= achieved <= 5
        )
        if not valid_depth:
            blocking.append(_issue("invalid_chapter_depth", "章节深度必须是 0-5 的整数。"))
        if chapter.get("selection_status") == "selected" and (
            chapter.get("answer_status") != "answered"
            or not valid_depth
            or (valid_depth and achieved < max(4, required))
            or not str(chapter.get("decision_question") or "").strip()
            or not str(chapter.get("report_language") or chapter.get("judgement") or "").strip()
            or not str(chapter.get("operating_implication") or "").strip()
        ):
            blocking.append(_issue("chapter_gate_failed", "正文章节必须回答业务问题并达到深度与经营含义门槛。"))
        judgement = str(chapter.get("report_language") or chapter.get("judgement") or "").strip()
        if chapter.get("selection_status") == "selected" and re.fullmatch(
            r"(?:已|已经|完成).{0,24}(?:核验|分析|计算|检查|验证)[^。！？!?]*[。.!]?", judgement,
        ):
            blocking.append(_issue("chapter_judgement_not_decision", "执行回执不能代替章节的经营判断。"))
        alignment = chapter.get("claim_chart_alignment")
        if isinstance(alignment, dict) and alignment.get("status") == "failed":
            blocking.append(_issue("claim_chart_alignment_failed", "章节主张与图表证据范围不一致。"))
    nested_chapters = (
        model.get("value_selection", {}).get("analysis_chapters")
        if isinstance(model.get("value_selection"), dict)
        else None
    )
    if nested_chapters is not None and nested_chapters != chapters:
        blocking.append(_issue("analysis_chapter_drift", "顶层章节与价值选择章节不一致。"))
    summary = model.get("executive_summary", {})
    if chapters_enabled and isinstance(summary, dict):
        conclusion_ids = [str(value) for value in summary.get("key_conclusion_chapter_ids", [])]
        conclusions = list(summary.get("key_conclusions", []))
        if (
            len(conclusion_ids) != len(conclusions)
            or any(value not in selected_chapter_ids for value in conclusion_ids)
        ):
            blocking.append(_issue("summary_chapter_link_missing", "管理摘要每条判断必须绑定已入选正文的章节。"))
    raw_fields = {str(value) for value in model.get("data_profile", {}).get("columns", [])}
    allowed_display = {str(value) for value in model.get("request", {}).get("dimensions", [])}
    for metric in model.get("metric_contracts", []):
        if isinstance(metric, dict):
            allowed_display.update(str(metric.get(key)) for key in ("name", "display_name") if metric.get(key))
    mappings = model.get("analysis_contract", {}).get("semantic_contract", {})
    for mapping in mappings.get("field_mappings", {}).values() if isinstance(mappings, dict) else ():
        if isinstance(mapping, dict) and mapping.get("source_field"):
            raw_fields.add(str(mapping["source_field"]))
    raw_fields -= allowed_display
    featured_ids = [str(value) for value in model.get("featured_insight_ids", [])]
    insight_by_id = {
        str(item.get("insight_id") or ""): item for item in model.get("insights", [])
    }
    if featured_ids:
        if len(featured_ids) != len(set(featured_ids)) or any(
            item_id not in insight_by_id for item_id in featured_ids
        ):
            blocking.append(_issue("invalid_featured_insight", "关键洞察引用无效或重复。"))
        for item_id in featured_ids:
            item = insight_by_id.get(item_id, {})
    questions = list(model.get("analysis_lenses", []))
    questions_by_id = {str(item["question_id"]): item for item in questions if item.get("question_id")}
    lenses = {}
    for item in questions:
        lenses.setdefault(str(item.get("lens")), []).append(item)
    for item in questions:
        lens = str(item.get("lens"))
        if item.get("status") != "selected":
            warnings.append(_issue("lens_missing", f"镜头 {lens} 未满足条件：{', '.join(item.get('missing_requirements', []))}"))

    def owners(record, kind):
        """None means invalid/ambiguous; [] is a legacy record without a lens."""
        own = []
        explicit = str(record.get("question_id") or "")
        lens = str(record.get("lens") or "")
        if explicit:
            question = questions_by_id.get(explicit)
            if (question is None or sum(q.get("question_id") == explicit for q in questions) != 1
                    or (lens and question.get("lens") != lens)):
                return None
            own.append(question)
        inherited = []
        if kind == "action":
            for source in record.get("source_insight_ids") or []:
                if source not in insight_by_id:
                    return None
                source_owners = owners(insight_by_id[source], "insight")
                if source_owners is None:
                    return None
                inherited.extend(source_owners)
            for cid in record.get("source_chapter_ids") or []:
                chapter = next((c for c in chapters if c.get("chapter_id") == cid), None)
                if chapter is None or chapter.get("question_id") not in questions_by_id:
                    return None
                inherited.append(questions_by_id[chapter["question_id"]])
        if explicit and inherited and explicit not in {q.get("question_id") for q in inherited}:
            return None
        own.extend(inherited)
        if not own and lens in lenses:
            if len(lenses[lens]) != 1:
                return None
            own = lenses[lens]
        if any(q.get("status") != "selected" for q in own):
            return None
        return own
    seen_claims: dict[str, frozenset[str]] = {}
    covered_lenses: set[str] = set()
    covered_question_ids: set[str] = set()
    for insight in model.get("insights", []):
        statement = str(insight.get("statement") or insight.get("headline") or "").strip()
        ids = set(str(value) for value in insight.get("evidence_ids", []))
        claim_type = str(insight.get("claim_type") or insight.get("kind") or "fact")
        if owners(insight, "insight") is None:
            blocking.append(_issue("unsupported_lens_output", "不支持的镜头不能生成正式洞察。"))
        if _contains_raw_field(statement, raw_fields):
            blocking.append(_issue("raw_field_leakage", "洞察泄漏原始字段名。"))
        if not (
            _has_evidence_anchor(statement, [model.get("evidence_index", {}).get(value, {}) for value in ids])
            or _has_claim_binding_anchor(statement, insight.get("claim_binding"))
        ):
            blocking.append(_issue("no_information_gain", "洞察与证据之间缺少可验证信息锚点。"))
        if not ids or not ids <= evidence:
            blocking.append(_issue("unsupported_insight", "洞察缺少可验证证据。"))
        from analysis_depth import has_bound_contribution_judgement
        if claim_type in {"diagnostic", "inference"} and len(ids) < 2 and not has_bound_contribution_judgement(insight, model.get('evidence_index', {})):
            blocking.append(_issue("unsupported_causality", "诊断或推断缺少交叉证据。"))
        if claim_type == "hypothesis" and not insight.get("limitations"):
            blocking.append(_issue("hypothesis_without_limitations", "假设必须说明限制。"))
        if int(insight.get("value_score", 1)) <= 0 or _is_numeric_restatement(statement, [model.get("evidence_index", {}).get(value, {}) for value in ids]):
            blocking.append(_issue("numeric_restatement", "纯数字复述不构成洞察。"))
        if re.search(r"由.{0,20}(?:导致|带动)|行业.{0,12}(?:平均|水平)|目标.{0,8}\d", statement):
            blocking.append(_issue("unsupported_causality", "因果、行业比较或目标值缺少依据。"))
        if claim_type == "hypothesis" or str(insight.get("evidence_strength", "")) == "low":
            warnings.append(_issue("low_evidence_downgrade", "证据不足已降级为假设。"))
    for action in model.get("actions", []):
        required = ("target", "basis", "rationale", "verification_signal")
        if owners(action, "action") is None:
            blocking.append(_issue("unsupported_lens_output", "不支持的镜头不能生成正式行动。"))
        if _contains_raw_field(str(action.get("text") or ""), raw_fields):
            blocking.append(_issue("raw_field_leakage", "行动泄漏原始字段名。"))
        if not set(str(value) for value in action.get("evidence_ids", [])) <= evidence or not action.get("evidence_ids") or any(not str(action.get(key) or "").strip() for key in required) or not action.get("formal", True):
            blocking.append(_issue("action_contract_incomplete", "行动缺少对象、依据、证据或验证信号。"))
        if chapters_enabled and action.get("formal", True):
            source_chapter_ids = [str(value) for value in action.get("source_chapter_ids", [])]
            if not source_chapter_ids or any(value not in selected_chapter_ids for value in source_chapter_ids):
                blocking.append(_issue("formal_action_chapter_link_missing", "正式行动必须绑定已入选章节。"))
            action_type = str(action.get("action_type") or "")
            steps = action.get("steps")
            guardrails = action.get("guardrails")
            limitations = action.get("limitations")
            if (
                action_type not in {"act_now", "controlled_test", "monitor", "data_governance"}
                or not isinstance(steps, list) or not steps or any(not str(value).strip() for value in steps)
                or not str(action.get("success_signal") or "").strip()
                or not isinstance(guardrails, list) or not guardrails or any(not str(value).strip() for value in guardrails)
                or not isinstance(limitations, list)
            ):
                blocking.append(_issue("formal_action_contract_incomplete", "正式行动缺少类型、步骤、成功信号、护栏或限制合同。"))
            success = re.sub(r"[\W_]+", "", str(action.get("success_signal") or "")).lower()
            observations = {
                re.sub(r"[\W_]+", "", str(action.get(key) or "")).lower()
                for key in ("basis", "text")
            }
            if action_type in {"controlled_test", "monitor"} and success and success in observations:
                blocking.append(_issue("formal_action_success_not_verifiable", "当前观测值不能重复充当试验成功信号或监控触发条件。"))
        unsupported_dimensions = set(
            str(value) for value in action.get("analysis_dimensions", [])
        ) - set(str(value) for value in model.get("request", {}).get("dimensions", []))
        if unsupported_dimensions:
            blocking.append(_issue("unsupported_action_dimension", "行动使用了请求中不存在的分析维度。"))
    if featured_ids:
        action_links = {
            str(value)
            for action in model.get("actions", [])
            if action.get("formal", True)
            for value in action.get("source_insight_ids", [])
        }
        for item_id in featured_ids:
            item = insight_by_id.get(item_id, {})
            if item.get("actionable") and item_id not in action_links and not item.get("no_action_reason"):
                blocking.append(_issue("featured_insight_missing_action", "可行动的关键洞察缺少正式行动闭环。"))
    featured_id_set = set(featured_ids)
    for action in model.get("actions", []):
        if not action.get("formal", True):
            continue
        source_ids = {
            str(value) for value in action.get("source_insight_ids", []) if str(value)
        }
        if source_ids and not source_ids <= featured_id_set:
            blocking.append(_issue(
                "formal_action_source_not_featured",
                "正式行动必须由正文 featured 洞察支撑，不能把附录或删除项直接升级为关键决策建议。",
            ))
    priorities = [
        action.get("priority") for action in model.get("actions", [])
        if action.get("formal", True)
    ]
    if priorities:
        if any(type(value) is not int for value in priorities):
            blocking.append(_issue("invalid_action_priority", "正式行动优先级必须为整数，不能使用布尔值。"))
        elif priorities != list(range(1, len(priorities) + 1)):
            blocking.append(_issue("non_contiguous_action_priority", "正式行动优先级必须连续。"))
    summary_actions = list(model.get("executive_summary", {}).get("priority_actions", []))
    if summary_actions:
        expected_actions = [
            str(item.get("headline") or item.get("text") or "").rstrip("。")
            for item in model.get("actions", [])[: len(summary_actions)]
        ]
        if summary_actions != expected_actions:
            blocking.append(_issue("summary_action_drift", "管理摘要行动必须来自最终正式行动。"))
    for slide in model.get("slide_plan", []):
        claim = str(slide.get("claim") or "").strip()
        expected_claim = canonical_claim_for_page(model, slide)
        if expected_claim and normalize_claim_text(claim) != expected_claim:
            blocking.append(_issue("appendix_claim_drift", "业务 appendix 页面 claim 必须等于 claim_ref 的 canonical finding。"))
        visual_spec = slide.get("visual_spec")
        if expected_claim and isinstance(visual_spec, dict) and "display_claim" in visual_spec and (
            normalize_claim_text(visual_spec.get("display_claim")) != expected_claim
        ):
            blocking.append(_issue("appendix_display_claim_drift", "业务 appendix 页面 display_claim 必须等于 claim_ref 的 canonical finding。"))
        declared_lenses = {
            str(value) for value in ([slide.get("lens")] + list(slide.get("covered_lenses", [])))
            if value
        }
        raw_leak = _contains_raw_field(claim, raw_fields)
        boilerplate = bool(re.fullmatch(r"(?:持续关注|建议加强|加强运营|持续关注并加强运营)[。！!]?", claim))
        if not claim or "{" in claim or "}" in claim:
            blocking.append(_issue("empty_slot", "页面存在空槽或未解析占位符。"))
        if raw_leak:
            blocking.append(_issue("raw_field_leakage", "页面泄漏原始字段名。"))
        if boilerplate:
            blocking.append(_issue("boilerplate", "页面只有套话，缺少可执行信息。"))
        if not claim or raw_leak or boilerplate:
            blocking.append(_issue("no_information_gain", "页面没有新增的可验证信息。"))
        if slide.get("layout_id") != "cover" and not slide.get("content_exemption") and not set(str(value) for value in slide.get("evidence_ids", [])) & evidence:
            blocking.append(_issue("missing_content_evidence", "非封面内容页缺少可验证 evidence_ids。"))
        if lenses and slide.get("layout_id") != "cover" and not slide.get("content_exemption") and not declared_lenses:
            blocking.append(_issue("missing_lens", "业务内容页必须声明 lens。"))
        page_owners = []
        page_invalid = False
        refs = slide.get("content_refs") or {}
        try:
            bindings = canonical_content_ref_bindings(model, {"content_refs": {
                key: refs.get(key, []) for key in ("insight_ids", "action_ids")}})
        except (ValueError, TypeError, KeyError):
            bindings, page_invalid = [], True
        for binding in bindings:
            resolved = owners(binding["visible"], "insight" if binding["key"] == "insight_ids" else "action")
            page_invalid |= resolved is None
            page_owners.extend(resolved or [])
        # KPI context is not an answer to a question, whether or not the
        # baseline carries a question identity.
        baseline_context = (
                slide.get("story_role") == "baseline" and slide.get("lens") == "overview"
                and refs.get("claim_ref") in refs.get("kpi_ids", [])
                and bool(refs.get("kpi_ids")) and not refs.get("action_ids")
                and all(binding["visible"].get("presentation_role") == "supporting"
                        and binding["visible"].get("claim_type") == "fact"
                        for binding in bindings)
        )
        if slide.get("question_id"):
            if not baseline_context and page_owners and any(q.get("question_id") != slide["question_id"] for q in page_owners):
                page_invalid = True
            resolved = owners(slide, "page")
            page_invalid |= resolved is None
            page_owners.extend(resolved or [])
        if not page_owners and not baseline_context:
            page_invalid |= any(value in lenses and (len(lenses[value]) != 1 or lenses[value][0].get("status") != "selected")
                                for value in declared_lenses)
        if page_invalid and not slide.get("content_exemption") and slide.get("layout_id") != "cover":
            blocking.append(_issue("unsupported_lens_output", "不支持的镜头不能生成正式页面。"))
        slide_records = [model.get("evidence_index", {}).get(value, {}) for value in slide.get("evidence_ids", [])]
        if slide.get("layout_id") != "action-roadmap" and _is_numeric_restatement(claim, slide_records):
            blocking.append(_issue("numeric_restatement", "页面标题仅复述数字。"))
        bound_findings = [
            finding for finding in model.get("insights", [])
            if isinstance(finding, dict)
            and set(str(value) for value in finding.get("evidence_ids", [])) <= set(slide.get("evidence_ids", []))
            and _has_claim_binding_anchor(claim, finding.get("claim_binding"))
        ]
        if (
            slide.get("layout_id") != "cover"
            and not slide.get("content_exemption")
            and not _has_evidence_anchor(claim, slide_records)
            and not bound_findings
        ):
            blocking.append(_issue("no_information_gain", "页面结论与证据之间缺少可验证信息锚点。"))
        # The cover repeats report identity, not a decision claim; only content
        # pages participate in conclusion de-duplication.
        if slide.get("layout_id") != "cover":
            normalized, evidence_scope = claim_signature(claim, list(slide.get("evidence_ids", [])))
            previous = seen_claims.get(normalized)
            summary_to_detail = (
                previous is not None
                and previous[0] == evidence_scope
                and "executive_summary" in {previous[1], str(slide.get("story_role") or "")}
            )
            if previous is not None and previous[0] == evidence_scope and not summary_to_detail:
                blocking.append(_issue("duplicate_conclusion", "等价结论跨页重复。"))
            seen_claims[normalized] = (evidence_scope, str(slide.get("story_role") or ""))
        if slide.get("layout_id") != "cover" and not slide.get("content_exemption") and not page_invalid:
            if slide.get("question_id"):
                covered_question_ids.add(str(slide["question_id"]))
            elif page_owners:
                covered_question_ids.update(str(q["question_id"]) for q in page_owners if q.get("question_id"))
            else:
                for lens in declared_lenses:
                    if len(lenses.get(lens, [])) == 1:
                        qid = lenses[lens][0].get("question_id")
                        if qid:
                            covered_question_ids.add(str(qid))
                        else:
                            covered_lenses.add(lens)
    narrative_validation = model.get("content_validation", {}).get("narrative_validation", {})
    question_coverage = (
        narrative_validation.get("question_coverage", {})
        if isinstance(narrative_validation, dict)
        else {}
    )
    question_dispositions = (
        narrative_validation.get("question_dispositions", [])
        if isinstance(narrative_validation, dict)
        else []
    )
    if not isinstance(question_dispositions, list):
        blocking.append(_issue("invalid_narrative_disposition", "问题处置必须是逐 finding 的列表。"))
        question_dispositions = []
    pages_by_id = {str(page.get("slide_id") or ""): page for page in model.get("slide_plan", [])}
    selection = model.get("value_selection") or model.get("content_validation", {}).get("value_selection")
    selection_classes = {
        str(record.get("insight_id") or ""): classification
        for classification in ("featured", "appendix", "dropped")
        for record in (selection.get(classification, []) if isinstance(selection, dict) else [])
        if isinstance(record, dict)
    }
    def sibling_question_ids(question: str, question_id: str) -> set[str]:
        return {str(q["question_id"]) for q in questions if q.get("question_id")
                and q["question_id"] != question_id and str(q.get("business_question") or "") == question}

    def coverage_is_real(question: str, question_id: str, lens: str, evidence_ids: list[str]) -> bool:
        targets = question_coverage.get(question)
        if not isinstance(targets, list) or not targets:
            return False
        siblings = sibling_question_ids(question, question_id)
        targets = [target for target in targets if pages_by_id.get(target, {}).get("question_id") not in siblings]
        return bool(targets) and all(
            target in pages_by_id
            and (
                pages_by_id[target].get("story_role") in {"driver", "opportunity", "risk"}
                or (pages_by_id[target].get("story_role") == "baseline" and lens == "overview")
            )
            and str(pages_by_id[target].get("business_question") or "") == question
            and (not question_id or str(pages_by_id[target].get("question_id") or "") == question_id)
            and set(evidence_ids) <= set(pages_by_id[target].get("evidence_ids", []))
            for target in targets
        )

    def disposition_is_real(
        disposition: dict[str, Any], question: str, question_id: str, evidence_ids: list[str]
    ) -> bool:
        target = pages_by_id.get(str(disposition.get("target_slide_id") or ""))
        kind = str(disposition.get("kind") or "")
        disposition_evidence = [str(value) for value in disposition.get("evidence_ids", [])]
        finding_ids = [str(value) for value in disposition.get("finding_ids", [])]
        common = (
            target is not None
            and str(disposition.get("reason") or "").strip()
            and disposition.get("content_refs") == target.get("content_refs", {})
            and str(disposition.get("business_question") or "") == question
            and (not question_id or str(disposition.get("question_id") or "") == question_id)
            and bool(disposition_evidence)
            and set(evidence_ids) <= set(disposition_evidence)
            and set(disposition_evidence) <= set(target.get("evidence_ids", []))
            and bool(finding_ids)
            and set(finding_ids) <= set(target.get("finding_ids", []))
            and not any(selection_classes.get(finding_id) == "dropped" for finding_id in finding_ids)
        )
        if kind == "appendix":
            return bool(common and target.get("story_role") == "appendix")
        if kind == "merged":
            return bool(
                common
                and target.get("story_role") in {"driver", "opportunity", "risk"}
                and str(target.get("business_question") or "") == question
                and str(disposition.get("merged_claim") or "") == str(target.get("claim") or "")
            )
        if kind == "not_selected":
            expected = next((item for item in unresolved_question_records(model, model.get("slide_plan", []))
                             if item["question_id"] == question_id), None)
            if (mixed_required or model.get("narrative_selection", {}).get("status") == "partial_coverage") and (
                expected is None or disposition.get("reason") != expected["reason"]
            ):
                return False
            return bool(
                target is not None
                and target.get("content_exemption") == "selection_meta"
                and str(disposition.get("reason") or "").strip()
                and disposition.get("content_refs") == target.get("content_refs", {})
                and str(disposition.get("business_question") or "") == question
                and (not question_id or str(disposition.get("question_id") or "") == question_id)
                and set(evidence_ids) <= set(disposition_evidence)
                and not finding_ids
                and isinstance(disposition.get("drop_reasons"), list)
                and isinstance(disposition.get("value_scores"), list)
                and str(disposition.get("evidence_status") or "") in {"answered", "partial"}
                and target.get("content_refs", {}).get("claim_ref") == "meta:value_selection_status"
            )
        return False

    def dispositions_for(question: str, question_id: str) -> list[dict[str, Any]]:
        siblings = sibling_question_ids(question, question_id)
        return [
            disposition for disposition in question_dispositions
            if isinstance(disposition, dict)
            and str(disposition.get("business_question") or "") == question
            and disposition.get("question_id") not in siblings
        ]

    pending_records = unresolved_question_records(model, model.get("slide_plan", []))
    mixed_required = "analysis_brief" in model and bool(pending_records) and bool(selection.get("featured", []))
    if model.get("narrative_selection", {}).get("status") == "partial_coverage" or mixed_required:
        if (model.get("narrative_selection", {}).get("status") != "partial_coverage"
                or model.get("narrative_selection", {}).get("unresolved_questions") != pending_records):
            blocking.append(_issue("question_disposition_drift", "未完成问题说明与真实问题深度、证据或停止原因不一致。"))

    if isinstance(selection, dict):
        selected_appendix_ids = [
            str(item.get("insight_id") or "")
            for item in selection.get("appendix", [])
            if isinstance(item, dict)
        ]
        appendix_pages = [
            page for page in model.get("slide_plan", [])
            if page.get("story_role") == "appendix" and page.get("finding_ids")
        ]
        appendix_page_ids = [
            str(page.get("finding_ids", [""])[0])
            for page in appendix_pages
            if isinstance(page.get("finding_ids"), list) and len(page["finding_ids"]) == 1
        ]
        appendix_dispositions = [
            disposition for disposition in question_dispositions
            if isinstance(disposition, dict) and str(disposition.get("kind") or "") == "appendix"
        ]
        appendix_disposition_ids = [
            str(disposition.get("finding_ids", [""])[0])
            for disposition in appendix_dispositions
            if isinstance(disposition.get("finding_ids"), list) and len(disposition["finding_ids"]) == 1
        ]
        if (
            len(selected_appendix_ids) != len(set(selected_appendix_ids))
            or any(len(page.get("finding_ids", [])) != 1 for page in appendix_pages)
            or any(len(disposition.get("finding_ids", [])) != 1 for disposition in appendix_dispositions)
            or set(selected_appendix_ids) != set(appendix_page_ids)
            or set(selected_appendix_ids) != set(appendix_disposition_ids)
            or len(appendix_page_ids) != len(set(appendix_page_ids))
            or len(appendix_disposition_ids) != len(set(appendix_disposition_ids))
        ):
            blocking.append(_issue("appendix_projection_drift", "已选择 appendix finding 必须与页面和逐项处置一一对应。"))

    for item in questions:
        lens = str(item.get("lens"))
        question = str(item.get("business_question") or "").strip()
        question_id = str(item.get("question_id") or "").strip()
        expected_evidence = [str(value) for value in item.get("evidence_ids", [])]
        covered_by_story = coverage_is_real(question, question_id, lens, expected_evidence)
        dispositions = dispositions_for(question, question_id)
        covered_by_disposition = any(
            disposition_is_real(disposition, question, question_id, expected_evidence)
            for disposition in dispositions
        )
        if dispositions and any(
            not disposition_is_real(disposition, question, question_id, expected_evidence)
            for disposition in dispositions
        ):
            blocking.append(_issue("invalid_narrative_disposition", "问题处置必须指向角色、引用与证据范围都匹配的真实页面。"))
        if question in question_coverage and not covered_by_story:
            blocking.append(_issue("invalid_narrative_coverage", "问题覆盖必须指向具备同问题同证据的真实业务页面。"))
        missing_coverage = (
            item.get("status") == "selected"
            and (
                (item.get("priority") == "high" and not (covered_by_story or covered_by_disposition))
                or (item.get("priority") != "high"
                    and not (question_id in covered_question_ids if question_id else lens in covered_lenses)
                    and not covered_by_story and not covered_by_disposition)
            )
        )
        credible_high_priority_answer = (
            item.get("priority") == "high"
            and str(item.get("answer_status") or "") in {"answered", "partial"}
            and bool(item.get("evidence_ids"))
            and set(str(value) for value in item.get("evidence_ids", [])) <= evidence
        )
        if missing_coverage and (item.get("priority") != "high" or credible_high_priority_answer):
            issue = _issue(
                "selected_high_priority_lens_missing_coverage"
                if item.get("priority") == "high" else "selected_lens_missing_coverage",
                f"已选择镜头 {lens} 未生成正式内容页。",
            )
            (blocking if item.get("priority") == "high" else warnings).append(issue)
    result = {"status": "blocked" if blocking else "passed", "blocking": blocking, "warnings": warnings}
    if isinstance(selection, dict):
        result["value_selection"] = selection
    return result
