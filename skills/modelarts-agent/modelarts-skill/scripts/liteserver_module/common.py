#!/usr/bin/env python3
from __future__ import annotations
"""
Lite Server 模块 - 公共函数文件

功能：Lite Server 特有公共函数
行数：< 200行
圈复杂度：< 10
"""

import sys
from typing import Any, Dict, List, Optional

sys.path.insert(0, '.')
# 导入公共模块的函数
from common_module import format_api_result, simple_api_call

def format_hyperinstance_list_result(result: Any) -> Dict[str, Any]:
    """
    格式化超节点列表查询结果（消除重复代码）
    Args:
        result: API 返回结果
    Returns:
        格式化后的结果
    """
    if isinstance(result, dict):
        data = {
            'hyperinstances': result.get('data', []),
            'total': result.get('total', 0),
            'current': result.get('current', 0),
            'size': result.get('size', 0)
        }
        return format_api_result(True, data=data)
    else:
        return format_api_result(True, data=result)

def execute_hyperinstance_operation(
    access,
    hyperinstance_id: str,
    method: str,
    uri: str,
    api_reference: str,
    action: Optional[str] = None
) -> Dict[str, Any]:
    """
    执行超节点通用操作（消除重复代码）
    Args:
        access: 认证后的 access 对象
        hyperinstance_id: 超节点 ID
        method: HTTP 方法 (GET/PUT/DELETE)
        uri: API 路径
        api_reference: API 参考字符串
        action: 操作类型，用于包装结果 (optional)
    Returns:
        标准化的 API 结果
    """
    valid, error = validate_required_params(
        {"hyperinstance_id": hyperinstance_id},
        ["hyperinstance_id"]
    )
    if not valid:
        return format_api_result(False, error=error)

    result = simple_api_call(
        access,
        method,
        uri,
        hyperinstance_id=hyperinstance_id
    )

    if action:
        data = {"action": action, "hyperinstance_id": hyperinstance_id, "result": result}
    else:
        data = result

    api_result = format_api_result(True, data=data)
    return add_api_reference(api_result, api_reference)

def validate_dev_server_params(name: Optional[str] = None, 
                              image_id: Optional[str] = None, 
                              network: Optional[Dict] = None,
                              admin_pass: Optional[str] = None, 
                              key_pair_name: Optional[str] = None,
                              flavor: Optional[str] = None, 
                              resource_flavor: Optional[str] = None) -> tuple[bool, Optional[str]]:
    """
    验证 Dev Server 创建参数
    Args:
        name: 服务器名称
        image_id: 镜像ID
        network: 网络信息
        admin_pass: 管理员密码
        key_pair_name: 密钥对名称
        flavor: 规格名称
        resource_flavor: 资源规格名称
    Returns:
        (是否有效, 错误信息)
    """
    if not name or not image_id or not network:
        return False, "name, image_id, and network are required"
    if not admin_pass and not key_pair_name:
        return False, "Either admin_pass or key_pair_name must be provided"
    if admin_pass and key_pair_name:
        return False, "admin_pass and key_pair_name cannot be provided at the same time"
    if not flavor and not resource_flavor:
        return False, "Either flavor or resource_flavor must be provided"
    if flavor and resource_flavor:
        return False, "flavor and resource_flavor cannot be provided at the same time"
    return True, None

def format_paginated_result(result: Any, data_key: str = "data") -> Dict[str, Any]:
    """
    格式化分页结果
    Args:
        result: API 返回结果
        data_key: 数据字段名
    Returns:
        标准化的分页结果
    """
    if isinstance(result, list):
        data = result
        total = len(result)
    elif isinstance(result, dict):
        # 支持多种返回格式
        if data_key in result and isinstance(result[data_key], list):
            data = result[data_key]
            total = result.get("total", len(data))
        elif "items" in result and isinstance(result["items"], list):
            data = result["items"]
            total = result.get("totalItems", len(data))
        else:
            data = []
            total = 0
    else:
        data = []
        total = 0
    return {
        data_key: data,
        "total": total,
        "current": result.get("current", 0) if isinstance(result, dict) else 0,
        "size": result.get("size", 0) if isinstance(result, dict) else 0
    }

def add_api_reference(result: Dict[str, Any], api_reference: str) -> Dict[str, Any]:
    """
    添加 API 参考信息到结果
    Args:
        result: 原始结果
        api_reference: API 参考字符串
    Returns:
        包含 api_reference 的结果
    """
    if "success" in result and result["success"]:
        result["api_reference"] = api_reference
    else:
        result["api_reference"] = api_reference
    return result

def validate_required_params(params: Dict[str, Any], required_keys: List[str]) -> tuple[bool, Optional[str]]:
    """
    通用参数验证
    Args:
        params: 参数字典
        required_keys: 必需参数键列表
    Returns:
        (是否有效, 错误信息)
    """
    for key in required_keys:
        if key not in params or params[key] is None:
            return False, f"{key} is required"
    return True, None

def build_request_body(required: Dict[str, Any], optional: Dict[str, Any]) -> Dict[str, Any]:
    """
    构建请求体
    Args:
        required: 必需参数
        optional: 可选参数
    Returns:
        请求体字典
    """
    body = {**required}
    for key, value in optional.items():
        if value is not None:
            body[key] = value
    return body

def build_query_params(**kwargs) -> Dict[str, Any]:
    """
    构建查询参数字典，过滤掉 None 值
    Args:
        **kwargs: 查询参数键值对
    Returns:
        干净的查询参数字典（不包含 None 值）
    """
    query = {}
    for key, value in kwargs.items():
        if value is not None:
            query[key] = value
    return query

def get_available_flavor(
    access,
    availability_zone: Optional[str] = None,
    arch: Optional[str] = None,
    prefer_resource_flavor: bool = True,
    limit: int = 100
) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    自动获取可用的规格（优先 resource_flavor）
    当用户没有指定 flavor 或 resource_flavor 时，自动查询可用规格：
    1. 优先查询 resource_flavor（ListDevServerResourceflavors）
    2. 如果没有可用的 resource_flavor，回退到 flavor（ListDevServerFlavors）
    3. 过滤掉售罄（sold_out）的规格
    Args:
        access: 认证后的 access 对象
        availability_zone: 可用区过滤 (optional)
        arch: 架构类型过滤 (optional) - X86 或 ARM
        prefer_resource_flavor: 是否优先使用 resource_flavor (默认 True)
        limit: 查询数量限制 (默认 100)
    Returns:
        (是否成功, 错误信息, 选中的规格信息 {"flavor": xxx, "resource_flavor": xxx})
        当成功时，第三个参数为规格详情，失败时为 None
    示例:
        >>> success, error, flavor_info = get_available_flavor(access, arch="X86")
        >>> if success:
        ...     print(f"Selected: {flavor_info}")
    """
    from common_module.api_helper import make_api_call
    
    def query_resource_flavors():
        """查询 resource_flavor"""
        query = {"limit": limit}
        if availability_zone:
            query["availability_zone"] = availability_zone
        if arch:
            query["arch"] = arch
        return access.sdk().execute(lambda s: make_api_call(
            s, 'GET', '/v1/{project_id}/dev-servers/resource-flavors', query=query
        ))
    
    def query_flavors():
        """查询普通 flavor"""
        query = {"limit": limit}
        if availability_zone:
            query["availability_zone"] = availability_zone
        if arch:
            query["arch"] = arch
        return access.sdk().execute(lambda s: make_api_call(
            s, 'GET', '/v1/{project_id}/dev-servers/flavors', query=query
        ))
    
    def filter_available(flavors: List[Dict], flavor_type: str) -> List[Dict]:
        """
        过滤可用规格，排除售罄状态
        Args:
            flavors: 规格列表
            flavor_type: "resource_flavor" 或 "flavor"
        Returns:
            可用规格列表
        """
        available = []
        for f in flavors:
            # 检查售罄状态 - 通常字段名为 "sold_out" 或 "status"
            sold_out = f.get("sold_out", False) or f.get("status") == "sold_out"
            if not sold_out:
                available.append(f)
        return available
    if prefer_resource_flavor:
        try:
            result = query_resource_flavors()
            if result and isinstance(result, (list, dict)):
                flavors = result if isinstance(result, list) else result.get("data", result.get("flavors", []))
                available = filter_available(flavors, "resource_flavor")
                if available:
                    # 选择第一个可用规格
                    selected = available[0]
                    return True, None, {
                        "resource_flavor": selected.get("resource_flavor_id") or selected.get("name"),
                        "flavor": None,
                        "flavor_info": selected,
                        "flavor_type": "resource_flavor"
                    }
        except Exception as e:
            # resource_flavor 查询失败，继续尝试 flavor
            pass
    try:
        result = query_flavors()
        if result and isinstance(result, (list, dict)):
            flavors = result if isinstance(result, list) else result.get("data", result.get("flavors", []))
            available = filter_available(flavors, "flavor")
            if available:
                # 选择第一个可用规格
                selected = available[0]
                return True, None, {
                    "flavor": selected.get("flavor_id") or selected.get("name"),
                    "resource_flavor": None,
                    "flavor_info": selected,
                    "flavor_type": "flavor"
                }
    except Exception as e:
        return False, f"查询 flavor 失败: {str(e)}", None
    return False, "未找到可用的规格，请检查可用区或架构参数", None

def get_image_by_flavor(
    access,
    flavor: Optional[str] = None,
    resource_flavor: Optional[str] = None,
    arch: Optional[str] = None,
    limit: int = 100
) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    根据规格自动获取可用镜像
    当用户没有指定 image_id 时，根据已选的规格自动查询可用镜像：
    1. 使用 flavor 或 resource_flavor 查询 ListDevServerImages
    2. 返回可用的镜像
    Args:
        access: 认证后的 access 对象
        flavor: 规格名称 (optional)
        resource_flavor: 资源规格名称 (optional)
        arch: 架构类型过滤 (optional) - X86 或 ARM
        limit: 查询数量限制 (默认 100)
    Returns:
        (是否成功, 错误信息, 选中的镜像信息)
        当成功时，第三个参数包含镜像详情，失败时为 None
    示例:
        >>> success, error, image_info = get_image_by_flavor(access, resource_flavor="snt9c.2xlarge")
        >>> if success:
        ...     print(f"Selected image: {image_info['image_id']}")
    """
    from common_module.api_helper import make_api_call
    query = {"limit": limit}
    if resource_flavor:
        query["resource_flavor"] = resource_flavor
    elif flavor:
        query["flavor"] = flavor
    if arch:
        query["arch"] = arch
    try:
        result = access.sdk().execute(lambda s: make_api_call(
            s, 'GET', '/v1/{project_id}/dev-servers/images', query=query
        ))
        if result and isinstance(result, (list, dict)):
            images = result if isinstance(result, list) else result.get("data", result.get("images", []))
            if images:
                # 选择第一个可用镜像
                selected = images[0]
                return True, None, {
                    "image_id": selected.get("image_id") or selected.get("id"),
                    "image_name": selected.get("name"),
                    "image_info": selected
                }
        return False, "未找到可用镜像", None
    except Exception as e:
        return False, f"查询镜像失败: {str(e)}", None
# 导出所有公共函数
__all__ = [
    'validate_dev_server_params',
    'format_paginated_result',
    'add_api_reference',
    'validate_required_params',
    'build_request_body',
    'build_query_params',
    'get_available_flavor',
    'get_image_by_flavor',
    'execute_hyperinstance_operation',
    'format_hyperinstance_list_result'
]
