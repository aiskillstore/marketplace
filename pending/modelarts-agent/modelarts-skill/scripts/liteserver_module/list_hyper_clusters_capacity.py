#!/usr/bin/env python3
"""
Lite Server 模块 - list_hyper_clusters_capacity 函数
功能：查询超节点集群容量信息
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, Optional
from .common import add_api_reference

@authenticated_api_call
def ma_liteserver_list_hyper_clusters_capacity(
    access,
    hyper_cluster_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get capacity information for Hyper Clusters.
    Args:
        hyper_cluster_id: Hyper Cluster ID (required) - 查询指定超节点集群的容量信息，
                          不传时返回所有集群容量
    Returns:
        Hyper Cluster capacity information
    """
    query = {}
    if hyper_cluster_id:
        query['id'] = hyper_cluster_id
    result = simple_api_call(
        access,
        'GET',
        '/v1/{project_id}/dev-servers/hyper-clusters/capacity',
        query=query if query else None
    )
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.40 ListHyperinstanceClustersCapacity (Page 1840)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_list_hyper_clusters_capacity']
