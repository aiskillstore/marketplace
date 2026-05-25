#!/usr/bin/env python3
"""
Notebook模块 - stop_notebook函数
功能：停止notebook实例
"""

from ._bootstrap import ensure_authentication, format_api_result, Any, Dict


def stop_notebook(notebook_id: str) -> Dict[str, Any]:
    """
    停止运行中的 Notebook 实例
    
        Args:
            notebook_id: Notebook 实例 ID（必填）
    
        Returns:
            停止结果
    
        示例:
            >>> from notebook_module import stop_notebook
            >>> result = stop_notebook('notebook-xxx-xxx-xxx')
            >>> if result['success']:
            ...     print("停止成功")
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        if not notebook_id:
            return format_api_result(False, error="notebook_id is required")

        print(f"  停止Notebook实例: {notebook_id}")

        def _api_call(session):
            from modelarts import constant
            from modelarts.config.auth import auth_by_apig
            
            request_url = f"/v1/{session.project_id}/notebooks/{notebook_id}/stop"
            return auth_by_apig(session, constant.HTTPS_POST, request_url)
        
        result = access.sdk().execute(_api_call)

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"停止notebook时发生异常: {e}")


__all__ = ['stop_notebook']