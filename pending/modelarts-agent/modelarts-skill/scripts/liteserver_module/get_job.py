#!/usr/bin/env python3
"""
Lite Server 模块 - get_job 函数
功能：查询指定 Lite Server 作业详情
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any
from .common import validate_required_params, add_api_reference

@authenticated_api_call
def ma_liteserver_get_job(
    access,
    job_id: str
) -> Dict[str, Any]:
    """
    Get details of a specific Lite Server job.
    Args:
        job_id: The job ID (required)
    Returns:
        Job details
    """
    valid, error = validate_required_params({"job_id": job_id}, ["job_id"])
    if not valid:
        return format_api_result(False, error=error)
    result = simple_api_call(
        access,
        'GET',
        '/v1/{project_id}/dev-servers/jobs/{job_id}',
        job_id=job_id
    )
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.43 GetDevServerJob (Page 1860)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_get_job']
