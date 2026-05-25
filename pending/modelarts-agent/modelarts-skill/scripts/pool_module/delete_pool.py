#!/usr/bin/env python3
"""
Pool模块 - delete_pool函数
功能：删除资源池
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def delete_pool(access, pool_name: str) -> Dict[str, Any]:
    """
    删除指定的专属资源池

    Args:
        pool_name: 资源池 ID（必填）格式: pool-xxx-xxx-xxx-xxx

    Returns:
        删除结果
    
    调用经验:
        - 传入的是资源池 ID，不是显示名称
        - 格式示例: pool-8560512e-2b7c-4a08-80b3-2a083ee22e18
        - 删除是异步操作，需要几分钟完成
    
    注意事项:
        - 请确保资源池内没有运行的任务
        - 删除前建议先 list_pools 确认 ID
        - 删除后资源不可恢复
    """
    if not pool_name:
        return format_api_result(False, error="pool_name is required")

    result = access_api_call(
        access,
        'DELETE',
        '/v2/{project_id}/pools/{pool_name}',
        pool_name=pool_name
    )

    return format_api_result(True, data=result)


__all__ = ['delete_pool']