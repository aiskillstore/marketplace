#!/usr/bin/env python3
"""
Notebook模块 - delete_obs_bucket函数
功能：删除OBS存储桶
"""

from ._bootstrap import ensure_authentication, format_api_result, Any, Dict


def delete_obs_bucket(bucket_name: str) -> Dict[str, Any]:
    """
    Delete an OBS bucket.

    SECURITY: Uses secure SDK wrapper. Credentials never exposed.

    Args:
        bucket_name: OBS bucket name (required)

    Returns:
        Bucket deletion result
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        if not bucket_name:
            return format_api_result(False, error="bucket_name is required")
        
        print(f"  删除OBS桶: {bucket_name}")

        def _delete_bucket(session):
            obs = session.obs_client
            return obs.delete_bucket(bucket_name)
        
        result = access.sdk().execute(_delete_bucket)

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"删除OBS桶时发生异常: {e}")


__all__ = ['delete_obs_bucket']