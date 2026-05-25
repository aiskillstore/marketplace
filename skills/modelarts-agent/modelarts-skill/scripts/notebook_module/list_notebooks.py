#!/usr/bin/env python3
"""
Notebook模块 - list_notebooks函数
功能：查询当前用户的Notebook实例列表
"""

from ._bootstrap import ensure_authentication, format_api_result, Any, Dict


def list_notebooks(
        feature: str = "NOTEBOOK",
        limit: int = 10,
        name: str = None,
        pool_id: str = None,
        offset: int = 0,
        owner: str = None,
        sort_dir: str = "DESC",
        sort_key: str = None,
        status: str = None,
        workspace_id: str = "0",
        flavor: str = None,
        image_id: str = None,
        id: str = None,
        billing: str = None,
        tags: str = None
) -> Dict[str, Any]:
    """
    Query list of Notebook instances for current user.

    API Reference: 5.2 ListNotebooks (Page 330)

    SECURITY: Uses secure SDK wrapper. Credentials never exposed.

    Args:
        feature: Instance category (optional) - DEFAULT: Free instance, NOTEBOOK: Paid instance (default: "NOTEBOOK")
        limit: Number of instances per page (optional) - Range: [10,20,50] (default: 10)
        name: Instance name, supports fuzzy matching (optional)
        pool_id: Dedicated resource pool ID (optional) - Lowercase letters, numbers, hyphens
        offset: Pagination offset (optional) (default: 0)
        owner: User ID of instance owner, effective for admin accounts (optional)
        sort_dir: Sort direction (optional) - ASC: Ascending, DESC: Descending (default: "DESC")
        sort_key: Field to sort by, multiple fields separated by comma (optional)
        status: Instance status (optional) - INIT/CREATING/STARTING/STOPPING/DELETING/RUNNING/STOPPED/SNAPSHOTTING/CREATE_FAILED/START_FAILED/DELETE_FAILED/ERROR/DELETED/FROZEN
        workspace_id: Workspace ID (optional) (default: "0")
        flavor: Machine flavor of the instance (optional)
        image_id: Image ID for the Notebook instance (optional) - UUID format
        id: Notebook instance ID (optional) - UUID format
        billing: Billing type (optional) - COMPUTE: Compute resource billing, STORAGE: Storage resource billing, ALL: All billing types
        tags: Instance tag information (optional)

    Returns:
        List of notebook instances with pagination info (current, data, pages, size, total)
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        query_params = {
            "feature": feature,
            "limit": limit,
            "offset": offset,
            "workspace_id": workspace_id
        }

        optional_params = {
            "name": name,
            "pool_id": pool_id,
            "owner": owner,
            "sort_dir": sort_dir,
            "sort_key": sort_key,
            "status": status,
            "flavor": flavor,
            "image_id": image_id,
            "id": id,
            "billing": billing,
            "tags": tags
        }
        
        for key, value in optional_params.items():
            if value is not None:
                query_params[key] = value
        
        print(f"  查询Notebook实例列表")

        def _list_notebooks(session):
            from modelarts import constant
            from modelarts.config.auth import auth_by_apig
            
            request_url = f"/v1/{session.project_id}/notebooks"
            return auth_by_apig(session, constant.HTTPS_GET, request_url, query=query_params)
        
        result = access.sdk().execute(_list_notebooks)

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"查询notebook列表时发生异常: {e}")


__all__ = ['list_notebooks']