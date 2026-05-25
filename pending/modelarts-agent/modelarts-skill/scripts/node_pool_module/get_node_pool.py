#!/usr/bin/env python3
"""
NodePool模块 - get_node_pool函数
功能：获取单个节点池的详细信息
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any


@authenticated_api_call
def get_node_pool(access, pool_name: str, node_pool_name: str) -> Dict[str, Any]:
    """
    获取节点池详细信息

    Args:
        pool_name: 资源池 ID（必填）格式: pool-xxx-xxx-xxx-xxx
        node_pool_name: 节点池名称（必填）通常是 nodepool-xxx-xxx-xxx

    调用经验:
        - 返回节点池的完整配置，包括规格、数量、状态等
        - status.readyNodeNum 表示就绪节点数量
        - spec.nodeNum 是期望节点数量
        - status.conditions 包含节点池的健康状态

    Returns:
        节点池详细信息
    """
    if not pool_name:
        return format_api_result(False, error="pool_name is required")
    if not node_pool_name:
        return format_api_result(False, error="node_pool_name is required")

    result = access_api_call(
        access,
        "GET",
        "/v2/{project_id}/pools/{p_id}/nodepools/{node_pool_name}",
        p_id=pool_name,
        node_pool_name=node_pool_name
    )

    return format_api_result(True, data=result)


__all__ = ["get_node_pool"]