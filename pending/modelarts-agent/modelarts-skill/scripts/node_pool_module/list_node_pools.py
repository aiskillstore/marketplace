#!/usr/bin/env python3
"""
NodePool模块 - list_node_pools函数
功能：列出资源池下的所有节点池
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def list_node_pools(access, pool_name: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    """
    列出资源池下的所有节点池

    Args:
        pool_name: 资源池 ID（必填）格式: pool-xxx-xxx-xxx-xxx
        limit: 分页大小，默认 100
        offset: 分页偏移量，默认 0

    调用经验:
        - 节点池是资源池下的节点分组
        - 每个资源池至少有一个默认节点池
        - 返回的 items 中包含所有节点池的完整配置

    Returns:
        节点池列表
    """
    if not pool_name:
        return format_api_result(False, error="pool_name is required")

    params = {}
    if limit:
        params["limit"] = limit
    if offset:
        params["offset"] = offset

    result = access_api_call(
        access,
        "GET",
        "/v2/{project_id}/pools/{p_id}/nodepools",
        p_id=pool_name, params=params
    )

    return format_api_result(True, data=result)


__all__ = ["list_node_pools"]