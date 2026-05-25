#!/usr/bin/env python3
"""
公共模块 - 初始化文件
功能：导出所有公共函数
"""

import sys

sys.path.insert(0, '.')

__version__ = "1.0.0"

from .auth import ensure_authentication
from .result import format_api_result
from .api_helper import authenticated_api_call, make_api_call, simple_api_call

__all__ = [
    'ensure_authentication',
    'format_api_result',
    'authenticated_api_call',
    'make_api_call',
    'simple_api_call'
]

__description__ = """
公共模块 - 提供认证、API调用、结果处理等公共函数
"""