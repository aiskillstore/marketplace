#!/usr/bin/env python3
"""
KMS 模块 - 查询SSH密钥对列表
功能：查询SSH密钥对列表（ListKeypairs）
API: GET https://kms.{region}.myhuaweicloud.com/v3/{project_id}/keypairs
"""

import sys
from typing import Dict, Any, Optional

sys.path.insert(0, '.')

from common_module import ensure_authentication, format_api_result
from kms_module.common import format_error_result, format_success_result, kms_api_call

def list_keypairs(
    limit: str = "1000",
    marker: Optional[str] = None
) -> Dict[str, Any]:
    """
    查询SSH密钥对列表（ListKeypairs）

    API: GET https://kms.{region}.myhuaweicloud.com/v3/{project_id}/keypairs
    Args:
        limit: 每页返回的个数，默认值1000
        marker: 分页查询起始的资源id，为空时查询第一页
    Returns:
        Dict[str, Any]:
        {
            "success": bool,
            "data": {
                "keypairs": [
                    {
                        "name": "keypair-name",
                        "type": "ssh",
                        "scope": "user",
                        "public_key": "ssh-rsa AAAA...",
                        "fingerprint": "65:ca:87:...",
                        "is_key_protection": false,
                        "frozen_state": 0
                    },
                    ...
                ],
                "page_info": {
                    "next_marker": "...",
                    "previous_marker": "...",
                    "current_count": 49
                },
                "total": int
            },
            "status_code": int
        }
    Example:
        >>> from kms_module import list_keypairs
        >>> result = list_keypairs()
        >>> if result['success']:
        ...     for kp in result['data']['keypairs']:
        ...         print(f"{kp['name']} ({kp['type']}): fingerprint={kp['fingerprint']}")
    """
    try:
        auth_result = ensure_authentication()
        if not auth_result['success']:
            return format_api_result(False, error=auth_result.get('error', 'Authentication failed'))

        access = auth_result['access']

        def _list_keypairs(session):
            api_path = f"/v3/{session.project_id}/keypairs"
            query_params = {}
            if limit != "1000":
                query_params['limit'] = limit
            if marker:
                query_params['marker'] = marker
            return kms_api_call(session, "GET", api_path, query_params)
        result = access.sdk().execute(_list_keypairs)
        if result.get("success"):
            raw_keypairs = result.get("data", {}).get("keypairs", [])
            page_info = result.get("data", {}).get("page_info", {})
            keypairs = [item.get("keypair", {}) for item in raw_keypairs]
            return format_success_result(
                data={
                    "keypairs": keypairs,
                    "page_info": page_info,
                    "total": len(keypairs)
                },
                status_code=result.get("status_code", 200)
            )
        else:
            error_msg = result.get("error", "Unknown API error")
            status_code = result.get("status_code", 500)
            return format_error_result(
                error=f"KMS API error: {error_msg}",
                status_code=status_code
            )
    except Exception as e:
        return format_error_result(error=f"Failed to list keypairs: {str(e)}", status_code=500)
__all__ = ['list_keypairs']
