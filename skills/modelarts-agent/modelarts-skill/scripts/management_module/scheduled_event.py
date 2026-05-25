#!/usr/bin/env python3
"""
计划事件管理模块

计划事件授权、列表查询等功能
"""

import sys
sys.path.insert(0, '.')

from common_module.api_helper import authenticated_api_call, simple_api_call


@authenticated_api_call
def ma_scheduled_event_accept(access, event_id: str,
                               notBefore: str = None,
                               workspaceId: str = None):
    """
    授权/接受计划事件

    API: POST /v1/{project_id}/scheduled-events/{event_id}/accept

    Args:
        event_id: 要授权的计划事件ID (required)
        notBefore: 计划执行开始时间 (optional)
            格式: yyyy-MM-ddTHH:mm:ssZ
            必须晚于当前时间, 默认立即执行
        workspaceId: 工作空间ID (optional, 默认0)

    Returns:
        授权结果
    """
    if not event_id:
        return {"success": False, "error": "event_id is required"}

    body = {}
    if notBefore:
        body["notBefore"] = notBefore

    query = {}
    if workspaceId:
        query["workspaceId"] = workspaceId

    result = simple_api_call(access, 'POST',
                            '/v1/{project_id}/scheduled-events/{event_id}/accept',
                            body=body, query=query, event_id=event_id)
    return result


@authenticated_api_call
def ma_scheduled_event_list(access, status: str = None,
                            limit: int = 100, offset: int = 0):
    """
    列出项目所有计划事件

    API: GET /v1/{project_id}/scheduled-events

    Args:
        status: 按状态过滤 (optional)
        limit: 每页最大结果数 (default: 100)
        offset: 分页偏移量 (default: 0)

    Returns:
        带分页的计划事件列表
    """
    query = {}
    if status:
        query["status"] = status
    if limit != 100:
        query["limit"] = limit
    if offset > 0:
        query["offset"] = offset

    result = simple_api_call(access, 'GET', '/v1/{project_id}/scheduled-events', query=query)
    return result
