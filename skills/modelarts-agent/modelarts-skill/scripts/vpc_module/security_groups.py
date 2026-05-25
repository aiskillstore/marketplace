#!/usr/bin/env python3
"""
VPC 模块 - 查询安全组列表
功能：查询安全组列表（ListSecurityGroups）
API: GET https://vpc.{region}.myhuaweicloud.com/v1/{project_id}/security-groups
"""

import sys
from typing import Dict, Any, Optional

sys.path.insert(0, '.')

from vpc_module.common import list_vpc_resources, vpc_api_call

def list_security_groups(
    limit: int = 10,
    marker: Optional[str] = None,
    vpc_id: Optional[str] = None,
    enterprise_project_id: Optional[str] = None,
    remote_address_group_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    查询安全组列表（ListSecurityGroups）
    Args:
        limit: 分页查询每页返回的记录个数，取值范围为0~2000，默认2000
        marker: 分页查询的起始资源ID，表示从指定资源的下一条记录开始查询
                需要和limit配合使用。若不传入marker和limit参数，查询结果返回第一页全部资源记录
        vpc_id: 按照vpc_id过滤查询
        enterprise_project_id: 按照企业项目ID过滤查询
                               "0"表示默认企业项目，"all_granted_eps"表示查询所有企业项目
        remote_address_group_id: 远端IP地址组ID，和remote_ip_prefix, remote_group_id功能互斥
    Returns:
        Dict[str, Any]:
        {
            "success": bool,
            "data": {
                "security_groups": [
                    {
                        "id": "uuid",
                        "name": "sg-name",
                        "description": "security group description",
                        "vpc_id": "vpc-uuid",
                        "enterprise_project_id": "0",
                        "security_group_rules": [
                            {
                                "id": "rule-uuid",
                                "direction": "ingress",
                                "protocol": "tcp",
                                "port_range_min": 22,
                                "port_range_max": 22,
                                "remote_ip_prefix": "0.0.0.0/0",
                                "description": "SSH access",
                                ...
                            },
                            ...
                        ],
                        ...
                    },
                    ...
                ],
                "total": int
            },
            "status_code": int
        }
    Example:
        >>> from vpc_module import list_security_groups
        >>> # 查询所有安全组
        >>> result = list_security_groups()
        >>> if result['success']:
        ...     for sg in result['data']['security_groups']:
        ...         print(f"{sg['name']} ({sg['id']}): {len(sg['security_group_rules'])} rules")
        >>>
        >>> # 查询指定VPC下的安全组
        >>> result = list_security_groups(vpc_id='3ec3b33f-ac1c-4630-ad1c-7dba1ed79d85')
        >>>
        >>> # 查看安全组规则
        >>> result = list_security_groups()
        >>> if result['success']:
        ...     for sg in result['data']['security_groups']:
        ...         for rule in sg.get('security_group_rules', []):
        ...             print(f"{rule['direction']}: {rule['protocol']} {rule.get('port_range_min', 'all')}->{rule.get('port_range_max', 'all')}")
    Related:
        - 查询VPC列表: vpcs.list_vpcs()
        - 查询子网: subnets.list_subnets(vpc_id=vpc_id)
    """
    def _do_list(session):
        api_path = f"/v1/{session.project_id}/security-groups"
        query_params = {}
        if limit != 2000:
            query_params['limit'] = str(limit)
        if marker:
            query_params['marker'] = marker
        if vpc_id:
            query_params['vpc_id'] = vpc_id
        if enterprise_project_id:
            query_params['enterprise_project_id'] = enterprise_project_id
        if remote_address_group_id:
            query_params['remote_address_group_id'] = remote_address_group_id
        return vpc_api_call(session, "GET", api_path, query_params)
    return list_vpc_resources("security_groups", "SecurityGroup", _do_list)
__all__ = ['list_security_groups']
