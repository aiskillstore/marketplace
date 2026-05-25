#!/usr/bin/env python3
"""
训练模块 - 任务删除

功能：训练任务的删除功能
"""

import sys
from typing import Dict, Any, List

sys.path.insert(0, '.')

from common_module import ensure_authentication, format_api_result
from train_module.common import format_error_result, format_success_result


def ma_train_job_delete(training_job_id: str,
                        confirm: bool = False, debug: bool = False) -> Dict[str, Any]:
    """
    删除训练作业
    
    接口: DELETE /v2/{project_id}/training-jobs/{training_job_id}
    
    🔥  【危险】删除操作不可逆！
        - 作业及其所有数据将被永久性删除
        - 无法恢复，请确保数据已备份
        - 建议：只删除已完成的作业（status: Completed/Failed/Terminated）
    
    Args:
        training_job_id: 训练作业 ID
            获取方式: 调用 train_module.ma_train_job_list()
        confirm (bool, 必填): 强制确认删除操作
            - 默认值: False
            - 当 confirm=False 时，返回提示信息，需要与大模型确认后传递 confirm=True 才能执行
            - 当 confirm=True 时，直接执行删除操作
            示例: ma_train_job_delete(job_id, confirm=True)
        debug: 是否返回调试信息
    
    Returns:
        Dict[str, Any]:
        {
            "success": bool,
            "job_id": str,
            "status_code": int (202 表示成功)
        }
    
    Example:
        # 删除任务（需要确认）
        from train_module import ma_train_job_delete
        result = ma_train_job_delete(
            training_job_id="job-xxx-xxx",
            confirm=True  # 确认后传递 True
        )
    
    Related:
        - 查询任务: train_module.ma_train_job_list()
        - 停止任务: train_module.ma_train_job_stop()
    """
    try:
        if not confirm:
            return {
                "success": False,
                "status_code": 400,
                "error": f"【删除任务需要确认】\n\n"
                           f"任务 ID: {training_job_id}\n"
                           f"⚠️  警告: 此操作不可逆，数据将被永久删除\n\n"
                           f"请与用户确认是否删除此任务？\n"
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

        def _delete_job(session):
            from modelarts.config.auth import auth_by_apig
            
            path = f"/v2/{session.project_id}/training-jobs/{training_job_id}"
            
            headers = {'Content-Type': 'application/json'}
            if hasattr(session, 'user_id') and session.user_id:
                headers['x-modelarts-user-id'] = session.user_id
            
            return auth_by_apig(session, "DELETE", path, headers=headers)
        
        api_result = access.sdk().execute(_delete_job)
        if api_result is None:
            result = format_success_result(
                data={'message': 'Training job deletion initiated'},
                job_id=training_job_id,
                status_code=202
            )
            return result
        elif isinstance(api_result, dict) and ("metadata" in api_result or "status" in api_result):
            result_data = api_result
            
            result = format_success_result(
                data=result_data,
                job_id=training_job_id,
                status_code=202
            )

            if debug:
                result["debug_info"] = {
                    "training_job_id": training_job_id,
                    "access_source": "modelarts-v2"
                }
            
            return result
        else:
            error_msg = "Unknown API error"
            error_code = 500
            
            if api_result and isinstance(api_result, dict):
                error_msg = api_result.get("error", "Unknown API error")
                error_code = api_result.get("status_code", 500)

            if error_code == 404:
                error_msg = f"训练作业不存在或已被删除: {training_job_id}"
            elif error_code == 409:
                error_msg = f"训练作业无法删除（可能仍在运行中）: {training_job_id}"
            
            return format_error_result(
                error=f"删除作业失败: {error_msg}",
                status_code=error_code
            )
            
    except Exception as e:
        return format_api_result(False, error=f"Unexpected error: {str(e)}")


def delete_training_job_simple(training_job_id: str) -> Dict[str, Any]:
    """
    删除训练任务的简化版本
    
    """
    return ma_train_job_delete(training_job_id)


def delete_completed_training_jobs() -> Dict[str, Dict[str, Any]]:
    """
    删除所有已完成的训练任务
    
    """
    from train_module.job_list import list_completed_training_jobs
    result = list_completed_training_jobs()
    
    if not result.get("success"):
        return {
            "success": False,
            "error": result.get("error", "无法获取已完成的任务列表"),
            "details": {}
        }
    
    jobs = result.get("data", {}).get("jobs", [])
    
    if not jobs:
        return {
            "success": True,
            "message": "没有已完成的训练任务",
            "details": {}
        }

    results = {}
    for job in jobs:
        job_id = job.get("job_id")
        job_name = job.get("name", "Unknown")
        job_status = job.get("status", "Unknown")
        
        if job_id:
            if job_status in ["Completed", "Succeeded", "Failed"]:
                delete_result = ma_train_job_delete(job_id)
                results[job_id] = {
                    "name": job_name,
                    "status": job_status,
                    "success": delete_result.get("success", False),
                    "error": delete_result.get("error"),
                    "status_code": delete_result.get("status_code", 500)
                }
            else:
                results[job_id] = {
                    "name": job_name,
                    "status": job_status,
                    "success": False,
                    "error": f"作业状态 '{job_status}' 不适合删除，建议只删除已完成的作业",
                    "status_code": 400
                }
    total = len(results)
    successful = sum(1 for r in results.values() if r.get("success"))
    failed = total - successful
    
    return {
        "success": successful > 0,
        "message": f"已尝试删除 {total} 个已完成的训练任务，成功 {successful} 个，失败 {failed} 个",
        "details": results,
        "summary": {
            "total": total,
            "successful": successful,
            "failed": failed
        }
    }


def delete_jobs_by_status(status_list: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    按状态删除训练任务
    
    """
    from train_module.job_list import ma_train_job_list

    result = ma_train_job_list(filters=[{"key": "status", "operator": "in", "value": status_list}])
    
    if not result.get("success"):
        return {
            "success": False,
            "error": result.get("error", f"无法获取状态为 {status_list} 的任务列表"),
            "details": {}
        }
    
    jobs = result.get("data", {}).get("jobs", [])
    
    if not jobs:
        return {
            "success": True,
            "message": f"没有状态为 {status_list} 的训练任务",
            "details": {}
        }
    results = {}
    for job in jobs:
        job_id = job.get("job_id")
        if job_id:
            delete_result = ma_train_job_delete(job_id)
            results[job_id] = {
                "success": delete_result.get("success", False),
                "error": delete_result.get("error"),
                "status_code": delete_result.get("status_code", 500)
            }
    
    return {
        "success": True,
        "message": f"已处理 {len(results)} 个状态为 {status_list} 的训练任务",
        "details": results
    }


__all__ = [
    'ma_train_job_delete',
    'delete_training_job_simple',
    'delete_completed_training_jobs',
    'delete_jobs_by_status'
]
