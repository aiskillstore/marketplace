#!/usr/bin/env python3
"""
Lite Server 模块 - reinstall_os 函数
功能：重装 Lite Server 操作系统镜像
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, Optional
from .common import validate_required_params, build_request_body, add_api_reference

@authenticated_api_call
def ma_liteserver_reinstall_os(
    access,
    server_id: str,
    admin_pass: Optional[str] = None,
    key_pair_name: Optional[str] = None,
    image_id: Optional[str] = None,
    user_data: Optional[str] = None
) -> Dict[str, Any]:
    """
    Reinstall OS image for a Lite Server instance.
    Prerequisites:
        - Server must be STOPPED
        - admin_pass and key_pair_name are mutually exclusive (at least one required)
        - image_id is required for OS change scenarios
    Args:
        server_id: The server ID (required)
        admin_pass: Admin password (8-26 chars, must include upper/lower/digit/special)
        key_pair_name: SSH key pair name (mutually exclusive with admin_pass)
        image_id: New image ID (required for OS change)
        user_data: Base64-encoded user data (max 32K before encoding)
    Returns:
        Server details with status REINSTALLINGOS
    """
    valid, error = validate_required_params({"server_id": server_id}, ["server_id"])
    if not valid:
        return format_api_result(False, error=error)

    if not admin_pass and not key_pair_name:
        return format_api_result(
            False,
            error="Either admin_pass or key_pair_name must be provided"
        )

    if admin_pass and key_pair_name:
        return format_api_result(
            False,
            error="admin_pass and key_pair_name cannot be provided at the same time"
        )
    optional = {}
    if admin_pass is not None:
        optional['admin_pass'] = admin_pass
    if key_pair_name is not None:
        optional['key_pair_name'] = key_pair_name
    if image_id is not None:
        optional['image_id'] = image_id
    if user_data is not None:
        optional['user_data'] = user_data
    body = build_request_body({}, optional)
    result = simple_api_call(
        access,
        'POST',
        '/v1/{project_id}/dev-servers/{server_id}/reinstallos',
        body=body,
        server_id=server_id
    )
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "ReinstallDevServerOS")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_reinstall_os']
