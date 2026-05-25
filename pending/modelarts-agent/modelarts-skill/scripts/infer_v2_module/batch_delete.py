#!/usr/bin/env python3

"""批量删除推理服务模块 - v2版本"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, simple_api_call, Dict, Any, List

def check_service_ids(service_ids):
    if not service_ids: return "服务ID列表不能为空"
    if not isinstance(service_ids, list): return "service_ids必须是列表"
    if len(service_ids) == 0: return "服务ID列表不能为空"
    return None

@authenticated_api_call
def ma_inference_service_batch_delete(access, service_ids: List[str], **kwargs) -> Dict[str, Any]:
    """批量删除推理服务 - v2版本"""
    check = check_service_ids(service_ids)
    if check: return format_api_result(False, error=check)

    print(f"  批量删除推理服务v2: {len(service_ids)}个服务")

    body = {"service_ids": service_ids}

    result = simple_api_call(access, 'POST', '/v2/{project_id}/services/batch-delete', body=body)

    return format_api_result(True, data=result)

@authenticated_api_call
def quick_batch_delete_v2(access, service_ids: List[str]) -> Dict[str, Any]:
    """快速批量删除v2服务"""
    return ma_inference_service_batch_delete(access=access, service_ids=service_ids)

__all__ = ['ma_inference_service_batch_delete', 'quick_batch_delete_v2']
