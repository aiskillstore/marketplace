#!/usr/bin/env python3
"""
Notebook模块 - list_all_notebooks函数
功能：查询所有Notebook实例列表
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def list_all_notebooks(limit: int = 10, offset: int = 0, workspace_id: str = "0") -> Dict[str, Any]:
    """
    查询当前工作空间下所有用户的 Notebook 实例列表。

    与 list_notebooks 的区别：
    - list_notebooks: 只返回当前用户自己创建的实例
    - list_all_notebooks: 返回当前工作空间下所有用户的实例

    API 路径: GET /v1/{project_id}/notebooks/all

    Args:
        limit: 每页数量 (可选，默认 10)
        offset: 分页偏移量 (可选，默认 0)
        workspace_id: 工作空间 ID (可选，默认 "0")

    Returns:
        Notebook 实例列表，包含分页信息
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        query_params = {
            "limit": limit,
            "offset": offset,
            "workspace_id": workspace_id
        }

        print(f"  查询所有Notebook实例列表")

        result = simple_api_call(
            access,
            'GET',
            '/v1/{project_id}/notebooks/all',
            query=query_params
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"查询所有Notebook实例时发生异常: {e}")


__all__ = ['list_all_notebooks']