#!/usr/bin/env python3
"""
VPC 模块 - 查询子网列表
功能：查询子网列表（ListSubnets）
API: GET https://vpc.{region}.myhuaweicloud.com/v1/{project_id}/subnets
"""

import sys
from typing import Dict, Any, Optional

sys.path.insert(0, '.')

from vpc_module.common import list_vpc_resources, vpc_api_call

def list_subnets(
    limit: int = 10,
    marker: Optional[str] = None,
    vpc_id: Optional[str] = None,
    enterprise_project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    查询子网列表（ListSubnets）

    API: GET https://vpc.{region}.myhuaweicloud.com/v1/{project_id}/subnets
    Args:
        limit: 分页查询每页返回的记录个数，取值范围为0~2000，默认2000
        marker: 分页查询的起始资源ID，表示从指定资源的下一条记录开始查询
                需要和limit配合使用。若不传入marker和limit参数，查询结果返回第一页全部资源记录
        vpc_id: 按照子网所在VPC ID过滤查询。企业项目细粒度授权场景下，该字段必传
        enterprise_project_id: 按照企业项目ID过滤查询
                               "0"表示默认企业项目，"all_granted_eps"表示查询所有企业项目
    Returns:
        Dict[str, Any]:
        {
            "success": bool,
            "data": {
                "subnets": [
                    {
                        "id": "uuid",
                        "name": "subnet-name",
                        "cidr": "192.168.1.0/24",
                        "gateway_ip": "192.168.1.1",
                        "vpc_id": "vpc-uuid",
                        "status": "ACTIVE",
                        "dhcp_enable": true,
                        "dnsList": ["114.xx.xx.114", "114.xx.xx.115"],
                        "availability_zone": "aa-bb-cc",
                        "neutron_subnet_id": "neutron-uuid",
                        "available_ip_address_count": 251,
                        "created_at": "2022-12-15T02:42:07",
                        "updated_at": "2022-12-15T02:42:07",
                        ...
                    },
                    ...
                ],
                "total": int
            },
            "status_code": int
        }
    Example:
        >>> from vpc_module import list_subnets
        >>> # 查询所有子网
        >>> result = list_subnets()
        >>> if result['success']:
        ...     for subnet in result['data']['subnets']:
        ...         print(f"{subnet['name']} ({subnet['vpc_id']}): {subnet['cidr']}")
        >>>
        >>> # 查询指定VPC下的子网
        >>> result = list_subnets(vpc_id='3ec3b33f-ac1c-4630-ad1c-7dba1ed79d85')
    Related:
        - 查询VPC列表: vpcs.list_vpcs()
        - 查询安全组: security_groups.list_security_groups(vpc_id=vpc_id)
    """
    def _do_list(session):
        api_path = f"/v1/{session.project_id}/subnets"
        query_params = {}
        if limit != 2000:
            query_params['limit'] = str(limit)
        if marker:
            query_params['marker'] = marker
        if vpc_id:
            query_params['vpc_id'] = vpc_id
        if enterprise_project_id:
            query_params['enterprise_project_id'] = enterprise_project_id
        return vpc_api_call(session, "GET", api_path, query_params)
    return list_vpc_resources("subnets", "Subnet", _do_list)
__all__ = ['list_subnets']
