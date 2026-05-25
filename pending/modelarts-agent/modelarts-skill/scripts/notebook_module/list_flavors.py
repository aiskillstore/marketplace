#!/usr/bin/env python3
"""
Notebook模块 - list_flavors函数
功能：列出可用的计算规格
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def list_flavors(category: str = None, type: str = None, feature: str = "NOTEBOOK",
                 flavor_type: str = None, limit: int = None, offset: int = 0,
                 sort_key: str = None, sort_dir: str = "DESC") -> Dict[str, Any]:
    """
    查询 Notebook 实例可用的计算规格列表。

    API 路径: GET /v1/{project_id}/notebooks/flavors

    Args:
        category: 处理器类型，"CPU"/"GPU"/"ASCEND" (可选)
        type: 集群类型，"MANAGED"（公共集群）或 "DEDICATED"（专属集群） (可选)
        feature: 特性名称，默认 "NOTEBOOK" (可选，默认 "NOTEBOOK")
        flavor_type: 资源类型，"ASCEND_SNT9"/"ASCEND_SNT9B"/"ASCEND_SNT3" (可选)
        limit: 每页显示数量 (可选，默认不限制)
        offset: 分页偏移量 (可选，默认 0)
        sort_key: 排序字段，多字段用逗号分隔 (可选)
        sort_dir: 排序方式，"ASC" 或 "DESC" (可选，默认 "DESC")

    Returns:
        可用规格列表

    示例:
        >>> from notebook_module import list_flavors
        >>> # 查询所有CPU规格
        >>> result = list_flavors(category='CPU')
        >>> if result['success']:
        ...     for f in result['data']['data']:
        ...         print(f['name'], f['billing_item'])
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        query = {"feature": feature, "offset": offset, "sort_dir": sort_dir}
        if category:
            query["category"] = category
        if type:
            query["type"] = type
        if flavor_type:
            query["flavor_type"] = flavor_type
        if limit:
            query["limit"] = limit
        if sort_key:
            query["sort_key"] = sort_key

        print(f"  获取可用的计算规格列表")

        result = simple_api_call(
            access,
            'GET',
            '/v1/{project_id}/notebooks/flavors',
            query=query
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"获取规格列表时发生异常: {e}")


__all__ = ['list_flavors']