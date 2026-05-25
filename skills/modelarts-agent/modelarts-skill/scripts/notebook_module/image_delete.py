#!/usr/bin/env python3
"""
Notebook模块 - image_delete函数
功能：删除镜像
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def image_delete(image_id: str, is_force: bool = False) -> Dict[str, Any]:
    """
    删除自定义镜像。

    API 路径: DELETE /v1/{project_id}/images/{id}

    Args:
        image_id: 镜像 ID (必填)
        is_force: 是否同时删除 SWR 中的镜像内容 (必填，默认 False)
            - True: 删除镜像内容（仅对个人私有镜像有效）
            - False: 不删除镜像内容

    Returns:
        删除结果

    示例:
        >>> from notebook_module import image_delete, image_list
        >>> result = image_delete('image-id', is_force=True)
        >>> if result['success']:
        ...     print("删除成功")
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        if not image_id:
            return format_api_result(False, error="image_id is required")

        body = {"is_force": is_force}

        print(f"  删除镜像: {image_id}")

        result = simple_api_call(
            access,
            'DELETE',
            '/v1/{project_id}/images/{image_id}',
            body=body,
            image_id=image_id
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"删除镜像时发生异常: {e}")


__all__ = ['image_delete']