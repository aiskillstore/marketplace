#!/usr/bin/env python3
"""
资源标签管理模块

资源池标签查询、获取等功能
"""

import sys
sys.path.insert(0, '.')

from common_module.api_helper import authenticated_api_call, simple_api_call


@authenticated_api_call
def ma_tag_list_pool(access):
    """
    列出资源池所有标签

    API: GET /v1/{project_id}/pools/tags

    Returns:
        所有资源池标签及其使用次数
    """
    result = simple_api_call(access, 'GET', '/v1/{project_id}/pools/tags')
    return result


@authenticated_api_call
def ma_tag_get_pool(access, pool_name: str):
    """
    获取指定资源池的所有标签

    API: GET /v1/{project_id}/pools/{pool_name}/tags

    Args:
        pool_name: 资源池名称

    Returns:
        该资源池的标签列表
    """
    if not pool_name:
        return {"success": False, "error": "pool_name is required"}

    result = simple_api_call(access, 'GET', '/v1/{project_id}/pools/{pool_name}/tags',
                            pool_name=pool_name)
    return result
