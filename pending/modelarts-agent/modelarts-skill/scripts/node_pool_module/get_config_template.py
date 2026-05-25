#!/usr/bin/env python3
"""
NodePool模块 - get_config_template函数
功能：查询节点配置模板接口用于获取指定节点配置模板的详细信息。
该接口适用于以下场景：当用户需要查看节点配置模板的内容、管理节点配置或进行相关操作时，
可通过此接口获取指定节点配置模板的详细信息。
"""

def get_config_template(nodeconfigtemplate_name: str):
    """
    获取指定节点配置模板的详细信息。

    该接口适用于以下场景：当用户需要查看节点配置模板的内容、管理节点配置或进行相关操作时，
    可通过此接口获取指定节点配置模板的详细信息。

    使用该接口的前提条件是节点配置模板已存在且用户具有相应的访问权限。
    调用该接口后，系统将返回指定节点配置模板的详细信息，包括模板名称、版本、配置参数及描述等。

    Args:
        nodeconfigtemplate_name: 节点配置模板的名称（必需）

    Returns:
        节点配置模板的详细信息，包括模板名称、版本、配置参数及描述等

    API文档：
        - URI: GET /v1/{project_id}/nodeconfigtemplates/{nodeconfigtemplate_name}
        - 权限：需要查询权限
        - 返回：节点配置模板的详细信息
        - 错误：若节点配置模板不存在或用户无权限访问，接口将返回相应的错误信息
    """
    try:
        from common_module.auth import ensure_authentication
        from common_module.api_helper import simple_api_call
        from common_module.result import format_api_result

        auth_result = ensure_authentication()
        if not auth_result.get('success'):
            return format_api_result(False, error=auth_result.get('error', '认证失败'))
        
        access = auth_result.get('access')

        result = simple_api_call(
            access,
            "GET",
            "/v1/{project_id}/nodeconfigtemplates/{template_name}",
            template_name=nodeconfigtemplate_name
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=str(e))


__all__ = ["get_config_template"]