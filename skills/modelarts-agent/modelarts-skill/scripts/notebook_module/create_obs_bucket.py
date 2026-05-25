#!/usr/bin/env python3
"""
Notebook模块 - create_obs_bucket函数
功能：创建OBS存储桶
"""

from ._bootstrap import ensure_authentication, format_api_result, Any, Dict


def create_obs_bucket(bucket_name: str, region: str = None) -> Dict[str, Any]:
    """
    Create a new OBS bucket.

    SECURITY: Uses secure SDK wrapper. Credentials never exposed.

    Args:
        bucket_name: OBS bucket name (required) - 必须全局唯一，3-63字符，小写字母、数字、中划线
        region: Region name (optional) - 默认使用当前session的region

    Returns:
        Bucket creation result
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        if not bucket_name:
            return format_api_result(False, error="bucket_name is required")
        
        print(f"  创建OBS桶: {bucket_name}")

        def _create_bucket(session):
            obs = session.obs_client
            bucket_region = region if region else session.region_name
            return obs.create_bucket(bucket_name, location=bucket_region)
        
        result = access.sdk().execute(_create_bucket)

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"创建OBS桶时发生异常: {e}")


__all__ = ['create_obs_bucket']