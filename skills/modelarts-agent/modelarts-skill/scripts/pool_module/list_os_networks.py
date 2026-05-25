#!/usr/bin/env python3
"""
Pool模块 - list_os_networks函数
功能：列出 OS 网络
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def list_os_networks(access, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    """
    列出可用的 OS 网络
    
        Args:
            limit: 最大返回数量（可选，默认: 100）
            offset: 分页偏移量（可选，默认: 0）
    
        Returns:
            网络列表
    
        示例:
            >>> from pool_module import list_os_networks
            >>> result = list_os_networks(limit=10)
            >>> if result['success']:
            ...     networks = result['data'].get('items', [])
            ...     for n in networks:
            ...         name = n['metadata'].get('name')
            ...         status = n['status'].get('phase')
            ...         print(f"{name}: {status}")
    """
    

    result = access_api_call(
        access,
        "GET",
        "/v1/{project_id}/networks",
        query={"limit": limit, "offset": offset}
    )

    return format_api_result(True, data=result)


__all__ = ["list_os_networks"]