#!/usr/bin/env python3

"""区域一致性创建服务模块 - v2版本"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, simple_api_call, Dict, Any, List

def check_name(name):
    if not name or len(name) > 64: return "服务名称必须为1-64字符"
    return None

def check_image(image_path):
    if not image_path: return "镜像路径不能为空"
    return None

@authenticated_api_call
def ma_inference_service_create_with_region_consistency(access, name: str, image_path: str, 
    **kwargs) -> Dict[str, Any]:
    """区域一致性创建服务 - v2版本"""

    checks = [
        (check_name(name), "name"),
        (check_image(image_path), "image_path")
    ]

    for check, param in checks:
        if check: return format_api_result(False, error=f"{param}: {check}")

    print(f"  区域一致性创建v2服务: {name}")

    region_result = simple_api_call(access, 'GET', '/v2/{project_id}/region/detect')

    if isinstance(region_result, dict) and "region" in region_result:
        region = region_result["region"]

        default_params = {
            "version": "1.0.0",
            "deploy_type": "SINGLE",
            "instance_count": 1,
            "port": 8080,
            "protocol": "HTTP",
            "auth_type": "NONE",
            "workspace_id": "0",
            "deploy_timeout_minutes": 30
        }

        params = default_params.copy()
        params.update(kwargs)
        params.update({"name": name, "image_path": image_path})

        create_body = {
            "name": name,
            "version": params["version"],
            "type": "REAL_TIME",
            "deploy_type": params["deploy_type"],
            "deploy_timeout_minutes": params["deploy_timeout_minutes"],
            "workspace_id": params["workspace_id"],
            "group_configs": [{
                "weight": 100,
                "name": f"instance-{name}",
                "count": params["instance_count"],
                "unit_configs": [{
                    "image": {
                        "source": "SWR",
                        "swr_path": image_path
                    }
                }]
            }],
            "runtime_config": {
                "service_invoke": {
                    "port": params["port"],
                    "protocol": params["protocol"],
                    "auth_type": params["auth_type"]
                },
                "service_limit": {
                    "request_size_limit": 20,
                    "request_timeout": 30,
                    "rate_limit": {
                        "num": 200,
                        "unit": "SECONDS"
                    }
                }
            },
            "upgrade_config": {
                "type": "ROLLING",
                "rolling_update": {
                    "max_surge": "20%",
                    "max_unavailable": "20%"
                }
            },
            "custom_metrics_path": "http,8080,metrics"
        }

        if "description" in params:
            create_body["description"] = params["description"]

        if "tags" in params:
            create_body["tags"] = params["tags"]

        result = simple_api_call(access, 'POST', '/v2/{project_id}/services', body=create_body)

        return format_api_result(True, data={
            "service_creation": result,
            "detected_region": region,
            "region_info": region_result
        })
    else:
        return format_api_result(False, error="无法检测区域信息")

@authenticated_api_call
def quick_create_v2_with_region(access, name: str, image_path: str) -> Dict[str, Any]:
    """快速区域一致性创建v2服务"""
    return ma_inference_service_create_with_region_consistency(access, name=name, image_path=image_path)

__all__ = ['ma_inference_service_create_with_region_consistency', 'quick_create_v2_with_region']
