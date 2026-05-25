#!/usr/bin/env python3
"""
Notebook模块 - image_list函数
功能：列出可用的镜像
"""

from ._bootstrap import ensure_authentication, format_api_result, Any, Dict


def image_list(limit: int = 100, offset: int = 0, name: str = None, 
               status: str = None, sort_dir: str = "DESC") -> Dict[str, Any]:
    """
    Query list of custom images.

    API Reference: 5.26 ListImages (Page 536)

    SECURITY: Uses secure SDK wrapper. Credentials never exposed.

    Args:
        limit: Maximum number of images per page (optional) (default: 100)
        offset: Pagination offset (optional) (default: 0)
        name: Filter by image name (optional)
        status: Filter by image status (optional)
        sort_dir: Sort direction (optional) - ASC/DESC (default: "DESC")

    Returns:
        List of custom images with pagination info
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        def _list_images(session):
            from modelarts import constant
            from modelarts.config.auth import auth_by_apig
            
            request_url = f"/v1/{session.project_id}/images"
            query_params = {"limit": limit, "offset": offset}
            
            if name:
                query_params["name"] = name
            if status:
                query_params["status"] = status
            if sort_dir:
                query_params["sort_dir"] = sort_dir
            
            return auth_by_apig(session, constant.HTTPS_GET, request_url, query=query_params)
        
        print(f"  获取镜像列表 (limit={limit}, offset={offset})")

        result = access.sdk().execute(_list_images)

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"执行操作时发生异常: {e}")


__all__ = ['image_list']