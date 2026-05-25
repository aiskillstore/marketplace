#!/usr/bin/env python3
"""
Inference模块 - 推理服务列表模块
功能：列出所有推理服务
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from infer_v1_module._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, make_api_call, Dict, Any

def build_query(workspace_id, offset, limit, infer_type, status, service_name, **kwargs):
    """构建查询参数"""
    q = {"offset": offset, "limit": limit}
    if workspace_id != "0": q["workspace_id"] = workspace_id
    if infer_type: q["infer_type"] = infer_type
    if status: q["status"] = status
    if service_name: q["service_name"] = service_name
    q.update(kwargs)
    return q

@authenticated_api_call
def ma_old_inference_service_list(access, workspace_id: str = "0", offset: int = 0, limit: int = 100,
                                  infer_type: str = None, status: str = None, service_name: str = None, **kwargs) -> Dict[str, Any]:
    """列表推理服务"""
    print(f"  列表推理服务")
    result = access.sdk().execute(lambda s: make_api_call(s, 'GET', '/v1/{project_id}/services',
        query=build_query(workspace_id, offset, limit, infer_type, status, service_name, **kwargs)))
    return format_api_result(True, data=result)

@authenticated_api_call
def quick_list_old_services(access, limit: int = 10) -> Dict[str, Any]:
    """快速列表推理服务"""
    return ma_old_inference_service_list(workspace_id="0", offset=0, limit=limit)

__all__ = ['ma_old_inference_service_list', 'quick_list_old_services']
