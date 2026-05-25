#!/usr/bin/env python3
"""
Lite Server 模块 - list_all 函数
功能：查询所有Lite Server实例（跨用户/全部）
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, Optional
from .common import add_api_reference

@authenticated_api_call
def ma_liteserver_list_all(
    access,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Query list of all Lite Server instances for tenant.
    Args:
        status: Filter by status (optional)
        limit: Maximum results (default: 100)
        offset: Offset for pagination (default: 0)
        user_id: Filter by user ID (optional)
    Returns:
        List of all Lite Server instances with pagination
    """
    query = {}
    if status:
        query['status'] = status
    if user_id:
        query['user_id'] = user_id
    if limit:
        query['limit'] = str(limit)
    if offset:
        query['offset'] = str(offset)
    result = simple_api_call(
        access,
        'GET',
        '/v1/{project_id}/dev-servers/all',
        query=query if query else None
    )
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.32 ListAllDevServers (Page 1788)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_list_all']
