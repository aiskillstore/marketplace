#!/usr/bin/env python3
"""
Notebook模块 - cancel_obs函数
功能：卸载OBS存储
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def cancel_obs(notebook_id: str, storage_id: str) -> Dict[str, Any]:
    """
    卸载 Notebook 实例中已挂载的 OBS 存储。

    API 路径: DELETE /v1/{project_id}/notebooks/{instance_id}/storage/{storage_id}

    Args:
        notebook_id: Notebook 实例 ID (必填)
        storage_id: 存储 ID (必填)

    Returns:
        卸载结果

    示例:
        >>> from notebook_module import cancel_obs, list_attachable_obs
        >>> # 先获取已挂载的存储列表
        >>> result = list_attachable_obs('notebook-id')
        >>> storage_id = result['data']['data'][0]['id']
        >>> # 卸载
        >>> cancel_obs('notebook-id', storage_id)
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

        print(f"  卸载OBS存储: {notebook_id} -> {storage_id}")

        result = simple_api_call(
            access,
            'DELETE',
            '/v1/{project_id}/notebooks/{notebook_id}/storage/{storage_id}',
            notebook_id=notebook_id,
            storage_id=storage_id
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"卸载OBS存储时发生异常: {e}")


__all__ = ['cancel_obs']