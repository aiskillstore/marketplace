#!/usr/bin/env python3
"""
Notebook模块 - 公共函数文件
"""

import sys
sys.path.insert(0, '.')

from common_module import (
    ensure_authentication,
    format_api_result,
    authenticated_api_call,
    simple_api_call
)

__all__ = [
    'ensure_authentication',
    'format_api_result',
    'authenticated_api_call',
    'simple_api_call'
]