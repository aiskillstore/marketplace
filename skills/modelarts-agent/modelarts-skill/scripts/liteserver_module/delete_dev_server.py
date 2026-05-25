#!/usr/bin/env python3
"""
Lite Server 模块 - delete_dev_server 函数
功能：删除 Lite Server 实例
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any
from .common import validate_required_params, add_api_reference

@authenticated_api_call
def ma_liteserver_delete(access, server_id: str) -> Dict[str, Any]:
    """
    Delete a Lite Server instance.
    Args:
        server_id: The server ID (required)
    Returns:
        Deletion status
    """
    valid, error = validate_required_params({"server_id": server_id}, ["server_id"])
    if not valid:
        return format_api_result(False, error=error)
    result = access.sdk().execute(lambda s: make_api_call(
        s,
        'DELETE',
        '/v1/{project_id}/dev-servers/{server_id}',
        server_id=server_id
    ))
    data = {
        "action": "delete",
        "server_id": server_id,
        "result": result
    }
    api_result = format_api_result(True, data=data)
    return add_api_reference(api_result, "22.7 DeleteDevServer (Page 1617)")
from common_module.api_helper import make_api_call
__all__ = ['ma_liteserver_delete']