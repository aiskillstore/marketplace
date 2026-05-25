#!/usr/bin/env python3
"""
Lite Server 模块 - list_resource_flavors 函数（增强版）
功能：查询 Lite Server 资源规格列表，支持过滤参数
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, List, Optional
from .common import add_api_reference, build_query_params

@authenticated_api_call
def ma_liteserver_list_resource_flavors(
    access,
    availability_zone: Optional[str] = None,
    arch: Optional[str] = None,
    resource_flavor: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    sort_key: Optional[str] = None,
    sort_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Query list of resource flavors for Lite Server with optional filters.
    Args:
        availability_zone: 可用区名称 (optional) - 过滤指定可用区的规格
        arch: 架构类型 (optional) - X86: X86架构, ARM: ARM架构
        resource_flavor: 资源规格名称 (optional) - 过滤指定规格
        limit: 每页数量 (optional) - 默认10，最大100
        offset: 偏移量 (optional) - 默认0
        sort_key: 排序键 (optional) - 支持: flavor_id, resource_flavor_id, name
        sort_dir: 排序方向 (optional) - ASC: 升序, DESC: 降序
    Returns:
        List of resource flavors with availability info
    """
    query = build_query_params(
        availability_zone=availability_zone,
        arch=arch,
        resource_flavor=resource_flavor,
        limit=limit,
        offset=offset,
        sort_key=sort_key,
        sort_dir=sort_dir
    )
    result = access.sdk().execute(lambda s: make_api_call(
        s,
        'GET',
        '/v1/{project_id}/dev-servers/resource-flavors',
        query=query
    ))
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.30 ListDevServerResourceflavors (Page 1779)")

from common_module.api_helper import make_api_call
__all__ = ['ma_liteserver_list_resource_flavors']
