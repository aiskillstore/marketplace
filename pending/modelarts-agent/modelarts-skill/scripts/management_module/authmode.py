#!/usr/bin/env python3
"""
授权模式管理模块

授权模式查询、更新相关功能
"""

import sys
sys.path.insert(0, '.')

from common_module.api_helper import authenticated_api_call, simple_api_call


@authenticated_api_call
def ma_authmode_show(access):
    """
    查询授权模式详情

    API: GET /v1/auth-mode

    Returns:
        当前授权模式配置
        - domain_id: 账号域ID
        - mode: 授权模式 (strict|loose)
    """
    result = simple_api_call(access, 'GET', '/v1/auth-mode')
    return result


@authenticated_api_call
def ma_authmode_update(access, mode: str):
    """
    更新授权模式

    API: PUT /v1/auth-mode

    Args:
        mode: 新授权模式 (required)
            - strict: 严格模式 - 所有操作需要权限检查
            - loose: 宽松模式 - 更宽松的访问权限

    Returns:
        更新后的授权模式配置
    """
    if not mode:
        return {"success": False, "error": "mode is required, must be 'strict' or 'loose'"}

    if mode not in ["strict", "loose"]:
        return {"success": False, "error": "mode must be 'strict' or 'loose'"}

    body = {"mode": mode}
    result = simple_api_call(access, 'PUT', '/v1/auth-mode', body=body)
    return result
