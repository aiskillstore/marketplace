#!/usr/bin/env python3
"""
NodePool模块 - 启动引导与依赖注入
"""

import os
import sys
from typing import Dict, Any, List, Optional, Callable
from functools import wraps

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'common_module'))

from .common import (
    ensure_authentication,
    format_api_result,
    authenticated_api_call,
    simple_api_call,
    make_api_call,
    access_api_call
)

__all__ = [
    'ensure_authentication',
    'format_api_result',
    'authenticated_api_call',
    'simple_api_call',
    'make_api_call',
    'access_api_call',
    'os',
    'sys',
    'Dict',
    'Any',
    'List',
    'Optional',
    'Callable',
    'wraps'
]