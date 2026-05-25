#!/usr/bin/env python3
"""
Notebook模块 - show_tags函数
功能：获取Notebook标签
"""

from ._bootstrap import ensure_authentication, format_api_result, Any, Dict


def show_tags(workspace_id: str = None) -> Dict[str, Any]:
    """
    查询当前 Project 下所有 Notebook 实例的标签
    
    功能说明：
        获取用户当前 project 下所有 Notebook 实例的标签信息
        用于管理或统计 Notebook 资源时查询标签信息

    Args:
        workspace_id: 工作空间 ID（可选）
            未创建工作空间时默认值为 "0"
            存在创建并使用的工作空间，以实际取值为准

    Returns:
        所有 Notebook 的标签列表，包含标签名称、标签值等信息
    
    示例:
        >>> from notebook_module import show_tags
        >>> result = show_tags()
        >>> if result['success']:
        ...     tags = result['data']
        ...     print(f"共 {len(tags)} 个标签")
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        print(f"  查询所有Notebook标签")

        query_params = {}
        if workspace_id:
            query_params["workspace_id"] = workspace_id
        
        def _api_call(session):
            from modelarts import constant
            from modelarts.config.auth import auth_by_apig
            
            request_url = f"/v1/{session.project_id}/notebooks/tags"
            return auth_by_apig(session, constant.HTTPS_GET, request_url, query=query_params)
        
        result = access.sdk().execute(_api_call)

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"获取Notebook标签时发生异常: {e}")

__all__ = ['show_tags']