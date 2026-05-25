#!/usr/bin/env python3
"""
Inference模块 - 模型查询模块
功能：根据查询和用的部署模型
"""

import sys, os, logging
logger = logging.getLogger(__name__)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from infer_v1_module._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, make_api_call, Dict, Any

std_custom = lambda m: {"id": m.get("model_id"), "name": m.get("model_name", "未命名"), "type": "custom",
    "model_version": m.get("model_version"), "model_type": m.get("model_type"),
    "description": m.get("description", ""), "model_status": m.get("model_status"),
    "create_at": m.get("create_at"), "install_type": m.get("install_type", []), "model_source": m.get("model_source")}

std_sub = lambda s: {"id": s.get("content_id"), "name": s.get("content_name", "未命名"), "type": "subscription",
    "subscription_id": s.get("subscription_id"), "content_type": s.get("content_type"),
    "description": s.get("content_detail_info", {}).get("description", ""), "cover_url": s.get("cover_url"),
    "status": s.get("status"), "short_desc": s.get("short_desc", "")}

fetch_custom = lambda a, w, l, o: [std_custom(m) for m in (a.sdk().execute(lambda s: make_api_call(s, 'GET', '/v1/{project_id}/models',
    query={'workspace_id': w, 'limit': l, 'offset': o})) or {}).get('models', [])]

def fetch_sub_versions(a, sid, w):
    try:
        v = (a.sdk().execute(lambda s: make_api_call(s, 'GET', f'/v1/aihub/model/subscriptions/{sid}/versions',
            query={'offset': 0, 'limit': 10, 'status': '', 'region': 'cn-north-4', 'project_name': 'cn-north-4',
                   'sort_dir': 'desc', 'sort_key': 'gmt_create', 'workspace_id': w})) or {}).get('versions', [])
        return v[0] if v else {}
    except Exception as e:
        logger.warning(f"获取版本失败: {e}")
    return {}

fetch_subs = lambda a, w, l, o: [dict(std_sub(s), **{"model_version": v.get("version_num"),
    "install_type": v.get("install_type", []), "model_type": None, "version_detail": v})
    for s in ((a.sdk().execute(lambda s: make_api_call(s, 'GET', '/v1/aihub/subscriptions',
    query={'content_types': 'model', 'status': '1', 'search_content': '', 'attribute_id': '', 'offset': o,
           'limit': max(5, l) if l > 0 else 5, 'sort_by': 'desc', 'workspace_id': w})) or {}).get('subscription_infos', []))
    if (v := fetch_sub_versions(a, s.get("subscription_id", ""), w)) and "real-time" in v.get("install_type", [])]

@authenticated_api_call
def ma_old_inference_list_models(access, workspace_id: str = '0', model_type: str = 'all', limit: int = 100, offset: int = 0, **kwargs) -> Dict[str, Any]:
    print(f"  查询所有可用模型 (类型: {model_type})")
    try:
        c, s = ([], [])[::1]
        if model_type in ['all', 'custom']:
            c = fetch_custom(access, workspace_id, limit, offset)
            print(f"  找到 {len(c)} 个自定义模型")
        if model_type in ['all', 'subscription']:
            s = fetch_subs(access, workspace_id, limit, offset)
            print(f"  找到 {len(s)} 个订阅模型")
        return format_api_result(True, data={"custom_models": c, "subscription_models": s,
            "total_count": len(c) + len(s), "summary": {"custom_count": len(c), "subscription_count": len(s)}})
    except Exception as e:
        return format_api_result(False, error=str(e))

@authenticated_api_call
def ma_old_inference_list_custom_models(access, workspace_id: str = '0', limit: int = 100, offset: int = 0, **kwargs) -> Dict[str, Any]:
    print(f"  查询自定义模型")
    try:
        models = fetch_custom(access, workspace_id, limit, offset)
        print(f"  找到 {len(models)} 个自定义模型")
        return format_api_result(True, data=models)
    except Exception as e:
        return format_api_result(False, error=str(e))

@authenticated_api_call
def ma_old_inference_list_subscription_models(access, workspace_id: str = '0', limit: int = 100, offset: int = 0, **kwargs) -> Dict[str, Any]:
    print(f"  查询订阅模型")
    try:
        models = fetch_subs(access, workspace_id, limit, offset)
        return format_api_result(True, data=models)
    except Exception as e:
        return format_api_result(False, error=str(e))

@authenticated_api_call
def get_subscription_model_versions(access, subscription_id: str, workspace_id: str = '0', limit: int = 10, **kwargs) -> Dict[str, Any]:
    print(f"  查询订阅模型版本 (subscription_id: {subscription_id})")
    try:
        result = access.sdk().execute(lambda s: make_api_call(s, 'GET',
            f'/v1/aihub/model/subscriptions/{subscription_id}/versions',
            query={'offset': 0, 'limit': limit, 'status': '', 'region': 'cn-north-4', 'project_name': 'cn-north-4',
                   'sort_dir': 'desc', 'sort_key': 'gmt_create', 'workspace_id': workspace_id}))
        if isinstance(result, dict):
            versions = result.get('versions', [])
            print(f"  找到 {len(versions)} 个版本")
            return format_api_result(True, data={"versions": versions, "total_count": result.get('total_count', len(versions))})
        return format_api_result(True, data=result)
    except Exception as e:
        return format_api_result(False, error=str(e))

__all__ = ['ma_old_inference_list_models', 'ma_old_inference_list_custom_models', 'ma_old_inference_list_subscription_models', 'get_subscription_model_versions']
