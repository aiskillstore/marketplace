#!/usr/bin/env python3
"""
Notebook模块 - list_practices函数
功能：获取实践列表
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def list_practices(limit: int = 10, offset: int = 0, practice_id: str = None,
                   sort_key: str = None, sort_dir: str = "DESC") -> Dict[str, Any]:
    """
    查询 Notebook 实践案例列表。

    API 路径: GET /v1/{project_id}/notebooks/practices

    Args:
        limit: 每页数量 (可选，默认 10，范围 1-100)
        offset: 分页偏移量 (可选，默认 0)
        practice_id: 实践案例 ID (可选，UUID 格式)
        sort_key: 排序字段，多字段用逗号分隔 (可选)
        sort_dir: 排序方式，"ASC" 或 "DESC" (可选，默认 "DESC")

    Returns:
        实践案例列表

    示例:
        >>> from notebook_module import list_practices
        >>> result = list_practices()
        >>> if result['success']:
        ...     for practice in result['data']['data']:
        ...         print(practice['name'])
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        query = {"limit": limit, "offset": offset, "sort_dir": sort_dir}
        if practice_id:
            query["practice_id"] = practice_id
        if sort_key:
            query["sort_key"] = sort_key

        print(f"  获取实践列表")

        result = simple_api_call(
            access,
            'GET',
            '/v1/{project_id}/notebooks/practices',
            query=query
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"获取实践列表时发生异常: {e}")


__all__ = ['list_practices']