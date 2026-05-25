#!/usr/bin/env python3

"""列出推理服务模块 - v2版本"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, simple_api_call, Dict, Any

def check_limit(limit):
    if not 1 <= limit <= 1000: return "limit必须在1-1000之间"
    return None

def check_offset(offset):
    if offset < 0: return "offset不能为负数"
    return None

@authenticated_api_call
def ma_inference_service_list(access, limit: int = 100, offset: int = 0, **kwargs) -> Dict[str, Any]:
    """列出推理服务 - v2版本"""
    checks = [
        (check_limit(limit), "limit"),
        (check_offset(offset), "offset")
    ]

    for check, param in checks:
        if check: return format_api_result(False, error=f"{param}: {check}")

    print(f"  列出推理服务v2: limit={limit}, offset={offset}")

    query = {"limit": limit, "offset": offset}
    if kwargs:
        query.update(kwargs)

    api_response = simple_api_call(access, 'GET', '/v2/{project_id}/services', query=query)
    
    total_services = api_response.get('total', 0)
    print(f"  API返回: 共 {total_services} 个服务")

    standardized_data = {
        'services': api_response.get('data', []),
        'total_count': api_response.get('total', 0),
        'offset': offset,
        'limit': limit,
        'current_page': api_response.get('current', 0),
        'total_pages': api_response.get('pages', 1),
        'page_size': api_response.get('size', limit)
    }

    return format_api_result(True, data=standardized_data)

@authenticated_api_call
def quick_list_v2_services(access, limit: int = 20) -> Dict[str, Any]:
    """快速列出v2服务"""

    if not 1 <= limit <= 1000:
        return format_api_result(False, error="limit必须在1-1000之间")
    
    print(f"  快速列出推理服务v2: limit={limit}")

    api_response = simple_api_call(access, 'GET', '/v2/{project_id}/services', query={'limit': limit, 'offset': 0})
    
    total_services = api_response.get('total', 0)
    print(f"  API返回: 共 {total_services} 个服务")

    standardized_data = {
        'services': api_response.get('data', []),
        'total_count': total_services,
        'offset': 0,
        'limit': limit,
        'current_page': api_response.get('current', 0),
        'total_pages': api_response.get('pages', 1),
        'page_size': api_response.get('size', limit)
    }

    return format_api_result(True, data=standardized_data)

__all__ = ['ma_inference_service_list', 'quick_list_v2_services']
