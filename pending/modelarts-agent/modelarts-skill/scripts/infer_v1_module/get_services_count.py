#!/usr/bin/env python3
"""
Inference模块 - 获取服务数量模块
功能：查询服务数量
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from infer_v1_module._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, make_api_call, Dict, Any


@authenticated_api_call
def get_old_service_count(
    access,
    workspace_id: str = '0', **kwargs
) -> Dict[str, Any]:
    """
    查询服务数量
        Args:
            workspace_id: 工作空间ID（可选，默认: "0"）
            **kwargs: 其他配置参数
        Returns:
            查询数量结果
        示例:
            >>> from infer1.0_module import get_old_service_count
            >>> result = get_old_service_count()
            >>> if result['success']:
            ...     print("查询数量成功")
    """
    print(f"  查询数量推理服务")

    result = access.sdk().execute(lambda s: make_api_call(
        s,
        'GET',
        '/v1/{project_id}/services/count',
        query={'workspace_id': workspace_id}
    ))

    return format_api_result(True, data=result)


__all__ = ['get_old_service_count']
