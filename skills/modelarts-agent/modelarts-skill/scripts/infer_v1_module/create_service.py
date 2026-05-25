#!/usr/bin/env python3
"""
创建推理服务模块
"""

import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from infer_v1_module._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, make_api_call, Dict, Any

_conf = {"confirmed": False, "service_config": None, "timestamp": None}

def clear_conf():
    global _conf
    _conf = {"confirmed": False, "service_config": None, "timestamp": None}

def check_name(name):
    if not name: return "服务名称不能为空"
    return None

def check_model(model_id):
    if not model_id: return "模型ID不能为空"
    return None

def check_count(count):
    if not 1 <= count <= 128: return "实例数量必须在1-128之间"
    return None

def check_infer(t):
    if t not in ["real-time", "batch", "edge"]: return "推理类型必须是real-time、batch或edge"
    return None

def build_body(name, model_id, spec, ws, count, desc, infer, weight, timeout, hours, **kw):
    b = {"service_name": name, "model_id": model_id, "instance_count": count, "workspace_id": ws,
         "infer_type": infer, "specification": spec, "weight": weight, "deploy_timeout_seconds": timeout,
         "config": [{"model_id": model_id, "specification": spec, "instance_count": count}],
         "schedule": [{"type": "stop", "time_unit": "HOURS", "duration": hours}]}
    if desc: b["description"] = desc
    b.update(kw)
    return b

@authenticated_api_call
def ma_old_inference_service_create(access, name: str, model_id: str, specification: str = "modelarts.vm.cpu.2u",
    instance_count: int = 1, workspace_id: str = "0", description: str = None, infer_type: str = "real-time",
    weight: int = 100, deploy_timeout_seconds: int = 1200, schedule_stop_hours: int = 1, force_confirm: bool = False, **kwargs) -> Dict[str, Any]:
    """创建推理服务"""
    for check, msg in [(check_name(name), "name"), (check_model(model_id), "model"),
                        (check_count(instance_count), "count"), (check_infer(infer), "infer")]:
        if check: return format_api_result(False, error=check)

    if not force_confirm:
        p = _conf.get("service_config")
        if not p: return format_api_result(False, error="请先确认配置")
        if p.get("name") != name or p.get("model_id") != model_id or p.get("specification") != specification:
            return format_api_result(False, error="配置已变更")
        if _conf.get("timestamp") and (time.time() - _conf["timestamp"]) > 180:
            clear_conf()
            return format_api_result(False, error="确认已过期")
    
    print(f"  创建: {name}, 模型:{model_id}, 规格:{specification}, 实例:{instance_count}")
    result = access.sdk().execute(lambda s: make_api_call(s, 'POST', '/v1/{project_id}/services',
        body=build_body(name, model_id, specification, workspace_id, instance_count, description, infer_type,
                        weight, deploy_timeout_seconds, schedule_stop_hours, **kwargs)))
    clear_conf()
    return format_api_result(True, data=result)

@authenticated_api_call
def quick_create_old_service(access, name: str, model_id: str, specification: str = "modelarts.vm.cpu.2u",
    instance_count: int = 1, workspace_id: str = "0", description: str = None, **kwargs) -> Dict[str, Any]:
    """快速创建"""
    return ma_old_inference_service_create(access, name, model_id, specification, instance_count,
                                          workspace_id, description, force_confirm=True, **kwargs)

__all__ = ['ma_old_inference_service_create', 'quick_create_old_service', 'clear_conf']
