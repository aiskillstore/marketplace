#!/usr/bin/env python3
"""
Lite Server 模块 - bind_eip 函数
功能：为 Lite Server 绑定弹性公网IP（EIP）
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, Optional
from .common import validate_required_params, build_request_body, add_api_reference

@authenticated_api_call
def ma_liteserver_bind_eip(
    access,
    server_id: str,
    public_ip_id: Optional[str] = None,
    public_ip_address: Optional[str] = None
) -> Dict[str, Any]:
    """
    Prerequisites: Server must be RUNNING, user must have EIP binding permission.
    Args:
        server_id: The server ID (required)
        public_ip_id: EIP ID to bind (required if public_ip_address not provided)
        public_ip_address: EIP IP address to bind (required if public_ip_id not provided)
    Returns:
        {
            "public_ips": [
                {
                    "id": "eip-id",
                    "address": "x.x.x.x"
                }
            ]
        }
    """
    valid, error = validate_required_params({"server_id": server_id}, ["server_id"])
    if not valid:
        return format_api_result(False, error=error)

    if not public_ip_id and not public_ip_address:
        return format_api_result(False, error="public_ip_id or public_ip_address is required")
    body = {}
    if public_ip_id:
        body['public_ip_id'] = public_ip_id
    result = simple_api_call(
        access,
        'POST',
        '/v1/{project_id}/dev-servers/{server_id}/publicips',
        body=body,
        server_id=server_id
    )

    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "BindDevServerPublicIP")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_bind_eip']
