#!/usr/bin/env python3
"""
Inference模块 - ma_old_inference_service_create_tags函数
功能：创建服务标签
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from infer_v1_module._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, make_api_call, Dict, Any


@authenticated_api_call
def ma_old_inference_service_create_tags(
    access,
    service_id: str, tags: list = None, workspace_id: str = '0', **kwargs
) -> Dict[str, Any]:
    """
    创建服务标签
        Args:
            service_id: 创建标签目标（必填）
            tags: 标签列表（可选）
            workspace_id: 工作空间ID（可选，默认: "0"）
            **kwargs: 其他配置参数
        Returns:
            创建标签结果
        示例:
            >>> from infer1.0_module import ma_old_inference_service_create_tags
            >>> result = ma_old_inference_service_create_tags('service-xxx-xxx-xxx')
            >>> if result['success']:
            ...     print("创建标签成功")
    """
    if not service_id:
        return format_api_result(False, error="service_id is required")

    print(f"  创建标签推理服务: {service_id}")

    result = access.sdk().execute(lambda s: make_api_call(
        s,
        'POST',
        '/v1/{project_id}/services/{service_id}/tags',
        body={'tags': tags}, query={'workspace_id': workspace_id}
    ))

    return format_api_result(True, data=result)


__all__ = ['ma_old_inference_service_create_tags']
