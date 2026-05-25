#!/usr/bin/env python3

"""查询服务事件模块 - v2版本"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, simple_api_call, Dict, Any

def check_service_id(service_id):
    if not service_id: return "服务ID不能为空"
    return None

def check_limit(limit):
    if not 1 <= limit <= 1000: return "limit必须在1-1000之间"
    return None

def check_offset(offset):
    if offset < 0: return "offset不能为负数"
    return None

@authenticated_api_call
def ma_inference_service_get_events(access, service_id: str, limit: int = 50, offset: int = 0, **kwargs) -> Dict[str, Any]:
    """查询服务事件 - v2版本"""
    checks = [
        (check_service_id(service_id), "service_id"),
        (check_limit(limit), "limit"),
        (check_offset(offset), "offset")
    ]

    for check, param in checks:
        if check: return format_api_result(False, error=f"{param}: {check}")

    print(f"  查询服务v2事件: {service_id}, limit={limit}, offset={offset}")

    query = {"limit": limit, "offset": offset}
    if kwargs:
        query.update(kwargs)

    result = simple_api_call(access, 'GET', '/v2/{project_id}/services/{service_id}/events', 
                           service_id=service_id, query=query)

    return format_api_result(True, data=result)

@authenticated_api_call
def quick_get_v2_events(access, service_id: str) -> Dict[str, Any]:
    """快速查询v2服务事件"""
    return ma_inference_service_get_events(access, service_id=service_id, limit=20)

__all__ = ['ma_inference_service_get_events', 'quick_get_v2_events']
