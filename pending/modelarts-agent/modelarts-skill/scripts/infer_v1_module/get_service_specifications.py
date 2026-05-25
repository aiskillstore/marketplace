#!/usr/bin/env python3
"""
Inference模块 - 查询推理服务可用规格
功能：查询可用规格
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from infer_v1_module._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, make_api_call, Dict, Any


@authenticated_api_call
def ma_old_inference_get_specifications(
    access,
    **kwargs
) -> Dict[str, Any]:
    """
    查询可用规格
        Args:
            **kwargs: 其他配置参数
        Returns:
            查询规格结果
        示例:
            >>> from infer1.0_module import ma_old_inference_get_specifications
            >>> result = ma_old_inference_get_specifications()
            >>> if result['success']:
            ...     print("查询规格成功")
    """
    print(f"  查询规格推理服务")

    result = access.sdk().execute(lambda s: make_api_call(
        s,
        'GET',
        '/v1/{project_id}/services/specifications',
    ))

    return format_api_result(True, data=result)


__all__ = ['ma_old_inference_get_specifications']
