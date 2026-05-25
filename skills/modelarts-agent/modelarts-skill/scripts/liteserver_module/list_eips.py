#!/usr/bin/env python3
"""
Lite Server 模块 - list_eips 函数
功能：查询弹性公网IP列表
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, Optional
from .common import add_api_reference

@authenticated_api_call
def ma_liteserver_list_eips(
    access,
    server_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Query list of elastic public IPs for Lite Server.
    Args:
        server_id: Server ID for filtering EIPs (optional)
    Returns:
        EIP list
    """
    query = {}
    if server_id:
        query['id'] = server_id
    result = simple_api_call(
        access,
        'GET',
        '/v1/{project_id}/dev-servers/eips',
        query=query if query else None
    )
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "ListEips")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_list_eips']
