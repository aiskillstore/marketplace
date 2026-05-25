#!/usr/bin/env python3
"""
Notebook模块 - list_attachable_obs函数
功能：列出可挂载的OBS存储
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def list_attachable_obs(notebook_id: str) -> Dict[str, Any]:
    """
    查询 Notebook 实例已挂载的 OBS 存储列表。

    API 路径: GET /v1/{project_id}/notebooks/{instance_id}/storage

    Args:
        notebook_id: Notebook 实例 ID (必填)

    Returns:
        已挂载的存储列表，包含挂载路径、OBS URI、状态等信息
    
    示例:
        >>> from notebook_module import list_attachable_obs
        >>> result = list_attachable_obs('notebook-id-xxx')
        >>> if result['success']:
        ...     for storage in result['data']['data']:
        ...         print(storage['mount_path'], storage['uri'])
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        if not notebook_id:
            return format_api_result(False, error="notebook_id is required")

        print(f"  获取Notebook已挂载的存储列表: {notebook_id}")

        result = simple_api_call(
            access,
            'GET',
            '/v1/{project_id}/notebooks/{notebook_id}/storage',
            notebook_id=notebook_id
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"获取存储列表时发生异常: {e}")


__all__ = ['list_attachable_obs']