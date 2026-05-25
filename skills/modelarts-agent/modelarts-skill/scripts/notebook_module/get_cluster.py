#!/usr/bin/env python3
"""
Notebook模块 - get_cluster函数
功能：获取集群详情
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def get_cluster(cluster_id: str) -> Dict[str, Any]:
    """
    获取单个资源集群的详细信息。

    API 路径: GET /v1/{project_id}/authoring/clusters/{cluster_id}

    Args:
        cluster_id: 集群 ID (必填)

    Returns:
        集群详情

    示例:
        >>> from notebook_module import get_cluster
        >>> result = get_cluster('cluster-id-xxx')
        >>> if result['success']:
        ...     print('集群名称:', result['data']['name'])
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        if not cluster_id:
            return format_api_result(False, error="cluster_id is required")

        print(f"  获取集群详情: {cluster_id}")

        result = simple_api_call(
            access,
            'GET',
            '/v1/{project_id}/authoring/clusters/{cluster_id}',
            cluster_id=cluster_id
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"获取集群详情时发生异常: {e}")


__all__ = ['get_cluster']