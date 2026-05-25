#!/usr/bin/env python3
"""
Notebook模块 - show_attachable_obs函数
功能：获取Notebook单个OBS存储详情
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def show_attachable_obs(notebook_id: str, storage_id: str) -> Dict[str, Any]:
    """
    获取 Notebook 实例中指定 OBS 存储的挂载详情。

    API 路径: GET /v1/{project_id}/notebooks/{instance_id}/storage/{storage_id}

    Args:
        notebook_id: Notebook 实例 ID (必填)
        storage_id: 存储 ID (必填)

    Returns:
        存储详情，包含挂载路径、URI、状态等

    示例:
        >>> from notebook_module import show_attachable_obs
        >>> result = show_attachable_obs('notebook-id', 'storage-id')
        >>> if result['success']:
        ...     print(result['data']['uri'], result['data']['mount_path'])
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        if not notebook_id:
            return format_api_result(False, error="notebook_id is required")
        if not storage_id:
            return format_api_result(False, error="storage_id is required")

        print(f"  获取存储详情: {notebook_id} -> {storage_id}")

        result = simple_api_call(
            access,
            'GET',
            '/v1/{project_id}/notebooks/{notebook_id}/storage/{storage_id}',
            notebook_id=notebook_id,
            storage_id=storage_id
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"获取存储详情时发生异常: {e}")


__all__ = ['show_attachable_obs']