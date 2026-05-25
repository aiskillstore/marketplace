#!/usr/bin/env python3

"""查询专属池支持的规格模块 - v2版本"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ._bootstrap import ensure_authentication, format_api_result, authenticated_api_call, simple_api_call, Dict, Any, List

def check_pool_id(pool_id):
    if not pool_id: return "专属池ID不能为空"
    return None

@authenticated_api_call
def ma_inference_service_get_flavors(access, pool_id: str, **kwargs) -> Dict[str, Any]:
    checks = [
        (check_pool_id(pool_id), "pool_id"),
    ]

    for check, param in checks:
        if check: return format_api_result(False, error=f"{param}: {check}")

    print(f"  查询v2专属池规格: pool_id={pool_id}")

    try:
        result = simple_api_call(access, 'GET', '/v2/{project_id}/services/clusters/{pool_id}', pool_id=pool_id)

        if not result:
            return format_api_result(False, error="API返回空结果")

        pool_info = {
            'pool_id': result.get('pool_id', ''),
            'logic_cluster_id': result.get('logic_cluster_id', ''),
            'status': result.get('status', ''),
            'type': result.get('type', ''),
            'resource_categories': result.get('resource_categories', []),
            'workspace_id': result.get('workspace_id', ''),
            'project_id': result.get('project_id', ''),
            'domain_id': result.get('domain_id', ''),
            'create_at': result.get('create_at'),
            'update_at': result.get('update_at')
        }

        raw_flavors = result.get('flavors', [])
        flavors_info = []
        
        for flavor in raw_flavors:
            memory_kb = flavor.get('memory', 0)
            memory_gb = memory_kb / (1024 * 1024) if memory_kb else 0

            billing = flavor.get('billing', {})
            unit_num = billing.get('unit_num', 1)
            
            flavor_info = {
                'id': flavor.get('id', ''),
                'name': flavor.get('name', ''),
                'description': flavor.get('description', ''),
                'category': flavor.get('category', ''),
                'arch': flavor.get('arch', ''),
                'vcpus': flavor.get('vcpus', 0),
                'memory_kb': memory_kb,
                'memory_gb': round(memory_gb, 2),
                'memory_readable': f"{memory_gb:.1f}GB",
                'feature': flavor.get('feature', ''),
                'free': flavor.get('free', False),
                'sold_out': flavor.get('sold_out', False),
                'storages': flavor.get('storages', []),
                'billing': billing,
                'unit_num': unit_num
            }
            flavors_info.append(flavor_info)

        flavors_info.sort(key=lambda x: x['vcpus'])

        cpu_flavors = [f for f in flavors_info if f['category'] == 'CPU']
        gpu_flavors = [f for f in flavors_info if f['category'] == 'GPU' or 'GPU' in f.get('name', '')]
        ascend_flavors = [f for f in flavors_info if f['category'] == 'ASCEND' or 'Ascend' in f.get('name', '')]
        
        stats = {
            'total_flavors': len(flavors_info),
            'cpu_flavors': len(cpu_flavors),
            'gpu_flavors': len(gpu_flavors),
            'ascend_flavors': len(ascend_flavors),
            'free_flavors': len([f for f in flavors_info if f['free']]),
            'available_flavors': len([f for f in flavors_info if not f['sold_out']])
        }

        recommendations = {
            'light_weight': next((f for f in cpu_flavors if f['vcpus'] <= 2 and f['memory_gb'] <= 8), None),
            'medium_weight': next((f for f in cpu_flavors if 2 < f['vcpus'] <= 8 and 8 < f['memory_gb'] <= 32), None),
            'heavy_weight': next((f for f in cpu_flavors if f['vcpus'] > 8 and f['memory_gb'] > 32), None),
            'cheapest': next((f for f in flavors_info if not f['sold_out']), None),
            'most_powerful': max(flavors_info, key=lambda x: x['vcpus']) if flavors_info else None
        }
        
        return format_api_result(True, data={
            'pool_info': pool_info,
            'flavors': flavors_info,
            'stats': stats,
            'recommendations': recommendations,
            'api_response': result
        })
        
    except Exception as e:
        return format_api_result(False, error=f"API调用失败: {str(e)}")

@authenticated_api_call
def quick_get_v2_flavors(pool_id: str, **kwargs) -> Dict[str, Any]:
    """快速查询v2专属池规格"""
    return ma_inference_service_get_flavors(pool_id=pool_id, **kwargs)

def suggest_flavor_for_custom_spec(flavors, custom_spec):
    """根据自定义规格建议最接近的flavor"""
    if not flavors or not custom_spec:
        return None
    
    target_cpu = custom_spec.get('cpu', 0)
    target_memory_gb = custom_spec.get('memory', 0) / 1024.0

    best_match = None
    best_score = float('inf')
    
    for flavor in flavors:
        flavor_cpu = flavor.get('vcpus', 0)
        flavor_memory_gb = flavor.get('memory_gb', 0)

        cpu_diff = abs(flavor_cpu - target_cpu)
        memory_diff = abs(flavor_memory_gb - target_memory_gb)
        score = cpu_diff * 2 + memory_diff
        
        if score < best_score:
            best_score = score
            best_match = flavor
    
    return best_match

__all__ = ['ma_inference_service_get_flavors', 'quick_get_v2_flavors', 'suggest_flavor_for_custom_spec']