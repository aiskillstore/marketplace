#!/usr/bin/env python3
"""
Lite Server 模块 - delete_hyperinstance 函数
功能：删除超节点实例
"""

from ._bootstrap import authenticated_api_call, Dict, Any
from .common import execute_hyperinstance_operation

@authenticated_api_call
def ma_liteserver_delete_hyperinstance(
    access,
    hyperinstance_id: str
) -> Dict[str, Any]:
    """
    Delete a Lite Server hyperinstance.
    Args:
        hyperinstance_id: The hyperinstance ID (required)
    Returns:
        Deletion status
    """
    return execute_hyperinstance_operation(
        access,
        hyperinstance_id,
        'DELETE',
        '/v1/{project_id}/dev-servers/hyperinstance/{hyperinstance_id}',
        "22.21 DeleteHyperinstance (Page 1720)",
        action="delete"
    )

__all__ = ['ma_liteserver_delete_hyperinstance']
