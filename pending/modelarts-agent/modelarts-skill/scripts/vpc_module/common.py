#!/usr/bin/env python3
"""
VPC 模块 - 公共函数
功能：VPC模块的公共辅助函数
"""

import sys
from typing import Dict, Any, List, Optional

sys.path.insert(0, '.')

from common_module.result import format_api_result

def format_error_result(error: str, status_code: int = 400) -> dict:
    result = format_api_result(success=False, error=error)
    result['status_code'] = status_code
    return result

def format_success_result(data=None, status_code: int = 200, **kwargs) -> dict:
    result = format_api_result(success=True, data=data)
    result['status_code'] = status_code
    for k, v in kwargs.items():
        result[k] = v
    return result

def list_vpc_resources(
    data_key: str,
    error_prefix: str,
    api_call_fn: callable
) -> Dict[str, Any]:
    """
    VPC 列表查询通用处理（消除重复代码）

    封装：认证 → 执行API → 格式化结果
    Args:
        data_key: 响应数据中的键名（如 "vpcs", "security_groups", "subnets"）
        error_prefix: 错误消息前缀（如 "VPC", "SecurityGroup", "Subnet"）
        api_call_fn: 执行API调用的函数，接受session参数
    Returns:
        标准化的API结果
    """
    from common_module import ensure_authentication

    try:
        auth_result = ensure_authentication()
        if not auth_result['success']:
            return format_api_result(False, error=auth_result.get('error', 'Authentication failed'))

        access = auth_result['access']
        result = access.sdk().execute(api_call_fn)

        if result.get("success"):
            items = result.get("data", {}).get(data_key, [])
            return format_success_result(
                data={data_key: items, "total": len(items)},
                status_code=result.get("status_code", 200)
            )
        else:
            return format_error_result(
                error=f"{error_prefix} API error: {result.get('error', 'Unknown API error')}",
                status_code=result.get("status_code", 500)
            )
    except Exception as e:
        return format_error_result(error=f"Failed to list {error_prefix.lower()}s: {str(e)}", status_code=500)

def vpc_api_call(
    session,
    method: str,
    api_path: str,
    query_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    VPC API 统一请求处理（消除重复代码）
    Args:
        session: SDK session 对象
        method: HTTP 方法
        api_path: API 路径（不含 endpoint）
        query_params: 查询参数
    Returns:
        {"success": bool, "data": Any, "status_code": int, "error": str}
    """
    try:
        import requests
        from huaweicloudsdkcore.auth.credentials import BasicCredentials
        from huaweicloudsdkcore.signer.signer import Signer
        from huaweicloudsdkcore.sdk_request import SdkRequest
        from urllib.parse import urlparse

        ak = getattr(session, 'access_key', None)
        sk = getattr(session, 'secret_key', None)
        region = getattr(session, 'region_name', 'cn-north-4')
        security_token = getattr(session, 'security_token', None)
        project_id = getattr(session, 'project_id', None)

        if not ak or not sk:
            return {"success": False, "error": "Missing credentials"}
        if not project_id:
            return {"success": False, "error": "Missing project_id"}

        endpoint = f"https://vpc.{region}.myhuaweicloud.com"
        full_url = f"{endpoint}{api_path}"
        parsed = urlparse(full_url)

        sdk_request = SdkRequest()
        sdk_request.method = method
        sdk_request.schema = parsed.scheme
        sdk_request.host = parsed.netloc
        sdk_request.resource_path = parsed.path
        sdk_request.query_params = list(query_params.items()) if query_params else []
        sdk_request.header_params = {'Content-Type': 'application/json'}

        if security_token:
            sdk_request.header_params['X-Security-Token'] = security_token

        credentials = BasicCredentials(ak, sk)
        if security_token:
            credentials = credentials.with_security_token(security_token)

        signer = Signer(credentials)
        signed_request = signer.sign(sdk_request)

        request_headers = dict(signed_request.header_params)
        response = requests.request(
            method=signed_request.method,
            url=f"{signed_request.schema}://{signed_request.host}{signed_request.resource_path}",
            headers=request_headers,
            params=query_params,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "data": data,
                "status_code": response.status_code
            }
        else:
            return {
                "success": False,
                "error": f"API error: {response.status_code} - {response.text}",
                "status_code": response.status_code
            }

    except ImportError as ie:
        return {"success": False, "error": f"Huawei SDK not available: {str(ie)}"}
    except Exception as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}

__all__ = [
    'format_error_result',
    'format_success_result',
    'list_vpc_resources',
    'vpc_api_call'
]
