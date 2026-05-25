#!/usr/bin/env python3
"""
Lite Server 模块 - list_jobs 函数
功能：查询 Lite Server 作业列表
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, Optional
from .common import add_api_reference

@authenticated_api_call
def ma_liteserver_list_jobs(
    access,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Query list of Lite Server jobs.
    Args:
        status: Filter by job status (optional)
        limit: Maximum results (optional) - default 100
        offset: Offset for pagination (optional) - default 0
    Returns:
        Job list with pagination info
    """
    query = {}
    if status:
        query['status'] = status
    if limit:
        query['limit'] = str(limit)
    if offset:
        query['offset'] = str(offset)
    result = simple_api_call(
        access,
        'GET',
        '/v1/{project_id}/dev-servers/jobs',
        query=query if query else None
    )
    # 处理响应：jobs 在 result['data'] 中（分页结构：{current, data, pages, size, total}）
    if isinstance(result, dict):
        jobs_data = result.get('data', [])
        paginated = {
            'jobs': jobs_data,
            'current': result.get('current', 0),
            'pages': result.get('pages', 1),
            'size': result.get('size', 0),
            'total': result.get('total', 0)
        }
        api_result = format_api_result(True, data=paginated)
    else:
        api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.44 ListDevServerJobs (Page 1863)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_list_jobs']
