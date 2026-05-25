#!/usr/bin/env python3
"""
Lite Server 模块 - detach_volume 函数
功能：从Lite Server卸载云硬盘
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any
from .common import validate_required_params, add_api_reference

@authenticated_api_call
def ma_liteserver_detach_volume(
    access,
    server_id: str,
    volume_id: str
) -> Dict[str, Any]:
    """
    Detach a volume from a Lite Server.
    Args:
        server_id: The server ID (required)
        volume_id: The volume ID (required)
    Returns:
        Detachment status
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
        'DELETE',
        '/v1/{project_id}/dev-servers/{server_id}/detachvolume/{volume_id}',
        body=body,
        server_id=server_id,
        volume_id=volume_id
    )

    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.26 DetachDevServerVolume (Page 1767)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_detach_volume']
