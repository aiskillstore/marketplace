#!/usr/bin/env python3
"""
Lite Server 模块 - get_job_service 函数
功能：查询 Lite Server 作业服务信息
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, Optional
from .common import add_api_reference

@authenticated_api_call
def ma_liteserver_get_job_service(
    access,
    server_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get Lite Server job service information.
    Args:
        server_id: Server ID (optional, passed as id query param)
    Returns:
        Job service info
    """
    query = None
    if server_id:
        query = {'id': server_id}
    result = simple_api_call(
        access,
        'GET',
        '/v1/{project_id}/dev-servers/job-service',
        query=query
    )
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.51 GetDevServerJobService (Page 1889)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_get_job_service']
