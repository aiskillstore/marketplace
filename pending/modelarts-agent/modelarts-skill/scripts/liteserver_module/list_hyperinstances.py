#!/usr/bin/env python3
"""
Lite Server 模块 - list_hyperinstances 函数
功能：查询超节点实例列表
"""

from ._bootstrap import authenticated_api_call, Dict, Any, Optional
from .common import add_api_reference, format_hyperinstance_list_result

@authenticated_api_call
def ma_liteserver_list_hyperinstances(
    access,
    cluster_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Query list of hyperinstances.
    Args:
        cluster_id: Filter by Hyper Cluster ID (optional)
        status: Filter by status (optional)
        limit: Maximum results (default: 100)
        offset: Offset for pagination (default: 0)
    Returns:
        List of hyperinstances
    """
    query = {}
    if cluster_id:
        query['cluster_id'] = cluster_id
    if status:
        query['status'] = status
    if limit:
        query['limit'] = str(limit)
    if offset:
        query['offset'] = str(offset)

    result = simple_api_call(
        access,
        'GET',
        '/v1/{project_id}/dev-servers/hyperinstance',
        query=query if query else None
    )

    api_result = format_hyperinstance_list_result(result)
    return add_api_reference(api_result, "22.19 ListHyperinstances (Page 1695)")

from common_module.api_helper import make_api_call
__all__ = ['ma_liteserver_list_hyperinstances']
