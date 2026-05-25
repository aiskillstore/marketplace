#!/usr/bin/env python3
"""
训练模块 - 查询训练作业详情

功能：获取指定训练作业的详细信息
"""

import sys
from typing import Dict, Any

sys.path.insert(0, '.')

from common_module import ensure_authentication, format_api_result
from train_module.common import format_error_result, format_success_result


def ma_show_training_job_details(training_job_id: str, debug: bool = False) -> Dict[str, Any]:
    """
    查询训练作业详情
    
    接口: GET /v2/{project_id}/training-jobs/{training_job_id}
    
    📌 功能说明:
    查询ModelArts平台上指定训练作业的详细信息。
    
    Args:
        training_job_id (str, 必填): 训练作业ID
            获取方式: 调用 train_module.ma_train_job_list()
            约束: 不涉及
        debug: 是否返回调试信息
    
    Returns:
        Dict[str, Any]:
        {
            "success": bool,
            "job_id": str,
            "data": {
                "metadata": {作业元数据信息},
                "status": {作业状态信息},
                "spec": {作业规格配置},
                ...
            },
            "status_code": int
        }
    
    Example:
        # 查询训练作业详情
        from train_module import ma_show_training_job_details
        result = ma_show_training_job_details(
            training_job_id="job-xxx-xxx"
        )
    
    Related:
        - 查询任务列表: train_module.ma_train_job_list()
        - 停止任务: train_module.ma_train_job_stop()
        - 删除任务: train_module.ma_train_job_delete()
    """
    try:
        if not training_job_id or not training_job_id.strip():
            return format_error_result(
                error="必须提供有效的训练作业ID（training_job_id）",
                status_code=400
            )

        auth_result = ensure_authentication()
        if not auth_result['success']:
            return format_api_result(False, error=auth_result.get('error', 'Authentication failed'))
        
        access = auth_result['access']

        def _get_job_details(session):
            from modelarts.config.auth import auth_by_apig
            
            path = f"/v2/{session.project_id}/training-jobs/{training_job_id}"
            
            headers = {}
            if hasattr(session, 'user_id') and session.user_id:
                headers['x-modelarts-user-id'] = session.user_id
            
            return auth_by_apig(session, "GET", path, headers=headers)
        
        api_result = access.sdk().execute(_get_job_details)

        if api_result is None:
            return format_error_result(
                error="API返回为空，请检查训练作业ID是否正确",
                status_code=404
            )
        
        if isinstance(api_result, dict):
            if "error_code" in api_result or "error_msg" in api_result:
                error_msg = api_result.get("error_msg", api_result.get("error_code", "Unknown error"))
                return format_error_result(
                    error=f"查询作业详情失败: {error_msg}",
                    status_code=api_result.get("status_code", 500)
                )

            result = format_success_result(
                data=api_result,
                job_id=training_job_id,
                status_code=200
            )

            if debug:
                result["debug_info"] = {
                    "training_job_id": training_job_id,
                    "access_source": "modelarts-v2"
                }
            
            return result
        else:
            return format_error_result(
                error="API响应格式异常",
                status_code=500
            )
            
    except Exception as e:
        return format_api_result(False, error=f"Unexpected error: {str(e)}")


__all__ = [
    'ma_show_training_job_details'
]
