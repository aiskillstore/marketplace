#!/usr/bin/env python3
"""
Lite Server 模块 - attach_volume 函数
功能：挂载云硬盘到Lite Server
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any
from .common import validate_required_params, add_api_reference

@authenticated_api_call
def ma_liteserver_attach_volume(
    access,
    server_id: str,
    volume_id: str
) -> Dict[str, Any]:
    """
    Args:
        server_id: The server ID (required)
        volume_id: The existing volume ID to attach (required)
    Returns:
        Attachment status
    """
    valid, error = validate_required_params(
        {"server_id": server_id, "volume_id": volume_id},
        ["server_id", "volume_id"]
    )
    if not valid:
        return format_api_result(False, error=error)

    body = {"volume_id": volume_id}

    result = simple_api_call(
        access,
        'POST',
        '/v1/{project_id}/dev-servers/{server_id}/attachvolume',
        body=body,
        server_id=server_id
    )

    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.25 AttachDevServerVolume (Page 1764)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_attach_volume']
