#!/usr/bin/env python3

"""查询服务版本模块 - v2版本"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, simple_api_call, Dict, Any

def check_service_id(service_id):
    if not service_id: return "服务ID不能为空"
    return None

def check_version_id(version_id):
    if not version_id: return "版本ID不能为空"
    return None

@authenticated_api_call
def ma_inference_service_get_version(access, service_id: str, version_id: str, **kwargs) -> Dict[str, Any]:
    """查询服务版本详情 - v2版本"""
    checks = [
        (check_service_id(service_id), "service_id"),
        (check_version_id(version_id), "version_id")
    ]

    for check, param in checks:
        if check: return format_api_result(False, error=f"{param}: {check}")

    print(f"  查询服务v2版本详情: {service_id}/{version_id}")

    result = simple_api_call(access, 'GET', '/v2/{project_id}/services/{service_id}/versions/{version_id}', 
                           service_id=service_id, version_id=version_id, query=kwargs if kwargs else None)

    return format_api_result(True, data=result)

@authenticated_api_call
def quick_get_v2_version(access, service_id: str, version_id: str) -> Dict[str, Any]:
    """快速查询v2版本"""
    return ma_inference_service_get_version(access, service_id=service_id, version_id=version_id)

__all__ = ['ma_inference_service_get_version', 'quick_get_v2_version']
