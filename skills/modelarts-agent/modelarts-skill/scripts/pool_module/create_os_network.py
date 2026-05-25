#!/usr/bin/env python3
"""
Pool模块 - create_os_network函数
功能：创建 OS 网络
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def create_os_network(
    access,
    name: str,
    subnet_cidr: str,
    subnet_gateway_ip: str,
    dns_servers: list = None
) -> Dict[str, Any]:
    """
    创建专属 OS 网络

    Args:
        name: 网络名称（必填）
        subnet_cidr: 子网 CIDR（必填）
        subnet_gateway_ip: 子网网关 IP（必填）
        dns_servers: DNS 服务器列表（可选）


    调用经验:
        - 请求体必须是 K8s 风格，包含 metadata 和 spec
        - metadata.labels 中需要设置 os.modelarts/name
        - 网络 CIDR 使用私有地址段，如 192.168.x.0/24
    
    注意事项:
        - 创建网络后需要等待几秒才能达到 Active 状态
        - 创建资源池需要 5-10 分钟节点才能就绪

    Returns:
        创建结果
    """
    if not name:
        return format_api_result(False, error="name is required")
    if not subnet_cidr:
        return format_api_result(False, error="subnet_cidr is required")
    if not subnet_gateway_ip:
        return format_api_result(False, error="subnet_gateway_ip is required")

    body = {
        "apiVersion": "v1",
        "kind": "Network",
        "metadata": {
            "labels": {
                "os.modelarts/name": name
            }
        },
        "spec": {
            "cidr": subnet_cidr,
            "subnets": [
                {
                    "cidr": subnet_cidr,
                    "name": "default-subnet"
                }
            ]
        }
    }
    if dns_servers:
        body["spec"]["dns_servers"] = dns_servers

    result = access_api_call(
        access,
        "POST",
        "/v1/{project_id}/networks",
        body=body
    )

    return format_api_result(True, data=result)


__all__ = ["create_os_network"]