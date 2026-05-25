#!/usr/bin/env python3
"""
训练模块 - 获取公共规格

功能：获取训练作业支持的公共规格列表
"""

import sys
from typing import Dict, Any, Optional

sys.path.insert(0, '.')

from common_module import ensure_authentication, format_api_result
from train_module.common import format_error_result, format_success_result


def ma_train_job_get_flavors(flavor_type: Optional[str] = None,
                              debug: bool = False) -> Dict[str, Any]:
    """
    获取训练作业支持的公共规格列表
    
    接口: GET /v2/{project_id}/training-job-flavors
    
    📌 使用场景:
    创建公共池训练任务时，需要先获取可用的公共规格
    然后使用 flavor_id 和 flavor_label 来创建任务
    
    Args:
        flavor_type (str, 可选): 查询训练作业规格的类型
            取值范围:
                - "CPU": CPU资源规格
                - "GPU": GPU资源规格
                - "Ascend": NPU资源规格
                - 不填: 查询所有规格
        debug: 是否返回调试信息
    
    Returns:
        Dict[str, Any]:
        {
            "success": bool,
            "data": {
                "total_count": int,
                "flavors": [
                    {
                        "flavor_id": str,
                        "flavor_name": str,
                        "flavor_type": str,
                        "pool_id": str,
                        "max_num": int,
                        "flavor_info": {
                            "max_num": int,
                            "cpu": {"arch": str, "core_num": int},
                            "gpu": {"unit_num": int, "product_name": str, "memory": str},
                            "npu": {"unit_num": str, "product_name": str, "memory": str},
                            "memory": {"size": int, "unit": str},
                            "disk": {"size": int, "unit": str}
                        },
                        "billing": {"code": str, "unit_num": int},
                        "attributes": {}
                    },
                    ...
                ]
            },
            "status_code": int
        }
    
    Example:
        # 获取所有公共规格
        from train_module import ma_train_job_get_flavors
        result = ma_train_job_get_flavors()
        
        # 只获取 GPU 规格
        result = ma_train_job_get_flavors(flavor_type="GPU")
        
        if result['success']:
            for flavor in result['data']['flavors']:
                print(f"{flavor['flavor_name']}: {flavor['flavor_id']}")
    
    Related:
        - 创建公共池任务: train_module.ma_train_job_create() (使用 flavor_id, flavor_label)
    """
    try:
        auth_result = ensure_authentication()
        if not auth_result['success']:
            return format_api_result(False, error=auth_result.get('error', 'Authentication failed'))
        
        access = auth_result['access']

        query_params = {}
        if flavor_type:
            if flavor_type not in ["CPU", "GPU", "Ascend"]:
                return format_error_result(
                    error=f"无效的 flavor_type: {flavor_type}，取值范围: CPU, GPU, Ascend",
                    status_code=400
                )
            query_params["flavor_type"] = flavor_type

        def _get_flavors(session):
            from modelarts.config.auth import auth_by_apig
            
            path = f"/v2/{session.project_id}/training-job-flavors"
            
            headers = {'Content-Type': 'application/json'}
            if hasattr(session, 'user_id') and session.user_id:
                headers['x-modelarts-user-id'] = session.user_id
            
            return auth_by_apig(session, "GET", path, query=query_params if query_params else None, headers=headers)
        
        api_result = access.sdk().execute(_get_flavors)

        if "flavors" in api_result:
            result_data = api_result

            flavors = result_data.get("flavors", [])
            total_count = result_data.get("total_count", len(flavors))

            normalized_flavors = []
            for flavor in flavors:
                normalized = _normalize_flavor_info(flavor)
                normalized_flavors.append(normalized)
            
            result = format_success_result(
                data={
                    "total_count": total_count,
                    "flavors": normalized_flavors
                },
                status_code=200
            )

            if debug:
                result["debug_info"] = {
                    "request_path": f"/v2/{{project_id}}/training-job-flavors",
                    "query_params": query_params,
                    "raw_flavors_count": len(flavors)
                }
            
            return result
        else:
            error_msg = api_result.get("error", "Unknown API error")
            status_code = api_result.get("status_code", 500)
            return format_error_result(
                error=f"获取公共规格失败: {error_msg}",
                status_code=status_code
            )
            
    except Exception as e:
        return format_api_result(False, error=f"Unexpected error: {str(e)}")


def _normalize_flavor_info(flavor: Dict[str, Any]) -> Dict[str, Any]:
    """
    规范化规格信息
    
    简化返回结构，便于使用
    """
    flavor_info = flavor.get("flavor_info", {})
    billing = flavor.get("billing", {})
    attributes = flavor.get("attributes", {})

    cpu_info = flavor_info.get("cpu", {})
    gpu_info = flavor_info.get("gpu", {})
    npu_info = flavor_info.get("npu", {})
    memory_info = flavor_info.get("memory", {})
    disk_info = flavor_info.get("disk", {})

    if gpu_info:
        label_parts = [f"{gpu_info.get('unit_num', 1)}*GP-Vnt1"]
    elif npu_info:
        label_parts = [f"{npu_info.get('unit_num', '1')}*NPU"]
    else:
        label_parts = [""]
    
    if cpu_info:
        label_parts.append(f"{cpu_info.get('core_num', 0)}vCPUs")
    
    if memory_info:
        label_parts.append(f"{memory_info.get('size', 0)}{memory_info.get('unit', 'GiB')}")
    
    flavor_label = " | ".join(label_parts)
    
    return {
        "flavor_id": flavor.get("flavor_id", ""),
        "flavor_name": flavor.get("flavor_name", ""),
        "flavor_type": flavor.get("flavor_type", ""),
        "pool_id": flavor.get("pool_id", ""),
        "max_num": flavor.get("max_num", 1),
        "flavor_label": flavor_label,
        "flavor_info": {
            "max_num": flavor_info.get("max_num", 1),
            "cpu": cpu_info,
            "gpu": gpu_info,
            "npu": npu_info,
            "memory": memory_info,
            "disk": disk_info
        },
        "billing": billing,
        "attributes": attributes
    }


def list_training_job_flavors(flavor_type: Optional[str] = None) -> Dict[str, Any]:
    """
    获取训练作业公共规格列表（简化版本）
    
    Args:
        flavor_type: 规格类型 (CPU/GPU/Ascend)
    
    Returns:
        规格列表
    
    Example:
        from train_module import list_training_job_flavors
        result = list_training_job_flavors(flavor_type="GPU")
    """
    return ma_train_job_get_flavors(flavor_type=flavor_type)


__all__ = [
    'ma_train_job_get_flavors',
    'list_training_job_flavors'
]
