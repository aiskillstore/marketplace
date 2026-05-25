#!/usr/bin/env python3
"""
公共模块 - 结果处理函数文件
功能：结果处理公共函数
"""

import sys
from typing import Any, Dict

sys.path.insert(0, '.')


def format_api_result(success: bool, data: Any = None, 
                      error: str = None) -> Dict[str, Any]:
    result = {
        "success": success
    }
    
    if success and data is not None:
        result["data"] = data
    
    if not success and error:
        result["error"] = error
    
    return result


__all__ = ['format_api_result']