#!/usr/bin/env python3
"""
Notebook模块 - list_obs_buckets函数
功能：列出可用的OBS存储桶
"""

from ._bootstrap import ensure_authentication, format_api_result, Any, Dict, List


def list_obs_buckets() -> Dict[str, Any]:
    """
    List all available OBS buckets.

    SECURITY: Uses secure SDK wrapper. Credentials never exposed.

    Args:
        None

    Returns:
        List of OBS bucket names
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        print(f"  获取OBS桶列表")

        def _list_buckets(session):
            obs = session.obs_client
            return obs.list_buckets()
        
        result = access.sdk().execute(_list_buckets)

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"获取OBS桶列表时发生异常: {e}")


__all__ = ['list_obs_buckets']