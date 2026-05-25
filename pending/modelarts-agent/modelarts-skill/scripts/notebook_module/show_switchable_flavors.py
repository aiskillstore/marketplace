#!/usr/bin/env python3
"""
Notebook模块 - show_switchable_flavors函数
功能：查询Notebook可切换的规格列表
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def show_switchable_flavors(notebook_id: str, limit: int = None, offset: int = 0, 
                            sort_key: str = None, sort_dir: str = "DESC") -> Dict[str, Any]:
    """
    查询 Notebook 实例可切换的计算规格列表。

    API 路径: GET /v1/{project_id}/notebooks/{id}/flavors

    Args:
        notebook_id: Notebook 实例 ID (必填)
        limit: 每页显示数量 (可选，默认不限制)
        offset: 分页偏移量 (可选，默认 0)
        sort_key: 排序字段，多字段用逗号分隔 (可选)
        sort_dir: 排序方式，"ASC" 或 "DESC" (可选，默认 "DESC")

    Returns:
        可切换的规格列表

    示例:
        >>> from notebook_module import show_switchable_flavors
        >>> result = show_switchable_flavors('notebook-id')
        >>> if result['success']:
        ...     for flavor in result['data']['data']:
        ...         print(flavor['name'], flavor['billing_item'])
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        if not notebook_id:
            return format_api_result(False, error="notebook_id is required")

        query = {"offset": offset, "sort_dir": sort_dir}
        if limit:
            query["limit"] = limit
        if sort_key:
            query["sort_key"] = sort_key

        print(f"  查询可切换规格列表: {notebook_id}")

        result = simple_api_call(
            access,
            'GET',
            '/v1/{project_id}/notebooks/{notebook_id}/flavors',
            query=query,
            notebook_id=notebook_id
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"查询可切换规格时发生异常: {e}")


__all__ = ['show_switchable_flavors']