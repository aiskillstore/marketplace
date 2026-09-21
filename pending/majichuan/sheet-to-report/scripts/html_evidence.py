"""Read-only business presentation of existing evidence and calculation scopes."""
from __future__ import annotations

import math
import re

from analysis_scope import record_evidence_ids


ROLE_LABELS = {"time": "日期", "customer": "客户标识", "order": "订单标识", "product": "商品", "geography": "地域",
               "quantity": "数量", "unit_price": "单价", "status": "状态", "sales": "销售额", "orders": "订单数",
               "average_order_value": "单均金额", "customers": "客户数"}
BINDING_LABELS = {"baseline": "基期", "previous": "基期", "comparison": "比较期", "current": "本期", "latest": "本期",
                  "affected": "受影响", "unaffected": "未受影响", "amount_baseline": "金额基准", "amount_affected": "受影响金额",
                  "baseline_amount": "金额基准", "affected_amount": "受影响金额",
                  "baseline_customers": "基期客户覆盖", "current_customers": "本期客户覆盖"}
INTERNAL_FIELD_LABELS = {"__transaction_order": "订单标识", "__transaction_quantity": "数量",
                         "__transaction_unit_price": "单价", "__story_outcome": "交易金额", "__period": "期间"}


def business_name(model: dict, name, *, fallback="指标") -> str:
    name = str(name or "")
    for contract in model.get("metric_contracts", []):
        if name in {contract.get("name"), contract.get("metric_id")}:
            display = str(contract.get("display_name") or contract.get("name") or "")
            if display and not display.startswith("__"):
                return display
    semantic = (model.get("analysis_contract") or {}).get("semantic_contract") or {}
    for role, mapping in (semantic.get("field_mappings") or {}).items():
        if isinstance(mapping, dict) and name == mapping.get("source_field"):
            return ROLE_LABELS.get(role, name if not name.startswith("__") else fallback)
    if name in INTERNAL_FIELD_LABELS:
        return INTERNAL_FIELD_LABELS[name]
    return ROLE_LABELS.get(name, name if name and not name.startswith("__") else fallback)


def number(value) -> str:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("证明表需要真实有限数值")
    return f"{value:,}" if isinstance(value, int) else f"{value:,.6f}".rstrip("0").rstrip(".")


def _percent(value) -> str:
    number(value)  # Reject booleans, absent values and non-finite inputs first.
    return number(value * 100)


def _with_unit(label, unit):
    return label + (f"（{unit}）" if unit else "")


def _scope_chain(model, scope_id):
    catalog = {item["scope_id"]: item for item in model.get("scope_catalog", [])}
    chain, seen = [], set()
    while scope_id in catalog:
        if scope_id in seen:
            raise ValueError("证据范围父链循环")
        seen.add(scope_id)
        scope = catalog[scope_id]
        chain.append(scope.get("rules", {}))
        scope_id = scope.get("parent_scope_id")
    if scope_id and any(chain):
        raise ValueError("证据范围父链引用缺失")
    return chain


def _filter_note(model, predicate):
    field = business_name(model, predicate.get("field"), fallback="相关字段")
    operator = predicate.get("predicate") or predicate.get("operator")
    if operator in {"eq", "equals", "not_equals", "ne", "lt", "le", "gt", "ge"}:
        label = {"eq": "为", "equals": "为", "not_equals": "不为", "ne": "不为",
                 "lt": "小于", "le": "不大于", "gt": "大于", "ge": "不小于"}[operator]
        return field + label + str(predicate["value"])
    if operator in {"in", "not_in", "period_in"}:
        values = predicate.get("values", predicate.get("value"))
        if not isinstance(values, (list, tuple)):
            raise ValueError("证据范围集合筛选缺少取值列表")
        return ("期间" if operator == "period_in" else field) + ("不属于" if operator == "not_in" else "属于") + "、".join(map(str, values))
    labels = {"not_blank": "非空白且非缺失", "not_null": "非缺失", "notna": "非缺失",
              "is_blank": "为空白或缺失", "is_null": "缺失", "finite": "为有效有限数值",
              "numeric": "为有效数值", "is_finite": "为有效有限数值"}
    if operator not in labels:
        raise ValueError("证据范围筛选规则缺少可读展示映射：" + str(operator))
    return field + labels[operator]


def _binding_leaves(value, labels=()):
    if isinstance(value, str):
        yield labels, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from _binding_leaves(child, (*labels, str(key)))


def scope_notes(model: dict, record: dict) -> list[str]:
    """Rows describe inputs, never customers/orders or ratio denominators."""
    catalog = {item["scope_id"]: item for item in model.get("scope_catalog", [])}
    if not record.get("scope_id"):
        return []
    if record["scope_id"] not in catalog:
        raise ValueError("证据范围未登记，不能展示范围说明")
    notes = []

    def describe(sid, label="", trail=()):
        if sid not in catalog or sid in trail:
            raise ValueError("证据范围引用缺失或循环")
        scope = catalog[sid]
        if scope.get("kind") == "comparison":
            notes.append((label + "：" if label else "") + "分范围比较，不共用分母；覆盖记录不是比率分母。")
            for member in scope.get("member_scope_ids", []):
                describe(member, trail=(*trail, sid))
            return
        chain = _scope_chain(model, sid)
        clauses = [label] if label else []
        # Descriptive legacy records have no structured rules; modern scopes
        # never publish their raw definition (which can contain tool/field IDs).
        if not any(chain) and scope.get("definition"):
            clauses.append(str(scope["definition"]))
        for rules in chain:
            comparison = rules.get("comparison") or rules.get("comparison_scope") or {}
            role = rules.get("role") or comparison.get("role")
            if comparison:
                for key in ((role,) if role in {"baseline", "current"} else ("baseline", "current")):
                    if comparison.get(key):
                        clauses.append(BINDING_LABELS[key] + "：" + "、".join(map(str, comparison[key])))
                break
            periods = (rules.get("time_scope") or {}).get("periods", [])
            if periods:
                clauses.append("分析期：" + "、".join(map(str, periods)))
                break
        contract = next((rules["metric_contract"] for rules in chain if rules.get("metric_contract")), {})
        if contract:
            clauses.append(business_name(model, contract.get("name")))
            aggregation = contract.get("aggregation")
            comparison_aggregation = next(((r.get("comparison") or r.get("comparison_scope") or {}).get("aggregation")
                                           for r in chain if r.get("comparison") or r.get("comparison_scope")), None)
            if comparison_aggregation == "monthly_mean":
                clauses.append("按各月指标值计算月均值")
            elif aggregation == "ratio":
                numerator = business_name(model, contract.get("numerator"), fallback="分子")
                denominator = business_name(model, contract.get("denominator"), fallback="分母")
                clauses.append(f"{numerator}合计 ÷ {denominator}合计 × {number(contract.get('scale', 1))}")
            elif aggregation == "sum_product":
                factors = [business_name(model, value, fallback="因子") for value in contract.get("factors", [])]
                clauses.append(" × ".join(factors) + "逐行相乘后合计")
            elif aggregation in {"distinct_count", "median"}:
                field = business_name(model, contract.get("source_field"), fallback="指标源字段")
                clauses.append(field + ("去重计数" if aggregation == "distinct_count" else "中位数"))
            else:
                clauses.append({"sum": "有效值合计", "average": "按确认口径计算均值",
                                "last": "按日期取期末值"}.get(aggregation, "按已确认指标口径计算"))
        for rules in reversed(chain):
            for predicate in rules.get("filters", []):
                clauses.append(_filter_note(model, predicate))
            if rules.get("quality_filter"):
                clauses.append({"baseline": "质量基准", "affected": "受影响部分", "unaffected": "未受影响部分"}.get(rules.get("role"), "质量范围"))
                clauses.append("受影响判定：" + _filter_note(model, rules["quality_filter"]))
        policies = {
            "duplicate_policy": {"keep": "完全重复记录保留", "drop_exact": "完全重复记录去重"},
            "invalid_date_policy": {"exclude": "无效日期排除"},
            "numeric_error_policy": {"fail": "数值解析错误即停止", "coerce_and_warn": "数值解析错误转为缺失并警告"},
            "missing_dimension_policy": {"include_unclassified": "缺失对象保留为未分类"},
        }
        for key, labels in policies.items():
            value = next((rules[key] for rules in chain if rules.get(key)), None)
            if isinstance(value, dict):
                value = value.get("policy")
            if value in labels:
                clauses.append(labels[value])
        clauses.append("有效输入记录 " + number(scope["included_rows"]) + " 行")
        if scope.get("excluded_rows"):
            clauses.append("相对上级范围排除 " + number(scope["excluded_rows"]) + " 行")
        notes.append("；".join(dict.fromkeys(clauses)))

    describe(record["scope_id"])
    # Per-metric bindings take precedence over a broad composite row count.
    for bindings in (record.get("metric_scope_bindings", {}), record.get("scope_bindings", {})):
        for labels, sid in _binding_leaves(bindings):
            binding_labels = {**BINDING_LABELS, **({"baseline": "质量基准"} if record.get("kind") in {"quality_impact", "quality_diagnostic"} else {})}
            label = "／".join(binding_labels.get(value, value if re.fullmatch(r"\d{4}-\d{2}.*", value)
                          else business_name(model, value, fallback="分项")) for value in labels)
            describe(sid, label)
    return list(dict.fromkeys(notes))


def _chart_covers(model, chart, evidence):
    # A provenance reference is not a visual proof. Only direct single-metric
    # series/rank payloads can omit their table; comparisons/bridges/diagnostics
    # retain a table even when a related background chart cites their evidence.
    kind = evidence.get("kind")
    if kind == "metric_trend":
        categories, values = evidence.get("periods", []), evidence.get("values", [])
    elif kind in {"dimension_contribution", "dimension_breakdown"}:
        source_rows = evidence.get("result", {}).get("groups", evidence.get("rows", []))
        if any(any(key in row for key in ("order_count", "average_order_value", "share")) for row in source_rows):
            return False  # Extra decision-bearing measures are not in the rank chart.
        categories, values = [], []
        for row in source_rows:
            keys = row.get("dimensions") or [row.get("value", row.get("key"))]
            if len(keys) != 1 or keys[0] is None:
                return False
            categories.append(keys[0])
            values.append(row.get("metric"))
    else:
        return False
    if not categories or list(map(str, categories)) != list(map(str, chart.get("categories", []))):
        return False
    metric_names = {evidence.get("metric"), business_name(model, evidence.get("metric"))}
    return any(series.get("name") in metric_names and series.get("values") == values
               for series in chart.get("series", []))


def uncovered_evidence_ids(model: dict, chapter: dict) -> list[str]:
    chart_ids = set(chapter.get("chart_ids", []))
    covered = {ref for chart in model.get("charts", []) if chart.get("chart_id") in chart_ids
               for ref in chart.get("evidence_ids", []) if _chart_covers(model, chart, model.get("evidence_index", {}).get(ref, {}))}
    refs = record_evidence_ids(chapter)
    if not chart_ids and not refs:
        raise ValueError("章节缺少可见证明所需的证据")
    return [ref for ref in refs if ref not in covered]


def proof_table(model: dict, evidence_id: str) -> dict:
    """No recalculation or new claims: present the existing typed result."""
    evidence = model.get("evidence_index", {}).get(evidence_id)
    if not isinstance(evidence, dict):
        raise ValueError("章节证明引用的证据不存在")
    kind, result = evidence.get("kind"), evidence.get("result", {})
    contract = next((c for c in model.get("metric_contracts", []) if c.get("name") == evidence.get("metric")), {})
    chain = _scope_chain(model, evidence.get("scope_id"))
    scope_contract = next((r["metric_contract"] for r in chain if r.get("metric_contract")), {})
    metric = business_name(model, evidence.get("metric"))
    unit = str(evidence.get("unit") or contract.get("unit") or scope_contract.get("unit") or "")
    headers = ["对象／期间", _with_unit(metric, unit)]
    if kind == "seasonality":
        headers[-1] = _with_unit(metric + "月均值", unit)
    rows = []
    if kind in {"dimension_contribution", "dimension_breakdown", "cross_breakdown"}:
        dimensions = evidence.get("dimensions") or result.get("dimensions") or [evidence.get("dimension") or evidence.get("source_dimension")]
        headers = [business_name(model, value, fallback=f"维度{index + 1}") for index, value in enumerate(dimensions)] + [headers[-1]]
        source_rows = result.get("groups", evidence.get("rows", []))
        extra_labels = {"order_count": "订单数（单）", "average_order_value": _with_unit("单均金额", unit), "share": "占比（%）"}
        extras = [key for key in extra_labels if any(key in row for row in source_rows)]
        headers += [extra_labels[key] for key in extras]
        for row in source_rows:
            keys = row.get("dimensions") or [row.get("value", row.get("key"))]
            if len(keys) != len(dimensions) or any(value is None for value in keys):
                raise ValueError("证明表分组对象与维度不一致")
            if len(keys) == 1 and "display_value" in row:
                label = str(row["display_value"])
                keys = [label + "（名称缺失，显示编码）" if row.get("display_missing") else label]
            rows.append([*map(str, keys), number(row.get("metric")), *[
                "暂无有效值" if row.get(key) is None else (_percent(row[key]) if key == "share" else number(row[key])) for key in extras]])
    elif kind in {"dimension_yoy", "dimension_slice_yoy", "seasonality"}:
        obj = str(evidence.get("value") or "")
        if evidence.get("dimension"):
            obj = business_name(model, evidence["dimension"], fallback="对象") + "：" + obj
        if evidence.get("secondary_dimension"):
            obj += "／" + business_name(model, evidence["secondary_dimension"], fallback="细分对象") + "：" + str(evidence.get("secondary_value", ""))
        for key, period_key in (("comparison", "comparison_period"), ("latest", "latest_period")):
            period = evidence.get(period_key) or "、".join(evidence.get("comparison_periods" if key == "comparison" else "periods", []))
            if not period:
                raise ValueError("证明表缺少实际比较周期")
            rows.append([obj + " · " + str(period), number(evidence.get(key))])
        if evidence.get("ratio_components"):
            headers += ["分子", "分母"]
            for row, role in zip(rows, ("comparison", "latest")):
                components = evidence["ratio_components"][role]
                row.extend([number(components["numerator"]), number(components["denominator"])])
    elif kind == "metric_trend":
        periods, values = evidence.get("periods", []), evidence.get("values", [])
        if len(periods) != len(values):
            raise ValueError("证明表周期与数值数量不一致")
        rows = [[str(period), "暂无有效值" if value is None else number(value)] for period, value in zip(periods, values)]
    elif kind == "period_comparison":
        periods = result.get("comparison_scope") or next((r.get("comparison") or r.get("comparison_scope") for r in chain if r.get("comparison") or r.get("comparison_scope")), {})
        for key in ("baseline", "current"):
            labels = result.get(key + "_periods") or periods.get(key) or []
            rows.append([BINDING_LABELS[key] + ("：" + "、".join(map(str, labels)) if labels else ""), number(result.get(key))])
    elif kind == "transaction_driver_bridge":
        headers = ["指标", str(evidence.get("comparison_period") or "基期"), str(evidence.get("latest_period") or "本期")]
        for key, driver in evidence.get("semantics", {}).get("drivers", {}).items():
            if isinstance(driver, dict) and "previous" in driver and "latest" in driver:
                if driver["previous"] is None and driver["latest"] is None:
                    continue
                driver_unit = {"sales": unit, "orders": "单", "average_order_value": unit, "customers": "个"}.get(key, "")
                rows.append([_with_unit(business_name(model, key), driver_unit), *[
                    "暂无有效值" if driver[period] is None else number(driver[period]) for period in ("previous", "latest")]])
    elif kind in {"quality_impact", "quality_diagnostic"}:
        values = result if kind == "quality_impact" else evidence
        headers = ["质量口径", "数值"]
        labels = {"baseline_total": _with_unit("基准" + metric + "合计", unit), "affected_total": _with_unit("受影响" + metric + "合计", unit),
                  "unaffected_total": _with_unit("未受影响" + metric + "合计", unit), "affected_rows": "受影响记录（行）",
                  "affected_amount": _with_unit("受影响净金额", unit), "affected_absolute_amount": _with_unit("受影响绝对金额", unit),
                  "baseline_absolute_amount": _with_unit("基准绝对金额", unit)}
        rows = [[label, number(values[key])] for key, label in labels.items() if key in values]
    elif kind == "concentration":
        headers = ["集中度口径", "数值"]
        rows = [["头部占比（%）", _percent(result.get("top_share"))], ["对象数量", number(result.get("group_count"))]]
    else:
        raise ValueError("证据类型没有可靠的证明表展示：" + str(kind))
    if not rows:
        raise ValueError("证据证明表没有实际数据")
    table = {"headers": headers, "rows": rows, "scope_notes": scope_notes(model, evidence)}
    history = evidence.get("semantics", {}).get("concentration_continuity", [])
    if history:
        history_rows = []
        for item in history:
            history_rows.append([str(item["period"]), *[
                "暂无有效值" if item.get(key) is None else (_percent(item[key]) if key.endswith("share") else number(item[key]))
                for key in ("top_1_share", "top_5_share", "top_5_amount", "total", "sample_count")]])
        table["history"] = {"headers": ["月份", "首位占比（%）", "前五占比（%）", "前五金额", "同月总额", "有效记录（行）"], "rows": history_rows}
    return table
