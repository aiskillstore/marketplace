#!/usr/bin/env python3
"""
Inference模块 - ma_old_inference_service_full_update函数
功能：更新推理服务
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from infer_v1_module._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, make_api_call, Dict, Any


@authenticated_api_call
def ma_old_inference_service_full_update(
    access,
    service_id: str, **kwargs
) -> Dict[str, Any]:
    """
    更新推理服务
        Args:
            service_id: 更新目标（必填）
            **kwargs: 其他配置参数
        Returns:
            更新结果
        示例:
            >>> from infer1.0_module import ma_old_inference_service_full_update
            >>> result = ma_old_inference_service_full_update('service-xxx-xxx-xxx')
            >>> if result['success']:
            ...     print("更新成功")
    """
    if not service_id:
        return format_api_result(False, error="service_id is required")

    print(f"  更新推理服务: {service_id}")

    result = access.sdk().execute(lambda s: make_api_call(
        s,
        'PATCH',
        '/v1/{project_id}/services/{service_id}',
    ))

    return format_api_result(True, data=result)


__all__ = ['ma_old_inference_service_full_update']
