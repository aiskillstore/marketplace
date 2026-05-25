#!/usr/bin/env python3
"""
Lite Server 模块 - get_topologies 函数
功能：获取Lite Server网络拓扑
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any
from .common import add_api_reference

@authenticated_api_call
def ma_liteserver_get_topologies(
    access,
    server_id: str = None
) -> Dict[str, Any]:
    """
    Get network topologies for Lite Server instances.
    Args:
        server_id: Server ID for topology (optional)
    Returns:
        Network topology information
    """
    query = {}
    if server_id:
        query['id'] = server_id

    result = simple_api_call(
        access,
        'GET',
        '/v1/{project_id}/dev-servers/topologies',
        query=query if query else None
    )

    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.41 GetTopologies (Page 1818)")

from common_module.api_helper import make_api_call
__all__ = ['ma_liteserver_get_topologies']
