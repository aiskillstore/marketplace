#!/usr/bin/env python3
"""
Lite Server 模块 - list_hyper_clusters 函数
功能：查询超节点集群列表
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, Optional
from .common import add_api_reference

@authenticated_api_call
def ma_liteserver_list_hyper_clusters(
    access,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Query list of Hyper Cluster details.
    Args:
        limit: Maximum results (default: 100)
        offset: Offset for pagination (default: 0)
    Returns:
        List of Hyper Clusters with pagination
    """
    query = {}
    if limit:
        query['limit'] = str(limit)
    if offset:
        query['offset'] = str(offset)

    result = simple_api_call(
        access,
        'GET',
        '/v1/{project_id}/dev-servers/hyper-clusters',
        query=query if query else None
    )
    # 标准化响应结构
    if isinstance(result, dict):
        data = {
            'clusters': result.get('hyper_clusters', []),
            'total': len(result.get('hyper_clusters', [])),
            'current': 0,
            'size': len(result.get('hyper_clusters', []))
        }
        api_result = format_api_result(True, data=data)
    else:
        api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.9 ListHyperCluster (Page 1628)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_list_hyper_clusters']
