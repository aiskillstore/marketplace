#!/usr/bin/env python3
"""
Notebook模块 - attach_obs函数
功能：挂载OBS存储
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def attach_obs(notebook_id: str, uri: str, mount_path: str = None, category: str = "OBSFS") -> Dict[str, Any]:
    """
    动态挂载 OBS 存储到 Notebook 实例。

    API 路径: POST /v1/{project_id}/notebooks/{instance_id}/storage

    Args:
        notebook_id: Notebook 实例 ID (必填)
        uri: OBS 对象路径，如 "obs://bucket-name/path" (必填)
        mount_path: 挂载路径，必须在 /data/ 子目录下 (可选，默认 /home/ma-user/work/)
        category: 存储类型，固定 "OBS" (可选，默认 "OBS")

    Returns:
        挂载结果

    示例:
        >>> from notebook_module import attach_obs
        >>> result = attach_obs(
        ...     'notebook-id-xxx',
        ...     'obs://my-bucket/data',
        ...     '/home/ma-user/work/mydata'
        ... )
        >>> if result['success']:
        ...     print("挂载成功，存储ID:", result['data']['id'])
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        if not notebook_id:
            return format_api_result(False, error="notebook_id is required")
        if not uri:
            return format_api_result(False, error="uri is required")

        body = {
            "uri": uri,
            "category": category
        }
        if mount_path:
            body["mount_path"] = mount_path

        print(f"  挂载OBS存储到Notebook {notebook_id}: {uri} -> {mount_path or '/home/ma-user/work/'}")

        result = simple_api_call(
            access,
            'POST',
            '/v1/{project_id}/notebooks/{notebook_id}/storage',
            body=body,
            notebook_id=notebook_id
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"挂载OBS存储时发生异常: {e}")


__all__ = ['attach_obs']