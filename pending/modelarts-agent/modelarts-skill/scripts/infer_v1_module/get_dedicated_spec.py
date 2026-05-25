#!/usr/bin/env python3
"""
Inference模块 - 查询专属池规格
功能：根据专属池信息查询该池支持的资源规格
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from infer_v1_module._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, make_api_call, Dict, Any


def format_spec_display(spec, index):
    """格式化规格显示"""
    display = spec.get('display_cn') or spec.get('display_en') or spec.get('specification', '')
    status = "✅" if spec.get('is_open') and spec.get('spec_status') == 'normal' else "❌"
    free = " [免费]" if spec.get('is_free') else ""
    print(f"  {index}. {display} {status}{free}")


@authenticated_api_call
def get_dedicated_specs(
    access, infer_type: str = "real-time", is_personal_cluster: bool = True,
    node_flavor: str = None, runtime: str = None, cluster_id: str = None, **kwargs
) -> Dict[str, Any]:
    """查询专属池支持的规格"""
    print(f"  查询专属池规格 (cluster_id: {cluster_id})")
    query_params = {"infer_type": infer_type, "is_personal_cluster": str(is_personal_cluster).lower()}
    if node_flavor:
        query_params["node_flavor"] = node_flavor
    if runtime:
        query_params["runtime"] = runtime
    if cluster_id:
        query_params["cluster_id"] = cluster_id
    query_params.update(kwargs)
    result = access.sdk().execute(lambda s: make_api_call(s, 'GET', '/v1/{project_id}/services/specifications', query=query_params))
    if isinstance(result, dict):
        specifications = result.get('specifications', [])
        print(f"\n=== 专属池规格列表 ===\n总数量: {result.get('total_count', len(specifications))}\n")
        for i, spec in enumerate(specifications, 1):
            format_spec_display(spec, i)
        return format_api_result(True, data=result)
    return format_api_result(True, data=result)


@authenticated_api_call
def get_pool_specs_by_cluster(
    access, cluster_id: str, node_flavor: str = None, runtime: str = None, **kwargs
) -> Dict[str, Any]:
    """根据专属池ID查询支持的规格"""
    return get_dedicated_specs(access=access, cluster_id=cluster_id, node_flavor=node_flavor,
                               runtime=runtime, infer_type="real-time", is_personal_cluster=True, **kwargs)


__all__ = ['get_dedicated_specs', 'get_pool_specs_by_cluster']
