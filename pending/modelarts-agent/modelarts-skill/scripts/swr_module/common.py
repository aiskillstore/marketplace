#!/usr/bin/env python3
"""
SWR 模块 - 公共函数

功能：SWR模块的公共辅助函数
"""

import sys
from typing import Dict, Any, List

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


def validate_image_url(image_url: str) -> Dict[str, Any]:
    if not image_url or not isinstance(image_url, str):
        return format_error_result(
            error="Image URL must be a non-empty string",
            status_code=400
        )
    parts = image_url.split(':')
    if len(parts) != 2:
        return format_error_result(
            error="Image URL must be in format: namespace/repository:tag",
            status_code=400
        )
    
    namespace_repo = parts[0]
    tag = parts[1]
    if '/' not in namespace_repo:
        return format_error_result(
            error="Image URL must contain namespace and repository separated by '/'",
            status_code=400
        )
    
    namespace, repository = namespace_repo.split('/', 1)
    
    if not namespace or not repository:
        return format_error_result(
            error="Namespace and repository cannot be empty",
            status_code=400
        )
    
    if not tag:
        return format_error_result(
            error="Image tag cannot be empty",
            status_code=400
        )
    
    return format_success_result(data={
        "namespace": namespace,
        "repository": repository,
        "tag": tag,
        "is_valid": True
    })


def parse_image_url(image_url: str) -> Dict[str, str]:
    try:
        if ':' not in image_url:
            return {
                "namespace": "",
                "repository": image_url,
                "tag": "latest",
                "full_url": f"{image_url}:latest"
            }
        
        namespace_repo, tag = image_url.split(':', 1)
        
        if '/' not in namespace_repo:
            return {
                "namespace": "",
                "repository": namespace_repo,
                "tag": tag,
                "full_url": image_url
            }
        
        namespace, repository = namespace_repo.split('/', 1)
        
        return {
            "namespace": namespace,
            "repository": repository,
            "tag": tag,
            "full_url": image_url
        }
    except Exception as e:
        print(f"Error parsing image URL '{image_url}': {e}")
        return {
            "namespace": "",
            "repository": "",
            "tag": "",
            "full_url": ""
        }


def build_image_display_info(image_info: Dict[str, Any]) -> str:
    namespace = image_info.get("namespace", "")
    repository = image_info.get("name", image_info.get("repository", ""))
    tags = image_info.get("tags", [])
    
    if not namespace or not repository:
        return "Invalid image information"

    display = f"{namespace}/{repository}"

    if tags:
        if len(tags) <= 3:
            display += f" (tags: {', '.join(tags)})"
        else:
            display += f" (tags: {', '.join(tags[:3])}, ... +{len(tags)-3} more)"
    else:
        display += " (no tags available)"

    category = image_info.get("category", "")
    if category:
        display += f" [{category}]"
    
    is_public = image_info.get("is_public", False)
    if is_public:
        display += " [public]"
    
    return display


def filter_images_by_category(images: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
    if not category:
        return images
    
    return [
        image for image in images 
        if image.get("category", "").lower() == category.lower()
    ]


__all__ = [
    'validate_image_url',
    'parse_image_url',
    'build_image_display_info',
    'filter_images_by_category'
]
