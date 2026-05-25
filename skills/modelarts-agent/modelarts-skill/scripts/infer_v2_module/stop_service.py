#!/usr/bin/env python3

"""停止推理服务模块 - v2版本"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, simple_api_call, Dict, Any

def check_service_id(service_id):
    if not service_id: return "服务ID不能为空"
    return None

@authenticated_api_call
def ma_inference_service_stop(access, service_id: str, **kwargs) -> Dict[str, Any]:
    """停止推理服务 - v2版本"""
    check = check_service_id(service_id)
    if check: return format_api_result(False, error=check)

    print(f"  停止推理服务v2: {service_id}")

    result = simple_api_call(access, 'POST', '/v2/{project_id}/services/{service_id}/stop', 
                           service_id=service_id, query=kwargs if kwargs else None)

    return format_api_result(True, data=result)

@authenticated_api_call
def quick_stop_v2_service(access, service_id: str) -> Dict[str, Any]:
    """快速停止v2服务"""
    return ma_inference_service_stop(access=access, service_id=service_id)

__all__ = ['ma_inference_service_stop', 'quick_stop_v2_service']
