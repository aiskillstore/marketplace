#!/usr/bin/env python3
"""
Lite Server 模块 - get_operation 函数
功能：查询指定 Operation 的详情信息
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any
from .common import validate_required_params, add_api_reference

@authenticated_api_call
def ma_liteserver_get_operation(
    access,
    server_id: str,
    operation_id: str
) -> Dict[str, Any]:
    """
    Get details of a specific Operation.
    Args:
        server_id: The Lite Server instance ID (required)
        operation_id: The operation ID to query (required)
    Returns:
        {
            "operation_id": "UUID",
            "operation_status": "running",
            "operation_type": "node_detach_volume",
            "operation_error": {...}
        }
    """
    valid, error = validate_required_params(
        {"server_id": server_id, "operation_id": operation_id},
        ["server_id", "operation_id"]
    )
    if not valid:
        return format_api_result(False, error=error)
    result = simple_api_call(
        access,
        'GET',
        '/v1/{project_id}/dev-servers/{server_id}/operation/{operation_id}',
        server_id=server_id,
        operation_id=operation_id
    )
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "GetDevServerOperation")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_get_operation']
