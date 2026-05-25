#!/usr/bin/env python3
"""
训练模块 - 任务停止

功能：训练任务的停止和终止功能
"""

import sys
from typing import Dict, Any, List

sys.path.insert(0, '.')

from common_module import ensure_authentication, format_api_result
from train_module.common import format_error_result, format_success_result


def ma_train_job_stop(training_job_id: str, 
                     confirm: bool = False, debug: bool = False) -> Dict[str, Any]:
    """
    终止训练作业
    
    接口: POST /v2/{project_id}/training-jobs/{training_job_id}/actions
    
    ⚠️  【危险】终止操作不可逆！
        - 作业将立即停止运行，无法恢复
        - 已产生的数据和计算结果将丢失
        - 如需重新运行，需要重新创建任务
    
    Args:
        training_job_id: 训练作业 ID
            获取方式: 调用 train_module.ma_train_job_list()
        confirm (bool, 必填): 强制确认终止操作
            - 默认值: False
            - 当 confirm=False 时，返回提示信息，需要与大模型确认后传递 confirm=True 才能执行
            - 当 confirm=True 时，直接执行终止操作
            示例: ma_train_job_stop(job_id, confirm=True)
        debug: 是否返回调试信息
    
    Returns:
        Dict[str, Any]:
        {
            "success": bool,
            "job_id": str,
            "status_code": int
        }
    
    Example:
        # 终止任务（需要确认）
        from train_module import ma_train_job_stop
        result = ma_train_job_stop(
            training_job_id="job-xxx-xxx",
            confirm=True  # 确认后传递 True
        )
    
    Related:
        - 查询任务: train_module.ma_train_job_list()
        - 删除任务: train_module.ma_train_job_delete()
    """
    try:
        if not confirm:
            return {
                "success": False,
                "status_code": 400,
                "error": f"【终止任务需要确认】\n\n"
                           f"任务 ID: {training_job_id}\n"
                           f"⚠️  警告: 此操作不可逆，任务将立即停止运行\n\n"
                           f"请与用户确认是否终止此任务？\n"
                           f"确认后请再次调用并传递 confirm=True 参数。"
            }

        if not training_job_id or not training_job_id.strip():
            return format_error_result(
                error="必须提供有效的训练作业ID（training_job_id）",
                status_code=400
            )

        auth_result = ensure_authentication()
        if not auth_result['success']:
            return format_api_result(False, error=auth_result.get('error', 'Authentication failed'))
        
        access = auth_result['access']

        request_body = {
            "action_type": "terminate"
        }

        def _stop_job(session):
            from modelarts.config.auth import auth_by_apig
            import json
            
            path = f"/v2/{session.project_id}/training-jobs/{training_job_id}/actions"
            body_bytes = json.dumps(request_body).encode('utf-8')
            
            headers = {'Content-Type': 'application/json'}
            if hasattr(session, 'user_id') and session.user_id:
                headers['x-modelarts-user-id'] = session.user_id
            
            return auth_by_apig(session, "POST", path, body=body_bytes, headers=headers)
        
        api_result = access.sdk().execute(_stop_job)

        if "metadata" in api_result or "status" in api_result:
            result_data = api_result
            
            result = format_success_result(
                data=result_data,
                job_id=training_job_id,
                status_code=200
            )

            if debug:
                result["debug_info"] = {
                    "request_body": request_body,
                    "training_job_id": training_job_id,
                    "access_source": "modelarts-v2"
                }
            
            return result
        else:
            error_msg = api_result.get("error", "Unknown API error")
            error_code = api_result.get("status_code", 500)

            if error_code == 404:
                error_msg = f"训练作业不存在或已被删除: {training_job_id}"
            elif error_code == 409:
                error_msg = f"训练作业无法终止（可能已处于终止状态）: {training_job_id}"
            
            return format_error_result(
                error=f"终止作业失败: {error_msg}",
                status_code=error_code
            )
            
    except Exception as e:
        return format_api_result(False, error=f"Unexpected error: {str(e)}")


def stop_training_job_simple(training_job_id: str) -> Dict[str, Any]:
    """
    停止训练任务的简化版本
    
    """
    return ma_train_job_stop(training_job_id)


def stop_pending_training_jobs() -> Dict[str, Dict[str, Any]]:
    """
    停止所有等待中的训练任务
    
    """
    from train_module.job_list import list_pending_training_jobs
    
    # 获取等待中的任务
    result = list_pending_training_jobs()
    
    if not result.get("success"):
        return {
            "success": False,
            "error": result.get("error", "无法获取等待中的任务列表"),
            "details": {}
        }
    
    jobs = result.get("data", {}).get("jobs", [])
    
    if not jobs:
        return {
            "success": True,
            "message": "没有等待中的训练任务",
            "details": {}
        }

    results = {}
    for job in jobs:
        job_id = job.get("job_id")
        job_name = job.get("name", "Unknown")
        
        if job_id:
            stop_result = ma_train_job_stop(job_id)
            results[job_id] = {
                "name": job_name,
                "success": stop_result.get("success", False),
                "error": stop_result.get("error"),
                "status_code": stop_result.get("status_code", 500)
            }

    total = len(results)
    successful = sum(1 for r in results.values() if r.get("success"))
    failed = total - successful
    
    return {
        "success": successful > 0,
        "message": f"已尝试停止 {total} 个等待中的训练任务，成功 {successful} 个，失败 {failed} 个",
        "details": results,
        "summary": {
            "total": total,
            "successful": successful,
            "failed": failed
        }
    }


def stop_jobs_by_status(status: str) -> Dict[str, Dict[str, Any]]:
    """
    按状态停止训练任务
    
    """
    from train_module.job_list import ma_train_job_list

    result = ma_train_job_list(filters=[{"key": "status", "operator": "eq", "value": status}])
    
    if not result.get("success"):
        return {
            "success": False,
            "error": result.get("error", f"无法获取状态为 '{status}' 的任务列表"),
            "details": {}
        }
    
    jobs = result.get("data", {}).get("jobs", [])
    
    if not jobs:
        return {
            "success": True,
            "message": f"没有状态为 '{status}' 的训练任务",
            "details": {}
        }

    results = {}
    for job in jobs:
        job_id = job.get("job_id")
        if job_id:
            stop_result = ma_train_job_stop(job_id)
            results[job_id] = {
                "success": stop_result.get("success", False),
                "error": stop_result.get("error"),
                "status_code": stop_result.get("status_code", 500)
            }
    
    return {
        "success": True,
        "message": f"已处理 {len(results)} 个状态为 '{status}' 的训练任务",
        "details": results
    }


__all__ = [
    'ma_train_job_stop',
    'stop_training_job_simple',
    'stop_pending_training_jobs',
    'stop_jobs_by_status'
]
