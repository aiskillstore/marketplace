#!/usr/bin/env python3
"""
Pool模块 - list_os_events函数
功能：列出 OS 事件
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def list_os_events(access, resource: str, name: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    """
    列出 OS 事件

    Args:
        resource: 资源类型（必填），如 "pools"
        name: 资源ID（必填），如资源池ID
        limit: 最大返回数量（可选）
        offset: 分页偏移量（可选）


    调用经验:
        - 必须同时提供 resource 和 name 两个参数
        - resource 可选值: 'pools'
        - name 是资源池 ID
        - 事件按照时间倒序排列，最新的在前
    
    注意事项:
        - 不传递参数会返回 400 错误
        - 事件只保留最近一段时间的记录

    Returns:
        事件列表
    """
    if not resource:
        return format_api_result(False, error="resource is required")
    if not name:
        return format_api_result(False, error="name is required")

    result = access_api_call(
        access,
        "GET",
        "/v1/{project_id}/events",
        query={"resource": resource, "name": name, "limit": limit, "offset": offset}
    )

    return format_api_result(True, data=result)


__all__ = ["list_os_events"]