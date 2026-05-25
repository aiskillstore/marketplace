#!/usr/bin/env python3
"""
Lite Server 模块 - start_hyperinstance 函数
功能：启动超节点实例
"""

from ._bootstrap import authenticated_api_call, Dict, Any
from .common import execute_hyperinstance_operation

@authenticated_api_call
def ma_liteserver_start_hyperinstance(
    access,
    hyperinstance_id: str
) -> Dict[str, Any]:
    """
    Start a Lite Server hyperinstance server.
    Args:
        hyperinstance_id: The hyperinstance ID (required)
    Returns:
        Start status
    """
    return execute_hyperinstance_operation(
        access,
        hyperinstance_id,
        'PUT',
        '/v1/{project_id}/dev-servers/hyperinstance/{hyperinstance_id}/start',
        "22.23 StartHyperinstance (Page 1742)",
        action="start"
    )

__all__ = ['ma_liteserver_start_hyperinstance']
