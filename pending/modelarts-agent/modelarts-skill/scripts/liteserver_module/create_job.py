#!/usr/bin/env python3
"""
Lite Server 模块 - create_job 函数
功能：创建 Lite Server 作业
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, List, Optional
from .common import validate_required_params, build_request_body, add_api_reference

@authenticated_api_call
def ma_liteserver_create_job(
    access,
    name: str,
    server_ids: List[str],
    type: str,
    items: List[Dict[str, Any]],
    description: Optional[str] = None,
    is_reboot: bool = False
) -> Dict[str, Any]:
    """
    Create a Lite Server job.
    Args:
        name: Job name (required) - ^[-_.a-zA-Z0-9]{1,64}$
        server_ids: List of server IDs (required)
        type: Job template type (required) - e.g., COMMON, SERVICE_DEPLOY
        items: Job instance list (required) - Array of DevServerJobItem objects
        description: Job description (optional)
        is_reboot: Whether to reboot on job failure (optional) - default False
    Returns:
        Created job details including id, name, type, status
    """
    valid, error = validate_required_params(
        {"name": name, "server_ids": server_ids, "type": type, "items": items},
        ["name", "server_ids", "type", "items"]
    )
    if not valid:
        return format_api_result(False, error=error)
    required = {
        "name": name,
        "server_ids": server_ids,
        "type": type,
        "items": items
    }
    optional = {}
    if description is not None:
        optional['description'] = description
    if is_reboot:
        optional['is_reboot'] = is_reboot

    body = build_request_body(required, optional)
    result = simple_api_call(
        access,
        'POST',
        '/v1/{project_id}/dev-servers/jobs',
        body=body
    )

    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.46 CreateDevServerJob (Page 1870)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_create_job']
