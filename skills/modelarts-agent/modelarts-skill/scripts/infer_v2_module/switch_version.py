#!/usr/bin/env python3

"""切换服务版本模块 - v2版本"""
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
def ma_inference_service_switch_version(access, service_id: str, version_id: str, **kwargs) -> Dict[str, Any]:
    """切换服务版本 - v2版本"""
    checks = [
        (check_service_id(service_id), "service_id"),
        (check_version_id(version_id), "version_id")
    ]

    for check, param in checks:
        if check: return format_api_result(False, error=f"{param}: {check}")

    print(f"  切换服务v2版本: {service_id} -> {version_id}")

    body = {"version_id": version_id}

    result = simple_api_call(access, 'POST', '/v2/{project_id}/services/{service_id}/switch-version', 
                           body=body, service_id=service_id)

    return format_api_result(True, data=result)

@authenticated_api_call
def quick_switch_v2_version(access, service_id: str, version_id: str) -> Dict[str, Any]:
    """快速切换v2版本"""
    return ma_inference_service_switch_version(access, service_id=service_id, version_id=version_id)

__all__ = ['ma_inference_service_switch_version', 'quick_switch_v2_version']
