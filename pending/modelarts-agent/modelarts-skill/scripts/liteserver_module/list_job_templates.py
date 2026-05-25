#!/usr/bin/env python3
"""
Lite Server 模块 - list_job_templates 函数
功能：查询 Lite Server 作业模板列表
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, Optional
from .common import add_api_reference

@authenticated_api_call
def ma_liteserver_list_job_templates(
    access,
    server_id: Optional[str] = None,
    job_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Query list of Lite Server job templates.
    Args:
        server_id: Server ID for filtering (optional, required for some server types)
        job_type: Filter by job type (optional) - e.g., COMMON
        limit: Maximum results (optional) - default 100
        offset: Offset for pagination (optional) - default 0
    Returns:
        Job template list with pagination
    """
    query = {}
    if server_id:
        query['id'] = server_id
    if job_type:
        query['job_type'] = job_type
    if limit:
        query['limit'] = str(limit)
    if offset:
        query['offset'] = str(offset)
    result = simple_api_call(
        access,
        'GET',
        '/v1/{project_id}/dev-servers/job-templates',
        query=query if query else None
    )
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.47 ListDevServerJobTemplates (Page 1875)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_list_job_templates']
