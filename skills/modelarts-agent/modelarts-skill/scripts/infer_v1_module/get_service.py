#!/usr/bin/env python3
"""
Inference模块 - 查询推理服务详情
功能：查询推理服务详情
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from infer_v1_module._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, simple_api_call, Dict, Any

@authenticated_api_call
def ma_old_inference_service_get(access, service_id: str, workspace_id: str = "0", **kwargs) -> Dict[str, Any]:
    """查询推理服务详情"""
    if not service_id: return format_api_result(False, error="服务ID不能为空")
    print(f"  查询推理服务详情: {service_id}")
    q = dict(kwargs)
    if workspace_id != "0": q["workspace_id"] = workspace_id
    result = simple_api_call(access, 'GET', '/v1/{project_id}/services/{service_id}', query=q if q else None, service_id=service_id)
    return format_api_result(True, data=result)

@authenticated_api_call
def quick_get_old_service(access, service_id: str) -> Dict[str, Any]:
    """快速查询推理服务"""
    return ma_old_inference_service_get(access=access, service_id=service_id, workspace_id="0")

__all__ = ['ma_old_inference_service_get', 'quick_get_old_service']
