#!/usr/bin/env python3
"""
NodePool模块 - 公共函数文件
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


__all__ = [
    'ensure_authentication',
    'format_api_result',
    'authenticated_api_call',
    'make_api_call',
    'simple_api_call',
    'access_api_call'
]