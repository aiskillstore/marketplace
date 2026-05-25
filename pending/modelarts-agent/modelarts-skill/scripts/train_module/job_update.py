#!/usr/bin/env python3
"""
训练模块 - 更新训练作业描述

功能：更新训练作业的描述信息
"""

import sys
from typing import Dict, Any

sys.path.insert(0, '.')

from common_module import ensure_authentication, format_api_result
from train_module.common import format_error_result, format_success_result


def ma_train_job_update_description(training_job_id: str, description: str = None,
                                     debug: bool = False) -> Dict[str, Any]:
    """
    更新训练作业描述
    
    接口: PUT /v2/{project_id}/training-jobs/{training_job_id}
    
    📌 功能说明:
    更新训练作业的描述信息。该接口用于修改已存在的训练作业的描述信息。
    使用该接口的前提条件是训练作业已存在且用户具有相应的权限。
    
    Args:
        training_job_id: 训练作业 ID
            获取方式: 调用 train_module.ma_train_job_list()
        description (str, 可选): 对训练作业的描述
            长度限制: 0-256 字符
            默认: 默认为"NULL"
        debug: 是否返回调试信息
    
    Returns:
        Dict[str, Any]:
        {
            "success": bool,
            "job_id": str,
            "data": {更新后的作业信息},
            "status_code": int
        }
    
    Example:
        # 更新训练任务描述
        from train_module import ma_train_job_update_description
        result = ma_train_job_update_description(
            training_job_id="job-xxx-xxx",
            description="更新后的描述信息"
        )
    
    Related:
        - 查询任务: train_module.ma_train_job_list()
        - 创建任务: train_module.ma_train_job_create()
    """
    try:
        if not training_job_id or not training_job_id.strip():
            return format_error_result(
                error="必须提供有效的训练作业ID（training_job_id）",
                status_code=400
            )

        if description is not None and len(description) > 256:
            return format_error_result(
                error=f"描述长度不能超过256个字符，当前长度: {len(description)}",
                status_code=400
            )

        auth_result = ensure_authentication()
        if not auth_result['success']:
            return format_api_result(False, error=auth_result.get('error', 'Authentication failed'))
        
        access = auth_result['access']

        request_body = {}
        if description is not None:
            request_body["description"] = description

        def _update_job(session):
            from modelarts.config.auth import auth_by_apig
            import json
            
            path = f"/v2/{session.project_id}/training-jobs/{training_job_id}"
            body_bytes = json.dumps(request_body).encode('utf-8') if request_body else None
            
            headers = {'Content-Type': 'application/json'}
            if hasattr(session, 'user_id') and session.user_id:
                headers['x-modelarts-user-id'] = session.user_id
            
            return auth_by_apig(session, "PUT", path, body=body_bytes, headers=headers)
        
        api_result = access.sdk().execute(_update_job)

        if api_result is None or (isinstance(api_result, dict) and ("metadata" in api_result or "status" in api_result)):
            result_data = api_result if api_result else {}
            
            result = format_success_result(
                data=result_data,
                job_id=training_job_id,
                status_code=200
            )

            if debug:
                result["debug_info"] = {
                    "training_job_id": training_job_id,
                    "description": description,
                    "access_source": "modelarts-v2"
                }
            
            return result
        else:
            error_msg = "Unknown API error"
            if api_result and isinstance(api_result, dict):
                error_msg = api_result.get("error_msg", api_result.get("error", "Unknown API error"))
            
            return format_error_result(
                error=f"更新作业描述失败: {error_msg}",
                status_code=500
            )
            
    except Exception as e:
        return format_api_result(False, error=f"Unexpected error: {str(e)}")


__all__ = [
    'ma_train_job_update_description'
]
