#!/usr/bin/env python3
"""
Inference模块 - 查询专属池及支持的规格
功能：查询专属池列表，以及每个专属池支持的资源规格
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from infer_v1_module._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, make_api_call, Dict, Any


def format_pool_item(item):
    """格式化单个专属池数据"""
    metadata = item.get('metadata', {})
    spec = item.get('spec', {})
    status_info = item.get('status', {})
    flavors = [{"flavor": r.get('flavor'), "count": r.get('count', 0), "max_count": r.get('maxCount', 0)}
               for r in spec.get('resources', [])]
    return {
        "name": metadata.get('name'),
        "creation_timestamp": metadata.get('creationTimestamp'),
        "labels": metadata.get('labels', {}),
        "type": spec.get('type'),
        "scope": spec.get('scope', []),
        "flavors": flavors,
        "status_phase": status_info.get('phase'),
        "available_resources": status_info.get('resources', {}).get('available', [])
    }


def format_pool_specs(pool, available):
    """格式化专属池规格"""
    specs_list = []
    for flavor in pool.get('flavors', []):
        spec_name = flavor.get('flavor')
        count = flavor.get('count', 0)
        max_count = flavor.get('max_count', 0)
        available_count = 0
        for avail in available:
            if avail.get('flavor') == spec_name:
                available_count = sum(az.get('count', 0) for az in avail.get('azs', []))
                break
        specs_list.append({"specification": spec_name, "total_count": count, "max_count": max_count, "available_count": available_count})
    return specs_list


@authenticated_api_call
def get_dedicated_pools(access, workspace_id: str = "0", status: str = "created", **kwargs) -> Dict[str, Any]:
    """查询专属池列表"""
    print(f"  查询专属池列表 (status: {status})")
    project_id = access.project_id if hasattr(access, 'project_id') else kwargs.get('project_id', '0f2788726a80f4ec2fecc00b5844a0c2')
    query_params = {"projectId": project_id, "workspaceId": workspace_id, "status": status}
    result = access.sdk().execute(lambda s: make_api_call(s, 'GET', f'/v2/{project_id}/pools', query=query_params))
    if isinstance(result, dict) and 'items' in result:
        pools = [format_pool_item(item) for item in result.get('items', [])]
        return format_api_result(True, data={"pools": pools, "count": len(pools)})
    return format_api_result(True, data=result)


@authenticated_api_call
def get_dedicated_pool_specs(access, pool_name: str = None, workspace_id: str = "0", **kwargs) -> Dict[str, Any]:
    """查询专属池支持的规格"""
    pools_result = get_dedicated_pools(access, workspace_id)
    if not pools_result['success']:
        return pools_result
    pools = pools_result.get('data', {}).get('pools', [])
    if not pools:
        return format_api_result(True, data={"pools": [], "message": "没有找到专属池"})
    if pool_name:
        pools = [p for p in pools if p.get('name') == pool_name]
        if not pools:
            return format_api_result(False, error=f"未找到专属池: {pool_name}")
    print(f"\n=== 专属池支持的规格 ===")
    result_pools = []
    for pool in pools:
        pool_nm = pool.get('name')
        specs_list = format_pool_specs(pool, pool.get('available_resources', []))
        print(f"\n📦 {pool_nm}\n   状态: {pool.get('status_phase')}\n   类型: {pool.get('type')}")
        for spec in specs_list:
            print(f"   - {spec['specification']}: {spec['available_count']}/{spec['total_count']} 可用")
        result_pools.append({"pool_name": pool_nm, "status": pool.get('status_phase'), "type": pool.get('type'), "specifications": specs_list})
    return format_api_result(True, data={"pools": result_pools, "total_pools": len(result_pools)})


@authenticated_api_call
def ma_old_inference_get_dedicated_specs(access, **kwargs) -> Dict[str, Any]:
    """查询专属池规格（兼容旧接口）"""
    return get_dedicated_pool_specs(access, **kwargs)


__all__ = ['get_dedicated_pools', 'get_dedicated_pool_specs', 'ma_old_inference_get_dedicated_specs']
