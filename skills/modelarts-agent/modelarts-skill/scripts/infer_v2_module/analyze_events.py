#!/usr/bin/env python3

"""分析服务事件模块 - v2版本"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, simple_api_call, Dict, Any

def check_service_id(service_id):
    if not service_id: return "服务ID不能为空"
    return None

@authenticated_api_call
def ma_inference_service_analyze_events(access, service_id: str, **kwargs) -> Dict[str, Any]:
    """分析服务事件 - v2版本"""
    check = check_service_id(service_id)
    if check: return format_api_result(False, error=check)

    print(f"  分析服务v2事件: {service_id}")

    events_result = simple_api_call(access, 'GET', '/v2/{project_id}/services/{service_id}/events', 
                                  service_id=service_id, query={"limit": 100})

    if isinstance(events_result, dict) and "events" in events_result:
        events = events_result["events"]
        analysis = {
            "total_events": len(events),
            "error_count": sum(1 for e in events if e.get("level") in ["ERROR", "FATAL"]),
            "warning_count": sum(1 for e in events if e.get("level") == "WARNING"),
            "info_count": sum(1 for e in events if e.get("level") == "INFO"),
            "recent_errors": [e for e in events if e.get("level") in ["ERROR", "FATAL"]][:10],
            "service_id": service_id
        }
        return format_api_result(True, data=analysis)
    else:
        return format_api_result(True, data={"total_events": 0, "service_id": service_id})

@authenticated_api_call
def quick_analyze_v2_events(access, service_id: str) -> Dict[str, Any]:
    """快速分析v2服务事件"""
    return ma_inference_service_analyze_events(access, service_id=service_id)

__all__ = ['ma_inference_service_analyze_events', 'quick_analyze_v2_events']
