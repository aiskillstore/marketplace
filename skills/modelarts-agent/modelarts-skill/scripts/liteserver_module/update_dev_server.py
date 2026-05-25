#!/usr/bin/env python3
"""
Lite Server 模块 - update_dev_server 函数
功能：更新 Lite Server 实例名称
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, Optional
from .common import validate_required_params, build_request_body, add_api_reference

@authenticated_api_call
def ma_liteserver_update(
    access, 
    server_id: str, 
    name: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update a Lite Server instance name.
    Args:
        server_id: The server ID (required)
        name: New name (optional)
        description: New description (optional)
    Returns:
        Updated server details
    """
    valid, error = validate_required_params({"server_id": server_id}, ["server_id"])
    if not valid:
        return format_api_result(False, error=error)
    # 至少需要一个更新参数
    if name is None and description is None:
        return format_api_result(False, error="At least one of name or description must be provided")
    body = build_request_body({}, {"name": name, "description": description})
    result = simple_api_call(
        access,
        'PUT',
        '/v1/{project_id}/dev-servers/{server_id}',
        body=body,
        server_id=server_id
    )
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.4 UpdateDevServer (Page 1593)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_update']