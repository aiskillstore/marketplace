#!/usr/bin/env python3
"""
NodePool模块 - update_node_pool函数
功能：更新节点池配置（扩缩容、修改规格等）
"""

from ._bootstrap import authenticated_api_call, format_api_result, simple_api_call, Dict, Any, Optional


def _get_current_nodepool_config(
    access,
    pool_name: str,
    node_pool_name: str
) -> Optional[Dict]:
    """
    获取当前节点池配置（辅助函数）
    
    Returns:
        当前 spec.resources 配置，如果失败返回 None
    """
    result = simple_api_call(
        access,
        "GET",
        "/v2/{project_id}/pools/{p_id}/nodepools/{np_id}",
        p_id=pool_name,
        np_id=node_pool_name
    )
    return result.get('spec', {}).get('resources') if result and 'spec' in result else None


def _update_node_count_in_config(
    resources: Dict,
    node_num: Optional[int],
    max_node_num: Optional[int]
) -> Dict:
    """
    更新节点池配置中的节点数量（辅助函数）
    
    Args:
        resources: 当前 resources 配置
        node_num: 新的节点数量
        max_node_num: 新的最大节点数量
    
    Returns:
        更新后的 resources 配置
    """
    if node_num is not None:
        resources['count'] = node_num
        resources['maxCount'] = node_num
        if 'azs' in resources and len(resources['azs']) > 0:
            resources['azs'][0]['count'] = node_num
    
    if max_node_num is not None:
        resources['maxCount'] = max_node_num
    
    return resources


def _update_metadata_fields(body: Dict, labels: Dict, annotations: Dict) -> Dict:
    """
    更新节点池的元数据字段（辅助函数）
    
    Args:
        body: 请求体字典
        labels: 标签字典
        annotations: 注解字典
    
    Returns:
        更新后的 body
    """
    if labels or annotations:
        if "metadata" not in body:
            body["metadata"] = {}
        if labels:
            body["metadata"]["labels"] = labels
        if annotations:
            body["metadata"]["annotations"] = annotations
    return body


@authenticated_api_call
def update_node_pool(
    access,
    pool_name: str,
    node_pool_name: str,
    node_num: Optional[int] = None,
    max_node_num: Optional[int] = None,
    labels: Dict[str, str] = None,
    annotations: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    更新节点池配置（主要用于扩缩容）

    Args:
        pool_name: 资源池 ID（必填）格式: pool-xxx-xxx-xxx-xxx
        node_pool_name: 节点池名称（必填）
        node_num: 新的节点数量（选填）
        max_node_num: 新的最大节点数量（选填）
        labels: 更新的标签（选填）
        annotations: 更新的注解（选填）

    调用经验:
        - PATCH 请求需要特殊的 Content-Type
        - 必须设置: Content-Type: application/merge-patch+json
        - 扩容操作只需要修改 spec.resources.count 和 maxCount
        - 扩容后新节点需要 3-5 分钟才能就绪
        - 缩容会随机删除节点，如果需要指定删除节点请使用 batch_delete_nodes

    扩缩容示例:
        # 扩容到 5 个节点
        update_node_pool(pool_name, node_pool_name, node_num=5)
        
        # 缩容到 2 个节点
        update_node_pool(pool_name, node_pool_name, node_num=2)

    Returns:
        更新结果
    """
    if not pool_name:
        return format_api_result(False, error="pool_name is required")
    if not node_pool_name:
        return format_api_result(False, error="node_pool_name is required")

    has_update = any([node_num is not None, max_node_num is not None, labels, annotations])
    if not has_update:
        return format_api_result(False, error="no update fields specified")

    body = {}

    if node_num is not None or max_node_num is not None:
        current_resources = _get_current_nodepool_config(access, pool_name, node_pool_name)
        if not current_resources:
            return format_api_result(False, error="无法获取当前节点池配置")
        
        updated_resources = _update_node_count_in_config(current_resources, node_num, max_node_num)
        body["spec"] = {"resources": updated_resources}

    body = _update_metadata_fields(body, labels, annotations)

    headers = {"Content-Type": "application/merge-patch+json"}

    result = simple_api_call(
        access,
        "PATCH",
        "/v2/{project_id}/pools/{p_id}/nodepools/{np_id}",
        p_id=pool_name,
        np_id=node_pool_name,
        body=body,
        headers=headers
    )

    return format_api_result(True, data=result)


def scale_node_pool(
    pool_name: str,
    node_pool_name: str,
    node_num: int,
    max_node_num: Optional[int] = None
) -> Dict[str, Any]:
    """
    节点池扩缩容（便捷函数）

    Args:
        pool_name: 资源池 ID
        node_pool_name: 节点池名称
        node_num: 目标节点数量
        max_node_num: 最大节点数量（可选）

    这是 update_node_pool 的别名函数，专门用于扩缩容场景
    注意：此函数不加装饰器，让 update_node_pool 的装饰器处理认证
    """
    return update_node_pool(
        pool_name,
        node_pool_name,
        node_num,
        max_node_num
    )

__all__ = ["update_node_pool", "scale_node_pool"]