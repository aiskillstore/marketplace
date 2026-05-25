#!/usr/bin/env python3
"""
Pool模块 - list_pools函数
功能：列出资源池
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, parse_pool_data, Dict, Any, List


@authenticated_api_call
def list_pools(access, limit: int = 100) -> Dict[str, Any]:
    """
    列出所有专属资源池
    
        Args:
            limit: 最大返回数量（可选，默认: 100）
    
        Returns:
            资源池列表，包含 pools 和 total 字段
    
        示例:
            >>> from pool_module import list_pools
            >>> result = list_pools(limit=100)
            >>> if result['success']:
            ...     pools = result['data']['pools']
            ...     for pool in pools:
            ...         name = pool['metadata']['labels'].get('os.modelarts/name')
            ...         status = pool['status'].get('phase')
            ...         print(f"{name}: {status}")
    """
    result = access_api_call(
        access,
        'GET',
        '/v2/{project_id}/pools',
        query={'limit': limit}
    )

    return format_api_result(True, data=parse_pool_data(result))


__all__ = ['list_pools']