#!/usr/bin/env python3
"""
Inference模块 - 封装获取鉴权token模块
功能：封装获取token模块
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from infer_v1_module._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, make_api_call, Dict, Any

@authenticated_api_call
def make_token_auth_request(
    access,
    service_id: str, **kwargs
) -> Dict[str, Any]:
    """
    推理服务操作
        Args:
            service_id: 操作目标（必填）
            **kwargs: 其他配置参数
        Returns:
            操作结果
        示例:
            >>> from infer1.0_module import make_token_auth_request
            >>> result = make_token_auth_request('service-xxx-xxx-xxx')
            >>> if result['success']:
            ...     print("操作成功")
    """
    if not service_id:
        return format_api_result(False, error="service_id is required")

    print(f"  操作推理服务: {service_id}")

    result = access.sdk().execute(lambda s: make_api_call(
        s,
        'POST',
        '/v1/{project_id}/services/{service_id}',
    ))

    return format_api_result(True, data=result)


__all__ = ['make_token_auth_request']
