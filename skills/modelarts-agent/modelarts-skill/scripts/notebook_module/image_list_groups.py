#!/usr/bin/env python3
"""
Notebook模块 - image_list_groups函数
功能：获取镜像组列表
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def image_list_groups(name: str = None, name_fuzzy_match: bool = True,
                      namespace: str = None, type: str = None,
                      workspace_id: str = None, limit: int = 200,
                      offset: int = 0, swr_instance_id: str = None) -> Dict[str, Any]:
    """
    查询镜像组列表（按名称分组显示）。

    API 路径: GET /v1/{project_id}/images/group

    ⚠️ 重要提醒：建议始终指定 type 参数（"BUILD_IN" 或 "DEDICATED"）。
       不指定 type 可能导致 API 网关路由匹配异常，返回"镜像不存在"错误。
       - BUILD_IN: 系统内置公共镜像
       - DEDICATED: 用户自定义/保存的私有镜像

    Args:
        name: 镜像名称 (可选)
        name_fuzzy_match: 是否模糊匹配名称 (可选，默认 True)
        namespace: 镜像所属组织 (可选)
        type: 镜像类型 (强烈建议指定)
            - "BUILD_IN": 系统内置公共镜像
            - "DEDICATED": 用户自定义/保存的私有镜像
        workspace_id: 工作空间 ID (可选，默认 "0")
        limit: 每页数量 (可选，默认 200)
        offset: 分页偏移量 (可选，默认 0)
        swr_instance_id: 企业版 SWR 仓库 ID (可选)

    Returns:
        镜像组列表

    示例:
        >>> from notebook_module import image_list_groups
        >>> result = image_list_groups(namespace='dev-custom')
        >>> if result['success']:
        ...     for group in result['data']['data']:
        ...         print(group['name'], '-', group['count'], '个版本')
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        query = {"name_fuzzy_match": name_fuzzy_match, "limit": limit, "offset": offset}
        if name:
            query["name"] = name
        if namespace:
            query["namespace"] = namespace
        if type:
            query["type"] = type
        if workspace_id:
            query["workspace_id"] = workspace_id
        if swr_instance_id:
            query["swr_instance_id"] = swr_instance_id

        print(f"  获取镜像组列表")

        result = simple_api_call(
            access,
            'GET',
            '/v1/{project_id}/images/group',
            query=query
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"获取镜像组列表时发生异常: {e}")


__all__ = ['image_list_groups']