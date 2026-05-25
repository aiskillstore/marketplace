#!/usr/bin/env python3
"""
Pool模块 - patch_os_network函数
功能：更新 OS 网络配置
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def patch_os_network(
    access,
    network_name: str,
    description: str = None,
    peer_connection_list: List[dict] = None
) -> Dict[str, Any]:
    """
    更新 OS 网络配置

    Args:
        network_name: 网络名称（必填）
        description: 网络描述（可选）
        peer_connection_list: 对等连接列表（可选）


    调用经验:
        - PATCH 请求需要特殊的 Content-Type
        - 必须设置: Content-Type: application/merge-patch+json
        - 请求体使用 K8s 风格: {spec: {...}} 或 {metadata: {...}}
    
    注意事项:
        - 不要在请求体包含 apiVersion 和 kind，只需要更新的字段
        - 目前支持更新: metadata.annotations（描述）和 spec.connection（对等连接）
        - 更新后立即生效

    Returns:
        更新结果
    """
    if not network_name:
        return format_api_result(False, error="network_name is required")

    body = {
        "metadata": {
            "annotations": {}
        },
        "spec": {}
    }
    
    if description is not None:
        body["metadata"]["annotations"]["os.modelarts/description"] = description
    
    if peer_connection_list is not None:
        body["spec"]["connection"] = {
            "peerConnectionList": peer_connection_list
        }

    headers = {
        "Content-Type": "application/merge-patch+json"
    }

    result = access_api_call(
        access,
        "PATCH",
        "/v1/{project_id}/networks/{network_name}",
        network_name=network_name, body=body, headers=headers
    )

    return format_api_result(True, data=result)


__all__ = ["patch_os_network"]