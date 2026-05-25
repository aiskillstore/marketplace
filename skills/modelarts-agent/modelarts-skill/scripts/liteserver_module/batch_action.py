#!/usr/bin/env python3
"""
Lite Server 模块 - batch_action 函数
功能：批量操作 Lite Server 实例
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, List, Optional
from .common import validate_required_params, build_request_body, add_api_reference

def _validate_batch_action_params(type: str, servers: List[Dict[str, str]]) -> tuple[bool, Optional[str]]:
    """批量操作参数验证"""
    valid_types = ['START', 'STOP', 'REBOOT', 'CHANGEOS', 'REINSTALLOS', 'DELETE']
    if not type:
        return False, "type is required"
    if type not in valid_types:
        return False, f"type must be one of {valid_types}"
    if not servers:
        return False, "servers is required"
    for server in servers:
        if not isinstance(server, dict) or 'id' not in server:
            return False, "each server must be a dict with 'id' field"
    return True, None

@authenticated_api_call
def ma_liteserver_batch_action(
    access,
    type: str,
    servers: List[Dict[str, str]],
    extend_param: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Args:
        type: 批量操作类型 (required) - START: 批量启动Lite Server实例，STOP: 批量停止Lite Server实例，REBOOT: 批量重启Lite Server实例，CHANGEOS: 批量切换Lite Server服务器操作系统镜像，REINSTALLOS: 批量重装Lite Server服务器操作系统镜像，DELETE: 批量删除Lite Server实例
        servers: 批量操作Lite Server ID列表 (required) - Array of BatchActionDevServerIds objects, each with "id" field
        extend_param: 批量切换和重装Lite Server服务器操作系统镜像配置参数 (optional) - ServerOsRequest object with admin_pass, key_pair_name, image_id, user_data
    Returns:
        Batch operation status
    """
    valid, error = _validate_batch_action_params(type, servers)
    if not valid:
        return format_api_result(False, error=error)
    body = build_request_body(
        {"type": type, "servers": servers},
        {"extend_param": extend_param}
    )
    result = simple_api_call(
        access,
        'POST',
        '/v1/{project_id}/dev-servers/action',
        body=body
    )
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.42 BatchDevServersAction (Page 1846)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_batch_action']