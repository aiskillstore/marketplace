#!/usr/bin/env python3
"""
Pool模块 - get_pool函数
功能：获取资源池详情
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def get_pool(access, pool_name: str) -> Dict[str, Any]:
    """
    获取指定资源池的详细信息
    
        Args:
            pool_name: 资源池 ID（必填）格式: pool-xxx-xxx-xxx-xxx
    
        Returns:
            资源池详细信息
    
        示例:
            >>> from pool_module import get_pool
            >>> result = get_pool('pool-7923ba1a-338d-4b66-ae96-789cc4fd7da5')
            >>> if result['success']:
            ...     pool = result['data']
            ...     status = pool['status'].get('phase')
            ...     print(f"状态: {status}")
    """
    if not pool_name:
        return format_api_result(False, error="pool_name is required")

    result = access_api_call(
        access,
        'GET',
        '/v2/{project_id}/pools/{pool_name}',
        pool_name=pool_name
    )

    return format_api_result(True, data=result)


__all__ = ['get_pool']