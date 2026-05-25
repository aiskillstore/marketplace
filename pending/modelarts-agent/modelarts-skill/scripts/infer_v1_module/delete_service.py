#!/usr/bin/env python3
"""
Inference模块 - ma_old_inference_service_delete函数
功能：删除推理服务
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from infer_v1_module._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, simple_api_call, Dict, Any
from infer_v1_module.list_services import ma_old_inference_service_list


_delete_confirmation = {
    "confirmed": False,
    "confirmed_service_ids": [],
    "timestamp": None,
    "pending_service": None
}


def clear_confirmation():
    """清除删除确认状态"""
    global _delete_confirmation
    _delete_confirmation = {"confirmed": False, "confirmed_service_ids": [], "timestamp": None, "pending_service": None}


def preview_delete_services(status_filter: str = None) -> Dict[str, Any]:
    """预览待删除服务列表"""
    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    try:
        list_result = ma_old_inference_service_list(limit=100)
        if not list_result:
            return format_api_result(True, data={"services": [], "count": 0, "message": "当前没有服务"})
        services = list_result.get('services', [])
        if not services and 'data' in list_result:
            services = list_result.get('data', {}).get('services', [])
        if status_filter:
            services = [s for s in services if s.get('status') == status_filter]
        clear_confirmation()
        print("\n" + "="*50 + "\n⚠️  待删除服务列表\n" + "="*50)
        if not services:
            print("没有符合条件的服务")
            return format_api_result(True, data={"services": [], "count": 0})
        for i, s in enumerate(services, 1):
            print(f"{i}. {s.get('service_name')} ({s.get('service_id')}) - 状态: {s.get('status')}")
        print("="*50 + f"\n共 {len(services)} 个服务待删除\n")
        return format_api_result(True, data={"services": services, "count": len(services)})
    except Exception as e:
        return format_api_result(False, error=f"预览服务列表时发生异常: {e}")


def request_delete_confirmation(service_id: str, service_name: str) -> Dict[str, Any]:
    """请求二次确认删除"""
    global _delete_confirmation
    _delete_confirmation["pending_service"] = {"service_id": service_id, "service_name": service_name, "timestamp": time.time()}
    print(f"\n⚠️  高危操作确认\n服务名称: {service_name}\n服务ID: {service_id}\n⚠️  此操作不可恢复，确定要删除吗？\n请回复「确认删除 {service_name}」来确认删除\n")
    return format_api_result(True, data={"pending": True, "service_id": service_id, "service_name": service_name})


def confirm_final_delete(service_name: str) -> Dict[str, Any]:
    """最终确认删除"""
    global _delete_confirmation
    pending = _delete_confirmation.get("pending_service")
    if not pending:
        return format_api_result(False, error="没有待确认的删除操作，请先选择要删除的服务")
    if pending.get("service_name") != service_name:
        return format_api_result(False, error=f"服务名称不匹配，当前待确认: {pending.get('service_name')}")
    if pending.get("timestamp") and (time.time() - pending.get("timestamp")) > 180:
        clear_confirmation()
        return format_api_result(False, error="确认已过期，请重新选择服务")
    _delete_confirmation["confirmed"] = True
    _delete_confirmation["confirmed_service_ids"] = [pending.get("service_id")]
    _delete_confirmation["timestamp"] = time.time()
    print(f"\n✅ 已确认删除服务: {service_name} ({pending.get('service_id')})\n")
    return format_api_result(True, data={"confirmed": True, "service_id": pending.get("service_id"), "service_name": service_name})


@authenticated_api_call
def ma_old_inference_service_delete(
    access, service_id: str, workspace_id: str = '0', force: bool = False, **kwargs
) -> Dict[str, Any]:
    """删除推理服务"""
    global _delete_confirmation
    if not service_id:
        return format_api_result(False, error="service_id is required")
    if not force:
        if not _delete_confirmation["confirmed"]:
            return format_api_result(False, error="删除前必须先确认")
        if service_id not in _delete_confirmation["confirmed_service_ids"]:
            return format_api_result(False, error=f"服务 {service_id} 未在已确认的删除列表中")
        if _delete_confirmation["timestamp"] and (time.time() - _delete_confirmation["timestamp"]) > 300:
            clear_confirmation()
            return format_api_result(False, error="确认已过期，请重新操作")
    print(f"  删除推理服务: {service_id}")
    result = simple_api_call(access, 'DELETE', '/v1/{project_id}/services/{service_id}',
                            query={'workspace_id': workspace_id} if workspace_id != '0' else None, service_id=service_id)
    clear_confirmation()
    return format_api_result(True, data=result)


__all__ = ['ma_old_inference_service_delete', 'preview_delete_services', 'request_delete_confirmation', 'confirm_final_delete', 'clear_confirmation']
