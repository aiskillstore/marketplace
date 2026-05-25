#!/usr/bin/env python3
"""
Pool模块 - batch_delete_nodes函数
功能：批量删除资源池节点
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def batch_delete_nodes(access, pool_name: str, node_names: List[str]) -> Dict[str, Any]:
    """
    批量删除资源池节点

    Args:
        pool_name: 资源池 ID（必填）格式: pool-xxx-xxx-xxx-xxx
        node_names: 要删除的节点名称列表（必填）

    Returns:
        操作结果
    
    调用经验:
        - 请求体字段是 deleteNodeNames
        - 操作是异步的，返回 job_id
        - 删除节点会释放资源，请谨慎操作
    """
    if not pool_name:
        return format_api_result(False, error="pool_name is required")
    if not node_names or not isinstance(node_names, list) or len(node_names) == 0:
        return format_api_result(False, error="node_names is required and must be a non-empty list")

    body = {"deleteNodeNames": node_names}

    result = access_api_call(
        access,
        "POST",
        "/v2/{project_id}/pools/{pool_name}/nodes/batch-delete",
        pool_name=pool_name, body=body
    )

    return format_api_result(True, data=result)


__all__ = ["batch_delete_nodes"]