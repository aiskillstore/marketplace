#!/usr/bin/env python3
"""
Lite Server 模块 - scale_down_hyperinstance 函数
功能：缩容超节点实例
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any
from .common import validate_required_params, build_request_body, add_api_reference

@authenticated_api_call
def ma_liteserver_scale_down_hyperinstance(
    access,
    hyperinstance_id: str,
    target_size: int,
    scale_type: str = None
) -> Dict[str, Any]:
    """
    Scale down a Lite Server hyperinstance.
    Args:
        hyperinstance_id: The hyperinstance ID (required)
        target_size: Target instance count (required)
        scale_type: Scale type (optional)
    Returns:
        Scale down status
    """
    valid, error = validate_required_params(
        {"hyperinstance_id": hyperinstance_id, "target_size": target_size},
        ["hyperinstance_id", "target_size"]
    )
    if not valid:
        return format_api_result(False, error=error)

    optional = {}
    if scale_type:
        optional['scale_type'] = scale_type

    body = build_request_body({"target_size": target_size}, optional)
    result = simple_api_call(
        access,
        'POST',
        '/v1/{project_id}/dev-servers/hyperinstance/{hyperinstance_id}/scale-down',
        body=body,
        hyperinstance_id=hyperinstance_id
    )
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.30 ScaleDownHyperinstance (Page 1778)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_scale_down_hyperinstance']
