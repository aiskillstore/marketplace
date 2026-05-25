#!/usr/bin/env python3
"""
Notebook模块 - create_notebook函数
功能：创建Notebook实例
"""

import sys
from typing import Any, Dict

sys.path.insert(0, '.')

from common_module import authenticated_api_call, format_api_result


@authenticated_api_call
def create_notebook(
    access,
    name: str,
    flavor: str,
    image_id: str,
    volume: Dict[str, Any],
    workspace_id: str = None,
    pool_id: str = None,
    pool_scope: str = None,
    lease_type: str = 'timing',
    lease_duration: int = 3600000,
    auto_stop: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    创建新的 Notebook 实例
    
        Args:
            name: Notebook 名称（必填）
            flavor: 计算规格名称（必填），如 'CPU: 2vCPUs 8GB'
            image_id: 镜像 ID（必填）
            volume: 存储配置（必填）
                - EVS存储: {'category': 'EVS', 'capacity': 5, 'ownership': 'MANAGED'}
                - OBS存储: {'category': 'OBS', 'uri': 'obs://bucket-name/', 'ownership': 'DEDICATED', 'dew_secret_name': 'EXAMPLE'}
                  注意: ownership为'DEDICATED'是专属池, 'MANAGED'是公共池
            workspace_id: 工作空间 ID（可选，默认: "0"）
            pool_id: 专属资源池 ID（可选）
            auto_stop: 是否自动停止（可选，默认: True）
            lease_duration: 自动停止时长（毫秒，可选，默认: 3600000 = 1小时）
            **kwargs: 其他配置参数
    
        Returns:
            创建结果，包含 Notebook ID
    
        示例:
            # 示例1: 使用EVS存储
            >>> result = create_notebook(
            ...     name='my-notebook',
            ...     flavor='modelarts.vm.cpu.2u',
            ...     image_id='image-xxx-xxx-xxx',
            ...     volume={
            ...         'category': 'EVS',
            ...         'capacity': 5,
            ...         'ownership': 'MANAGED'
            ...     }
            ... )

            # 示例2: 使用OBS存储（专属资源池）
            >>> result = create_notebook(
            ...     name='my-obs-notebook',
            ...     flavor='modelarts.vm.cpu.2u',
            ...     image_id='278e88d1-5b71-4766-8502-b3ba72e824d9',
            ...     volume={
            ...         'category': 'OBS',
            ...         'uri': 'obs://0f2788726a80f4ec2fecc00b5844a0c2/',
            ...         'ownership': 'DEDICATED',
            ...         'dew_secret_name': 'AKSK'
            ...     },
            ...     pool_id='pool-xxx-xxx-xxx',
            ...     auto_stop=False
            ... )
            >>> if result['success']:
            ...     print(f"创建成功: {result['data']['id']}")
    """
    if not name:
        return format_api_result(False, error="name is required")
    if not flavor:
        return format_api_result(False, error="flavor is required")
    if not image_id:
        return format_api_result(False, error="image_id is required")
    if not volume or not isinstance(volume, dict):
        return format_api_result(False, error="volume is required and must be a dict")
    if 'category' not in volume:
        return format_api_result(False, error="volume.category is required")

    if volume['category'] == 'OBS':
        if 'uri' not in volume:
            return format_api_result(False, error="volume.uri is required for OBS storage")
        if 'ownership' not in volume:
            return format_api_result(False, error="volume.ownership is required for OBS storage")
        if 'dew_secret_name' not in volume:
            return format_api_result(False, error="volume.dew_secret_name is required for OBS storage")

    body = {
        'name': name,
        'flavor': flavor,
        'image': {'id': image_id},
        'volume': volume,
        'feature': 'Notebook'
    }

    optional_params = {
        'workspace_id': workspace_id or '0',
        'pool_id': pool_id,
        'pool_scope': pool_scope,
        **kwargs
    }
    for key, value in optional_params.items():
        if value is not None:
            body[key] = value

    body['lease'] = {
        'type': lease_type,
        'duration': lease_duration,
        'enable': auto_stop
    }

    result = access.sdk().execute(lambda s: make_api_call(
        s,
        'POST',
        '/v1/{project_id}/notebooks',
        body=body
    ))

    return format_api_result(True, data=result)


from common_module.api_helper import make_api_call

__all__ = ['create_notebook']