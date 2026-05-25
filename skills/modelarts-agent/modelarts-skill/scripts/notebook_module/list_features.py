#!/usr/bin/env python3
"""
Notebook模块 - list_features函数
功能：查询Notebook特性开关
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def list_features(feature: str = "NOTEBOOK") -> Dict[str, Any]:
    """
    查询 Notebook 相关特性开关状态。

    API 路径: GET /v1/{project_id}/authoring/features/{feature}

    Args:
        feature: 特性名称，默认 "NOTEBOOK" (可选，默认 "NOTEBOOK")

    Returns:
        特性开关状态列表

    示例:
        >>> from notebook_module import list_features
        >>> result = list_features()
        >>> if result['success']:
        ...     for feat in result['data']['data']:
        ...         print(feat['name'], feat['enabled'])
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        print(f"  查询Notebook特性列表: {feature}")

        result = simple_api_call(
            access,
            'GET',
            '/v1/{project_id}/authoring/features/{feature}',
            feature=feature
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"查询特性列表时发生异常: {e}")


__all__ = ['list_features']