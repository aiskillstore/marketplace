#!/usr/bin/env python3
"""
SWR 模块 - 镜像仓库查询

功能：查询SWR镜像仓库列表
"""

import sys
import json
from typing import Dict, Any

sys.path.insert(0, '.')

from common_module import ensure_authentication, format_api_result
from swr_module.common import format_error_result, format_success_result


def swr_get_train_image_repos(offset: int = 0) -> Dict[str, Any]:
    """
    获取支持创建训练任务的镜像仓库列表。
    
    调用 SWR API: GET https://swr-api.{region_id}.myhuaweicloud.com/v2/manage/repos
    查询参数: center::self|limit::10|offset::{offset}|order_column::updated_time|order_type::desc
    
    📌 使用场景:
    创建训练任务前，需要先获取可用的镜像，然后从中选择合适的 tag
    
    注意: 此函数不需要 access 参数，内部自动处理认证
    
    Args:
        offset: 分页偏移量，默认 0
    
    Returns:
        Dict[str, Any]:
        {
            "success": bool,
            "data": [
                {
                    "namespace": str,
                    "name": str,
                    "tags": ["tag1", "tag2", ...],
                    "category": str,
                    "is_public": bool
                },
                ...
            ]
        }
    
    Example:
        # 获取镜像列表
        from swr_module import swr_get_train_image_repos
        result = swr_get_train_image_repos(offset=0)
        
        if result['success']:
            for repo in result['data']:
                print(f"{repo['namespace']}/{repo['name']}: {repo['tags']}")
        
        # 使用示例：创建训练任务时指定完整镜像 URL
        # 格式: {namespace}/{name}:{tag}
        # 示例: dev-custom/openclaw-fxb-test:latest
    
    Related:
        - 创建训练任务: train_module.ma_train_job_create()
    """
    try:
        auth_result = ensure_authentication()
        if not auth_result['success']:
            return format_api_result(False, error=auth_result.get('error', 'Authentication failed'))
        access = auth_result['access']
        api_path = "/v2/manage/repos"
        filter_str = f"center::self|limit::10|offset::{offset}|order_column::updated_time|order_type::desc"
        query_params = {
            "filter": filter_str
        }
        def _get_repos(session):
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
                
                if not ak or not sk:
                    return {"success": False, "error": "Missing credentials"}
                endpoint = f"https://swr-api.{region}.myhuaweicloud.com"
                full_url = f"{endpoint}{api_path}"
                parsed = urlparse(full_url)
                sdk_request = SdkRequest()
                sdk_request.method = "GET"
                sdk_request.schema = parsed.scheme
                sdk_request.host = parsed.netloc
                sdk_request.resource_path = parsed.path
                sdk_request.query_params = list(query_params.items())
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
                    params=dict(query_params),
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    return {"success": True, "data": data, "status_code": response.status_code}
                else:
                    return {"success": False, "error": f"API error: {response.status_code}", "status_code": response.status_code}
                    
            except ImportError as ie:
                return {"success": False, "error": f"Huawei SDK not available: {str(ie)}"}
            except Exception as e:
                return {"success": False, "error": f"Request failed: {str(e)}"}
        
        result = access.sdk().execute(_get_repos)
        
        if result.get("success"):
            result_data = result.get("data", [])

            if isinstance(result_data, list):
                repos = result_data
            elif isinstance(result_data, dict):
                repos = result_data.get("repositories", [])
            else:
                repos = []

            normalized_repos = [_normalize_repo_info(repo) for repo in repos]
            
            return format_success_result(data=normalized_repos, status_code=200)
        else:
            error_msg = result.get("error", "Unknown API error")
            status_code = result.get("status_code", 500)
            return format_error_result(error=f"SWR API error: {error_msg}", status_code=status_code)
            
    except Exception as e:
        return format_error_result(error=f"Failed to get SWR repositories: {str(e)}", status_code=500)


def _normalize_repo_info(repo: Dict[str, Any]) -> Dict[str, Any]:
    """规范化仓库信息"""
    namespace = repo.get("namespace", "")
    name = repo.get("name", "")
    tags = repo.get("tags", []) or []
    
    return {
        "namespace": namespace,
        "name": name,
        "category": repo.get("category", "other"),
        "is_public": bool(repo.get("is_public", False)),
        "tags": tags,
        "num_images": repo.get("num_images", 0),
        "size": repo.get("size", 0),
        "updated_at": repo.get("updated_at", ""),
        "path": f"{namespace}/{name}" if namespace and name else "",
        "full_path": f"{namespace}/{name}" if namespace and name else "",
        "has_tags": len(tags) > 0,
        "available_for_training": len(tags) > 0,
        "example_image_url": f"{namespace}/{name}:{tags[0]}" if tags else f"{namespace}/{name}:latest"
    }


def get_available_image_tags(namespace: str, repository: str) -> Dict[str, Any]:
    """获取指定仓库的可用标签"""
    try:
        result = swr_get_train_image_repos(offset=0)
        if not result.get("success"):
            return result
        
        repos = result.get("data", [])
        target_repo = next((r for r in repos if r.get("namespace") == namespace and r.get("name") == repository), None)
        
        if not target_repo:
            return format_error_result(error=f"Repository not found: {namespace}/{repository}", status_code=404)
        
        tags = target_repo.get("tags", [])
        return format_success_result(data={"namespace": namespace, "repository": repository, "tags": tags, "total_tags": len(tags)})
        
    except Exception as e:
        return format_error_result(error=f"Failed to get image tags: {str(e)}", status_code=500)


__all__ = ['swr_get_train_image_repos', 'get_available_image_tags', '_normalize_repo_info']
