#!/usr/bin/env python3
"""
Lite Server 模块 - show_software 函数
功能：查询已安装的软件信息
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any
from .common import add_api_reference

@authenticated_api_call
def ma_liteserver_show_software(
    access,
    server_id: str = None
) -> Dict[str, Any]:
    """
    Show installed software for Lite Server instances.
    Args:
        server_id: Server ID filter (optional)
    Returns:
        Installed software information
    """
    query = {}
    if server_id:
        query['id'] = server_id

    result = simple_api_call(
        access,
        'GET',
        '/v1/{project_id}/dev-servers/software',
        query=query if query else None
    )

    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.34 ShowSoftware (Page 1801)")

from common_module.api_helper import make_api_call
__all__ = ['ma_liteserver_show_software']
