#!/usr/bin/env python3
"""
Lite Server 模块 - list_images 函数（增强版）
功能：查询 Lite Server 镜像列表，支持按规格过滤
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, List, Optional
from .common import add_api_reference, build_query_params

@authenticated_api_call
def ma_liteserver_list_images(
    access,
    flavor: Optional[str] = None,
    resource_flavor: Optional[str] = None,
    arch: Optional[str] = None,
    os_type: Optional[str] = None,
    image_id: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    sort_key: Optional[str] = None,
    sort_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Query list of images for Lite Server with optional filters.
    Args:
        flavor: 规格名称 (optional) - 过滤支持指定规格的镜像
        resource_flavor: 资源规格名称 (optional) - 过滤支持指定资源规格的镜像
        arch: 架构类型 (optional) - X86: X86架构, ARM: ARM架构
        os_type: 操作系统类型 (optional) - Linux/Windows
        image_id: 镜像ID (optional) - 过滤指定镜像
        limit: 每页数量 (optional) - 默认10，最大100
        offset: 偏移量 (optional) - 默认0
        sort_key: 排序键 (optional) - 支持: image_id, name
        sort_dir: 排序方向 (optional) - ASC: 升序, DESC: 降序
    Returns:
        List of images
    """
    query = build_query_params(
        flavor=flavor,
        resource_flavor=resource_flavor,
        arch=arch,
        os_type=os_type,
        image_id=image_id,
        limit=limit,
        offset=offset,
        sort_key=sort_key,
        sort_dir=sort_dir
    )
    result = access.sdk().execute(lambda s: make_api_call(
        s,
        'GET',
        '/v1/{project_id}/dev-servers/images',
        query=query
    ))
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.34 ListDevServerImages (Page 1799)")

from common_module.api_helper import make_api_call
__all__ = ['ma_liteserver_list_images']
