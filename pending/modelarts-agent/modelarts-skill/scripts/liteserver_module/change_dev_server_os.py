#!/usr/bin/env python3
"""
Lite Server 模块 - change_dev_server_os 函数
功能：切换Lite Server操作系统镜像
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, Optional
from .common import validate_required_params, build_request_body, add_api_reference

@authenticated_api_call
def ma_liteserver_change_os(
    access,
    server_id: str,
    image_id: Optional[str] = None,
    key_pair_name: Optional[str] = None,
    admin_pass: Optional[str] = None,
    userdata: Optional[str] = None
) -> Dict[str, Any]:
    """
    Switch OS image for a Lite Server instance.
    Args:
        server_id: The server ID (required)
        image_id: New image ID (required for OS change scenario)
        key_pair_name: SSH key pair name (optional)
        admin_pass: Admin password (optional)
        userdata: Base64-encoded user data (optional)
    Returns:
        OS change status
    """
    valid, error = validate_required_params({"server_id": server_id}, ["server_id"])
    if not valid:
        return format_api_result(False, error=error)

    optional = {}
    if image_id is not None:
        optional['Image_id'] = image_id
    if key_pair_name is not None:
        optional['key_pair_name'] = key_pair_name
    if admin_pass is not None:
        optional['admin_pass'] = admin_pass
    if userdata is not None:
        optional['userdata'] = userdata

    body = build_request_body({}, optional)

    result = simple_api_call(
        access,
        'POST',
        '/v1/{project_id}/dev-servers/{server_id}/changeos',
        body=body,
        server_id=server_id
    )

    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.17 ChangeDevServerOS (Page 1675)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_change_os']
