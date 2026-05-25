#!/usr/bin/env python3
"""
NodePool模块 - create_pool_plugin函数

功能：创建插件实例接口用于在系统中创建一个新的插件实例
该接口适用于以下场景：当需要扩展系统功能、部署新的插件、更新现有插件配置或测试插件时
用户可通过此接口创建指定插件的实例
API: POST /v2/{project_id}/pools/{pool_name}/plugins
"""

from typing import Any, Dict, Optional

def create_pool_plugin(
    pool_name: str,
    template_name: str,
    version: Optional[str] = None,
    inputs: Optional[Dict[str, Any]] = None
):
    """
    在资源池中创建新的插件实例。

    该接口适用于以下场景：当需要扩展系统功能、部署新的插件、更新现有插件配置或测试插件时，
    用户可通过此接口创建指定插件的实例。

    使用该接口的前提条件是插件已存在且用户具有管理员权限或插件管理权限。
    创建操作完成后，插件实例将被成功创建并处于可用状态，相关配置信息将被记录。

    Args:
        pool_name: 资源池名称/ID（格式：pool-xxx-xxx-xxx-xxx）
        template_name: 待安装插件模板名称，如 "log-agent"（必需）
        version: 待安装、升级插件的版本号（可选）
        inputs: 插件模板安装参数（各插件不同），升级插件时需要填写全量安装参数，
                未填写参数将使用插件模板中的默认值（可选）

    Returns:
        插件实例创建结果，包括实例ID、状态等信息

    API文档：
        - URI: POST /v2/{project_id}/pools/{pool_name}/plugins
        - 权限：需要管理员权限或插件管理权限
        - 返回：插件实例创建结果
        - 错误：若插件不存在、用户无权限操作、配置参数错误或系统资源不足，接口将返回相应的错误信息
    """
    try:
        from common_module.auth import ensure_authentication
        from common_module.api_helper import simple_api_call
        from common_module.result import format_api_result

        auth_result = ensure_authentication()
        if not auth_result.get('success'):
            return format_api_result(False, error=auth_result.get('error', '认证失败'))
        
        access = auth_result.get('access')

        request_body = {
            "apiVersion": "v2",
            "kind": "Plugin",
            "spec": {
                "template": {
                    "name": template_name
                }
            }
        }
        
        if version:
            request_body["spec"]["template"]["version"] = version
        
        if inputs:
            request_body["spec"]["template"]["inputs"] = inputs

        result = simple_api_call(
            access,
            "POST",
            "/v2/{project_id}/pools/{p_id}/plugins",
            p_id=pool_name,
            body=request_body
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=str(e))


__all__ = ["create_pool_plugin"]