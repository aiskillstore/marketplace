#!/usr/bin/env python3
"""
Notebook模块 - delete_notebook函数
功能：删除notebook实例
"""

from ._bootstrap import ensure_authentication, format_api_result, Any, Dict


def delete_notebook(notebook_id: str) -> Dict[str, Any]:
    """
    删除 Notebook 实例
    
        Args:
            notebook_id: Notebook 实例 ID（必填）
    
        Returns:
            删除结果
    
        示例:
            >>> from notebook_module import delete_notebook
            >>> result = delete_notebook('notebook-xxx-xxx-xxx')
            >>> if result['success']:
            ...     print("删除成功")
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        if not notebook_id:
            return format_api_result(False, error="notebook_id is required")
        
        print(f"  删除Notebook实例: {notebook_id}")

        def _delete_notebook(session):
            from modelarts import constant
            from modelarts.config.auth import auth_by_apig
            
            request_url = f"/v1/{session.project_id}/notebooks/{notebook_id}"
            return auth_by_apig(session, constant.HTTPS_DELETE, request_url)
        
        result = access.sdk().execute(_delete_notebook)

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"删除notebook时发生异常: {e}")


__all__ = ['delete_notebook']