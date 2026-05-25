#!/usr/bin/env python3
"""
Pool模块 - delete_os_network函数
功能：删除 OS 网络
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def delete_os_network(access, network_name: str) -> Dict[str, Any]:
    """
    删除 OS 网络

    Args:
        network_name: 网络名称（必填）

    Returns:
        删除结果
    
    调用经验:
        - 传入网络的完整名称（含 project_id 后缀）
        - 删除前请确保网络未被资源池使用
        - 删除后不可恢复，请谨慎操作
    
    注意事项:
        - 正在使用的网络无法删除
        - 建议先 list_os_networks 确认网络状态
    """
    if not network_name:
        return format_api_result(False, error="network_name is required")

    result = access_api_call(
        access,
        "DELETE",
        "/v1/{project_id}/networks/{network_name}"
    , network_name=network_name)

    return format_api_result(True, data=result)


__all__ = ["delete_os_network"]