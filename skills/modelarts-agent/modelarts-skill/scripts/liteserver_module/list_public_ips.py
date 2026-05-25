#!/usr/bin/env python3
"""
Lite Server 模块 - list_public_ips 函数
功能：查询指定 Lite Server 已绑定的 EIP 列表
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any
from .common import validate_required_params, add_api_reference

@authenticated_api_call
def ma_liteserver_list_public_ips(
    access,
    server_id: str
) -> Dict[str, Any]:
    """
    Query public IPs bound to a Lite Server.
    Args:
        server_id: The server ID (required)
    Returns:
        {
            "public_ips": [
                {
                    "id": "eip-id",
                    "address": "x.x.x.x"
                },
                ...
            ]
        }
    """
    valid, error = validate_required_params({"server_id": server_id}, ["server_id"])
    if not valid:
        return format_api_result(False, error=error)
    result = simple_api_call(
        access,
        'GET',
        '/v1/{project_id}/dev-servers/{server_id}/publicips',
        server_id=server_id
    )
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "ListDevServerPublicIP")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_list_public_ips']
