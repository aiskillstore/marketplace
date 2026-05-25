#!/usr/bin/env python3
"""
Notebook模块 - get_notebook函数
功能：获取特定Notebook实例的详情
"""

from ._bootstrap import ensure_authentication, format_api_result, Dict, Any


def get_notebook(notebook_id: str) -> Dict[str, Any]:
    """
    获取特定 Notebook 实例的详情
    
        Args:
            notebook_id: Notebook 实例 ID（必填）
    
        Returns:
            Notebook 详细信息
    
        示例:
            >>> from notebook_module import get_notebook
            >>> result = get_notebook('notebook-xxx-xxx-xxx')
            >>> if result['success']:
            ...     nb = result['data']
            ...     print(f"名称: {nb.get('name')}")
            ...     print(f"状态: {nb.get('status')}")
            ...     print(f"规格: {nb.get('flavor')}")
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        if not notebook_id:
            return format_api_result(False, error="notebook_id is required")
        
        print(f"  获取Notebook详情: {notebook_id}")

        def _get_notebook(session):
            from modelarts import constant
            from modelarts.config.auth import auth_by_apig
            
            request_url = f"/v1/{session.project_id}/notebooks/{notebook_id}"
            return auth_by_apig(session, constant.HTTPS_GET, request_url)
        
        result = access.sdk().execute(_get_notebook)

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"获取notebook详情时发生异常: {e}")


__all__ = ['get_notebook']