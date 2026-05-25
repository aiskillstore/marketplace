#!/usr/bin/env python3
"""
Pool模块 - batch_lock_nodes函数
功能：批量锁定资源池节点
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def batch_lock_nodes(access, pool_name: str, node_names: List[str]) -> Dict[str, Any]:
    """
    批量锁定资源池节点

    Args:
        pool_name: 资源池 ID（必填）格式: pool-xxx-xxx-xxx-xxx
        node_names: 节点名称列表（必填）

    Returns:
        操作结果
    
    调用经验:
        - action 固定为 'delete'（表示设置不可调度标记）
        - 锁定后节点不会接受新的作业调度
        - 不影响正在运行的作业
    
    注意事项:
        - 字段名必须是 camelCase: 'nodeNames' 和 'actions'
        - action 必须是 'delete'，不是 'Lock' 或 'lock'
    """
    if not pool_name:
        return format_api_result(False, error="pool_name is required")
    if not node_names or not isinstance(node_names, list) or len(node_names) == 0:
        return format_api_result(False, error="node_names is required and must be a non-empty list")

    body = {"nodeNames": node_names, "actions": ["delete"]}

    result = access_api_call(
        access,
        "POST",
        "/v2/{project_id}/pools/{pool_name}/nodes/batch-lock",
        pool_name=pool_name, body=body
    )

    return format_api_result(True, data=result)


__all__ = ["batch_lock_nodes"]