#!/usr/bin/env python3
"""
Notebook模块 - show_lease函数
功能：获取Notebook租约
"""

from ._bootstrap import ensure_authentication, format_api_result, Any, Dict


def show_lease(notebook_id: str) -> Dict[str, Any]:
    """
    Get lease information of a Notebook instance.

    SECURITY: Uses secure SDK wrapper. Credentials never exposed.

    Args:
        notebook_id: The notebook ID (required)

    Returns:
        Lease information
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        if not notebook_id:
            return format_api_result(False, error="notebook_id is required")

        print(f"  获取Notebook租约: {notebook_id}")

        def _api_call(session):
            from modelarts import constant
            from modelarts.config.auth import auth_by_apig
            
            request_url = f"/v1/{session.project_id}/notebooks/{notebook_id}/lease"
            return auth_by_apig(session, constant.HTTPS_GET, request_url)
        
        result = access.sdk().execute(_api_call)

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"获取Notebook租约时发生异常: {e}")

__all__ = ['show_lease']