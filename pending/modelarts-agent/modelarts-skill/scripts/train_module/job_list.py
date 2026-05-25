#!/usr/bin/env python3
"""
训练模块 - 任务列表查询

功能：训练任务的查询和列表功能
"""

import sys
from typing import Dict, Any, List, Optional

sys.path.insert(0, '.')

from common_module import ensure_authentication, format_api_result
from train_module.common import format_error_result, format_success_result


def _validate_list_params(offset: int, limit: int, order: str) -> Optional[Dict[str, Any]]:
    if offset < 0:
        return format_error_result(f"参数错误: offset ({offset}) 不能小于0", 400)
    if limit < 1 or limit > 50:
        return format_error_result(f"参数错误: limit ({limit}) 必须在1-50之间", 400)
    if order not in ["asc", "desc"]:
        return format_error_result(f"参数错误: order ({order}) 必须是'asc'或'desc'", 400)
    return None


def _build_list_request_body(workspace_id: str, offset: int, limit: int,
                              sort_by: str, order: str, group_by: str = None,
                              unified_jobs: bool = False, train_type: str = None,
                              filters: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    request_body = {
        "workspace_id": workspace_id,
        "offset": offset,
        "limit": limit,
        "sort_by": sort_by,
        "order": order
    }
    
    if group_by:
        request_body["group_by"] = group_by
    if unified_jobs:
        request_body["unified_jobs"] = unified_jobs
    if train_type and unified_jobs:
        request_body["train_type"] = train_type

    if filters is None:
        try:
            from modelarts.session import Session
            session = Session()
            user_name = getattr(session, 'user_name', None)
            if user_name:
                request_body["filters"] = [{"key": "user_name", "operator": "in", "value": [user_name]}]
        except Exception as e:
            print(f"Warning: Failed to get user_name for filter: {e}")
            pass
    else:
        request_body["filters"] = filters
    
    return request_body


def _build_pagination(total: int, offset: int, limit: int, jobs_count: int) -> Dict[str, Any]:
    total_pages = (total + limit - 1) // limit
    current_page = offset // limit + 1
    remaining = total - (offset + jobs_count)
    
    return {
        "total_pages": total_pages,
        "current_page": current_page,
        "has_next": remaining > 0,
        "remaining_jobs": max(0, remaining)
    }


def _process_list_response(api_result: Dict[str, Any], offset: int, limit: int,
                           request_body: Dict[str, Any], debug: bool = False) -> Dict[str, Any]:
    if "items" not in api_result:
        error_msg = api_result.get("error_msg", api_result.get("error", "Unknown API error"))
        return format_error_result(f"API error: {error_msg}", 500)
    
    jobs = api_result.get("items", [])
    total = api_result.get("total", 0)
    normalized_jobs = [_normalize_job_info(job) for job in jobs]
    
    response_data = {
        "total": total,
        "jobs": normalized_jobs,
        "offset": offset,
        "limit": limit
    }
    
    if limit > 0:
        response_data["pagination"] = _build_pagination(total, offset, limit, len(normalized_jobs))
    
    result = format_success_result(data=response_data, status_code=api_result.get("status_code", 200))
    
    if debug:
        result["debug_info"] = {
            "request_body": request_body,
            "raw_response": api_result,
            "access_source": "modelarts-v2"
        }
    
    return result


def ma_train_job_list(workspace_id: str = "0",
                     offset: int = 0, limit: int = 20,
                     sort_by: str = "create_time", order: str = "desc",
                     group_by: str = None, unified_jobs: bool = False,
                     train_type: str = None, filters: List[Dict[str, Any]] = None,
                     debug: bool = False) -> Dict[str, Any]:
    """
    查询训练作业列表
    
    接口: POST /v2/{project_id}/training-job-searches
    
    📌 分页说明:
    - total: 总作业数量
    - offset: 当前页起始位置
    - limit: 每页数量 (1-50)
    - pagination.current_page: 当前页码
    - pagination.has_next: 是否有下一页
    
    Args:
        workspace_id: 工作空间 ID，默认 "0"
        offset: 查询起始位置，默认 0
        limit: 每页数量，默认 20，最大 50
        sort_by: 排序字段，默认 "create_time"
        order: 排序方向，默认 "desc" (desc/asc)
        filters: 过滤条件列表
            示例: [{"key": "phase", "operator": "in", "value": ["Running"]}]
        debug: 是否返回调试信息
    
    Returns:
        Dict[str, Any]: 
        {
            "success": bool,
            "data": {
                "total": int,
                "jobs": [作业列表],
                "pagination": {...}
            },
            "data_reminder": str
        }
    
    Related:
        - 停止任务: train_module.ma_train_job_stop()
        - 删除任务: train_module.ma_train_job_delete()
    """
    try:
        validation_error = _validate_list_params(offset, limit, order)
        if validation_error:
            return validation_error
        auth_result = ensure_authentication()
        if not auth_result['success']:
            return format_api_result(False, error=auth_result.get('error', 'Authentication failed'))
        access = auth_result['access']
        request_body = _build_list_request_body(
            workspace_id, offset, limit, sort_by, order,
            group_by, unified_jobs, train_type, filters
        )
        def _list_jobs(session):
            from modelarts.config.auth import auth_by_apig
            import json
            path = f"/v2/{session.project_id}/training-job-searches"
            body_bytes = json.dumps(request_body).encode('utf-8')
            headers = {'Content-Type': 'application/json'}
            if hasattr(session, 'user_id') and session.user_id:
                headers['x-modelarts-user-id'] = session.user_id
            return auth_by_apig(session, "POST", path, body=body_bytes, headers=headers)
        
        api_result = access.sdk().execute(_list_jobs)

        return _process_list_response(api_result, offset, limit, request_body, debug)
            
    except Exception as e:
        return format_api_result(False, error=f"Unexpected error: {str(e)}")


def _normalize_job_info(job: Dict[str, Any]) -> Dict[str, Any]:
    metadata = job.get("metadata", {})
    job_id = metadata.get("id", "") or job.get("id") or ""
    name = metadata.get("name", "") or job.get("name") or ""
    create_time = metadata.get("create_time", 0) or job.get("create_time", 0)
    user_name = metadata.get("user_name", "") or job.get("user_name", "")

    status = job.get("status", {})
    phase = "Unknown"
    if isinstance(status, dict):
        phase = status.get("phase", "Unknown")
    elif status:
        phase = str(status)
    
    runtime_type = job.get("runtime_type", "")
    spec = job.get("spec", {})
    if spec and isinstance(spec, dict):
        runtime_type = spec.get("runtime_type", runtime_type)
    
    pool_id = ""
    resource = spec.get("resource", {}) if isinstance(spec, dict) else {}
    if isinstance(resource, dict):
        pool_id = resource.get("pool_id", "")
    
    return {
        "id": job_id,
        "name": name,
        "phase": phase,
        "create_time": create_time,
        "user_name": user_name,
        "runtime_type": runtime_type,
        "pool_id": pool_id,
        "status": phase
    }


def list_training_jobs_simple() -> Dict[str, Any]:
    """查询所有训练任务的简化版本"""
    return ma_train_job_list(limit=10)


def list_debug_training_jobs() -> Dict[str, Any]:
    """查询调试模式训练任务"""
    return ma_train_job_list(filters=[{"key": "runtime_type", "operator": "eq", "value": "debug"}])


def list_running_training_jobs() -> Dict[str, Any]:
    """查询运行中的训练任务"""
    return ma_train_job_list(filters=[{"key": "status", "operator": "in", "value": ["Running", "Pending"]}])


def list_pending_training_jobs() -> Dict[str, Any]:
    """查询等待中的训练任务"""
    return ma_train_job_list(filters=[{"key": "status", "operator": "eq", "value": "Pending"}])


def list_completed_training_jobs() -> Dict[str, Any]:
    """查询已完成的训练任务"""
    return ma_train_job_list(filters=[{"key": "status", "operator": "in", "value": ["Completed", "Succeeded", "Failed"]}])


__all__ = [
    'ma_train_job_list',
    'list_training_jobs_simple',
    'list_debug_training_jobs',
    'list_running_training_jobs',
    'list_pending_training_jobs',
    'list_completed_training_jobs',
    '_normalize_job_info'
]
