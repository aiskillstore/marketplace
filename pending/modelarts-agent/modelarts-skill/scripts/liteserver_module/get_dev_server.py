#!/usr/bin/env python3
"""
Lite Server 模块 - get_dev_server 函数
功能：获取特定 Lite Server 实例详情
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any
from .common import validate_required_params, add_api_reference

@authenticated_api_call
def ma_liteserver_get(access, server_id: str) -> Dict[str, Any]:
    """
    Get details of a specific Lite Server instance.
    Args:
        server_id: The server ID (required)
    Returns:
        Complete server details
    """
    valid, error = validate_required_params({"server_id": server_id}, ["server_id"])
    if not valid:
        return format_api_result(False, error=error)
    result = simple_api_call(
        access,
        'GET',
        '/v1/{project_id}/dev-servers/{server_id}',
        server_id=server_id
    )
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.3 ShowDevServer (Page 1585)")
from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_get']