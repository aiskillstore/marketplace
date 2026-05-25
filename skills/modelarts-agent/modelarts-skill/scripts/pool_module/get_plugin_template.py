#!/usr/bin/env python3
"""
Pool模块 - get_plugin_template函数
功能：获取插件模板详情
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def get_plugin_template(access, plugintemplate_name: str) -> Dict[str, Any]:
    """
    获取插件模板详情

    Args:
        plugintemplate_name: 插件模板名称（必填），可选值: 'gpu-driver', 'npu-driver'


    调用经验:
        - list_plugin_templates 使用 v2 API: GET /v2/{project_id}/plugintemplates
        - get_plugin_template 使用 v1 API: GET /v1/{project_id}/plugintemplates/{name}
        - get_plugin_template 支持的名称: 'gpu-driver', 'npu-driver'

    Returns:
        模板详情

    示例:
        >>> from pool_module import get_plugin_template
        >>> result = get_plugin_template('gpu-driver')
        >>> if result['success']:
        ...     template = result['data']
        ...     print(template.get('metadata', {}).get('name'))
    """
    if not plugintemplate_name:
        return format_api_result(False, error="plugintemplate_name is required")

    result = access_api_call(
        access,
        "GET",
        "/v1/{project_id}/plugintemplates/{plugintemplate_name}",
        plugintemplate_name=plugintemplate_name
    )

    return format_api_result(True, data=result)


__all__ = ["get_plugin_template"]