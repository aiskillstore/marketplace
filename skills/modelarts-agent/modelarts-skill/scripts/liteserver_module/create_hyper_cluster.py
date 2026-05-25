#!/usr/bin/env python3
"""
Lite Server 模块 - create_hyper_cluster 函数
功能：创建 Hyper Cluster
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, Optional
from .common import validate_required_params, build_request_body, add_api_reference

@authenticated_api_call
def ma_liteserver_create_hyper_cluster(
    access,
    name: str,
    hyper_cluster_subnet_id: Optional[str] = None,
    type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a Hyper Cluster.
    Args:
        name: hyper cluster的名称 (required) - ^[-_.a-zA-Z0-9]{1,64}$
        hyper_cluster_subnet_id: hyper cluster的ID (optional) - ^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$
        type: 服务器类型 (optional) - HPS: 超节点服务，ECS: 弹性云服务
    Returns:
        Created cluster details including id, name, network_info
    """
    valid, error = validate_required_params({"name": name}, ["name"])
    if not valid:
        return format_api_result(False, error=error)
    body = build_request_body(
        {"name": name},
        {"hyper_cluster_subnet_id": hyper_cluster_subnet_id, "type": type}
    )
    result = access.sdk().execute(lambda s: make_api_call(
        s,
        'POST',
        '/v1/{project_id}/dev-servers/hyper-clusters',
        body=body
    ))
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.8 CreateHyperCluster (Page 1625)")

from common_module.api_helper import make_api_call
__all__ = ['ma_liteserver_create_hyper_cluster']