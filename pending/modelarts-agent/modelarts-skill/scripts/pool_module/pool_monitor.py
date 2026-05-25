#!/usr/bin/env python3
"""
Pool模块 - pool_monitor函数
功能：资源池监控指标
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def pool_monitor(access, pool_name: str, time_range: str = "-1.-1.60") -> Dict[str, Any]:
    """
    获取资源池监控指标
    
        Args:
            pool_name: 资源池 ID（必填）
            time_range: 时间范围（可选，默认: "-1.-1.60"）
    
        Returns:
            监控指标数据
    
        示例:
            >>> from pool_module import pool_monitor
            >>> result = pool_monitor('pool-7923ba1a-338d-4b66-ae96-789cc4fd7da5')
            >>> if result['success']:
            ...     metrics = result['data']
            ...     print(f"CPU使用率: {metrics.get('cpu', {}).get('usage', 0)}%")
    """
    if not pool_name:
        return format_api_result(False, error="pool_name is required")

    result = access_api_call(
        access,
        "GET",
        "/v2/{project_id}/pools/{pool_name}/monitor",
        pool_name=pool_name, query={"time_range": time_range}
    )

    return format_api_result(True, data=result)


__all__ = ["pool_monitor"]