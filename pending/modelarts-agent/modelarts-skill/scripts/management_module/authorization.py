#!/usr/bin/env python3
"""
授权管理模块

授权列表、添加、删除、创建委托等功能
"""

import sys
sys.path.insert(0, '.')

from common_module.api_helper import authenticated_api_call, simple_api_call


@authenticated_api_call
def ma_authorization_list(access):
    """
    列出所有授权

    API: GET /v2/{project_id}/authorizations

    Returns:
        所有授权列表，包含user_id和角色
    """
    result = simple_api_call(access, 'GET', '/v2/{project_id}/authorizations')
    return result


@authenticated_api_call
def ma_authorization_add(access, content: str,
                         user_id: str = None,
                         type: str = "AGENCY",
                         secret_key: str = None,
                         user_name: str = None,
                         user_type: str = "IAM"):
    """
    添加授权

    API: POST /v2/{project_id}/authorizations

    Args:
        content: 授权内容 (required)
            - type=AGENCY时: 委托名称
            - type=CREDENTIAL时: 访问密钥ID (AK)
        user_id: 用户ID (IAM/GRANT/ALL-USERS类型时必需)
            - user_id为"all"时表示授权所有IAM用户
        type: 授权类型 (optional, 默认 AGENCY)
            - AGENCY: 委托
            - CREDENTIAL: 访问密钥 (AK/SK)
        secret_key: 秘密访问密钥 (SK) (type=CREDENTIAL时必需)
        user_name: 用户名 (user_type=FEDERATE时必需)
        user_type: 授权对象类型 (optional, 默认 IAM)
            - IAM: IAM子用户, 需要user_id
            - FEDERATE: 联邦用户, 需要user_name
            - GRANT: 被委托用户, 需要user_id
            - ALL-USERS: 所有用户, 需要user_id="all"

    Returns:
        添加授权结果
    """
    if not content:
        return {"success": False, "error": "content is required"}

    if type == "CREDENTIAL" and not secret_key:
        return {"success": False, "error": "secret_key is required when type=CREDENTIAL"}

    if user_type == "FEDERATE" and not user_name:
        return {"success": False, "error": "user_name is required when user_type=FEDERATE"}

    if user_type in ["IAM", "GRANT", "ALL-USERS"] and not user_id:
        return {"success": False, "error": f"user_id is required when user_type={user_type}"}

    body = {"content": content}

    if user_id is not None:
        body["user_id"] = user_id
    if type is not None:
        body["type"] = type
    if secret_key is not None:
        body["secret_key"] = secret_key
    if user_name is not None:
        body["user_name"] = user_name
    if user_type is not None:
        body["user_type"] = user_type

    result = simple_api_call(access, 'POST', '/v2/{project_id}/authorizations', body=body)
    return result


@authenticated_api_call
def ma_authorization_delete(access, user_id: str = None):
    """
    删除授权

    API: DELETE /v2/{project_id}/authorizations

    Args:
        user_id: 要删除的用户ID (optional)
            - user_id="all"时删除所有IAM用户的授权
            - 不提供时删除...

    Returns:
        删除结果
    """
    query = {}
    if user_id is not None:
        query["user_id"] = user_id

    result = simple_api_call(access, 'DELETE', '/v2/{project_id}/authorizations', query=query)
    return result


@authenticated_api_call
def ma_authorization_agency_create(access, agency_name_suffix: str = None):
    """
    创建IAM委托授权

    API: POST /v2/{project_id}/agency

    Args:
        agency_name_suffix: 委托名称后缀 (optional)
            - 前缀固定为 'ma_agency'
            - 后缀为 'iam-user01' 时, 委托名称为 'ma_agency_iam-user01'
            - 为空时委托名称为 'ma_agency'
            - 长度 <= 50字符

    Returns:
        委托创建结果
    """
    body = {}
    if agency_name_suffix is not None:
        body["agency_name_suffix"] = agency_name_suffix

    result = simple_api_call(access, 'POST', '/v2/{project_id}/agency', body=body)
    return result
