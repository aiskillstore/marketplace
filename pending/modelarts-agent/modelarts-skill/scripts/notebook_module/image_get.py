#!/usr/bin/env python3
"""
Notebook模块 - image_get函数
功能：获取镜像详情
"""

from ._bootstrap import ensure_authentication, format_api_result, Any, Dict


def image_get(image_id: str) -> Dict[str, Any]:
    """
    Get details of an image.

    SECURITY: Uses secure SDK wrapper. Credentials never exposed.

    Args:
        image_id: The image ID (required)

    Returns:
        Image details
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        if not image_id:
            return format_api_result(False, error="image_id is required")

        print(f"  获取镜像详情: {image_id}")

        def _api_call(session):
            from modelarts import constant
            from modelarts.config.auth import auth_by_apig
            
            request_url = f"/v1/{session.project_id}/images/{image_id}"
            return auth_by_apig(session, constant.HTTPS_GET, request_url)
        
        result = access.sdk().execute(_api_call)

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"获取镜像详情时发生异常: {e}")


__all__ = ['image_get']