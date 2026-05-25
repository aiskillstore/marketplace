#!/usr/bin/env python3
"""
Lite Server 模块 - change_hyper_os 函数
功能：切换超节点操作系统镜像
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any
from .common import validate_required_params, add_api_reference

@authenticated_api_call
def ma_liteserver_change_hyper_os(
    access,
    hyperinstance_id: str,
    image_id: str
) -> Dict[str, Any]:
    """
    Switch OS image for a Lite Server hyperinstance.
    Args:
        hyperinstance_id: The hyperinstance ID (required)
        image_id: New image ID (required)
    Returns:
        OS change status
    """
    valid, error = validate_required_params(
        {"hyperinstance_id": hyperinstance_id, "image_id": image_id},
        ["hyperinstance_id", "image_id"]
    )
    if not valid:
        return format_api_result(False, error=error)

    body = {"image_id": image_id}

    result = simple_api_call(
        access,
        'POST',
        '/v1/{project_id}/dev-servers/hyperinstance/{hyperinstance_id}/changeos',
        body=body,
        hyperinstance_id=hyperinstance_id
    )

    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.18 ChangeHyperinstanceOS (Page 1682)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_change_hyper_os']
