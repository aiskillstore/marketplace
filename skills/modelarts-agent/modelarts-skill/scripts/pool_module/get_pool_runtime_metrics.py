#!/usr/bin/env python3
"""
Pool模块 - get_pool_runtime_metrics函数
功能：获取资源池运行时指标
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def get_pool_runtime_metrics(access) -> Dict[str, Any]:
    """
    获取资源池运行时指标
    
        Args:
            无
    
        Returns:
            运行时指标数据
    
        示例:
            >>> from pool_module import get_pool_runtime_metrics
            >>> result = get_pool_runtime_metrics()
            >>> if result['success']:
            ...     metrics = result['data']
            ...     print(metrics)
    """
    

    result = access_api_call(
        access,
        "GET",
        "/v2/{project_id}/metrics/runtime/pools",
        query={}
    )

    return format_api_result(True, data=result)


__all__ = ["get_pool_runtime_metrics"]