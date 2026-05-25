#!/usr/bin/env python3
"""
Notebook模块 - list_clusters函数
功能：获取集群列表
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def list_clusters(type: str = "MANAGED", workspace_id: str = "0",
                  limit: int = 1000, offset: int = 0, scope: str = "NOTEBOOK") -> Dict[str, Any]:
    """
    查询开发环境可用的资源集群列表。

    API 路径: GET /v1/{project_id}/authoring/clusters

    Args:
        type: 资源池类型 (必填)
            - "MANAGED": 公共池
            - "DEDICATED": 专属池
        workspace_id: 工作空间 ID (可选，默认 "0")
        limit: 每页数量 (可选，默认 1000)
        offset: 分页偏移量 (可选，默认 0)
        scope: 作业类型 (可选，默认 "NOTEBOOK")
            - "NOTEBOOK": 开发环境
            - "TRAIN": 训练作业
            - "INFER": 推理作业

    Returns:
        资源集群列表

    示例:
        >>> from notebook_module import list_clusters
        >>> # 查询公共池集群
        >>> result = list_clusters(type="MANAGED")
        >>> if result['success']:
        ...     for cluster in result['data']['data']:
        ...         print(cluster['name'], cluster['id'])
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        query = {"type": type, "workspace_id": workspace_id,
                 "limit": limit, "offset": offset, "scope": scope}

        print(f"  获取集群列表")

        result = simple_api_call(
            access,
            'GET',
            '/v1/{project_id}/authoring/clusters',
            query=query
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"获取集群列表时发生异常: {e}")


__all__ = ['list_clusters']