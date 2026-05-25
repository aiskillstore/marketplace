#!/usr/bin/env python3
"""
Lite Server 模块 - create_roce_network 函数
功能：创建RoCE网络
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, Optional
from .common import build_request_body, add_api_reference

@authenticated_api_call
def ma_liteserver_create_roce_network(
    access,
    network_type: Optional[str] = None,
    physical_network: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a RoCE network.
    Args:
        network_type: RoCE网络类型 (optional) - vxlan_roce, roce_v2
        physical_network: 物理网络名称 (optional) - 正则: ^[-_.a-zA-Z0-9]{1,64}$
    Returns:
        Created network details including network object
    """
    optional = {}
    if network_type is not None:
        optional['network_type'] = network_type
    if physical_network is not None:
        optional['physical_network'] = physical_network

    body = build_request_body({}, optional)

    result = simple_api_call(
        access,
        'POST',
        '/v1/{project_id}/dev-servers/networks',
        body=body
    )

    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "22.31 CreateRoceNetwork (Page 1785)")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_create_roce_network']
