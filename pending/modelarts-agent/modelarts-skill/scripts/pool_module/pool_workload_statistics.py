#!/usr/bin/env python3
"""
Pool模块 - pool_workload_statistics函数
功能：资源池工作负载统计
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def pool_workload_statistics(access, pool_name: str) -> Dict[str, Any]:
    """
    获取资源池工作负载统计信息
    
        Args:
            pool_name: 资源池 ID（必填）
    
        Returns:
            工作负载统计数据
    
        示例:
            >>> from pool_module import pool_workload_statistics
            >>> result = pool_workload_statistics('pool-7923ba1a-338d-4b66-ae96-789cc4fd7da5')
            >>> if result['success']:
            ...     stats = result['data']
            ...     print(stats)
    """
    if not pool_name:
        return format_api_result(False, error="pool_name is required")

    result = access_api_call(
        access,
        "GET",
        "/v2/{project_id}/statistics/pools/{pool_name}/workloads",
        pool_name=pool_name, query={}
    )

    return format_api_result(True, data=result)


__all__ = ["pool_workload_statistics"]