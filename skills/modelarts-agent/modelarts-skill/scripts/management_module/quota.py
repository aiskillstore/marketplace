#!/usr/bin/env python3
"""
配额管理模块

项目资源配额查询功能
"""

import sys
sys.path.insert(0, '.')

from common_module.api_helper import authenticated_api_call, simple_api_call


@authenticated_api_call
def ma_quota_list(access):
    """
    列出项目所有资源配额

    API: GET /v1/{project_id}/quotas

    Returns:
        所有资源配额列表，包含已使用/可用数量
    """
    result = simple_api_call(access, 'GET', '/v1/{project_id}/quotas')
    return result
