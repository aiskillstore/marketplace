from __future__ import annotations

from typing import Any, Iterable

from adapter_registry import get_adapter_registry, resolve_adapter
from semantic_contract import resolve_semantic_contract


SUPPORTED_PROFILES = {"auto", *get_adapter_registry()}
SUPPORTED_ROLES = {
    "outcome",
    "volume",
    "conversion",
    "quality",
    "cost",
    "efficiency",
    "unknown",
}
SUPPORTED_DIRECTIONS = {"higher_is_better", "lower_is_better", "neutral"}


def _normalized(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "").replace("_", "")


def infer_metric_semantics(name: str) -> tuple[str, str, str]:
    value = _normalized(name)
    rules: tuple[tuple[tuple[str, ...], str, str], ...] = (
        (("退款率", "退货率", "refundrate", "returnrate"), "quality", "lower_is_better"),
        (("投诉率", "差评率", "流失率", "超时率", "逾期率", "缺陷率", "错误率", "churnrate"), "quality", "lower_is_better"),
        (("满意度", "好评率", "复购率", "准时交付率", "按时交付率", "完成率", "达成率", "retentionrate"), "quality", "higher_is_better"),
        (("转化率", "conversionrate", "cvr"), "conversion", "higher_is_better"),
        (("roas", "投入产出比", "roi"), "efficiency", "higher_is_better"),
        (("平均处理时长", "响应时长", "交付时长", "handlingtime"), "efficiency", "lower_is_better"),
        (("营销成本", "获客成本", "成本", "spend", "cost"), "cost", "lower_is_better"),
        (("收入", "销售额", "成交额", "gmv", "revenue", "sales"), "outcome", "higher_is_better"),
        (("订单数", "订单量", "工单量", "访问量", "用户数", "发布内容数", "内容数", "阅读量", "播放量", "线索数", "交付数", "解决量", "orders", "visits"), "volume", "higher_is_better"),
    )
    for aliases, role, direction in rules:
        if value in aliases or any(alias and alias in value for alias in aliases):
            return role, direction, "inferred_high"
    return "unknown", "neutral", "inferred_low"


def enrich_metric_contract(
    contract: dict[str, Any], source_columns: Iterable[str] | None = None
) -> dict[str, Any]:
    enriched = dict(contract)
    name = str(enriched["name"])
    inferred_role, inferred_direction, inferred_confidence = infer_metric_semantics(name)
    role = str(enriched.get("role") or inferred_role)
    direction = str(enriched.get("direction") or inferred_direction)
    if role not in SUPPORTED_ROLES:
        raise ValueError(f"未知指标 role：{role}")
    if direction not in SUPPORTED_DIRECTIONS:
        raise ValueError(f"未知指标 direction：{direction}")

    numerator = enriched.get("numerator")
    denominator = enriched.get("denominator")
    is_derived = bool(numerator and denominator) or bool(enriched.get("derived"))
    if source_columns is not None and name not in set(str(value) for value in source_columns):
        is_derived = True

    display_name = str(enriched.get("display_name") or name)
    if _normalized(name) == "roas":
        display_name = str(enriched.get("display_name") or "投入产出比（ROAS）")

    if enriched.get("formula_display"):
        formula_display = str(enriched["formula_display"])
    elif numerator and denominator:
        formula_display = f"{numerator} ÷ {denominator}"
    elif enriched.get("aggregation") == "average":
        formula_display = f"{name}平均值"
    elif enriched.get("aggregation") == "last":
        formula_display = f"{name}期末值"
    elif enriched.get("aggregation") == "distinct_count":
        formula_display = f"{enriched.get('source_field')}去重计数"
    elif enriched.get("aggregation") == "median":
        formula_display = f"{enriched.get('source_field')}中位数"
    elif enriched.get("aggregation") == "sum_product":
        left, right = enriched["factors"]
        formula_display = f"{left} × {right}逐行乘积合计"
    elif enriched.get("aggregation") == "sum":
        formula_display = f"{name}合计"
    else:
        formula_display = name

    if enriched.get("definition"):
        definition = str(enriched["definition"])
    elif _normalized(name) == "roas" and numerator and denominator:
        definition = f"每投入 1 元{denominator}带来的{numerator}。"
    elif enriched.get("aggregation") == "ratio" and numerator and denominator:
        definition = f"{numerator}占{denominator}的比例。"
    elif enriched.get("aggregation") == "average":
        definition = f"{name}在当前统计周期内的算术平均值。"
    elif enriched.get("aggregation") == "last":
        definition = f"{name}取当前统计周期末的最后有效值。"
    elif enriched.get("aggregation") == "distinct_count":
        definition = f"{name}在当前统计周期内按{enriched.get('source_field')}去重计数。"
    elif enriched.get("aggregation") == "median":
        definition = f"{name}在当前统计周期内的中位数。"
    elif enriched.get("aggregation") == "sum_product":
        left, right = enriched["factors"]
        definition = f"{name}在当前统计周期内按每行{left} × {right}相乘后合计。"
    else:
        definition = f"{name}在当前统计周期内的合计值。"

    enriched.update(
        {
            "display_name": display_name,
            "role": role,
            "direction": direction,
            "semantics_confidence": (
                "confirmed"
                if contract.get("role") or contract.get("direction")
                else inferred_confidence
            ),
            "source_kind": "derived" if is_derived else "raw",
            "formula_display": formula_display,
            "definition": definition,
        }
    )
    return enriched


def _dimension_roles(dimensions: Iterable[str]) -> set[str]:
    roles: set[str] = set()
    for dimension in dimensions:
        value = _normalized(dimension)
        if value in {"渠道", "channel", "来源渠道", "流量渠道"}:
            roles.add("channel")
        if value in {"品类", "类目", "category", "productcategory"}:
            roles.add("category")
    return roles


def _profile_with_adapter(
    *,
    requested: str,
    adapter: dict[str, Any],
    reasons: list[str],
    metric_roles: Iterable[str],
    dimension_roles: Iterable[str],
    semantic_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    profile = {
        "requested": requested,
        "resolved": adapter["execution_profile"],
        "adapter_id": adapter["adapter_id"],
        "adapter_maturity": adapter["maturity"],
        "adapter_selection_reason": reasons[0],
        "reasons": reasons,
        "metric_roles": sorted(metric_roles),
        "dimension_roles": sorted(dimension_roles),
    }
    if semantic_contract is not None:
        profile["semantic_contract"] = semantic_contract
    return profile


def _assert_contract_adapter_matches(
    semantic_contract: dict[str, Any], actual_adapter_id: str
) -> None:
    if (
        semantic_contract.get("adapter_selection_reason")
        in {"explicit_verified", "confirmed_experimental"}
        and semantic_contract.get("adapter_id") != actual_adapter_id
    ):
        raise ValueError(
            "semantic_contract 适配器与最终 analysis_profile 不一致："
            f"{semantic_contract.get('adapter_id')} != {actual_adapter_id}"
        )


def resolve_analysis_profile(
    request: Any, contracts: list[dict[str, Any]]
) -> dict[str, Any]:
    requested = str(getattr(request, "analysis_profile", "auto") or "auto")
    if requested not in SUPPORTED_PROFILES:
        resolve_adapter(requested)
        raise ValueError(f"未知 analysis_profile：{requested}")

    raw_semantic_contract = getattr(request, "semantic_contract", None)
    transactional_requested = requested == "transactional_commerce"
    raw_semantic_domain = str(
        (raw_semantic_contract or {}).get("domain")
        or (raw_semantic_contract or {}).get("profile")
        or ""
    ) if isinstance(raw_semantic_contract, dict) else ""
    if transactional_requested and (
        raw_semantic_contract is None or raw_semantic_domain != "transactional_commerce"
    ):
        raise ValueError(
            "transactional_commerce 语义合同需要确认：请提供已声明为 transactional_commerce 的完整合同。"
        )
    semantic = resolve_semantic_contract(
        raw_semantic_contract,
        mode=str(getattr(request, "mode", "professional")),
    )
    normalized_semantic_contract = semantic.get("contract") or {}
    if normalized_semantic_contract.get("adapter_maturity") == "unavailable":
        resolve_adapter(str(normalized_semantic_contract.get("adapter_id") or ""))
    semantic_domain = str(
        normalized_semantic_contract.get("domain")
        or normalized_semantic_contract.get("profile")
        or ""
    )
    transactional_detected = bool(
        semantic.get("contract") and semantic_domain == "transactional_commerce"
    )
    experimental_domains = {"content_operations", "project_operations"}
    if (
        requested == "auto"
        and semantic_domain in experimental_domains
        and normalized_semantic_contract.get("adapter_id") == semantic_domain
    ):
        resolve_adapter(semantic_domain, auto_select=True)
    if requested in experimental_domains:
        if str(getattr(request, "mode", "professional")) == "quick":
            raise ValueError(
                f"Quick 仅可使用 verified 适配器；'{requested}' 当前为 experimental。"
            )
        if (
            semantic_domain != requested
            or normalized_semantic_contract.get("adapter_id") != requested
            or normalized_semantic_contract.get("adapter_maturity") != "experimental"
            or str(normalized_semantic_contract.get("confirmation_status") or "")
            != "confirmed"
        ):
            raise ValueError(
                f"{requested} experimental 适配器需要确认分析计划后才能启用。"
            )
        if semantic["status"] != "ready":
            raise ValueError(f"{requested} 语义合同需要确认：" + "；".join(semantic["questions"]))
        adapter = resolve_adapter(requested, allow_experimental=True)
        selected_semantic_contract = dict(semantic["contract"] or {})
        selected_semantic_contract.update(
            {
                "adapter_id": adapter["adapter_id"],
                "adapter_maturity": adapter["maturity"],
                "adapter_selection_reason": "confirmed_experimental",
                "execution_profile": adapter["execution_profile"],
            }
        )
        _assert_contract_adapter_matches(selected_semantic_contract, adapter["adapter_id"])
        return _profile_with_adapter(
            requested=requested,
            adapter=adapter,
            reasons=["已确认实验适配器分析计划，使用通用确定性执行"],
            metric_roles=(str(contract.get("role", "unknown")) for contract in contracts),
            dimension_roles=_dimension_roles(getattr(request, "dimensions", ())),
            semantic_contract=selected_semantic_contract,
        )
    if transactional_requested or (requested == "auto" and transactional_detected):
        if semantic["status"] != "ready":
            raise ValueError("transactional_commerce 语义合同需要确认：" + "；".join(semantic["questions"]))
        adapter = resolve_adapter(
            "transactional_commerce", auto_select=requested == "auto"
        )
        _assert_contract_adapter_matches(semantic["contract"] or {}, adapter["adapter_id"])
        return _profile_with_adapter(
            requested=requested,
            adapter=adapter,
            reasons=["已确认交易表粒度与订单、商品、客户、金额等字段映射"],
            metric_roles=(str(contract.get("role", "unknown")) for contract in contracts),
            dimension_roles=_dimension_roles(getattr(request, "dimensions", ())),
            semantic_contract=semantic["contract"],
        )

    roles = {str(contract.get("role", "unknown")) for contract in contracts}
    dimensions = _dimension_roles(getattr(request, "dimensions", ()))
    required_roles = {"outcome", "quality", "efficiency"}
    required_dimensions = {"channel", "category"}
    missing_roles = sorted(required_roles - roles)
    missing_dimensions = sorted(required_dimensions - dimensions)
    retail_ready = not missing_roles and not missing_dimensions

    if requested == "retail_growth" and not retail_ready:
        missing = [
            *(f"指标角色:{value}" for value in missing_roles),
            *(f"分析维度:{value}" for value in missing_dimensions),
        ]
        raise ValueError(f"retail_growth 配置缺少必要语义：{', '.join(missing)}")

    adapter_id = "retail_growth" if requested == "retail_growth" or (requested == "auto" and retail_ready) else "general"
    adapter = resolve_adapter(adapter_id, auto_select=requested == "auto")
    _assert_contract_adapter_matches(normalized_semantic_contract, adapter["adapter_id"])
    reasons = (
        ["已识别渠道、品类及结果/质量/效率指标语义"]
        if adapter_id == "retail_growth"
        else ["未满足零售增强的完整语义条件，使用通用确定性分析"]
    )
    return _profile_with_adapter(
        requested=requested,
        adapter=adapter,
        reasons=reasons,
        metric_roles=roles,
        dimension_roles=dimensions,
    )
