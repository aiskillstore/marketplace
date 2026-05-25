#!/usr/bin/env python3
"""
Lite Server 模块 - get_job_template 函数
功能：查询指定 Lite Server 作业模板详情
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any
from .common import validate_required_params, add_api_reference

@authenticated_api_call
def ma_liteserver_get_job_template(
    access,
    template_id: str
) -> Dict[str, Any]:
    """
    Get details of a specific Lite Server job template.
    Args:
        template_id: The job template ID (required)
    Returns:
        Job template details
    """
    valid, error = validate_required_params({"template_id": template_id}, ["template_id"])
    if not valid:
        return format_api_result(False, error=error)
    result = simple_api_call(
        access,
        'GET',
        '/v1/{project_id}/dev-servers/job-templates/{template_id}',
        template_id=template_id
    )
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.48 GetDevServerJobTemplate (Page 1879)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_get_job_template']
