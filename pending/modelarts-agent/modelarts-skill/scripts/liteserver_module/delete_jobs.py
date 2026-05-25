#!/usr/bin/env python3
"""
Lite Server 模块 - delete_jobs 函数
功能：批量删除 Lite Server Job
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, List
from .common import validate_required_params, add_api_reference

@authenticated_api_call
def ma_liteserver_delete_jobs(
    access,
    job_ids: List[str]
) -> Dict[str, Any]:
    """
    Delete Lite Server jobs in batch.
    Args:
        job_ids: List of job IDs to delete (required, array in request body)
    Returns:
        {
            "current": 1,
            "data": [
                {
                    "id": "...",
                    "name": "...",
                    "status": "FINISHED",
                    ...
                }
            ],
            "pages": 1,
            "size": 2,
            "total": 2
        }
    """
    valid, error = validate_required_params({"job_ids": job_ids}, ["job_ids"])
    if not valid:
        return format_api_result(False, error=error)
    # job_ids 通过请求体传递，不在路径中
    result = simple_api_call(
        access,
        'DELETE',
        '/v1/{project_id}/dev-servers/jobs',
        body={'job_ids': job_ids}
    )

    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "DeleteDevServerJobs")

from common_module.api_helper import make_api_call
__all__ = ['ma_liteserver_delete_jobs']
