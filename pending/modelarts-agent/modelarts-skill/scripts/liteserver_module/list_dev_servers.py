#!/usr/bin/env python3
"""
Lite Server 模块 - list_dev_servers 函数
功能：查询 Lite Server 实例列表
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, Optional
from .common import format_paginated_result, add_api_reference

@authenticated_api_call
def ma_liteserver_list(
    access,
    owner: Optional[str] = None,
    sort_dir: str = "ASC",
    sort_key: str = "createTime",
    limit: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Query list of Lite Server instances for current user.
    Args:
        owner: 实例归属的用户ID (optional) - 1-64字符，小写字母、数字和中划线；在大账号/有admin权限场景下生效，值通常为当前登录用户ID
        sort_dir: 排序方式 (optional) - ASC: 升序，DESC: 降序 (default: "ASC")
        sort_key: 排序字段 (optional) - createTime: 默认值，创建时间；updateTime: 更新时间 (default: "createTime")
        limit: 每一页的数量 (optional) - 取值范围：0-1024 (default: 10)
        offset: 分页记录的起始位置偏移量 (optional) - 取值范围：0-2147483647 (default: 0)
    Returns:
        List of Lite Server instances with pagination info (current, data, pages, size, total)
    """
    query_params = {}
    if owner is not None:
        query_params["owner"] = owner
    if sort_dir is not None:
        query_params["sort_dir"] = sort_dir
    if sort_key is not None:
        query_params["sort_key"] = sort_key
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    result = access.sdk().execute(lambda s: make_api_call(
        s,
        'GET',
        '/v1/{project_id}/dev-servers',
        query=query_params
    ))
    formatted_result = format_paginated_result(result)
    api_result = format_api_result(True, data=formatted_result)
    return add_api_reference(api_result, "22.2 ListDevServers (Page 1575)")

from common_module.api_helper import make_api_call
__all__ = ['ma_liteserver_list']