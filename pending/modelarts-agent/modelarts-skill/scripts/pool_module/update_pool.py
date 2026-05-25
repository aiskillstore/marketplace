#!/usr/bin/env python3
"""
Pool模块 - update_pool函数
功能：更新/扩容资源池
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def update_pool(access, pool_name: str, body: Dict) -> Dict[str, Any]:
    """
    更新/扩容资源池配置

    Args:
        pool_name: 资源池 ID（必填）格式: pool-xxx-xxx-xxx-xxx
        body: 更新配置字典（必填）


    调用经验:
        - PATCH 请求需要特殊的 Content-Type
        - 必须设置: Content-Type: application/merge-patch+json
        - 请求体使用 K8s 风格: {spec: {...}} 或 {metadata: {...}}
    
    注意事项:
        - 不要在请求体包含 apiVersion 和 kind，只需要更新的字段
        - 扩容操作只需要修改 spec.resources[0].count 和 maxCount
        - 扩容后新节点需要几分钟才能就绪

    Returns:
        更新结果
    """
    if not pool_name:
        return format_api_result(False, error="pool_name is required")
    if not body:
        return format_api_result(False, error="body is required")

    headers = {
        "Content-Type": "application/merge-patch+json"
    }

    result = access_api_call(
        access,
        "PATCH",
        "/v2/{project_id}/pools/{pool_name}",
        pool_name=pool_name, body=body, headers=headers
    )

    return format_api_result(True, data=result)


__all__ = ["update_pool"]
