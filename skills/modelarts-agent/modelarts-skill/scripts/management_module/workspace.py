#!/usr/bin/env python3
"""
工作空间管理模块

工作空间创建、查询、更新、删除、配额、权限验证等功能
"""

import sys
sys.path.insert(0, '.')

from common_module.api_helper import authenticated_api_call, simple_api_call


@authenticated_api_call
def ma_workspace_show(access, workspace_id: str):
    """
    查询工作空间详情

    API: GET /v1/{project_id}/workspaces/{workspace_id}

    Args:
        workspace_id: 工作空间ID (required)
            - 默认工作空间ID为 "0"

    Returns:
        工作空间完整信息
    """
    if not workspace_id:
        return {"success": False, "error": "workspace_id is required"}

    result = simple_api_call(access, 'GET', '/v1/{project_id}/workspaces/{workspace_id}',
                            workspace_id=workspace_id)
    return result


@authenticated_api_call
def ma_workspace_update(access, workspace_id: str, name: str = None,
                        description: str = None, auth_type: str = None):
    """
    更新工作空间

    API: PUT /v1/{project_id}/workspaces/{workspace_id}

    Args:
        workspace_id: 要更新的工作空间ID (required)
        name: 新工作空间名称 (optional) - 1-64字符, 字母、数字和连字符
        description: 新工作空间描述 (optional) - 最多512字符
        auth_type: 授权类型 (optional)
            - PUBLIC: 租户公开访问
            - PRIVATE: 仅创建者和根账号可访问
            - INTERNAL: 创建者、根账号和指定IAM用户可访问

    Returns:
        更新后的工作空间详情
    """
    if not workspace_id:
        return {"success": False, "error": "workspace_id is required"}

    body = {}
    if name is not None:
        body["name"] = name
    if description is not None:
        body["description"] = description
    if auth_type is not None:
        body["auth_type"] = auth_type

    if not body:
        return {"success": False, "error": "No updates specified"}

    result = simple_api_call(access, 'PUT', '/v1/{project_id}/workspaces/{workspace_id}',
                            body=body, workspace_id=workspace_id)
    return result


@authenticated_api_call
def ma_workspace_delete(access, workspace_id: str):
    """
    删除工作空间

    API: DELETE /v1/{project_id}/workspaces/{workspace_id}

    Args:
        workspace_id: 要删除的工作空间ID (required)

    Returns:
        删除结果
    """
    if not workspace_id:
        return {"success": False, "error": "workspace_id is required"}

    result = simple_api_call(access, 'DELETE', '/v1/{project_id}/workspaces/{workspace_id}',
                            workspace_id=workspace_id)
    return result


@authenticated_api_call
def ma_workspace_show_quotas(access, workspace_id: str):
    """
    查询工作空间配额

    API: GET /v1/{project_id}/workspaces/{workspace_id}/quotas

    Args:
        workspace_id: 工作空间ID (required)

    Returns:
        工作空间配额信息（已使用/限制）
    """
    if not workspace_id:
        return {"success": False, "error": "workspace_id is required"}

    result = simple_api_call(access, 'GET', '/v1/{project_id}/workspaces/{workspace_id}/quotas',
                            workspace_id=workspace_id)
    return result


@authenticated_api_call
def ma_workspace_update_quotas(access, workspace_id: str, quotas: list):
    """
    更新工作空间配额

    API: PUT /v1/{project_id}/workspaces/{workspace_id}/quotas

    Args:
        workspace_id: 工作空间ID (required)
        quotas: 配额配置列表 (required)
            每个配额格式: {"resource": "资源类型", "quota": 10}

    Returns:
        更新结果
    """
    if not workspace_id or not quotas:
        return {"success": False, "error": "workspace_id and quotas are required"}

    body = {"quotas": quotas}
    result = simple_api_call(access, 'PUT', '/v1/{project_id}/workspaces/{workspace_id}/quotas',
                            body=body, workspace_id=workspace_id)
    return result


@authenticated_api_call
def ma_workspace_list(access, limit: int = 100, offset: int = 0):
    """
    列出工作空间

    API: GET /v1/{project_id}/workspaces

    Args:
        limit: 每页最大数量 (default: 100)
        offset: 分页偏移量 (default: 0)

    Returns:
        带分页信息的工作空间列表
    """
    query = {}
    if limit != 100:
        query["limit"] = limit
    if offset > 0:
        query["offset"] = offset

    result = simple_api_call(access, 'GET', '/v1/{project_id}/workspaces', query=query)
    return result


@authenticated_api_call
def ma_workspace_create(access, name: str, description: str = None,
                        enterprise_project_id: str = None,
                        auth_type: str = None,
                        grants: list = None):
    """
    创建工作空间

    API: POST /v1/{project_id}/workspaces

    Args:
        name: 工作空间名称 (required)
            - 1-64字符, 字母、数字和连字符
            - "default" 为系统保留名称，不可使用
        description: 工作空间描述 (optional)
            - 最多512字符
        enterprise_project_id: 企业项目ID (optional)
            - 启用企业项目时为36字符
        auth_type: 授权类型 (optional)
            - PUBLIC: 租户公开访问 (默认)
            - PRIVATE: 仅创建者和根账号可访问
            - INTERNAL: 创建者、根账号和指定IAM用户可访问
        grants: 授权用户列表 (optional, auth_type=INTERNAL时必需)
            每个授权格式: {"user_id": "iam-user-id", "user_name": "username"}

    Returns:
        创建的工作空间详情
    """
    if not name:
        return {"success": False, "error": "name is required"}

    if name == "default":
        return {"success": False, "error": "\"default\" is reserved by system, cannot be used"}

    body = {"name": name}

    if description:
        body["description"] = description
    if enterprise_project_id:
        body["enterprise_project_id"] = enterprise_project_id
    if auth_type:
        body["auth_type"] = auth_type
    if grants and isinstance(grants, list):
        body["grants"] = grants

    if auth_type == "INTERNAL" and (not grants or len(grants) == 0):
        return {"success": False, "error": "grants list is required when auth_type=INTERNAL"}

    result = simple_api_call(access, 'POST', '/v1/{project_id}/workspaces', body=body)
    return result


@authenticated_api_call
def ma_workspace_validate_auth(access, workspace_id: str, requests: list):
    """
    验证工作空间权限

    API: POST /v1/{project_id}/workspaces/{workspace_id}/auth

    Args:
        workspace_id: 要验证的工作空间ID (required)
        requests: 权限检查请求列表 (required)
            每个请求格式: {
                "action_id": "random-uuid",  // 用于定位的随机UUID
                "action": "action-name",       // 细粒度的动作名称
                "resource": "resource-id",     // 可选资源标识
                "service_attributes": {}       // 可选服务属性
            }

    Returns:
        每个请求的权限验证结果
    """
    if not workspace_id:
        return {"success": False, "error": "workspace_id is required"}
    if not requests:
        return {"success": False, "error": "requests list is required"}

    for req in requests:
        if "action_id" not in req or "action" not in req:
            return {"success": False, "error": "Each request must have 'action_id' and 'action'"}

    body = {"requests": requests}
    result = simple_api_call(access, 'POST', '/v1/{project_id}/workspaces/{workspace_id}/auth',
                            body=body, workspace_id=workspace_id)
    return result
