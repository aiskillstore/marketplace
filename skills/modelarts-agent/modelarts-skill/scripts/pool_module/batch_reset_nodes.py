#!/usr/bin/env python3
"""
Pool模块 - batch_reset_nodes函数
功能：批量重置资源池节点
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def batch_reset_nodes(access, pool_name: str, node_names: List[str], rolling_strategy: str = "RollingByNumber", max_unavailable: int = 1) -> Dict[str, Any]:
    """
    批量重置资源池节点

    Args:
        pool_name: 资源池 ID（必填）格式: pool-xxx-xxx-xxx-xxx
        node_names: 节点名称列表（必填）
        rolling_strategy: 滚动策略（可选）: RollingByNumber / RollingByPercent
        max_unavailable: 最大不可用节点数（可选），默认: 1

    Returns:
        操作结果
    
    调用经验:
        - 需要 rollingConfig 配置滚动策略
        - 操作是异步的，返回 job_id 表示任务已提交
        - 任务完成需要几分钟
    """
    if not pool_name:
        return format_api_result(False, error="pool_name is required")
    if not node_names or not isinstance(node_names, list) or len(node_names) == 0:
        return format_api_result(False, error="node_names is required and must be a non-empty list")

    body = {
        "nodeNames": node_names,
        "rollingConfig": {
            "strategy": rolling_strategy,
            "maxUnavailable": max_unavailable
        }
    }
    

    result = access_api_call(
        access,
        "POST",
        "/v2/{project_id}/pools/{pool_name}/nodes/batch-reset",
        pool_name=pool_name, body=body
    )

    return format_api_result(True, data=result)


__all__ = ["batch_reset_nodes"]