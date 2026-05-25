#!/usr/bin/env python3
"""
Notebook模块 - renew_lease函数
功能：更新Notebook租约
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def renew_lease(notebook_id: str, duration: int = 3600000, type: str = "TIMING") -> Dict[str, Any]:
    """
    续订 Notebook 实例的租约（自动停止时长）。

    API 路径: PATCH /v1/{project_id}/notebooks/{id}/lease

    Args:
        notebook_id: Notebook 实例 ID (必填)
        duration: 续订时长，单位毫秒，范围 3600000-259200000 (可选，默认 1小时)
        type: 自动停止类型，"TIMING"（定时停止）或 "IDLE"（空闲停止） (可选，默认 "TIMING")

    Returns:
        续订结果

    示例:
        >>> from notebook_module import renew_lease, show_lease
        >>> # 续借2小时
        >>> result = renew_lease('notebook-id', duration=7200000)
        >>> if result['success']:
        ...     print("续借成功")
        >>> # 查询更新后的租期
        >>> show_lease('notebook-id')
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        if not notebook_id:
            return format_api_result(False, error="notebook_id is required")

        body = {
            "duration": duration,
            "type": type
        }

        print(f"  续订Notebook租约: {notebook_id}，时长={duration}ms")

        result = simple_api_call(
            access,
            'PATCH',
            '/v1/{project_id}/notebooks/{notebook_id}/lease',
            body=body,
            notebook_id=notebook_id
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"续订租约时发生异常: {e}")


__all__ = ['renew_lease']