#!/usr/bin/env python3

"""更新推理服务模块 - v2版本"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, simple_api_call, Dict, Any, List

def check_service_id(service_id):
    if not service_id: return "服务ID不能为空"
    return None

def build_v2_update_body(version, instance_count, description, tags):
    """构建v2更新请求体"""
    body = {}

    if version:
        body["version"] = version

    if instance_count is not None:
        body["instance_count"] = instance_count

    if description is not None:
        body["description"] = description

    if tags is not None:
        body["tags"] = tags

    return body

@authenticated_api_call
def ma_inference_service_update(access, service_id: str, version: str = None, 
    instance_count: int = None, description: str = None, tags: List[Dict[str, str]] = None, 
    **kwargs) -> Dict[str, Any]:
    """更新推理服务配置 - v2版本"""
    check = check_service_id(service_id)
    if check: return format_api_result(False, error=check)

    if version is None and instance_count is None and description is None and tags is None:
        return format_api_result(False, error="没有提供更新参数")

    print(f"  更新推理服务v2: {service_id}")

    body = build_v2_update_body(version, instance_count, description, tags)

    result = simple_api_call(access, 'PUT', '/v2/{project_id}/services/{service_id}', 
                           body=body, service_id=service_id)

    return format_api_result(True, data=result)

@authenticated_api_call
def quick_update_v2_service(access, service_id: str, version: str) -> Dict[str, Any]:
    """快速更新v2服务版本"""
    return ma_inference_service_update(access, service_id=service_id, version=version)

__all__ = ['ma_inference_service_update', 'quick_update_v2_service']
