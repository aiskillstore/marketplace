#!/usr/bin/env python3

"""获取专属池信息模块 - v2版本"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, simple_api_call, Dict, Any, List

def check_workspace_id(workspace_id):
    if not workspace_id: return "工作空间ID不能为空"
    return None

@authenticated_api_call
def ma_inference_service_get_pools(access, workspace_id: str = "0", **kwargs) -> Dict[str, Any]:
    checks = [
        (check_workspace_id(workspace_id), "workspace_id"),
    ]

    for check, param in checks:
        if check: return format_api_result(False, error=f"{param}: {check}")

    print(f"  查询v2专属池: workspace_id={workspace_id}")

    query = {"workspaceId": workspace_id}
    if kwargs:
        query.update(kwargs)

    try:
        result = simple_api_call(access, 'GET', '/v2/{project_id}/metrics/runtime/pools', query=query)

        if not result:
            return format_api_result(False, error="API返回空结果")

        items = result.get('items', [])
        pools_info = []
        
        for item in items:
            metadata = item.get('metadata', {})
            table = item.get('table', {})
            
            pool_info = {
                'name': metadata.get('name', ''),
                'display_name': metadata.get('labels', {}).get('os.modelarts/name', ''),
                'creation_timestamp': metadata.get('creationTimestamp', ''),
                'project_id': metadata.get('labels', {}).get('os.modelarts/tenant.project.id', ''),
                'workspace_id': metadata.get('labels', {}).get('os.modelarts/workspace.id', ''),
                'allocated': table.get('allocated', {}).get('value', {}),
                'capacity': table.get('capacity', {}).get('value', {}),
                'max_capacity': table.get('capacity', {}).get('maxValue', {}),
                'allocated_timestamp': table.get('allocated', {}).get('timestamp', ''),
                'capacity_timestamp': table.get('capacity', {}).get('timestamp', '')
            }
            pools_info.append(pool_info)

        for pool in pools_info:

            allocated_cpu = pool['allocated'].get('cpu', '0m')
            capacity_cpu = pool['capacity'].get('cpu', '0m')

            def cpu_to_cores(cpu_str):
                if cpu_str.endswith('m'):
                    return int(cpu_str[:-1]) / 1000.0
                return float(cpu_str) if cpu_str else 0.0
            
            def memory_to_gb(mem_str):
                if not mem_str:
                    return 0.0
                if mem_str.endswith('Mi'):
                    return int(mem_str[:-2]) / 1024.0
                elif mem_str.endswith('Gi'):
                    return float(mem_str[:-2])
                elif mem_str.endswith('m'):
                    return int(mem_str[:-1]) / (1024 * 1024.0)
                return float(mem_str) if mem_str else 0.0
            
            allocated_cpu_cores = cpu_to_cores(allocated_cpu)
            capacity_cpu_cores = cpu_to_cores(capacity_cpu)
            allocated_memory_gb = memory_to_gb(pool['allocated'].get('memory', '0Mi'))
            capacity_memory_gb = memory_to_gb(pool['capacity'].get('memory', '0Mi'))

            cpu_usage = (allocated_cpu_cores / capacity_cpu_cores * 100) if capacity_cpu_cores > 0 else 0
            memory_usage = (allocated_memory_gb / capacity_memory_gb * 100) if capacity_memory_gb > 0 else 0
            
            pool['cpu_usage_percent'] = round(cpu_usage, 2)
            pool['memory_usage_percent'] = round(memory_usage, 2)
            pool['allocated_cpu_cores'] = allocated_cpu_cores
            pool['capacity_cpu_cores'] = capacity_cpu_cores
            pool['allocated_memory_gb'] = allocated_memory_gb
            pool['capacity_memory_gb'] = capacity_memory_gb

            pool['available'] = cpu_usage < 90 and memory_usage < 90
            
        return format_api_result(True, data={
            'pools': pools_info,
            'total': len(pools_info),
            'available_count': len([p for p in pools_info if p['available']]),
            'api_response': result
        })
        
    except Exception as e:
        return format_api_result(False, error=f"API调用失败: {str(e)}")

@authenticated_api_call
def quick_get_v2_pools(**kwargs) -> Dict[str, Any]:
    """快速获取v2专属池信息"""
    return ma_inference_service_get_pools(workspace_id="0", **kwargs)

__all__ = ['ma_inference_service_get_pools', 'quick_get_v2_pools']