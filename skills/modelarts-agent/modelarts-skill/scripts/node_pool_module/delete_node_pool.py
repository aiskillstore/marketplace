#!/usr/bin/env python3
"""
NodePool模块 - delete_node_pool函数
功能：删除节点池
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any


@authenticated_api_call
def delete_node_pool(access, pool_name: str, node_pool_name: str) -> Dict[str, Any]:
    """
    删除节点池

    Args:
        pool_name: 资源池 ID（必填）格式: pool-xxx-xxx-xxx-xxx
        node_pool_name: 节点池名称（必填）

    调用经验:
        - 删除节点池会同时删除该节点池下的所有节点
        - 删除操作不可逆，请谨慎使用
        - 默认节点池（nodepool-xxx-default）不能删除
        - 删除过程需要几分钟，期间节点会进入 Terminating 状态

    注意事项:
        - 请确保没有工作负载运行在该节点池的节点上
        - 删除前建议先缩容到 0，观察影响后再真正删除
        - 如果有 Pod 绑定到特定节点，删除节点池会导致这些 Pod 失败

    Returns:
        删除结果
    """
    if not pool_name:
        return format_api_result(False, error="pool_name is required")
    if not node_pool_name:
        return format_api_result(False, error="node_pool_name is required")

    result = access_api_call(
        access,
        "DELETE",
        "/v2/{project_id}/pools/{p_id}/nodepools/{node_pool_name}",
        p_id=pool_name,
        node_pool_name=node_pool_name
    )

    return format_api_result(True, data=result)


__all__ = ["delete_node_pool"]