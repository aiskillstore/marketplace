#!/usr/bin/env python3
"""
Lite Server 模块 - get_image 函数
功能：查询指定镜像详情
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any
from .common import validate_required_params, add_api_reference

@authenticated_api_call
def ma_liteserver_get_image(
    access,
    image_id: str
) -> Dict[str, Any]:
    """
    Get details of a Lite Server image.
    Args:
        image_id: The image ID (required)
    Returns:
        Image details
    """
    valid, error = validate_required_params({"image_id": image_id}, ["image_id"])
    if not valid:
        return format_api_result(False, error=error)
    result = simple_api_call(
        access,
        'GET',
        '/v1/{project_id}/dev-servers/images/{image_id}',
        image_id=image_id
    )
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.33 GetDevServerImage (Page 1797)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_get_image']
