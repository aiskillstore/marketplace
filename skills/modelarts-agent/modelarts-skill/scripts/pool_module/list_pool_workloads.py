#!/usr/bin/env python3
"""
Pool模块 - list_pool_workloads函数
功能：列出资源池工作负载
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def list_pool_workloads(access, pool_name: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    """
    列出资源池中的工作负载
    
        Args:
            pool_name: 资源池 ID（必填）
    
        Returns:
            工作负载列表
    
        示例:
            >>> from pool_module import list_pool_workloads
            >>> result = list_pool_workloads('pool-7923ba1a-338d-4b66-ae96-789cc4fd7da5')
            >>> if result['success']:
            ...     workloads = result['data'].get('items', [])
            ...     print(f"工作负载数量: {len(workloads)}")
    """
    if not pool_name:
        return format_api_result(False, error="pool_name is required")

    result = access_api_call(
        access,
        "GET",
        "/v2/{project_id}/pools/{pool_name}/workloads",
        pool_name=pool_name, query={"limit": limit, "offset": offset}
    )

    return format_api_result(True, data=result)


__all__ = ["list_pool_workloads"]