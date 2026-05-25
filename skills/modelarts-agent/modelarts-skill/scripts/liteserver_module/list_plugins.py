#!/usr/bin/env python3
"""
Lite Server 模块 - list_plugins 函数
功能：查询Lite Server插件列表
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, Optional
from .common import add_api_reference

@authenticated_api_call
def ma_liteserver_list_plugins(
    access,
    server_id: str = None,
    plugin_type: str = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    List Lite Server plugins.
    Args:
        server_id: Server ID filter (optional)
        plugin_type: Plugin type filter (optional)
        limit: Maximum results (default: 100)
        offset: Offset for pagination (default: 0)
    Returns:
        Plugin list with pagination
    """
    query = {}
    if server_id:
        query['id'] = server_id
    if plugin_type:
        query['plugin_type'] = plugin_type
    if limit:
        query['limit'] = str(limit)
    if offset:
        query['offset'] = str(offset)
    result = simple_api_call(
        access,
        'GET',
        '/v1/{project_id}/dev-servers/plugins',
        query=query if query else None
    )
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.35 ListPlugins (Page 1805)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_list_plugins']
