#!/usr/bin/env python3
"""
Inference模块 - 获取API断点工具模块
功能：获取API端点Endpoint
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from infer_v1_module._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, make_api_call, Dict, Any


@authenticated_api_call
def getapiendpoint(
    access,
    service_id: str, **kwargs
) -> Dict[str, Any]:
    """
    查询推理服务
        Args:
            service_id: 查询目标（必填）
            **kwargs: 其他配置参数
        Returns:
            查询结果
        示例:
            >>> from infer1.0_module import getapiendpoint
            >>> result = getapiendpoint('service-xxx-xxx-xxx')
            >>> if result['success']:
            ...     print("查询成功")
    """
    if not service_id:
        return format_api_result(False, error="service_id is required")

    print(f"  查询推理服务: {service_id}")

    result = access.sdk().execute(lambda s: make_api_call(
        s,
        'GET',
        '/v1/{project_id}/services/{service_id}',
    ))

    return format_api_result(True, data=result)


__all__ = ['getapiendpoint']
