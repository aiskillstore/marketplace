#!/usr/bin/env python3
"""
Lite Server 模块 - create_hyper_tags 函数
功能：创建超节点标签
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, List
from .common import validate_required_params, add_api_reference

@authenticated_api_call
def ma_liteserver_create_hyper_tags(
    access,
    hyperinstance_id: str,
    tags: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Create tags for a Lite Server hyperinstance.
    API Reference: 22.13 CreateHyperinstanceTags (Page 1646)
    URI: POST /v1/{project_id}/dev-servers/hyperinstance/{id}/tags/create
    SECURITY: Uses secure SDK wrapper. Credentials never exposed.
    Args:
        hyperinstance_id: The hyperinstance ID (required)
        tags: List of tags, each with "key" and "value" (required)
    Returns:
        {"success": True, "data": {"tags": [...]}} on success
        Note: API returns 200 with empty body on success; None response is treated as success.
    """
    valid, error = validate_required_params(
        {"hyperinstance_id": hyperinstance_id, "tags": tags},
        ["hyperinstance_id", "tags"]
    )
    if not valid:
        return format_api_result(False, error=error)

    body = {"tags": tags}
    # Use simple_api_call which handles path variables (id -> {id})
    # Note: simple_api_call internally calls access.sdk().execute()
    result = simple_api_call(
        access,
        'POST',
        '/v1/{project_id}/dev-servers/hyperinstance/{id}/tags/create',
        body=body,
        id=hyperinstance_id
    )
    # None result means 200/201 with empty body - treat as success
    if result is None:
        api_result = format_api_result(True, data={"tags": tags})
    else:
        api_result = format_api_result(True, data=result)

    return add_api_reference(api_result, "22.13 CreateHyperinstanceTags (Page 1646)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_create_hyper_tags']
