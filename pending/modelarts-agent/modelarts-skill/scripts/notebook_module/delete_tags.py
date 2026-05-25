#!/usr/bin/env python3
"""
Notebook模块 - delete_tags函数
功能：删除Notebook标签
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def delete_tags(notebook_id: str, tags: list, workspace_id: str = None) -> Dict[str, Any]:
    """
    删除 Notebook 实例的标签

    Args:
        notebook_id: Notebook 实例 ID（必填）格式: UUID
        tags: 要删除的标签列表，格式: [{'key': 'xxx', 'value': 'yyy'}, ...]
        workspace_id: 工作空间 ID（可选）

    Returns:
        删除结果
    
    示例:
        >>> from notebook_module import delete_tags
        >>> result = delete_tags(
        ...     'notebook-xxx-xxx-xxx',
        ...     [{'key': 'env', 'value': 'prod'}, {'key': 'owner', 'value': 'admin'}]
        ... )
        >>> if result['success']:
        ...     print("标签删除成功")
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

        formatted_tags = []
        for tag in tags:
            if isinstance(tag, dict) and 'key' in tag and 'value' in tag:
                formatted_tags.append(tag)
            else:
                return format_api_result(False, error="每个标签必须包含 'key' 和 'value' 字段")
        
        body = {"tags": formatted_tags}
        
        query_params = {}
        if workspace_id:
            query_params["workspace_id"] = workspace_id

        print(f"  删除Notebook标签: {notebook_id}")

        result = simple_api_call(
            access,
            'DELETE',
            '/v1/{project_id}/notebooks/{resource_id}/tags/delete',
            body=body,
            query=query_params,
            resource_id=notebook_id
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"删除Notebook标签时发生异常: {e}")


__all__ = ['delete_tags']