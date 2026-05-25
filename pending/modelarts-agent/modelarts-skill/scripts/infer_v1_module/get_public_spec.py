#!/usr/bin/env python3
"""
Inference模块 - 查询公共池规格
功能：查询公共池可用的资源规格
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from infer_v1_module._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, make_api_call, Dict, Any


@authenticated_api_call
def ma_old_inference_get_public_specs(
    access,
    **kwargs
) -> Dict[str, Any]:
    """
    查询公共池可用规格
    Returns:
        公共池规格列表
    示例:
        >>> from infer_v1_module import ma_old_inference_get_public_specs
        >>> result = ma_old_inference_get_public_specs()
        >>> if result['success']:
        ...     specs = result['data'].get('specifications', [])
        ...     for s in specs:
        ...         print(s['specification'])
    """
    print(f"  查询公共池规格")

    result = access.sdk().execute(lambda s: make_api_call(
        s,
        'GET',
        '/v1/{project_id}/services/specifications',
    ))

    return format_api_result(True, data=result)


ma_old_inference_get_specifications = ma_old_inference_get_public_specs

__all__ = ['ma_old_inference_get_public_specs', 'ma_old_inference_get_specifications']
