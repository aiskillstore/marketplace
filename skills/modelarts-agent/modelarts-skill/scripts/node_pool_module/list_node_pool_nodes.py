#!/usr/bin/env python3
"""
NodePool模块 - list_node_pool_nodes函数
功能：列出指定节点池下的所有节点
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def list_node_pool_nodes(
    access,
    pool_name: str,
    node_pool_name: str,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    列出指定节点池下的所有节点

    Args:
        pool_name: 资源池 ID（必填）格式: pool-xxx-xxx-xxx-xxx
        node_pool_name: 节点池名称（必填）
        limit: 分页大小，默认 100
        offset: 分页偏移量，默认 0

    调用经验:
        - 可以通过 label 过滤特定节点池的节点
        - 节点的 status.phase 表示节点状态:
          - Available: 正常可用
          - Creating: 创建中
          - Terminating: 删除中
          - NotReady: 异常状态

    返回字段说明:
        - metadata.name: 节点名称 (os-node-created-xxx)
        - metadata.labels: 节点标签，包含节点池信息
        - spec.flavor: 节点规格
        - status.phase: 节点状态
        - status.nodeIp: 节点内网 IP
        - status.conditions: 节点健康状态

    Returns:
        节点池下的节点列表
    """
    if not pool_name:
        return format_api_result(False, error="pool_name is required")
    if not node_pool_name:
        return format_api_result(False, error="node_pool_name is required")

    params = {}
    if limit:
        params["limit"] = limit
    if offset:
        params["offset"] = offset

    result = access_api_call(
        access,
        "GET",
        "/v2/{project_id}/pools/{p_id}/nodes",
        p_id=pool_name, params=params
    )

    if result.get("success", True) and "data" in result:
        items = result["data"].get("items", [])
        filtered_items = [
            node for node in items
            if node.get("metadata", {}).get("labels", {}).get("os.modelarts.node/nodepoolname") == node_pool_name
            or node.get("metadata", {}).get("labels", {}).get("os.modelarts.node/nodepool") == node_pool_name
        ]
        result["data"]["items"] = filtered_items
        result["data"]["total"] = len(filtered_items)

    return format_api_result(True, data=result)


__all__ = ["list_node_pool_nodes"]