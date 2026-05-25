#!/usr/bin/env python3
"""
Lite Server 模块 - stop_hyperinstance 函数
功能：停止超节点实例
"""

from ._bootstrap import authenticated_api_call, Dict, Any
from .common import execute_hyperinstance_operation

@authenticated_api_call
def ma_liteserver_stop_hyperinstance(
    access,
    hyperinstance_id: str
) -> Dict[str, Any]:
    """
    Stop a Lite Server hyperinstance server.
    Args:
        hyperinstance_id: The hyperinstance ID (required)
    Returns:
        Stop status
    """
    return execute_hyperinstance_operation(
        access,
        hyperinstance_id,
        'PUT',
        '/v1/{project_id}/dev-servers/hyperinstance/{hyperinstance_id}/stop',
        "22.24 StopHyperinstance (Page 1753)",
        action="stop"
    )

__all__ = ['ma_liteserver_stop_hyperinstance']
