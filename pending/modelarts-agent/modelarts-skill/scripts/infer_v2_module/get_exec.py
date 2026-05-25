#!/usr/bin/env python3

"""查询服务exec登录信息模块 - v2版本"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, simple_api_call, Dict, Any

def check_service_id(service_id):
    if not service_id: return "服务ID不能为空"
    return None

def check_instance_group(instance_group):
    if not instance_group: return "实例组名不能为空"
    return None

def check_instance_name(instance_name):
    if not instance_name: return "实例名不能为空"
    return None

def check_pod_name(pod_name):
    if not pod_name: return "Pod实例名不能为空"
    return None

@authenticated_api_call
def ma_inference_service_get_exec(access, service_id: str, instance_group: str, instance_name: str, pod_name: str, **kwargs) -> Dict[str, Any]:
    """查询服务exec登录信息 - v2版本
    调用此接口可获取在线服务容器的 exec 登录信息（如容器 ID、登录命令等），
    用于调试或查看操作。调用者需具备足够权限，且目标容器必须处于运行状态。
    参数:
        access: 认证信息
        service_id: 服务ID，创建服务时返回，或通过"查询服务列表"接口获取
        instance_group: 实例组名，创建服务时自动生成，或通过"查询服务实例组列表"接口获取
        instance_name: 实例名，创建服务时填写，或通过"查询服务实例列表"接口获取
        pod_name: Pod实例名，由K8S自动生成，或通过"查询服务pod列表"接口获取
    返回:
        包含exec登录信息的字典，包括:
        - endpoint: 资源池 api-server 地址
        - pod_name: 待登录的容器名
        - pod_status: Pod状态
        - container_name: 待登录的容器名
        - namespace: Pod所在的namespace
        - cluster_token: 集群所属租户token
    """
    checks = [
        (check_service_id(service_id), "service_id"),
        (check_instance_group(instance_group), "instance_group"),
        (check_instance_name(instance_name), "instance_name"),
        (check_pod_name(pod_name), "pod_name")
    ]

    for check, param in checks:
        if check: return format_api_result(False, error=f"{param}: {check}")

    print(f"  查询服务v2 exec登录信息: {service_id}")
    print(f"  实例组: {instance_group}, 实例名: {instance_name}, Pod: {pod_name}")

    query = {
        "instance_group": instance_group,
        "instance_name": instance_name,
        "pod_name": pod_name
    }

    if kwargs:
        query.update(kwargs)

    try:
        result = simple_api_call(access, 'GET', '/v2/{project_id}/services/{service_id}/exec', 
                               query=query, service_id=service_id)

        if not result:
            return format_api_result(False, error="API返回空结果")
            
        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"API调用失败: {str(e)}")

@authenticated_api_call
def quick_get_v2_exec(access, service_id: str, instance_group: str) -> Dict[str, Any]:
    """快速查询v2服务exec信息（简化版）
    
    适用于已知服务ID和实例组的情况，需要用户提供实例名和Pod名
    
    参数:
        access: 认证信息
        service_id: 服务ID
        instance_group: 实例组名
        
    返回:
        需要用户进一步提供实例名和Pod名
    """
    print(f"  快速查询服务v2 exec信息: {service_id} (实例组: {instance_group})")
    print("  提示: 需要提供实例名(instance_name)和Pod名(pod_name)参数")
    
    return format_api_result(True, 
                           message="需要实例名和Pod名参数",
                           required_params=["instance_name", "pod_name"])

__all__ = ['ma_inference_service_get_exec', 'quick_get_v2_exec']