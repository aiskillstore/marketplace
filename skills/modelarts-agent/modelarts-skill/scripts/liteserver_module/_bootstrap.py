#!/usr/bin/env python3
"""
Lite Server 模块 - 统一引导文件
功能：消除重复导入代码，统一设置路径
"""

import os
import sys
from typing import Dict, Any, List, Optional
# 统一设置路径 - 只在这里做一次
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'common_module'))
# 导入通用公共函数
from common_module import (
    ensure_authentication,
    format_api_result,
    authenticated_api_call,
    simple_api_call,
    make_api_call
)
# 导入 liteserver_module 特有的函数
try:
    from .common import (
        validate_dev_server_params,
        format_paginated_result,
        add_api_reference,
        validate_required_params,
        build_request_body,
        build_query_params,
        get_available_flavor,
        get_image_by_flavor,
        execute_hyperinstance_operation
    )
except ImportError:
    # 第一次创建时 common.py 可能还不存在
    validate_dev_server_params = None
    format_paginated_result = None
    add_api_reference = None
    validate_required_params = None
    build_request_body = None
    build_query_params = None
    get_available_flavor = None
    get_image_by_flavor = None
    execute_hyperinstance_operation = None
# 导出所有公共函数
__all__ = [
    'ensure_authentication',
    'format_api_result',
    'authenticated_api_call',
    'simple_api_call',
    'make_api_call',
    'validate_dev_server_params',
    'format_paginated_result',
    'add_api_reference',
    'validate_required_params',
    'build_request_body',
    'build_query_params',
    'get_available_flavor',
    'get_image_by_flavor',
    'execute_hyperinstance_operation',
    'os',
    'sys',
    'Dict',
    'Any',
    'List',
    'Optional'
]
