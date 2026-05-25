#!/usr/bin/env python3

"""检测当前区域模块 - v2版本"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, simple_api_call, Dict, Any

@authenticated_api_call
def ma_region_detect_current(access, **kwargs) -> Dict[str, Any]:
    """检测当前区域 - v2版本"""
    print("  检测当前区域v2")

    result = simple_api_call(access, 'GET', '/v2/{project_id}/region/detect', 
                           query=kwargs if kwargs else None)

    return format_api_result(True, data=result)

@authenticated_api_call
def quick_detect_v2_region(access) -> Dict[str, Any]:
    """快速检测v2区域"""
    return ma_region_detect_current(access)

__all__ = ['ma_region_detect_current', 'quick_detect_v2_region']
