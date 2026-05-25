#!/usr/bin/env python3




"""消除重复导入代码，统一使用 common_module"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'common_module'))

try:
    from common_module import (
        ensure_authentication,
        format_api_result,
        authenticated_api_call,
        simple_api_call,
        make_api_call
    )
except ImportError as e:
    sys.stderr.write(f"公共模块导入警告: {e}\n")
    ensure_authentication = None
    format_api_result = None
    authenticated_api_call = None
    simple_api_call = None
    make_api_call = None

__all__ = [
    'ensure_authentication',
    'format_api_result',
    'authenticated_api_call',
    'simple_api_call',
    'make_api_call',
    'os',
    'sys',
    'Dict',
    'Any',
    'List'
]
