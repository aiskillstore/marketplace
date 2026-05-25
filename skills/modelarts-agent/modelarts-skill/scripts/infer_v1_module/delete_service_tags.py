#!/usr/bin/env python3
"""
Inference模块 - ma_old_inference_service_delete_tags函数
功能：删除服务标签
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from infer_v1_module._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, make_api_call, Dict, Any


@authenticated_api_call
def ma_old_inference_service_delete_tags(
    access,
    service_id: str, workspace_id: str = '0', **kwargs
) -> Dict[str, Any]:
    """
    删除服务标签
        Args:
            service_id: 删除标签目标（必填）
            workspace_id: 工作空间ID（可选，默认: "0"）
            **kwargs: 其他配置参数
        Returns:
            删除标签结果
        示例:
            >>> from infer1.0_module import ma_old_inference_service_delete_tags
            >>> result = ma_old_inference_service_delete_tags('service-xxx-xxx-xxx')
            >>> if result['success']:
            ...     print("删除标签成功")
    """
    if not service_id:
        return format_api_result(False, error="service_id is required")

    print(f"  删除标签推理服务: {service_id}")

    result = access.sdk().execute(lambda s: make_api_call(
        s,
        'DELETE',
        '/v1/{project_id}/services/{service_id}/tags',
        query={'workspace_id': workspace_id}
    ))

    return format_api_result(True, data=result)


__all__ = ['ma_old_inference_service_delete_tags']
