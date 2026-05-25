#!/usr/bin/env python3
"""
Pool模块 - batch_resize_nodes函数
功能：批量调整资源池节点规格
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def batch_resize_nodes(
    access,
    pool_name: str,
    nodes: List[dict],
    source: dict,
    target: dict
) -> Dict[str, Any]:
    """
    批量调整资源池节点规格

    Args:
        pool_name: 资源池 ID（必填）格式: pool-xxx-xxx-xxx-xxx
        nodes: 节点配置列表（必填），每个元素包含节点信息
        source: 源节点规格配置（必填），包含 nodePool、flavor 等
        target: 目标节点规格配置（必填），包含 nodePool、flavor 等

    Returns:
        操作结果
    
    调用经验:
        - 需要 nodes、source、target 三个核心参数
        - source 表示当前配置，target 表示目标配置
        - 操作是异步的，返回 job_id 表示任务已提交
    """
    if not pool_name:
        return format_api_result(False, error="pool_name is required")
    if not nodes or not isinstance(nodes, list) or len(nodes) == 0:
        return format_api_result(False, error="nodes is required and must be a non-empty list")
    if not source or not isinstance(source, dict):
        return format_api_result(False, error="source is required and must be a dict")
    if not target or not isinstance(target, dict):
        return format_api_result(False, error="target is required and must be a dict")

    body = {
        "nodes": nodes,
        "source": source,
        "target": target
    }

    result = access_api_call(
        access,
        "POST",
        "/v2/{project_id}/pools/{pool_name}/nodes/batch-resize",
        pool_name=pool_name, body=body
    )

    return format_api_result(True, data=result)


__all__ = ["batch_resize_nodes"]