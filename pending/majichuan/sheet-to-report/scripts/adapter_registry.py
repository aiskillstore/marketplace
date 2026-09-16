from __future__ import annotations

from copy import deepcopy
from typing import Any


ADAPTER_MATURITIES = {"verified", "experimental", "unavailable"}


_ADAPTER_REGISTRY: dict[str, dict[str, Any]] = {
    "general": {
        "adapter_id": "general",
        "maturity": "verified",
        "execution_profile": "general",
        "supported_objects": ("time_series", "business_table"),
        "required_semantic_roles": (),
        "question_templates": ("识别经营变化并提出下一步建议",),
        "limitations": ("不推断未确认的业务领域口径。",),
    },
    "retail_growth": {
        "adapter_id": "retail_growth",
        "maturity": "verified",
        "execution_profile": "retail_growth",
        "supported_objects": ("retail_growth_table",),
        "required_semantic_roles": ("outcome", "quality", "efficiency"),
        "question_templates": ("识别渠道和品类的增长驱动",),
        "limitations": ("需要已确认的渠道、品类和指标语义。",),
    },
    "transactional_commerce": {
        "adapter_id": "transactional_commerce",
        "maturity": "verified",
        "execution_profile": "transactional_commerce",
        "supported_objects": ("order", "order_line"),
        "required_semantic_roles": ("order", "quantity", "unit_price"),
        "question_templates": ("分析订单、商品和客户的经营变化",),
        "limitations": ("需要确认 order 或 order_line 表粒度。",),
    },
    "content_operations": {
        "adapter_id": "content_operations",
        "maturity": "experimental",
        "execution_profile": "general",
        "supported_objects": ("content_delivery_table",),
        "required_semantic_roles": ("volume", "quality"),
        "question_templates": ("分析内容生产与交付表现",),
        "limitations": ("实验适配器须经确认后运行，并使用 general 执行 profile。",),
    },
    "project_operations": {
        "adapter_id": "project_operations",
        "maturity": "experimental",
        "execution_profile": "general",
        "supported_objects": ("project_delivery_table",),
        "required_semantic_roles": ("volume", "quality"),
        "question_templates": ("分析项目交付与运营表现",),
        "limitations": ("实验适配器须经确认后运行，并使用 general 执行 profile。",),
    },
}


def get_adapter_registry() -> dict[str, dict[str, Any]]:
    """Return a caller-safe snapshot of the registered analysis adapters."""
    return deepcopy(_ADAPTER_REGISTRY)


def resolve_adapter(
    adapter_id: str,
    auto_select: bool = False,
    allow_experimental: bool = False,
) -> dict[str, Any]:
    """Resolve an adapter while enforcing its declared maturity boundary."""
    adapter = _ADAPTER_REGISTRY.get(str(adapter_id))
    if adapter is None or adapter["maturity"] == "unavailable":
        raise ValueError(f"adapter '{adapter_id}' is unavailable")
    if adapter["maturity"] == "experimental":
        if auto_select:
            raise ValueError(f"adapter '{adapter_id}' is experimental and cannot auto-select")
        if not allow_experimental:
            raise ValueError(f"adapter '{adapter_id}' is experimental and requires explicit confirmation")
    return deepcopy(adapter)
