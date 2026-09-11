from __future__ import annotations

"""Deterministic preparation for confirmed transactional-commerce tables."""

from typing import Any

import pandas as pd


_REQUIRED_ROLES = ("order", "quantity", "unit_price")
_OPTIONAL_SCOPE_ROLES = {
    "customer": "customer",
    "product": "product",
    "geography": "geography",
}
_ALLOWED_PREDICATES = {"equals", "not_equals", "in", "not_in", "is_null", "not_null"}
_QUALITY_DECISION_FIELDS = {
    "issue_id", "issue_type", "severity", "affected_rows",
    "affected_metric_value", "affected_fields", "decision_impact", "options",
    "selected_policy", "scope_ids", "status", "disclosure",
}


class QualityDecisionList(list[dict[str, Any]]):
    """List contract with read-only key access for v0.1 in-process callers."""

    def __init__(self, values: list[dict[str, Any]], legacy: dict[str, Any]) -> None:
        super().__init__(values)
        self._legacy = legacy

    def get(self, key: str, default: Any = None) -> Any:
        return self._legacy.get(key, default)

    def __getitem__(self, key: int | slice | str) -> Any:
        if isinstance(key, str):
            return self._legacy[key]
        return super().__getitem__(key)


def _blank(series: pd.Series) -> pd.Series:
    return series.isna() | series.astype(str).str.strip().eq("")


def _mapping_fields(
    contract: dict[str, Any], *, mode: str
) -> tuple[dict[str, str], list[str]]:
    mappings = contract.get("field_mappings", contract.get("mappings", {}))
    if not isinstance(mappings, dict):
        return {}, ["field_mappings"]
    fields: dict[str, str] = {}
    questions: list[str] = []
    for role, mapping in mappings.items():
        if isinstance(mapping, str):
            source_field, confidence = mapping, "high"
        elif isinstance(mapping, dict):
            source_field = str(mapping.get("source_field") or mapping.get("field") or "").strip()
            confidence = str(mapping.get("confidence") or "").lower()
        else:
            questions.append(str(role))
            continue
        confirmed_professional = (
            mode == "professional"
            and str(contract.get("confirmation_status") or "") == "confirmed"
        )
        accepted = confidence == "high" or (
            confidence == "medium" and confirmed_professional
        )
        if not source_field or not accepted:
            questions.append(str(role))
        else:
            fields[str(role)] = source_field
    return fields, questions


def _amount(series: pd.Series) -> float:
    return round(float(series.sum()), 6) if not series.empty else 0.0


def _filter_mask(frame: pd.DataFrame, rule: dict[str, Any]) -> pd.Series:
    predicate = str(rule.get("predicate") or rule.get("operator") or "").lower()
    field = str(rule.get("field") or "")
    if predicate not in _ALLOWED_PREDICATES:
        raise ValueError(f"交易过滤 predicate 不在白名单中：{predicate or '缺失'}")
    if field not in frame.columns:
        raise ValueError(f"交易过滤字段不存在：{field}")
    value = rule.get("value")
    values = rule.get("values", value)
    series = frame[field]
    if predicate == "equals":
        return series.eq(value)
    if predicate == "not_equals":
        return series.ne(value)
    if predicate == "in":
        return series.isin(values if isinstance(values, (list, tuple, set)) else [values])
    if predicate == "not_in":
        return ~series.isin(values if isinstance(values, (list, tuple, set)) else [values])
    if predicate == "is_null":
        return _blank(series)
    return ~_blank(series)


def _scope_record(name: str, input_frame: pd.DataFrame, retained: pd.DataFrame, rule: str) -> dict[str, Any]:
    excluded = input_frame.loc[~input_frame.index.isin(retained.index)]
    return {
        "scope": name,
        "filter_rule": rule,
        "input_rows": int(len(input_frame)),
        "retained_rows": int(len(retained)),
        "excluded_rows": int(len(excluded)),
        "affected_amount": _amount(excluded["__transaction_amount"]),
        "limitations": [],
    }


def _scope_catalog_record(
    scope_id: str,
    *,
    definition: str,
    input_frame: pd.DataFrame,
    included_frame: pd.DataFrame,
    filters: list[dict[str, Any]],
    quality_policy_ids: list[str],
) -> dict[str, Any]:
    return {
        "scope_id": scope_id,
        "definition": definition,
        "included_rows": int(len(included_frame)),
        "excluded_rows": int(len(input_frame) - len(included_frame)),
        "filters": filters,
        "quality_policy_ids": quality_policy_ids,
    }


def _confirmed_values(rule: Any) -> set[str]:
    if not isinstance(rule, dict):
        return set()
    values = rule.get("values", rule.get("value", ()))
    if not isinstance(values, (list, tuple, set)):
        values = (values,)
    return {str(value) for value in values if str(value).strip()}


def prepare_transactional_commerce(
    frame: pd.DataFrame,
    semantic_contract: dict[str, Any] | None,
    *,
    analysis_intent: str = "business_review",
    mode: str = "professional",
) -> dict[str, Any]:
    """Map a confirmed order-line table to safe columns and business scopes.

    No business labels, status values, or exclusions are inferred: every
    executable decision comes from a declarative confirmed contract.
    """
    contract = dict(semantic_contract or {})
    fields, questions = _mapping_fields(contract, mode=mode)
    if str(contract.get("table_grain") or "") not in {"order", "order_line"}:
        questions.append("table_grain")
    questions.extend(role for role in _REQUIRED_ROLES if role not in fields)
    questions.extend(
        f"{role}→{field}" for role, field in fields.items() if field not in frame.columns
    )
    if questions:
        return {
            "status": "needs_input",
            "questions": ["交易准备层需要确认：" + ", ".join(dict.fromkeys(questions))],
            "prepared_frame": frame.copy(),
            "analysis_lenses": [],
            "quality_decisions": [],
            "scope_catalog": [],
        }

    work = frame.copy()
    quantity = pd.to_numeric(work[fields["quantity"]], errors="coerce")
    unit_price = pd.to_numeric(work[fields["unit_price"]], errors="coerce")
    work["__transaction_quantity"] = quantity
    work["__transaction_unit_price"] = unit_price
    work["__transaction_amount"] = quantity * unit_price
    work["__transaction_order"] = work[fields["order"]]
    for role in ("customer", "product", "geography", "time", "status", "amount"):
        if role in fields:
            work[f"__transaction_{role}"] = work[fields[role]]

    filter_effects: list[dict[str, Any]] = []
    filtered = work
    filters = contract.get("filters", contract.get("filter_rules", ()))
    if not isinstance(filters, (list, tuple)):
        raise ValueError("交易 filters 必须是白名单谓词列表")
    for index, rule in enumerate(filters, start=1):
        if not isinstance(rule, dict):
            raise ValueError("交易 filters 每项必须是对象")
        before = filtered
        keep = _filter_mask(before, rule)
        filtered = before.loc[keep].copy()
        removed = before.loc[~keep]
        filter_effects.append({
            "rule_id": f"filter-{index}", "field": str(rule.get("field")),
            "predicate": str(rule.get("predicate") or rule.get("operator")).lower(),
            "input_rows": int(len(before)), "retained_rows": int(len(filtered)),
            "excluded_rows": int(len(removed)), "affected_amount": _amount(removed["__transaction_amount"]),
        })

    computable = filtered.loc[
        filtered["__transaction_quantity"].notna() & filtered["__transaction_unit_price"].notna()
        & ~_blank(filtered["__transaction_order"])
    ].copy()
    scopes: dict[str, dict[str, Any]] = {
        "sales": _scope_record("sales", filtered, computable, "有效订单标识且数量、单价可计算")
    }
    scopes["sales"]["limitations"] = ["取消、退货、负数量、零价和异常价默认保留并单独记录。"]
    for scope, role in _OPTIONAL_SCOPE_ROLES.items():
        field = fields.get(role)
        if not field:
            continue
        retained = computable.loc[~_blank(computable[field])].copy()
        scopes[scope] = _scope_record(scope, computable, retained, f"{field} 为有效非空值")
        if scope == "customer":
            scopes[scope]["limitations"] = ["缺失客户 ID 的交易仍保留在 sales，不被合并为匿名客户。"]

    status_values = _confirmed_values(contract.get("cancellation_rule"))
    return_values = _confirmed_values(contract.get("return_rule"))
    status_series = computable[fields["status"]].astype(str) if "status" in fields else pd.Series("", index=computable.index)
    cancellation = status_series.isin(status_values) if status_values else pd.Series(False, index=computable.index)
    returns = status_series.isin(return_values) if return_values else pd.Series(False, index=computable.index)
    abnormal_rule = contract.get("abnormal_price_rule")
    abnormal = pd.Series(False, index=computable.index)
    if isinstance(abnormal_rule, dict):
        if "max" in abnormal_rule:
            abnormal |= computable["__transaction_unit_price"].gt(float(abnormal_rule["max"]))
        if "min" in abnormal_rule:
            abnormal |= computable["__transaction_unit_price"].lt(float(abnormal_rule["min"]))
    negative = computable["__transaction_quantity"].lt(0)
    zero_price = computable["__transaction_unit_price"].eq(0)
    positive_sales = computable.loc[
        computable["__transaction_quantity"].gt(0)
        & computable["__transaction_unit_price"].gt(0)
        & ~cancellation
    ]
    normal_sales = positive_sales.loc[~returns].copy()

    metrics: dict[str, Any] = {
        "gross_sales": _amount(positive_sales["__transaction_amount"]),
        "net_sales": _amount(computable["__transaction_amount"]),
        "distinct_orders": int(computable["__transaction_order"].nunique()),
        "units": _amount(computable.loc[~cancellation, "__transaction_quantity"]),
    }
    metrics["average_order_value"] = round(
        metrics["net_sales"] / metrics["distinct_orders"], 6
    ) if metrics["distinct_orders"] else None
    if "product" in scopes:
        metrics["distinct_skus"] = int(scopes["product"] and computable.loc[~_blank(computable[fields["product"]]), fields["product"]].nunique())
    if "customer" in scopes:
        customer = computable.loc[~_blank(computable[fields["customer"]])]
        contribution = customer.groupby(fields["customer"])["__transaction_amount"].sum().sort_index()
        metrics["distinct_customers"] = int(contribution.index.nunique())
        metrics["customer_contribution"] = {str(key): round(float(value), 6) for key, value in contribution.items()}
        customer_scope_net_sales = _amount(customer["__transaction_amount"])
        metrics["customer_concentration_denominator"] = customer_scope_net_sales
        metrics["customer_concentration_top_1"] = round(
            float(contribution.max() / customer_scope_net_sales), 12
        ) if customer_scope_net_sales else None

    def decision(mask: pd.Series, rule: str) -> dict[str, Any]:
        rows = computable.loc[mask]
        return {"rule": rule, "count": int(len(rows)), "affected_amount": _amount(rows["__transaction_amount"])}

    legacy_decisions = {
        "negative_quantity": decision(negative, "quantity < 0"),
        "cancellation": decision(cancellation, "confirmed cancellation_rule" if status_values else "no confirmed cancellation rule"),
        "return": decision(returns, "confirmed return_rule" if return_values else "no confirmed return rule"),
        "zero_price": decision(zero_price, "unit_price = 0"),
        "abnormal_price": decision(abnormal, "confirmed abnormal_price_rule" if isinstance(abnormal_rule, dict) else "no confirmed abnormal price rule"),
        "scopes": scopes,
        "analysis_intent": {"mode": analysis_intent, "business_lenses_enabled": analysis_intent == "business_review"},
    }

    returns_scope = computable.loc[returns | negative].copy()
    cancellations_scope = computable.loc[cancellation].copy()
    scope_catalog = [
        _scope_catalog_record(
            "all_rows",
            definition="应用用户显式行过滤后的全部原始有效行；不静默排除质量问题",
            input_frame=work,
            included_frame=filtered,
            filters=[dict(rule) for rule in filters],
            quality_policy_ids=[],
        ),
        _scope_catalog_record(
            "computable_sales",
            definition="订单标识有效且数量、单价可计算的行；质量问题保留并另行披露",
            input_frame=filtered,
            included_frame=computable,
            filters=[{"rule": "订单标识非空且数量、单价可计算"}],
            quality_policy_ids=[
                "negative_quantity", "cancellation", "return", "zero_price", "abnormal_price"
            ],
        ),
        _scope_catalog_record(
            "normal_sales",
            definition="正数量、正单价且不属于已确认取消或退货状态的可计算销售行",
            input_frame=computable,
            included_frame=normal_sales,
            filters=[
                {"rule": "quantity > 0"},
                {"rule": "unit_price > 0"},
                {"rule": "not confirmed cancellation"},
                {"rule": "not confirmed return"},
            ],
            quality_policy_ids=["negative_quantity", "cancellation", "zero_price"],
        ),
        _scope_catalog_record(
            "returns",
            definition="负数量行或命中已确认退货状态的可计算行",
            input_frame=computable,
            included_frame=returns_scope,
            filters=[{"rule": "quantity < 0 or confirmed return_rule"}],
            quality_policy_ids=["negative_quantity", "return"],
        ),
    ]
    if status_values:
        scope_catalog.append(_scope_catalog_record(
            "cancellations",
            definition="命中已确认取消状态的可计算行",
            input_frame=computable,
            included_frame=cancellations_scope,
            filters=[{"rule": "confirmed cancellation_rule"}],
            quality_policy_ids=["cancellation"],
        ))

    def quality_record(
        issue_id: str,
        issue_type: str,
        mask: pd.Series,
        *,
        severity: str,
        affected_fields: list[str],
        decision_impact: str,
        options: list[str],
        selected_policy: str,
        scope_ids: list[str],
        status: str,
        disclosure: str,
    ) -> dict[str, Any]:
        rows = computable.loc[mask]
        record = {
            "issue_id": issue_id,
            "issue_type": issue_type,
            "severity": severity,
            "affected_rows": int(len(rows)),
            "affected_metric_value": _amount(rows["__transaction_amount"]),
            "affected_fields": [field for field in affected_fields if field],
            "decision_impact": decision_impact,
            "options": options,
            "selected_policy": selected_policy,
            "scope_ids": scope_ids,
            "status": status,
            "disclosure": disclosure,
        }
        if set(record) != _QUALITY_DECISION_FIELDS:
            raise AssertionError("quality decision contract construction drifted")
        return record

    cancellation_scope_ids = ["computable_sales"] + (["cancellations"] if status_values else [])
    quality_records = [
        quality_record(
            "negative_quantity", "negative_quantity", negative,
            severity="auto_disclose",
            affected_fields=[fields["quantity"], fields["unit_price"]],
            decision_impact="影响净销售与件数，并定义退货范围",
            options=["保留在净额并隔离披露", "经确认后排除"],
            selected_policy="retain_in_net_and_isolate_returns",
            scope_ids=["computable_sales", "returns"], status="applied",
            disclosure="负数量保留在净额口径，同时在 returns 范围单独披露。",
        ),
        quality_record(
            "cancellation", "cancellation", cancellation,
            severity="auto_disclose" if status_values else "continue_limited",
            affected_fields=[fields.get("status", "")],
            decision_impact="决定正常销售是否排除取消交易",
            options=["按已确认状态隔离", "未确认时不推断"],
            selected_policy="isolate_confirmed_cancellations" if status_values else "do_not_infer_cancellations",
            scope_ids=cancellation_scope_ids,
            status="applied" if status_values else "limited",
            disclosure=("已按确认规则隔离取消交易。" if status_values else "未提供取消规则，不推断取消交易。"),
        ),
        quality_record(
            "return", "return", returns,
            severity="auto_disclose" if return_values else "continue_limited",
            affected_fields=[fields.get("status", ""), fields["quantity"]],
            decision_impact="影响退货范围解释，不直接改写净额计算",
            options=["按已确认状态与负数量隔离", "仅使用负数量信号"],
            selected_policy="confirmed_status_plus_negative_quantity" if return_values else "negative_quantity_only",
            scope_ids=["computable_sales", "returns"],
            status="applied" if return_values else "limited",
            disclosure=("退货范围包含已确认退货状态与负数量行。" if return_values else "未提供退货状态规则，退货范围仅使用负数量信号。"),
        ),
        quality_record(
            "zero_price", "zero_price", zero_price,
            severity="auto_disclose",
            affected_fields=[fields["unit_price"]],
            decision_impact="零价行保留在净额，但不进入正常销售范围",
            options=["保留并披露", "经确认后排除"],
            selected_policy="retain_and_disclose",
            scope_ids=["computable_sales", "normal_sales"], status="applied",
            disclosure="零价行保留在可计算净额，并从 normal_sales 隔离。",
        ),
        quality_record(
            "abnormal_price", "abnormal_price", abnormal,
            severity="auto_disclose" if isinstance(abnormal_rule, dict) else "continue_limited",
            affected_fields=[fields["unit_price"]],
            decision_impact="限制异常价格诊断，不静默改变销售口径",
            options=["按已确认阈值披露", "无阈值时不推断异常"],
            selected_policy="disclose_confirmed_threshold" if isinstance(abnormal_rule, dict) else "do_not_infer_outliers",
            scope_ids=["computable_sales"],
            status="applied" if isinstance(abnormal_rule, dict) else "limited",
            disclosure=("按已确认阈值标记异常价格，销售口径保持不变。" if isinstance(abnormal_rule, dict) else "未提供异常价格阈值，不自动剔除或标记离群价格。"),
        ),
    ]
    quality_decisions = QualityDecisionList(quality_records, legacy_decisions)
    lenses = ["reconciliation", "quality_qa"] if analysis_intent == "engineering_regression" else list(scopes)
    return {
        "status": "ready", "prepared_frame": filtered, "standard_metric_contract": {
            "gross_sales": {"aggregation": "sum_product", "factors": [fields["quantity"], fields["unit_price"]]},
            "net_sales": {"aggregation": "sum_product", "factors": [fields["quantity"], fields["unit_price"]]},
        },
        "analysis_contract": {"table_grain": contract.get("table_grain"), "field_mappings": fields, "analysis_intent": analysis_intent},
        "metrics": metrics, "scopes": scopes, "scope_catalog": scope_catalog,
        "analysis_lenses": lenses, "quality_decisions": quality_decisions,
        "quality_summary": legacy_decisions, "filter_effects": filter_effects,
    }
