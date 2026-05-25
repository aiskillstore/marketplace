#!/usr/bin/env python3
"""
Pool模块 - get_os_network函数
功能：获取 OS 网络详情
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def get_os_network(access, network_name: str) -> Dict[str, Any]:
    """
    获取 OS 网络详情

    Args:
        network_name: 网络名称（必填），格式: xxx-{project_id}

    Returns:
        网络详情信息，包含:
        - metadata: 元数据（名称、标签、注解等）
        - spec: 网络规格（CIDR、子网等）
        - status: 状态（Active, Deleting, 等）

    调用经验:
        - 传入网络的完整名称（含 project_id 后缀）
        - 示例: network-fc5a-0f2788726a80f4ec2fecc00b5844a0c2
        - 可用于检查网络是否可用，判断是否可以被资源池使用
    """
    if not network_name:
        return format_api_result(False, error="network_name is required")

    result = access_api_call(
        access,
        "GET",
        "/v1/{project_id}/networks/{network_name}",
        network_name=network_name, query={}
    )

    return format_api_result(True, data=result)


__all__ = ["get_os_network"]