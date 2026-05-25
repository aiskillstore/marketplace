#!/usr/bin/env python3
"""
Lite Server 模块 - get_hyperinstance 函数
功能：查询指定超节点实例详情
"""

from ._bootstrap import authenticated_api_call, Dict, Any
from .common import execute_hyperinstance_operation

@authenticated_api_call
def ma_liteserver_get_hyperinstance(
    access,
    hyperinstance_id: str
) -> Dict[str, Any]:
    """
    Get details of a specific hyperinstance.
    Args:
        hyperinstance_id: The hyperinstance ID (required)
    Returns:
        Hyperinstance details
    """
    return execute_hyperinstance_operation(
        access,
        hyperinstance_id,
        'GET',
        '/v1/{project_id}/dev-servers/hyperinstance/{hyperinstance_id}',
        "22.20 GetHyperinstance (Page 1708)"
    )

__all__ = ['ma_liteserver_get_hyperinstance']
