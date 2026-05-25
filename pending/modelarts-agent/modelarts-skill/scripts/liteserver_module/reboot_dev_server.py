#!/usr/bin/env python3
"""
Lite Server 模块 - reboot_dev_server 函数
功能：重启运行中的 Lite Server 实例
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any
from .common import validate_required_params, add_api_reference

@authenticated_api_call
def ma_liteserver_reboot(access, server_id: str) -> Dict[str, Any]:
    """
    Reboot a running Lite Server instance.
    Args:
        server_id: The server ID (required)
    Returns:
        Reboot status
    """
    valid, error = validate_required_params({"server_id": server_id}, ["server_id"])
    if not valid:
        return format_api_result(False, error=error)
    result = simple_api_call(
        access,
        'PUT',
        '/v1/{project_id}/dev-servers/{server_id}/reboot',
        server_id=server_id
    )
    data = {
        "action": "reboot",
        "server_id": server_id,
        "result": result
    }
    api_result = format_api_result(True, data=data)
    return add_api_reference(api_result, "22.22 RebootDevServer (Page 1732)")
from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_reboot']
