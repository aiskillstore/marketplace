#!/usr/bin/env python3

"""查询服务健康状态模块 - v2版本"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, simple_api_call, Dict, Any

def check_service_id(service_id):
    if not service_id: return "服务ID不能为空"
    return None

@authenticated_api_call
def ma_inference_service_health(access, service_id: str, **kwargs) -> Dict[str, Any]:
    """查询服务健康状态 - v2版本"""
    check = check_service_id(service_id)
    if check: return format_api_result(False, error=check)

    print(f"  查询服务v2健康状态: {service_id}")

    result = simple_api_call(access, 'GET', '/v2/{project_id}/services/{service_id}/health', 
                           service_id=service_id, query=kwargs if kwargs else None)

    return format_api_result(True, data=result)

@authenticated_api_call
def quick_health_v2_service(access, service_id: str) -> Dict[str, Any]:
    """快速查询v2服务健康状态"""
    return ma_inference_service_health(access=access, service_id=service_id)

__all__ = ['ma_inference_service_health', 'quick_health_v2_service']
