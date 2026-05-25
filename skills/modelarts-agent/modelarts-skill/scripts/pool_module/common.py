#!/usr/bin/env python3
"""
Pool模块 - 公共函数文件
功能：公共导入和工具函数
"""

import sys
from typing import Any, Dict

sys.path.insert(0, '.')

from common_module import (
    ensure_authentication,
    format_api_result,
    authenticated_api_call,
    make_api_call,
    simple_api_call
)

def access_api_call(access, method, path_pattern, body=None, query=None, headers=None, **path_vars):
    return simple_api_call(access, method, path_pattern, body=body, query=query, headers=headers, **path_vars)


def parse_pool_data(raw_data: Any) -> Dict[str, Any]:
    """
    解析资源池数据，统一格式
    """
    if isinstance(raw_data, list):
        pools = raw_data
        total = len(raw_data)
    elif isinstance(raw_data, dict):
        list_field = None
        if "pools" in raw_data and isinstance(raw_data["pools"], list):
            list_field = "pools"
        elif "data" in raw_data and isinstance(raw_data["data"], list):
            list_field = "data"
        elif "items" in raw_data and isinstance(raw_data["items"], list):  # K8s 风格 API
            list_field = "items"
        
        if list_field:
            pools = raw_data[list_field]
            total = raw_data.get("total", raw_data.get("totalItems", len(pools)))
        else:
            pools = []
            total = 0
    else:
        pools = []
        total = 0

    return {
        "pools": pools,
        "total": total
    }


__all__ = [
    'ensure_authentication',
    'format_api_result',
    'authenticated_api_call',
    'make_api_call',
    'parse_pool_data'
]