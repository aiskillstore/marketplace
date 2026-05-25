#!/usr/bin/env python3
"""
Pool模块 - list_plugin_templates函数
功能：列出插件模板
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def list_plugin_templates(access, limit: int = 50) -> Dict[str, Any]:
    """
    列出插件模板

    Args:
        limit: 最大返回数量（可选）


    调用经验:
        - list_plugin_templates 使用 v2 API: GET /v2/{project_id}/plugintemplates
        - get_plugin_template 使用 v1 API: GET /v1/{project_id}/plugintemplates/{name}
        - get_plugin_template 支持的名称: 'gpu-driver', 'npu-driver'

    Returns:
        插件模板列表
    """
    

    result = access_api_call(
        access,
        "GET",
        "/v2/{project_id}/plugintemplates",
        query={"limit": limit}
    )

    return format_api_result(True, data=result)


__all__ = ["list_plugin_templates"]