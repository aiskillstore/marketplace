#!/usr/bin/env python3
"""
Pool模块 - create_pool函数
功能：创建专属资源池
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, List


def _validate_params(name, pool_type, scope, resources, network_name):
    """参数验证 - 分离验证逻辑，降低主函数复杂度"""
    if not name:
        return False, "name is required"
    if pool_type not in ['Dedicate', 'Logical']:
        return False, "pool_type must be 'Dedicate' or 'Logical'"
    if not scope or not isinstance(scope, list):
        return False, "scope is required and must be a list"
    if not resources or not isinstance(resources, list):
        return False, "resources is required and must be a list"
    if pool_type == 'Dedicate' and not network_name:
        return False, "network_name is required when pool_type is 'Dedicate'"
    
    for item in resources:
        if not isinstance(item, dict):
            return False, "each resource item must be a dict"
        if 'flavor' not in item or 'count' not in item:
            return False, "each resource item must contain 'flavor' and 'count'"
    
    return True, None


def _build_metadata(name, workspace_id, description, billing_mode):
    """构建 metadata - 分离构建逻辑"""
    labels = {'os.modelarts/name': name}
    if workspace_id:
        labels['os.modelarts/workspace.id'] = workspace_id

    metadata = {'labels': labels}
    annotations = {}
    if description:
        annotations['os.modelarts/description'] = description
    if billing_mode:
        annotations['os.modelarts/billing.mode'] = billing_mode
    if annotations:
        metadata['annotations'] = annotations
    
    return metadata


def _build_spec(pool_type, scope, resources, network_name):
    """构建 spec - 分离构建逻辑"""
    spec = {
        'type': pool_type,
        'scope': scope,
        'resources': resources
    }
    if network_name:
        spec['network'] = {'name': network_name}
    return spec


@authenticated_api_call
def create_pool(
    access,
    name: str,
    pool_type: str,
    scope: List[str],
    resources: List[Dict[str, Any]],
    workspace_id: str = None,
    network_name: str = None,
    description: str = None,
    billing_mode: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    创建专属资源池
    
        Args:
            name: 资源池名称（必填）
            pool_type: 资源池类型（必填）: 'Dedicate' 或 'Logical'
            scope: 支持的作业类型列表（必填），如: ['Notebook', 'Train', 'Infer']
            resources: 资源规格列表（必填），格式: [{'flavor': 'xxx', 'count': 1, 'maxCount': 1}]
            workspace_id: 工作空间 ID（可选）
            network_name: 网络名称（必填，pool_type = 'Dedicate' 时）
            description: 资源池描述（可选）
            billing_mode: 计费模式（可选）: '0' 按需, '1' 包周期
            **kwargs: 其他配置参数
    
    
    调用经验:
        - 请求体必须是 K8s 风格，包含 metadata 和 spec
        - metadata.labels 中需要设置 os.modelarts/name
        - 网络 CIDR 使用私有地址段，如 192.168.x.0/24
    
    注意事项:
        - 创建网络后需要等待几秒才能达到 Active 状态
        - 创建资源池需要 5-10 分钟节点才能就绪

    Returns:
            创建结果，包含资源池 ID
    
        示例:
            >>> from pool_module import create_pool
            >>> result = create_pool(
            ...     name='my-pool',
            ...     pool_type='Dedicate',
            ...     scope=['Notebook'],
            ...     resources=[{'flavor': 'modelarts.vm.cpu.16u64g.d', 'count': 1, 'maxCount': 1}],
            ...     network_name='network-fc5a-0f2788726a80f4ec2fecc00b5844a0c2',
            ...     description='测试资源池'
            ... )
            >>> if result['success']:
            ...     print(f"创建成功: {result['data']['metadata']['name']}")
    """
    valid, error = _validate_params(name, pool_type, scope, resources, network_name)
    if not valid:
        return format_api_result(False, error=error)

    metadata = _build_metadata(name, workspace_id, description, billing_mode)
    spec = _build_spec(pool_type, scope, resources, network_name)
    
    body = {
        'apiVersion': 'v2',
        'kind': 'Pool',
        'metadata': metadata,
        'spec': spec
    }

    result = access.sdk().execute(lambda s: make_api_call(
        s,
        'POST',
        '/v2/{project_id}/pools',
        body=body
    ))

    return format_api_result(True, data=result)

from common_module.api_helper import make_api_call

__all__ = ['create_pool']