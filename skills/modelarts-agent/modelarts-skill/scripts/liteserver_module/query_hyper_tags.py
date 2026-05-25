#!/usr/bin/env python3
"""
Lite Server 模块 - query_hyper_tags 函数
功能：查询超节点标签
"""

from ._bootstrap import authenticated_api_call, Dict, Any
from .common import execute_hyperinstance_operation

@authenticated_api_call
def ma_liteserver_query_hyper_tags(
    access,
    hyperinstance_id: str
) -> Dict[str, Any]:
    """
    Query tags for a Lite Server hyperinstance.
    Args:
        hyperinstance_id: The hyperinstance ID (required)
    Returns:
        Tag list
    """
    return execute_hyperinstance_operation(
        access,
        hyperinstance_id,
        'GET',
        '/v1/{project_id}/dev-servers/hyperinstance/{hyperinstance_id}/tags',
        "22.14 QueryHyperinstanceTags (Page 1648)"
    )

__all__ = ['ma_liteserver_query_hyper_tags']
