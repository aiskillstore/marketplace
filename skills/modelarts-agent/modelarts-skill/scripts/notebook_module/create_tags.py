#!/usr/bin/env python3
"""
Notebook模块 - create_tags函数
功能：创建Notebook标签
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def create_tags(notebook_id: str, tags: list, workspace_id: str = None) -> Dict[str, Any]:
    """
    为 Notebook 实例创建 TMS 标签

    Args:
        notebook_id: Notebook 实例 ID（必填）格式: UUID
        tags: TMS 标签列表（必填），格式: [{'key': 'xxx', 'value': 'xxx'}, ...]
        workspace_id: 工作空间 ID（可选）

    Returns:
        创建结果
    
    示例:
        >>> from notebook_module import create_tags
        >>> result = create_tags(
        ...     'notebook-xxx-xxx-xxx',
        ...     [{'key': 'env', 'value': 'test'}, {'key': 'owner', 'value': 'openclaw'}]
        ... )
        >>> if result['success']:
        ...     print("标签创建成功")
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        if not notebook_id:
            return format_api_result(False, error="notebook_id is required")
        if not tags:
            return format_api_result(False, error="tags is required")
        
        body = {"tags": tags}
        
        query_params = {}
        if workspace_id:
            query_params["workspace_id"] = workspace_id

        print(f"  创建Notebook标签: {notebook_id}")

        result = simple_api_call(
            access,
            'POST',
            '/v1/{project_id}/notebooks/{resource_id}/tags/create',
            body=body,
            query=query_params,
            resource_id=notebook_id
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"创建Notebook标签时发生异常: {e}")


__all__ = ['create_tags']