#!/usr/bin/env python3
"""
Inference模块 - 更新推理服务模块
功能：更新推理服务参数
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from infer_v1_module._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, simple_api_call, Dict, Any

@authenticated_api_call
def ma_old_inference_service_update(access, service_id: str, update_body: Dict = None, **kwargs) -> Dict[str, Any]:
    if not service_id: return format_api_result(False, error="service_id is required")
    print(f"  更新推理服务: {service_id}")
    result = simple_api_call(access, 'PATCH', '/v1/{project_id}/services/{service_id}', body=update_body or {}, service_id=service_id)
    return format_api_result(True, data=result)

__all__ = ['ma_old_inference_service_update']
