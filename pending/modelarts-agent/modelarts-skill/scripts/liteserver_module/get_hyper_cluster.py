#!/usr/bin/env python3
"""
Lite Server 模块 - get_hyper_cluster 函数
功能：查询指定超节点集群详情
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any
from .common import validate_required_params, add_api_reference

@authenticated_api_call
def ma_liteserver_get_hyper_cluster(
    access,
    cluster_id: str
) -> Dict[str, Any]:
    """
    Get details of a Hyper Cluster instance.
    Args:
        cluster_id: The cluster ID (required)
    Returns:
        Cluster details
    """
    valid, error = validate_required_params({"cluster_id": cluster_id}, ["cluster_id"])
    if not valid:
        return format_api_result(False, error=error)
    result = simple_api_call(
        access,
        'GET',
        '/v1/{project_id}/dev-servers/hyper-clusters/{cluster_id}',
        cluster_id=cluster_id
    )
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.10 GetHyperCluster (Page 1631)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_get_hyper_cluster']
