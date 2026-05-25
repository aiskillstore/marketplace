#!/usr/bin/env python3
"""
Notebook模块 - image_sync函数
功能：同步镜像状态
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def image_sync(image_id: str) -> Dict[str, Any]:
    """
    同步镜像状态（从 SWR 同步最新状态到 ModelArts。

    API 路径: POST /v1/{project_id}/images/{image_id}/sync

    Args:
        image_id: 镜像 ID (必填)

    Returns:
        同步结果

    示例:
        >>> from notebook_module import image_sync
        >>> result = image_sync('image-id')
        >>> if result['success']:
        ...     print("同步成功，当前状态:", result['data']['status'])
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        if not image_id:
            return format_api_result(False, error="image_id is required")

        print(f"  同步镜像状态: {image_id}")

        result = simple_api_call(
            access,
            'POST',
            '/v1/{project_id}/images/{image_id}/sync',
            image_id=image_id
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"同步镜像时发生异常: {e}")


__all__ = ['image_sync']