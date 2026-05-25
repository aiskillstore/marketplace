#!/usr/bin/env python3
"""
NodePool模块 - list_pool_plugins函数

功能：查询插件实例列表接口用于获取系统中已部署的插件实例信息。
该接口适用于以下场景：当用户需要查看系统中已部署的插件实例、监控插件运行状态、
管理插件配置或进行故障排查时，可通过此接口获取插件实例的详细信息。
"""

def list_pool_plugins(pool_name: str):
    """
    列出资源池下所有已安装的插件。

    该接口适用于以下场景：当用户需要查看系统中已部署的插件实例、监控插件运行状态、
    管理插件配置或进行故障排查时，可通过此接口获取插件实例的详细信息。

    Args:
        pool_name: 资源池名称/ID（格式：pool-xxx-xxx-xxx-xxx）

    Returns:
        插件实例列表，包括插件名称、类型、状态、版本及部署环境等信息

    API文档：
        - URI: GET /v2/{project_id}/pools/{pool_name}/plugins
        - 权限：需要查询权限，且系统中已部署至少一个插件实例
        - 返回：所有插件实例的列表，包括插件名称、类型、状态、版本及部署环境等信息
        - 错误：若用户无权限访问或系统中未部署任何插件实例，接口将返回相应的错误信息或空列表
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
            "/v2/{project_id}/pools/{p_id}/plugins",
            p_id=pool_name
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=str(e))


__all__ = ["list_pool_plugins"]