#!/usr/bin/env python3
"""
Lite Server 模块 - sync_dev_servers 函数
功能：实时同步指定 Lite Server 实例状态（通过 query 参数指定）
说明: server_id 通过 query 参数传入，非路径参数
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, Optional
from .common import validate_required_params, add_api_reference

@authenticated_api_call
def ma_liteserver_sync(
    access,
    server_id: Optional[str] = None,
    owner: Optional[str] = None,
    sort_dir: Optional[str] = None,
    sort_key: Optional[str] = None,
    offset: Optional[int] = None,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Real-time sync Lite Server instances status.
    Args:
        server_id: The server ID to sync (optional) - passed as query param
        owner: Instance owner user ID (optional) - admin only
        sort_dir: Sorting direction (optional) - ASC or DESC, default ASC
        sort_key: Sort field (optional) - createTime or updateTime, default createTime
        offset: Pagination offset (optional) - default 0
        limit: Page size (optional) - default 10, max 1024
    Returns:
        {
            "current": 0,
            "data": [ServerResponse...],
            "pages": 1,
            "size": 10,
            "total": 2
        }
    """
    query = {}
    if server_id is not None:
        query['id'] = server_id
    if owner is not None:
        query['owner'] = owner
    if sort_dir is not None:
        query['sort_dir'] = sort_dir
    if sort_key is not None:
        query['sort_key'] = sort_key
    if offset is not None:
        query['offset'] = str(offset)
    if limit is not None:
        query['limit'] = str(limit)
    # API 调用（全局接口，server_id 作为 query 参数传入）
    result = simple_api_call(
        access,
        'PUT',
        '/v1/{project_id}/dev-servers/sync',
        query=query if query else None
    )

    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.12 SyncDevServers (Page 1636)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_sync']
