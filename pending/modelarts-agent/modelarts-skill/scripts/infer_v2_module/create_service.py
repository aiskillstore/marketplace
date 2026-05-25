#!/usr/bin/env python3

"""创建推理服务模块 - v2版本"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, simple_api_call, Dict, Any, List

def check_name(name):
    if not name or len(name) > 64: return "服务名称必须为1-64字符"
    return None

def check_image(image_path):
    if not image_path: return "镜像路径不能为空"
    return None

def check_deploy_type(deploy_type):
    if deploy_type not in ["SINGLE", "MULTI"]: return "部署类型必须是SINGLE或MULTI"
    return None

def check_protocol(protocol):
    if protocol not in ["HTTP", "HTTPS", "WSS", "WS"]: return "协议必须是HTTP/HTTPS/WSS/WS"
    return None

def check_auth_type(auth_type):
    if auth_type not in ["TOKEN", "API_KEY", "NONE"]: return "认证类型必须是TOKEN/API_KEY/NONE"
    return None

def check_instance_count(count):
    if not 1 <= count <= 128: return "实例数量必须在1-128之间"
    return None

def check_port(port):
    if not 1 <= port <= 65535: return "端口必须在1-65535之间"
    return None

def check_deploy_timeout(timeout):
    if not 1 <= timeout <= 300: return "部署超时时间必须在1-300分钟之间"
    return None

def build_v2_body(name, version, deploy_type, image_path, instance_count, port, protocol, 
                  auth_type, workspace_id, deploy_timeout_minutes, description, tags,
                  custom_spec=None, pool_id=None):
    """构建v2 API请求体"""

    unit_config = {
        "image": {
            "source": "SWR",
            "swr_path": image_path
        },
        "count": 1  # 每个单元的实例数量，默认为1
    }

    if custom_spec:
        unit_config["custom_spec"] = custom_spec
        print(f"  ⚙️  使用自定义规格: {custom_spec}")

    group_config = {
        "weight": 100,
        "name": f"instance-{name}",
        "count": instance_count,
        "unit_configs": [unit_config]
    }

    if pool_id:
        group_config["pool_id"] = pool_id
        print(f"  🏊  使用专属池: {pool_id}")
    
    body = {
        "name": name,
        "version": version,
        "type": "REAL_TIME",
        "deploy_type": deploy_type,
        "deploy_timeout_minutes": deploy_timeout_minutes,
        "workspace_id": workspace_id,
        "group_configs": [group_config],
        "runtime_config": {
            "service_invoke": {
                "port": port,
                "protocol": protocol,
                "auth_type": auth_type
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

    if description:
        body["description"] = description

    if tags:
        body["tags"] = tags

    return body

@authenticated_api_call
def ma_inference_service_create(access, name: str, version: str = "1.0.0", deploy_type: str = "SINGLE",
    image_path: str = None, instance_count: int = 1, port: int = 8080, protocol: str = "HTTP",
    auth_type: str = "NONE", workspace_id: str = "0", description: str = None, 
    tags: List[Dict[str, str]] = None, deploy_timeout_minutes: int = 30, 
    custom_spec: Dict[str, Any] = None, pool_id: str = None, **kwargs) -> Dict[str, Any]:
    """创建推理服务 - v2版本"""
    checks = [
        (check_name(name), "name"),
        (check_image(image_path), "image"),
        (check_deploy_type(deploy_type), "deploy_type"),
        (check_protocol(protocol), "protocol"),
        (check_auth_type(auth_type), "auth_type"),
        (check_instance_count(instance_count), "instance_count"),
        (check_port(port), "port"),
        (check_deploy_timeout(deploy_timeout_minutes), "deploy_timeout")
    ]

    for check, param in checks:
        if check: return format_api_result(False, error=f"{param}: {check}")

    print(f"  创建推理服务v2: {name}, 镜像:{image_path}, 实例:{instance_count}")

    body = build_v2_body(name, version, deploy_type, image_path, instance_count, port, 
                        protocol, auth_type, workspace_id, deploy_timeout_minutes, 
                        description, tags, custom_spec, pool_id)

    result = simple_api_call(access, 'POST', '/v2/{project_id}/services', body=body)

    return format_api_result(True, data=result)

@authenticated_api_call
def quick_create_v2_service(access, name: str, image_path: str, **kwargs) -> Dict[str, Any]:
    """快速创建v2服务"""
    return ma_inference_service_create(access, name=name, image_path=image_path, **kwargs)

__all__ = ['ma_inference_service_create', 'quick_create_v2_service']
