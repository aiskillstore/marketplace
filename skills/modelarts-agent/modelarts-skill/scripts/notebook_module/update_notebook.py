#!/usr/bin/env python3
"""
Notebook模块 - update_notebook函数

功能：更新notebook实例
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def update_notebook(notebook_id: str, name: str = None, description: str = None) -> Dict[str, Any]:
    """
    Update Notebook instance metadata (name, description).

    SECURITY: Uses secure SDK wrapper. Credentials never exposed.

    Args:
        notebook_id: The notebook ID (required)
        name: New name (optional)
        description: New description (optional)

    Returns:
        Update status and result
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        if not notebook_id:
            return format_api_result(False, error="notebook_id is required")

        body = {}
        if name:
            body["name"] = name
        if description:
            body["description"] = description

        print(f"  更新Notebook实例: {notebook_id}")

        result = simple_api_call(
            access,
            'PUT',
            '/v1/{project_id}/notebooks/{notebook_id}',
            body=body,
            notebook_id=notebook_id
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"更新notebook时发生异常: {e}")


__all__ = ['update_notebook']