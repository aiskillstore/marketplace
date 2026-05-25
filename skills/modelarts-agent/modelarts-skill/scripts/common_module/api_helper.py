#!/usr/bin/env python3
"""
API 辅助工具
功能：统一认证处理、标准 API 调用模板
"""

import sys
from typing import Any, Dict, Callable
from functools import wraps

sys.path.insert(0, '.')

from common_module.result import format_api_result


def authenticated_api_call(func):
    """
    认证装饰器 - 统一处理认证检查，减少每个函数的重复代码

    用法:
        @authenticated_api_call
        def my_function(access, param1, param2, **kwargs):
            # 不需要再写认证检查
            # access 已经直接可用
            return result
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        from common_module.auth import ensure_authentication

        auth_result = ensure_authentication()
        if not auth_result['success']:
            return format_api_result(False, error=auth_result['error'])

        access = auth_result['access']

        try:
            return func(access, *args, **kwargs)
        except Exception as e:
            return format_api_result(False, error=str(e))

    return wrapper


def make_api_call(
    session,
    method: str,
    path: str,
    body: Dict = None,
    query: Dict = None,
    headers: Dict = None
) -> Any:
    """
    标准 API 调用函数 - 统一处理 header、序列化、project_id

    Args:
        session: ModelArts session 对象
        method: HTTP 方法 ('GET', 'POST', 'DELETE', 'PATCH')
        path: API 路径（包含 {project_id} 占位符会自动替换）
        body: 请求体（自动 JSON 序列化）
        query: 查询参数
        headers: 额外 header（自动添加 x-modelarts-user-id）

    Returns:
        API 响应结果
    """
    from modelarts.config.auth import auth_by_apig
    import json

    request_headers = {'Content-Type': 'application/json'}
    if hasattr(session, 'user_id') and session.user_id:
        request_headers['x-modelarts-user-id'] = session.user_id
    if headers:
        request_headers.update(headers)

    if '{project_id}' in path:
        path = path.format(project_id=session.project_id)

    body_bytes = None
    if body is not None:
        body_bytes = json.dumps(body).encode('utf-8')

    return auth_by_apig(
        session,
        method,
        path,
        query=query,
        body=body_bytes,
        headers=request_headers
    )


def simple_api_call(
    access,
    method: str,
    path_pattern: str,
    body: Dict = None,
    query: Dict = None,
    headers: Dict = None,
    **path_vars
) -> Any:
    """
    简化版 API 调用 - 推荐使用

    Args:
        access: 认证后的 access 对象
        method: HTTP 方法
        path_pattern: 路径模式（包含 {project_id}, {pool_name} 等占位符）
        body: 请求体
        query: 查询参数
        headers: 额外 header
        **path_vars: 路径占位符变量（pool_name, network_name 等）

    用法:
        result = simple_api_call(
            access,
            'GET',
            '/v2/{project_id}/pools/{pool_name}/monitor',
            query={'limit': 100},
            pool_name='pool-xxx'
        )
    """
    def _call(session):
        all_vars = {'project_id': session.project_id}
        all_vars.update(path_vars)
        path = path_pattern.format(**all_vars)
        return make_api_call(session, method, path, body, query, headers)

    return access.sdk().execute(_call)


__all__ = ['authenticated_api_call', 'make_api_call', 'simple_api_call']
