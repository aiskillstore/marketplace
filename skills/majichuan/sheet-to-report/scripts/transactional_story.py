from __future__ import annotations

"""Evidence-first business narrative for confirmed transaction-line tables."""

import re
from typing import Any

import pandas as pd


ROLE_LENSES = {
    "geography": "geography",
    "product": "product",
    "customer": "customer",
}
ROLE_LABELS = {
    "geography": "地域",
    "product": "商品",
    "customer": "客户",
}


def semantic_dimension_lenses(
    semantic_contract: dict[str, Any] | None,
    dimensions: tuple[str, ...] | list[str],
) -> dict[str, str]:
    """Resolve dimension lenses from confirmed roles before name heuristics."""

    contract = semantic_contract or {}
    mappings = contract.get("field_mappings", {}) if isinstance(contract, dict) else {}
    source_roles = {
        str(mapping.get("source_field")): ROLE_LENSES[role]
        for role, mapping in mappings.items()
        if role in ROLE_LENSES and isinstance(mapping, dict) and mapping.get("source_field")
    }
    resolved: dict[str, str] = {}
    for dimension in dimensions:
        name = str(dimension)
        if name in source_roles:
            resolved[name] = source_roles[name]
            continue
        lowered = name.lower()
        if any(marker in lowered for marker in ("区域", "地域", "region", "geo", "country", "market")):
            resolved[name] = "geography"
        elif any(marker in lowered for marker in ("品类", "商品", "产品", "sku", "product", "stock")):
            resolved[name] = "product"
        elif any(marker in lowered for marker in ("客户", "用户", "customer", "user", "buyer")):
            resolved[name] = "customer"
        else:
            resolved[name] = "growth_driver"
    return resolved


def _blank(series: pd.Series) -> pd.Series:
    return series.isna() | series.astype(str).str.strip().eq("")


def _number(value: float) -> str:
    return f"{float(value):,.2f}"


def _pct(value: float | None) -> str:
    return "不可计算" if value is None else f"{float(value):.1%}"


def _is_identifier_field(field: str) -> bool:
    """Use field tokens/suffixes rather than arbitrary substrings (e.g. PaidCountry)."""

    text = str(field).strip()
    if text.endswith(("编号", "编码", "代码")):
        return True
    chunks = re.split(r"[^A-Za-z0-9]+", text)
    tokens: list[str] = []
    for chunk in chunks:
        tokens.extend(
            token.lower()
            for token in re.findall(r"[A-Z]+(?=[A-Z][a-z]|\d|$)|[A-Z]?[a-z]+|\d+", chunk)
        )
    if tokens and tokens[-1] in {"id", "key", "code", "sku", "stock", "number", "no"}:
        return True
    fused = re.sub(r"[^a-z0-9]+", "", text.lower())
    return bool(re.fullmatch(
        r"(?:customer|user|buyer|product|item|stock|account|order|invoice|transaction)"
        r"(?:id|key|code|sku|stock|number|no)",
        fused,
    ))


def _identifier_value(value: Any) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    text = str(value).strip()
    if text.endswith(".0"):
        prefix = text[:-2]
        if prefix.lstrip("-").isdigit():
            return prefix
    return text


def _display_object_value(
    value: Any, *, role: str, identifier: bool, display_value: Any | None = None,
) -> str:
    label = ROLE_LABELS[role]
    key = _identifier_value(value)
    named = str(display_value or "").strip()
    if named and named != key:
        # A verified display field is the presentation contract.  The
        # identifier remains in evidence.rows[].key for audit, never headline copy.
        return named
    if identifier:
        return f"{label}编号 {key}" if role == "customer" else f"{label}编码 {key}"
    return key


def _additive_sales_contract(analysis: dict[str, Any]) -> dict[str, Any] | None:
    contracts = list(analysis.get("metric_contracts", []))
    return next(
        (
            item for item in contracts
            if item.get("role") == "outcome"
            and item.get("aggregation") in {"sum", "sum_product"}
        ),
        next((item for item in contracts if item.get("aggregation") in {"sum", "sum_product"}), None),
    )


def _story_outcome_series(
    frame: pd.DataFrame,
    contract: dict[str, Any],
) -> tuple[pd.Series, str] | None:
    """Evaluate the selected additive outcome using the metric whitelist only."""

    aggregation = str(contract.get("aggregation") or "")
    if aggregation == "sum":
        source_field = str(contract.get("source_field") or contract.get("name") or "")
        if not source_field or source_field not in frame.columns:
            return None
        return (
            pd.to_numeric(frame[source_field], errors="coerce"),
            f"按 {source_field} 合计",
        )
    if aggregation == "sum_product":
        factors = contract.get("factors")
        if (
            not isinstance(factors, (list, tuple))
            or len(factors) != 2
            or any(str(field) not in frame.columns for field in factors)
        ):
            return None
        left_field, right_field = (str(field) for field in factors)
        left = pd.to_numeric(frame[left_field], errors="coerce")
        right = pd.to_numeric(frame[right_field], errors="coerce")
        return (
            left * right,
            f"按 {left_field} × {right_field} 逐行计算后合计",
        )
    return None


def _amount(series: pd.Series) -> float:
    value = pd.to_numeric(series, errors="coerce").sum(min_count=1)
    return 0.0 if pd.isna(value) else float(value)


def _concentration_summary(history: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [row for row in history if row.get("top_5_share") is not None]
    lowest = min(valid, key=lambda row: row["top_5_share"]) if valid else None
    highest = max(valid, key=lambda row: row["top_5_share"]) if valid else None
    return {
        "period_count": len(history), "valid_period_count": len(valid),
        "min_period": lowest["period"] if lowest else None,
        "max_period": highest["period"] if highest else None,
        "top_5_share_min": lowest["top_5_share"] if lowest else None,
        "top_5_share_max": highest["top_5_share"] if highest else None,
        "top_5_share_range_pp": (highest["top_5_share"] - lowest["top_5_share"]) * 100 if valid else None,
    }


def _history_statement(label: str, semantics: dict[str, Any]) -> str:
    summary = semantics["concentration_summary"]
    if summary["valid_period_count"] < 2:
        return f"{label}历史完整月有效分母不足，稳定性待核"
    return (
        f"历史完整月{label}Top 5为{_pct(summary['top_5_share_min'])}"
        f"至{_pct(summary['top_5_share_max'])}，"
        f"极差{summary['top_5_share_range_pp']:.2f}个百分点"
    )


def _contribution_record(
    frame: pd.DataFrame,
    *,
    role: str,
    field: str,
    metric_name: str,
    unit: str,
    formula: str,
    mapping: dict[str, Any] | None = None,
    time_field: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]] | None:
    scope = frame.loc[~_blank(frame[field])].copy()
    if scope.empty:
        return None
    grouped = (
        scope.groupby(field, dropna=False)["__story_outcome"]
        .sum()
        .sort_values(ascending=False, kind="mergesort")
    )
    if grouped.empty:
        return None
    total = float(grouped.sum())
    top = grouped.head(5)
    mapping = mapping or {}
    display_field = str(
        mapping.get("display_field") or mapping.get("display_name_field") or ""
    )
    if display_field not in scope.columns:
        display_field = ""
    value_kind = str(mapping.get("value_kind") or "").strip().lower()
    identifier = value_kind == "identifier" or (
        value_kind != "business_object" and _is_identifier_field(field)
    )

    def display_for(value: Any) -> str:
        display_value = None
        if display_field:
            values = scope.loc[scope[field].eq(value), display_field]
            values = values.loc[~_blank(values)]
            if not values.empty:
                display_value = values.astype(str).mode().iloc[0]
        return _display_object_value(
            value, role=role, identifier=identifier, display_value=display_value,
        )

    rows = []
    for index, (value, amount) in enumerate(top.items()):
        grouped_rows = scope.loc[scope[field].eq(value)]
        order_count = int(grouped_rows["__transaction_order"].nunique())
        rows.append({
            "value": display_for(value), "key": _identifier_value(value),
            "metric": float(amount), "rank": index + 1, "is_other": False,
            "order_count": order_count,
            "average_order_value": float(amount / order_count) if order_count else None,
        })
    if len(grouped) > len(top):
        rows.append({
            "value": "其他",
            "metric": float(grouped.iloc[len(top):].sum()),
            "rank": None,
            "is_other": True,
            "member_count": int(len(grouped) - len(top)),
        })
    top_1_share = float(top.iloc[0] / total) if total else None
    top_5_share = float(top.sum() / total) if total else None
    continuity: list[dict[str, Any]] = []
    if time_field and time_field in scope.columns:
        periods = pd.to_datetime(scope[time_field], errors="coerce").dt.to_period("M")
        for period in sorted(periods.dropna().unique()):
            period_rows = scope.loc[periods.eq(period)]
            period_values = period_rows.groupby(field)["__story_outcome"].sum()
            period_total = float(period_values.sum())
            top_1_amount = float(period_values.max())
            top_5_amount = float(period_values.nlargest(5).sum())
            continuity.append({
                "period": str(period), "total": period_total,
                "top_1_amount": top_1_amount, "top_5_amount": top_5_amount,
                "sample_count": int(len(period_rows)),
                "top_1_share": top_1_amount / period_total if period_total > 0 else None,
                "top_5_share": top_5_amount / period_total if period_total > 0 else None,
            })
    concentration_summary = _concentration_summary(continuity)
    lens = ROLE_LENSES[role]
    label = ROLE_LABELS[role]
    evidence_id = f"transaction:{lens}:net_sales"
    limitations = []
    if role == "customer":
        limitations.append("缺失客户标识的交易保留在销售总盘，但不进入客户贡献排名。")
    if role == "product":
        limitations.append("费用、调整等非商品项在未获确认前保留，不自动从商品字段剔除。")
    evidence = {
        "evidence_id": evidence_id,
        "kind": "dimension_contribution",
        "dimension": label,
        "source_dimension": field,
        "metric": metric_name,
        "unit": unit,
        "value": float(top.iloc[0]),
        "rows": rows,
        "formula": formula,
        "filter_scope": f"{label}标识有效且交易金额可计算",
        "sample_count": int(len(scope)),
        "affected_rows": int(len(frame) - len(scope)),
        "affected_amount": _amount(frame.loc[_blank(frame[field]), "__story_outcome"]),
        "business_objects": [role, "sales"],
        "limitations": limitations,
        "semantics": {
            "view_type": "contribution",
            "value_kind": "identifier" if identifier else "business_object",
            "identifier_field": field if identifier else None,
            "display_field": display_field or None,
            "top_1_share": top_1_share,
            "top_5_share": top_5_share,
            "total_member_count": int(len(grouped)),
            "scope_total": total,
            "concentration_continuity": continuity,
            "concentration_summary": concentration_summary,
            "concentration_stable": (
                concentration_summary["top_5_share_range_pp"] < 10
            ) if concentration_summary["valid_period_count"] >= 2 else None,
        },
    }
    top_value = rows[0]["value"]
    id_only = identifier and not display_field
    if id_only:
        headline = f"{label}贡献已量化，但当前仅有{label}{'编号' if role == 'customer' else '编码'}"
        statement = (
            f"当前表可计算{label}Top 1 与 Top 5的{metric_name}贡献（{_pct(top_1_share)}、{_pct(top_5_share)}），"
            f"但仅有{label}{'编号' if role == 'customer' else '编码'}，不能把标识符当作业务名称。"
        )
    else:
        headline = f"{top_value}的{metric_name}贡献最高"
        statement = (
            f"{label}“{top_value}”的{metric_name}贡献最高，占有效{label}{metric_name}的"
            f"{_pct(top_1_share)}；Top 5 合计贡献{_pct(top_5_share)}。"
        )
    history_supported = concentration_summary["valid_period_count"] >= 2
    if not id_only and history_supported:
        statement = (
            f"{label}“{top_value}”贡献最高（{_pct(top_1_share)}），"
            f"覆盖{rows[0]['order_count']:,}笔订单，单均金额"
            f"{_number(rows[0]['average_order_value'])}{unit}；"
            f"{_history_statement(label, evidence['semantics'])}。"
        )
    insight = {
        "insight_id": f"transaction-{lens}-01",
        "headline": headline,
        "statement": statement,
        "answer_text": statement,
        "answer_status": "partial" if id_only else "answered",
        "evidence_strength": "high",
        "kind": "fact",
        "presentation_role": "supporting" if id_only else "featured",
        "actionable": bool(not id_only and history_supported),
        "confidence": "high",
        "implication": (
            f"{label}头部贡献需要与订单覆盖及单均金额一起管理；以已算出的历史占比范围作为下一完整月的变化触发线，超出后先定位对象变化。"
            if not id_only and history_supported else
            f"{label}贡献结构已经量化，应结合后续完整周期判断集中度是否持续。"
        ),
        "evidence_ids": [evidence_id],
        "lens": lens,
        "value_score": 4,
        "limitations": limitations,
    }
    chart = {
        "chart_id": f"chart-transaction-{lens}-sales",
        "chart_type": "bar",
        "title": f"{metric_name}按{label}贡献",
        "editable": True,
        "aspect_ratio": 1.85,
        "categories": [row["value"] for row in rows],
        "series": [{"name": metric_name, "values": [row["metric"] for row in rows]}],
        "evidence_ids": [evidence_id],
        "unit": unit,
        "display_unit": unit,
        "display_scale": 1.0,
        "number_format": "#,##0",
        "scope_label": f"有效{label}交易范围",
        "takeaway": str(insight["headline"]),
        "lens": lens,
    }
    return evidence, insight, chart


def _latest_period_driver_bridge(
    frame: pd.DataFrame,
    *,
    time_field: str,
    customer_field: str | None,
    metric_name: str,
    unit: str,
    formula: str,
    retained_periods: list[str] | None = None,
    excluded_periods: list[str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    """Decompose sales change into orders, average order value and customers."""

    if time_field not in frame.columns:
        return None
    dates = pd.to_datetime(frame[time_field], errors="coerce")
    scoped = frame.loc[dates.notna()].copy()
    if scoped.empty:
        return None
    scoped["__story_period"] = dates.loc[scoped.index].dt.to_period("M")
    periods = sorted(scoped["__story_period"].dropna().unique())
    if len(periods) < 2:
        return None
    previous_period, latest_period = periods[-2], periods[-1]
    if int(latest_period.ordinal) - int(previous_period.ordinal) != 1:
        return None

    def snapshot(period: Any) -> dict[str, float | int | None]:
        rows = scoped.loc[scoped["__story_period"].eq(period)]
        sales = _amount(rows["__story_outcome"])
        orders = int(rows["__transaction_order"].nunique())
        customers = (
            int(rows.loc[~_blank(rows[customer_field]), customer_field].nunique())
            if customer_field and customer_field in rows.columns else None
        )
        return {
            "sales": sales,
            "orders": orders,
            "average_order_value": float(sales / orders) if orders else None,
            "customers": customers,
        }

    previous = snapshot(previous_period)
    latest = snapshot(latest_period)

    def change(name: str) -> float | None:
        before, after = previous[name], latest[name]
        if before in (None, 0) or after is None:
            return None
        return float((float(after) - float(before)) / float(before))

    drivers = {
        key: {"previous": previous[key], "latest": latest[key], "change_pct": change(key)}
        for key in ("sales", "orders", "average_order_value", "customers")
    }
    evidence = {
        "evidence_id": "transaction:driver_bridge:latest_complete_period",
        "kind": "transaction_driver_bridge",
        "metric": metric_name,
        "dimension": "成交单量",
        "unit": unit,
        "value": latest["sales"],
        "latest": latest["sales"],
        "previous": previous["sales"],
        "change_pct": change("sales"),
        "formula": formula,
        "filter_scope": "分析窗口内相邻完整月的有效订单交易范围",
        "sample_count": int(len(scoped.loc[scoped["__story_period"].isin([previous_period, latest_period])])),
        "latest_period": str(latest_period),
        "comparison_period": str(previous_period),
        "business_objects": ["sales", "orders", "average_order_value", "customers"],
        "semantics": {
            "drivers": drivers,
            "identity": "sales = orders × average_order_value",
            "retained_periods": list(retained_periods or [str(value) for value in periods]),
            "excluded_periods": list(excluded_periods or []),
        },
        "limitations": [
            "客户数仅在客户标识有效时计算；未确认的取消、退货和调整项仍保留在销售总盘。"
        ],
    }
    statement = (
        f"{latest_period}相对{previous_period}，{metric_name}{_pct(change('sales'))}，"
        f"成交单量{_pct(change('orders'))}，单均销售额{_pct(change('average_order_value'))}，"
        f"有效客户覆盖{_pct(change('customers'))}；销售额按成交单量×单均销售额拆解。"
    )
    insight = {
        "insight_id": "transaction-growth-driver-01",
        "headline": f"{metric_name}{_pct(change('sales'))}需按成交单量与单均销售额共同拆解",
        "statement": statement,
        "answer_text": statement,
        "answer_status": "answered",
        "evidence_strength": "high",
        "kind": "fact",
        "presentation_role": "featured",
        "actionable": True,
        "confidence": "high",
        "implication": "先判断订单规模和客单变化是否同向，再将地域、商品和客户贡献作为结构验证。",
        "evidence_ids": ["transaction:driver_bridge:latest_complete_period"],
        "lens": "growth_driver",
        "value_score": 5,
        "limitations": list(evidence["limitations"]),
    }
    return evidence, insight


def build_transactional_business_content(
    *,
    analysis: dict[str, Any],
    transactional_result: dict[str, Any],
    semantic_contract: dict[str, Any],
    scope_registry=None,
    scope_parent_id: str = "source_rows",
) -> dict[str, list[dict[str, Any]] | dict[str, dict[str, Any]]]:
    """Create general transaction insights without case-specific labels or rules."""

    sales_contract = _additive_sales_contract(analysis)
    if not sales_contract:
        return {"evidence_index": {}, "insights": [], "actions": [], "charts": []}
    metric_name = str(sales_contract["name"])
    unit = str(sales_contract.get("unit") or "")
    frame = transactional_result["prepared_frame"]
    outcome = _story_outcome_series(frame, sales_contract)
    if outcome is None:
        return {"evidence_index": {}, "insights": [], "actions": [], "charts": []}
    outcome_series, outcome_formula = outcome
    frame = frame.assign(__story_outcome=outcome_series)
    computable = frame.loc[
        frame["__story_outcome"].notna()
        & ~_blank(frame["__transaction_order"])
    ].copy()
    if len(computable) < 2:
        return {"evidence_index": {}, "insights": [], "actions": [], "charts": []}
    mappings = transactional_result.get("analysis_contract", {}).get("field_mappings", {})

    def register_scope(rows, *, filters, comparison=None, definition):
        return scope_registry.register(rows, parent_scope_id=scope_parent_id, rules={
            "metric_contract": sales_contract, "filters": filters,
            "comparison": comparison, "stage": "transactional_story",
        }, definition=definition)

    computable_filters = [
        {"field": "__story_outcome", "operator": "not_null", "formula": outcome_formula},
        {"field": "__transaction_order", "operator": "not_blank"},
    ]

    evidence: dict[str, dict[str, Any]] = {}
    insights: list[dict[str, Any]] = []
    levers: list[dict[str, Any]] = []
    charts: list[dict[str, Any]] = []
    role_records: dict[str, dict[str, Any]] = {}
    semantic_mappings = (
        semantic_contract.get("field_mappings", {})
        if isinstance(semantic_contract, dict) else {}
    )
    for role in ("geography", "product", "customer"):
        field = mappings.get(role)
        if not field or field not in computable.columns:
            continue
        built = _contribution_record(
            computable,
            role=role,
            field=str(field),
            metric_name=metric_name,
            unit=unit,
            formula=outcome_formula,
            mapping=(semantic_mappings.get(role) if isinstance(semantic_mappings.get(role), dict) else None),
            time_field=str(mappings.get("time") or ""),
        )
        if not built:
            continue
        record, insight, chart = built
        if scope_registry is not None:
            object_rows = computable.loc[~_blank(computable[str(field)])]
            record["scope_id"] = register_scope(object_rows,
                filters=[*computable_filters, {"field": str(field), "operator": "not_blank"}],
                definition=f"分析窗口内金额可计算、订单及{field}有效的交易；排名分母不含缺失{field}记录。")
            time_field = str(mappings.get("time") or "")
            if time_field in object_rows.columns:
                object_periods = pd.to_datetime(object_rows[time_field], errors="coerce").dt.to_period("M").astype(str)
                record["scope_bindings"] = {}
                for item in record["semantics"]["concentration_continuity"]:
                    period = item["period"]
                    item["scope_id"] = register_scope(object_rows.loc[object_periods.eq(period)],
                        filters=[*computable_filters, {"field": str(field), "operator": "not_blank"},
                                 {"field": time_field, "operator": "period_in", "values": [period], "period_type": "month"}],
                        definition=f"{period}完整月有效{ROLE_LABELS[role]}交易；本月净金额为占比分母。")
                    record["scope_bindings"][period] = item["scope_id"]
        from analysis_depth import contribution_judgement_binding
        binding = contribution_judgement_binding(record)
        if binding:
            insight['claim_binding'] = binding
            insight['kind'] = 'diagnostic'
        evidence[str(record["evidence_id"])] = record
        insights.append(insight)
        charts.append(chart)
        role_records[role] = record

    story_period_scope = transactional_result.get("story_period_scope", {})
    bridge = _latest_period_driver_bridge(
        computable,
        time_field=str(mappings.get("time") or ""),
        customer_field=(str(mappings["customer"]) if mappings.get("customer") else None),
        metric_name=metric_name,
        unit=unit,
        formula=outcome_formula,
        retained_periods=(list(story_period_scope.get("retained_periods") or []) if isinstance(story_period_scope, dict) else None),
        excluded_periods=(list(story_period_scope.get("excluded_periods") or []) if isinstance(story_period_scope, dict) else None),
    )
    if bridge:
        bridge_evidence, bridge_insight = bridge
        if scope_registry is not None:
            time_field = str(mappings.get("time") or "")
            periods = pd.to_datetime(computable[time_field], errors="coerce").dt.to_period("M").astype(str)
            comparison = {"field": time_field, "period_type": "month", "aggregation": "metric_aggregate",
                          "baseline": [bridge_evidence["comparison_period"]], "current": [bridge_evidence["latest_period"]]}
            rows = computable.loc[periods.isin([*comparison["baseline"], *comparison["current"]])]
            bridge_evidence["scope_id"] = register_scope(rows, filters=computable_filters, comparison=comparison,
                definition=f"{comparison['baseline'][0]}与{comparison['current'][0]}相邻月：金额可计算且订单有效的交易。")
            bindings = {}
            for role, labels in (("baseline", comparison["baseline"]), ("current", comparison["current"])):
                period_rows = rows.loc[periods.loc[rows.index].isin(labels)]
                bindings[role] = register_scope(period_rows, filters=computable_filters,
                    comparison={**comparison, "role": role}, definition=f"驱动拆解{role}：{','.join(labels)}有效订单交易。")
                customer_field = mappings.get("customer")
                if customer_field and customer_field in rows.columns:
                    bindings[role + "_customers"] = register_scope(period_rows.loc[~_blank(period_rows[customer_field])],
                        filters=[*computable_filters, {"field": customer_field, "operator": "not_blank"}],
                        comparison={**comparison, "role": role}, definition=f"{','.join(labels)}客户覆盖：仅有效客户标识的订单交易。")
            bridge_evidence["scope_bindings"] = bindings
            bridge_evidence["metric_scope_bindings"] = {
                metric: {role: bindings[role + "_customers"] if metric == "customers" else bindings[role]
                         for role in ("baseline", "current")}
                for metric in ("sales", "orders", "average_order_value", "customers")
                if metric != "customers" or "baseline_customers" in bindings
            }
        evidence[str(bridge_evidence["evidence_id"])] = bridge_evidence
        insights.append(bridge_insight)
        drivers = bridge_evidence["semantics"]["drivers"]
        levers.extend([
            {
                "lever_id": "transaction-lever-orders",
                "label": "成交单量",
                "headline": f"成交单量{_pct(drivers['orders']['change_pct'])}",
                "takeaway": "订单规模是销售变化的第一层驱动。",
                "evidence_ids": [str(bridge_evidence["evidence_id"])],
            },
            {
                "lever_id": "transaction-lever-aov",
                "label": "单均销售额",
                "headline": f"单均销售额{_pct(drivers['average_order_value']['change_pct'])}",
                "takeaway": "单均销售额与成交单量共同决定销售变化。",
                "evidence_ids": [str(bridge_evidence["evidence_id"])],
            },
            *([{
                "lever_id": "transaction-lever-customers",
                "label": "有效客户覆盖",
                "headline": f"有效客户覆盖{_pct(drivers['customers']['change_pct'])}",
                "takeaway": "有效客户覆盖用于验证订单变化是否来自客户覆盖。",
                "evidence_ids": [str(bridge_evidence["evidence_id"])],
            }] if drivers["customers"]["change_pct"] is not None else []),
        ])

    geography_aov_opportunity: dict[str, Any] | None = None
    geography_record = role_records.get("geography")
    if geography_record:
        ranked_geographies = [
            row for row in geography_record["rows"] if not row.get("is_other")
        ]
        if ranked_geographies:
            core = ranked_geographies[0]
            core_orders = int(core.get("order_count") or 0)
            core_aov = core.get("average_order_value")
            minimum_orders = max(3, int((core_orders * 0.2) + 0.999999))
            candidate = next((
                row for row in ranked_geographies[1:]
                if int(row.get("order_count") or 0) >= minimum_orders
                and core_aov not in (None, 0)
                and row.get("average_order_value") is not None
                and float(row["average_order_value"]) >= float(core_aov) * 1.2
            ), None)
            if candidate:
                geography_aov_opportunity = candidate
                statement = (
                    f"非头部地域“{candidate['value']}”有{int(candidate['order_count']):,}笔订单，"
                    f"单均订单额{_number(float(candidate['average_order_value']))}{unit}，"
                    f"高于核心地域“{core['value']}”的{_number(float(core_aov))}{unit}；"
                    "先做受控验证，不直接作为扩张结论。"
                )
                insights.append({
                    "insight_id": "transaction-geography-aov-opportunity-01",
                    "headline": f"{candidate['value']}呈现可验证的高单均订单额机会",
                    "statement": statement,
                    "answer_text": statement,
                    "answer_status": "answered",
                    "evidence_strength": "high",
                    "kind": "fact",
                    "presentation_role": "featured",
                    "actionable": True,
                    "confidence": "high",
                    "implication": "先在该地域复核商品组合、客户结构与履约条件，再决定是否投入扩张资源。",
                    "evidence_ids": [str(geography_record["evidence_id"])],
                    "lens": "geography",
                    "value_score": 5,
                    "signal_type": "opportunity",
                    "limitations": [
                        "当前表未提供毛利、履约成本或营销投入，不能据此判断盈利性或扩张回报。"
                    ],
                })

    concentration_roles = [
        role for role in ("product", "customer") if role in role_records
    ]
    concentration_ids = [
        str(role_records[role]["evidence_id"]) for role in concentration_roles
    ]
    def concentration_history(role: str) -> str:
        return _history_statement(ROLE_LABELS[role], role_records[role]["semantics"])
    concentration_history_text = "；".join(
        concentration_history(role) for role in concentration_roles
    )
    if len(concentration_ids) >= 2:
        product_share = role_records["product"]["semantics"]["top_5_share"]
        customer_share = role_records["customer"]["semantics"]["top_5_share"]
        insights.insert(0, {
            "insight_id": "transaction-concentration-01",
            "headline": "商品与客户贡献集中度需要联合管理",
            "statement": (
                f"商品Top 5占{_pct(product_share)}，客户Top 5占{_pct(customer_share)}；"
                f"{concentration_history_text}。"
            ),
            "answer_text": (
                f"商品Top 5占{_pct(product_share)}，客户Top 5占{_pct(customer_share)}；"
                f"{concentration_history_text}。"
            ),
            "answer_status": "answered",
            "evidence_strength": "high",
            "kind": "diagnostic",
            "presentation_role": "featured",
            "actionable": True,
            "confidence": "high",
            "implication": "商品集中影响供给暴露，客户集中影响需求稳定性，两类风险需要分别验证。",
            "evidence_ids": concentration_ids,
            "lens": "concentration",
            "value_score": 5,
            "limitations": [
                "集中度来自当前数据范围，不包含表外合同、毛利或客户关系信息。"
            ],
        })

    decisions = transactional_result.get("quality_decisions", {})
    quality_scope = frame.loc[
        frame["__transaction_quantity"].notna()
        & frame["__transaction_unit_price"].notna()
        & ~_blank(frame["__transaction_order"])
    ].copy()
    scope_rows = int(len(quality_scope))

    def quality_amount(mask: pd.Series) -> tuple[float, float, int, int]:
        rows = quality_scope.loc[mask]
        values = pd.to_numeric(rows["__story_outcome"], errors="coerce")
        absolute_amount = values.abs().sum(min_count=1)
        return (
            _amount(values),
            0.0 if pd.isna(absolute_amount) else float(absolute_amount),
            int(values.notna().sum()),
            int(values.isna().sum()),
        )

    def quality_source_diagnostics(mask: pd.Series) -> dict[str, list[dict[str, Any]]]:
        rows = quality_scope.loc[mask]
        def top_counts(values: pd.Series, name: str) -> list[dict[str, Any]]:
            return [{name: _identifier_value(value), "rows": int(count)} for value, count in values.value_counts().head(5).items()]
        time_field = str(mappings.get("time") or "")
        by_month = []
        if time_field in rows.columns:
            by_month = top_counts(pd.to_datetime(rows[time_field], errors="coerce").dt.to_period("M").dropna().astype(str), "period")
        product_field = str(mappings.get("product") or "")
        return {
            "by_month": by_month,
            "by_order": top_counts(rows["__transaction_order"].dropna(), "order_key"),
            "by_product": top_counts(rows[product_field].dropna(), "product_key") if product_field in rows.columns else [],
        }

    negative_mask = quality_scope["__transaction_quantity"].lt(0)
    zero_price_mask = quality_scope["__transaction_unit_price"].eq(0)
    quality_specs = [
        ("negative_quantity", "负数量交易", str(decisions.get("negative_quantity", {}).get("rule") or "quantity < 0"), negative_mask),
        ("zero_price", "零价交易", str(decisions.get("zero_price", {}).get("rule") or "unit_price = 0"), zero_price_mask),
    ]
    customer_field = mappings.get("customer")
    if customer_field and customer_field in quality_scope.columns:
        quality_specs.append((
            "missing_customer", "缺失客户标识交易",
            "customer identifier is blank", _blank(quality_scope[customer_field]),
        ))
    quality_ids: list[str] = []
    material_quality_ids: list[str] = []
    quality_scope_values = pd.to_numeric(quality_scope["__story_outcome"], errors="coerce")
    quality_scope_amount = quality_scope_values.abs().sum(min_count=1)
    quality_scope_amount = 0.0 if pd.isna(quality_scope_amount) else float(quality_scope_amount)
    for code, label, rule, mask in quality_specs:
        evidence_id = f"transaction:quality:{code}"
        quality_ids.append(evidence_id)
        amount_value, affected_absolute_amount, amount_sample_count, amount_missing_rows = quality_amount(mask)
        limitations = []
        if amount_missing_rows:
            limitations.append(
                f"{amount_missing_rows:,} 行满足质量规则但当前 outcome 不可计算，影响金额未包含这些行。"
            )
        affected_rows = int(mask.fillna(False).sum())
        row_share = float(affected_rows / scope_rows) if scope_rows else 0.0
        amount_share = float(affected_absolute_amount / quality_scope_amount) if quality_scope_amount else 0.0
        tier = "high" if max(row_share, amount_share) >= 0.01 else ("low" if affected_rows else "zero")
        if tier == "high":
            material_quality_ids.append(evidence_id)
        limitations.append(f"材料性按行占比或绝对金额占比≥1%判定；当前为{tier}（行{_pct(row_share)}，金额{_pct(amount_share)}）。")
        evidence[evidence_id] = {
            "evidence_id": evidence_id,
            "kind": "quality_diagnostic",
            "metric": label,
            "value": affected_rows,
            "affected_amount": amount_value,
            "affected_absolute_amount": affected_absolute_amount,
            "baseline_absolute_amount": quality_scope_amount,
            "amount_formula": outcome_formula,
            "amount_sample_count": amount_sample_count,
            "formula": rule,
            "filter_scope": "可计算交易范围",
            "sample_count": scope_rows,
            "affected_rows": affected_rows,
            "business_objects": ["sales", "quality"],
            "limitations": limitations,
            "semantics": {"materiality": {"tier": tier, "row_share": row_share, "amount_share": amount_share, "high_threshold": 0.01}},
            "source_diagnostics": quality_source_diagnostics(mask),
        }
        if scope_registry is not None:
            base_filters = [
                {"field": "__transaction_quantity", "operator": "not_null"},
                {"field": "__transaction_unit_price", "operator": "not_null"},
                {"field": "__transaction_order", "operator": "not_blank"},
            ]
            quality_predicate = {
                "negative_quantity": {"field": "__transaction_quantity", "operator": "lt", "value": 0},
                "zero_price": {"field": "__transaction_unit_price", "operator": "eq", "value": 0},
                "missing_customer": {"field": customer_field, "operator": "is_blank"},
            }[code]
            base_id = register_scope(quality_scope, filters=base_filters,
                definition="分析窗口内数量与单价可解析、订单有效的交易质量总盘；金额影响另按有效金额计算。")
            affected = quality_scope.loc[mask.fillna(False)]
            evidence[evidence_id]["scope_id"] = base_id
            evidence[evidence_id]["scope_bindings"] = {
                "baseline": base_id,
                "affected": register_scope(affected, filters=[*base_filters, quality_predicate], definition=label + "影响行范围。"),
                "baseline_amount": register_scope(quality_scope.loc[quality_scope_values.notna()],
                    filters=[*base_filters, computable_filters[0]], definition="质量总盘中金额可计算记录；分母为逐行金额绝对值之和。"),
                "affected_amount": register_scope(affected.loc[affected["__story_outcome"].notna()],
                    filters=[*base_filters, quality_predicate, computable_filters[0]], definition=label + "中金额可计算记录；影响按逐行绝对值合计。"),
            }
    if material_quality_ids:
        material_quality_rows = [evidence[evidence_id] for evidence_id in material_quality_ids]
        material_labels = [str(item["metric"]) for item in material_quality_rows]
        quality_headline = "、".join(material_labels) + "达到材料性阈值"
        quality_statement = "；".join(
            f"{item['metric']}{int(item['affected_rows']):,}行，绝对影响金额{_number(item['affected_absolute_amount'])}{unit}"
            for item in material_quality_rows
        ) + "，需优先治理"
        insights.insert(0, {
            "insight_id": "transaction-quality-01",
            "headline": quality_headline,
            "statement": quality_statement + "。",
            "answer_text": quality_statement + "。",
            "answer_status": "answered",
            "evidence_strength": "high",
            "kind": "diagnostic" if len(material_quality_ids) >= 2 else "fact",
            "presentation_role": "featured",
            "actionable": bool(len(material_quality_ids) >= 2),
            "confidence": "high",
            "implication": "主线只治理达到材料性阈值的例外，低材料性与零例外保留在证据附录。",
            "evidence_ids": material_quality_ids,
            "lens": "quality",
            "value_score": 5,
            "limitations": [
                "未确认取消、退货或异常价格业务规则，因此不把负数量自动等同为退款。"
            ],
            "signal_type": "risk",
            "display_label": "交易质量",
        })
        charts.append({
            "chart_id": "chart-transaction-quality-exceptions",
            "chart_type": "bar",
            "title": "交易质量例外行数",
            "editable": True,
            "aspect_ratio": 1.85,
            "categories": material_labels,
            "series": [{
                "name": "影响行数",
                "values": [int(item["affected_rows"]) for item in material_quality_rows],
            }],
            "evidence_ids": material_quality_ids,
            "unit": "行",
            "display_unit": "行",
            "display_scale": 1.0,
            "number_format": "#,##0",
            "scope_label": "可计算交易范围",
            "takeaway": quality_headline,
            "lens": "quality",
        })

    driver_ids = [
        str(role_records[role]["evidence_id"])
        for role in ("geography", "product", "customer") if role in role_records
    ]
    if len(driver_ids) >= 2 and not bridge:
        insights.insert(0, {
            "insight_id": "transaction-growth-driver-01",
            "headline": "增长判断需要同时观察地域、商品与客户结构",
            "statement": (
                f"{metric_name}的地域、商品与客户贡献均已量化；"
                "地域、商品与客户贡献必须交叉观察，单一榜单不能代表综合增长质量。"
            ),
            "answer_text": (
                f"{metric_name}的地域、商品与客户贡献均已量化；"
                "地域、商品与客户贡献必须交叉观察，单一榜单不能代表综合增长质量。"
            ),
            "answer_status": "answered",
            "evidence_strength": "medium",
            "kind": "inference",
            "presentation_role": "featured",
            "actionable": False,
            "confidence": "medium",
            "implication": "下一周期应同时核验结构贡献、集中度与交易质量是否同向改善。",
            "evidence_ids": driver_ids,
            "lens": "growth_driver",
            "value_score": 5,
            "limitations": ["当前数据未包含毛利、履约或获客成本，不能据此判断利润贡献。"],
        })

    actions: list[dict[str, Any]] = []

    def monitoring_contract(roles: list[str]) -> dict[str, Any]:
        labels = "与".join(ROLE_LABELS[role] for role in roles)
        ranges = []
        for role in roles:
            summary = role_records[role]["semantics"]["concentration_summary"]
            if summary["valid_period_count"] >= 2:
                ranges.append(f"{ROLE_LABELS[role]}Top 5的{_pct(summary['top_5_share_min'])}至{_pct(summary['top_5_share_max'])}")
        trigger = (
            f"下一完整月各对象Top 5占比若超出各自历史观察范围（{'；'.join(ranges)}），触发头部对象及订单来源复核；范围内保持监控。"
            if len(ranges) == len(roles) else
            "下一完整月先确认各对象占比分母为正且至少两个完整月可比；不足时触发口径核验，不作稳定性结论。"
        )
        return {
            "action_type": "monitor",
            "steps": [f"按相同对象有效性与净金额口径，分别计算下一完整月{labels}Top 1、Top 5占比。",
                      "逐对象对照已展示的历史范围；越界后定位头部成员更替、订单覆盖与单均金额变化。"],
            "success_signal": trigger,
            "guardrails": ["分母非正、对象标识缺失策略变化或周期不完整时暂停跨期判断；越界原因未核清前暂停扩大投入。"],
            "limitations": ["观察范围来自本表历史，不是行业风险阈值；月度Top对象可以更替，不代表同一组对象的留存。",
                            *list(dict.fromkeys(note for role in roles for note in role_records[role]["limitations"]))],
        }

    if bridge:
        drivers = bridge[0]["semantics"]["drivers"]
        sales_change = _pct(drivers["sales"]["change_pct"])
        order_change = _pct(drivers["orders"]["change_pct"])
        aov_change = _pct(drivers["average_order_value"]["change_pct"])
        actions.append({
            "action_id": "transaction-action-growth-driver",
            "priority": 1,
        "headline": "按成交单量与单均销售额拆解下一周期销售变化",
            "text": (
                f"当前销售额变化为{sales_change}，成交单量为{order_change}、单均销售额为{aov_change}；"
                "下一周期先识别单量与单均变化是否反向，再用地域、商品与客户贡献定位变化来源。"
            ),
            "target": f"成交单量与单均销售额驱动（销售额环比{sales_change}）",
            "basis": "最近两个可比完整月已完成销售额=成交单量×单均销售额的确定性拆解。",
            "rationale": "先区分规模和单均销售额，避免把销售变化误判为单一市场或单一商品问题。",
            "verification_signal": "下一完整月销售额、成交单量、单均销售额与有效客户覆盖的环比变化是否符合目标方向",
            "evidence_ids": ["transaction:driver_bridge:latest_complete_period"],
            "source_insight_ids": ["transaction-growth-driver-01"],
            "lens": "growth_driver",
            "action_type": "monitor",
            "steps": ["使用相同完整月与订单有效口径，分别计算成交单量和单均销售额相对本期的变化。",
                      "订单量与单均金额反向变化时，按地域、商品和客户范围定位变化来源后再调整资源。"],
            "success_signal": "下一完整月成交单量和单均销售额若一升一降，触发结构拆解；销售额与单量×单均金额不一致时触发口径核验。",
            "guardrails": ["缺少相邻完整月或订单分母为零时暂停比较；未核实毛利与履约成本前不据销售增长扩大投入。"],
            "limitations": list(bridge[0]["limitations"]),
        })
    if geography_aov_opportunity:
        actions.append({
            "action_id": "transaction-action-geography-aov",
            "priority": 1,
            "headline": "以小范围验证非头部地域的高单均订单额",
            "text": (
                f"当前“{geography_aov_opportunity['value']}”已有{int(geography_aov_opportunity['order_count']):,}笔订单且单均订单额更高；"
                "先复核商品组合与客户结构，再以小范围投入验证订单数和单均订单额能否同步保持。"
            ),
            "target": f"地域“{geography_aov_opportunity['value']}”的高单均订单额机会",
            "basis": "非头部地域已满足最小订单样本并显著高于核心地域的单均订单额。",
            "rationale": "先验证结构与单位经济，再决定是否扩大市场投入，避免把单均差异直接等同于增长结论。",
            "verification_signal": "下一完整月该地域订单数、单均订单额、商品组合与客户覆盖是否仍高于核心地域基线",
            "evidence_ids": [str(geography_record["evidence_id"])],
            "source_insight_ids": ["transaction-geography-aov-opportunity-01"],
            "lens": "geography",
            "action_type": "controlled_test",
            "steps": [f"在“{geography_aov_opportunity['value']}”选择商品组合、客户结构可比的小范围订单，与核心地域“{core['value']}”同期对照。",
                      "先记录试验前订单数与单均金额；下一完整月分别比较试验范围与未调整对照的订单覆盖和单均金额，确认两组口径一致。"],
            "success_signal": f"在组合与客户结构可比时，“{geography_aov_opportunity['value']}”相对同期“{core['value']}”的单均金额优势保持，且自身订单覆盖不低于试验前可比完整月，才考虑后续扩大。",
            "guardrails": ["单均金额优势消失、可比订单覆盖下降或组合不可比时停止扩展；未取得毛利、履约成本证据前不得宣称盈利改善。"],
            "limitations": ["现有地域差异不是因果效果；对照未控制的结构差异仍可能影响结果。"],
        })
    if material_quality_ids:
        actions.append({
            "action_id": "transaction-action-quality",
            "priority": 1,
            "headline": f"建立{'、'.join(material_labels)}例外清单并按月复核",
            "text": f"已按订单、商品和月份定位{'、'.join(material_labels)}来源；下一完整周期复核其是否重复，并确认对应业务规则。",
            "target": "达到材料性阈值的交易质量例外：" + "、".join(material_labels),
            "basis": quality_statement + "，且已完成表内来源定位。",
            "rationale": "表内来源已定位；后续周期与已确认业务规则才是仍需验证的边界。",
            "verification_signal": f"下一完整月{'、'.join(material_labels)}的行数、绝对影响金额及已确认业务规则",
            "evidence_ids": material_quality_ids,
            "source_insight_ids": ["transaction-quality-01"],
            "lens": "quality",
            "action_type": "data_governance",
            "steps": ["按已定位的月份、订单与商品关联例外，逐类确认负向交易、缺失标识及调整记录的业务含义。",
                      "记录经确认的保留或排除规则，下一完整月按相同规则复算影响行数及绝对金额，并保留可追溯的变更记录。"],
            "success_signal": "每类材料性例外均有已确认业务规则和可追溯处理记录；相同规则下例外影响可复算，未确认项单独披露。",
            "guardrails": ["规则未经确认不得自动删除、补填或把负数量等同退款；治理前后口径不同不得直接比较增长。"],
            "limitations": ["仅能识别表内异常特征，不能推定异常的业务原因或自动纠正原始记录。"],
        })
    if concentration_ids:
        concentration_labels = "与".join(ROLE_LABELS[role] for role in concentration_roles)
        concentration_source_insights = (
            ["transaction-concentration-01"]
            if len(concentration_ids) >= 2
            else [f"transaction-{ROLE_LENSES[concentration_roles[0]]}-01"]
        )
        actions.append({
            "action_id": "transaction-action-concentration",
            "priority": 2,
            "headline": f"建立{concentration_labels}Top贡献跟踪",
            "text": f"历史完整月判断已完成：{concentration_history_text}；下一完整月验证该状态是否延续。",
            "target": f"高贡献{concentration_labels}",
            "basis": f"{concentration_labels}Top 5贡献已按有效范围计算；历史完整月判断为：{concentration_history_text}。",
            "rationale": f"{concentration_labels}集中度已分对象计算，需要独立验证各自的经营暴露。",
            "verification_signal": f"下一完整月{concentration_labels}Top 1、Top 5贡献占比及订单覆盖",
            "evidence_ids": concentration_ids,
            "source_insight_ids": concentration_source_insights,
            "lens": "concentration",
            **monitoring_contract(concentration_roles),
        })
    for role in ("product", "customer"):
        record = role_records.get(role)
        source_insight = next((item for item in insights if item["insight_id"] == f"transaction-{role}-01"), None)
        if not record or not source_insight or not source_insight["actionable"]:
            continue
        label = ROLE_LABELS[role]
        actions.append({
            "action_id": f"transaction-action-{role}", "priority": 2,
            "headline": f"按历史范围管理{label}头部暴露",
            "text": f"{concentration_history(role)}；结合头部订单覆盖定位变化后决定是否调整。",
            "target": f"{label}头部对象及其订单覆盖",
            "basis": source_insight["statement"],
            "rationale": f"{label}贡献、订单与历史波动已经可核验，越界后再定位对象变化，避免仅凭当前排名配置资源。",
            "verification_signal": f"下一完整月{label}Top 5占比是否落在历史观察范围内",
            "evidence_ids": [record["evidence_id"]], "source_insight_ids": [source_insight["insight_id"]],
            "lens": role, **monitoring_contract([role]),
        })
    geography = role_records.get("geography")
    if geography:
        top_geography = str(geography["rows"][0]["value"])
        actions.append({
            "action_id": "transaction-action-geography",
            "priority": 3,
            "headline": f"复核{top_geography}的贡献延续性与非头部市场变化",
            "text": f"按完整月拆解{top_geography}的销售与订单贡献，并对照其他地域的结构变化。",
            "target": top_geography,
            "basis": f"{top_geography}是当前地域{metric_name}最大贡献项。",
            "rationale": "地域头部贡献已量化，但是否可持续需要下一完整周期验证。",
            "verification_signal": f"下一完整月{top_geography}的销售、订单贡献占比及其他地域变化",
            "evidence_ids": [str(geography["evidence_id"])],
            "source_insight_ids": ["transaction-geography-01"],
            "lens": "geography",
            **monitoring_contract(["geography"]),
        })

    # Keep the visible verification field and the typed contract aligned.
    for action in actions:
        if action.get("success_signal"):
            action["verification_signal"] = action["success_signal"]

    return {
        "evidence_index": evidence,
        "insights": insights,
        "actions": actions,
        "levers": levers,
        "charts": charts,
    }
