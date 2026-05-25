#!/usr/bin/env python3
"""
Pool模块 - list_resource_flavors函数
功能：列出可用资源规格
"""

from ._bootstrap import authenticated_api_call, format_api_result, simple_api_call, Dict, Any, List


@authenticated_api_call
def list_resource_flavors(access, limit: int = 50) -> Dict[str, Any]:
    """
    列出可用的资源规格
    
        Args:
            无
    
        Returns:
            资源规格列表
    
        示例:
            >>> from pool_module import list_resource_flavors
            >>> result = list_resource_flavors()
            >>> if result['success']:
            ...     flavors = result['data'].get('items', [])
            ...     for f in flavors:
            ...         name = f['metadata'].get('name')
            ...         cpu = f['spec'].get('cpu')
            ...         mem = f['spec'].get('memory')
            ...         print(f"{name}: {cpu}核 {mem}")
    """
    result = simple_api_call(
        access,
        "GET",
        "/v1/{project_id}/resourceflavors",
        query={"limit": limit}
    )

    return format_api_result(True, data=result)


__all__ = ['list_resource_flavors']