#!/usr/bin/env python3
"""
Inference模块 - 停止推理服务模块
功能：停止推理服务
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from infer_v1_module._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, simple_api_call, Dict, Any

@authenticated_api_call
def ma_old_inference_service_stop(access, service_id: str, workspace_id: str = '0', **kwargs) -> Dict[str, Any]:
    if not service_id: return format_api_result(False, error="service_id is required")
    print(f"  停止推理服务: {service_id}")
    body = {"status": "stopped", "workspace_id": workspace_id}
    result = simple_api_call(access, 'PUT', '/v1/{project_id}/services/{service_id}', body=body,
                            query={'workspace_id': workspace_id} if workspace_id != '0' else None, service_id=service_id)
    return format_api_result(True, data=result)

__all__ = ['ma_old_inference_service_stop']
