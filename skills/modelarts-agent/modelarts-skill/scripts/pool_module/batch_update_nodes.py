#!/usr/bin/env python3
"""
Pool模块 - batch_update_nodes函数
功能：批量更新资源池节点
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def batch_update_nodes(
    access,
    pool_name: str,
    node_names: List[str],
    action: str,
    ha_redundant_enable: bool = None,
    ha_redundant_effect: str = None,
    driver: dict = None,
    tags: List[dict] = None
) -> Dict[str, Any]:
    """
    批量更新资源池节点

    Args:
        pool_name: 资源池 ID（必填）格式: pool-xxx-xxx-xxx-xxx
        node_names: 节点名称列表（必填）
        action: 更新操作类型（必填）:
            - 'openHaRedundant': 开启高可用冗余标签
            - 'closeHaRedundant': 关闭高可用冗余标签
            - 'createTags': 批量添加节点标签
            - 'deleteTags': 批量删除节点标签
        ha_redundant_enable: 是否开启高可用冗余（open/close action 必填）
        ha_redundant_effect: 高可用冗余标签效果: NoSchedule / NoExecute（可选）
        driver: 驱动更新配置（可选）
        tags: 标签列表，每个标签包含 key 和 value 字段（可选）

    Returns:
        操作结果
    
    调用经验:
        - 开启高可用冗余: action='openHaRedundant', ha_redundant_enable=True
        - 返回 successNodeNames 列表表示成功的节点
    """
    if not pool_name:
        return format_api_result(False, error="pool_name is required")
    if not node_names or not isinstance(node_names, list) or len(node_names) == 0:
        return format_api_result(False, error="node_names is required and must be a non-empty list")
    if not action:
        return format_api_result(False, error="action is required")

    body = {"nodeNames": node_names, "action": action}
    
    if ha_redundant_enable is not None:
        body["haRedundantEnable"] = ha_redundant_enable
    if ha_redundant_effect is not None:
        body["haRedundantEffect"] = ha_redundant_effect
    if driver is not None:
        body["driver"] = driver
    if tags is not None:
        body["tags"] = tags

    result = access_api_call(
        access,
        "POST",
        "/v2/{project_id}/pools/{pool_name}/nodes/batch-update",
        pool_name=pool_name, body=body
    )

    return format_api_result(True, data=result)


__all__ = ["batch_update_nodes"]