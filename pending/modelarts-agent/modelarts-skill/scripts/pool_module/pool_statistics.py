#!/usr/bin/env python3
"""
Pool模块 - pool_statistics函数
功能：资源池统计信息
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def pool_statistics(access) -> Dict[str, Any]:
    """
    获取所有资源池的统计信息
    
        Args:
            无
    
        Returns:
            资源池统计数据
    
        示例:
            >>> from pool_module import pool_statistics
            >>> result = pool_statistics()
            >>> if result['success']:
            ...     stats = result['data']
            ...     print(f"总资源池数: {stats.get('total', 0)}")
    """
    

    result = access_api_call(
        access,
        "GET",
        "/v2/{project_id}/statistics/pools",
        query={}
    )

    return format_api_result(True, data=result)


__all__ = ["pool_statistics"]