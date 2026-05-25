#!/usr/bin/env python3
"""
VPC 模块 - 查询虚拟私有云列表
功能：查询当前账号下的VPC列表（ListVpcs）
API: GET https://vpc.{region}.myhuaweicloud.com/v1/{project_id}/vpcs
"""

import sys
from typing import Dict, Any, Optional

sys.path.insert(0, '.')

from vpc_module.common import list_vpc_resources, vpc_api_call

def list_vpcs(
    limit: int = 10,
    marker: Optional[str] = None,
    vpc_id: Optional[str] = None,
    enterprise_project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    查询虚拟私有云列表（ListVpcs）

    API: GET https://vpc.{region}.myhuaweicloud.com/v1/{project_id}/vpcs
    Args:
        limit: 分页查询每页返回的记录个数，取值范围为0~2000，默认2000
        marker: 分页查询的起始资源ID，表示从指定资源的下一条记录开始查询
                需要和limit配合使用。若不传入marker和limit参数，查询结果返回第一页全部资源记录
        vpc_id: 按照VPC ID过滤查询
        enterprise_project_id: 按照企业项目ID过滤查询
                               "0"表示默认企业项目，"all_granted_eps"表示查询所有企业项目
    Returns:
        Dict[str, Any]:
        {
            "success": bool,
            "data": {
                "vpcs": [
                    {
                        "id": "uuid",
                        "name": "vpc-name",
                        "cidr": "192.168.0.0/16",
                        "status": "OK",
                        "description": "...",
                        "enterprise_project_id": "0",
                        "routes": [],
                        "created_at": "2022-12-15T02:11:13",
                        "updated_at": "2022-12-15T02:11:13",
                        ...
                    },
                    ...
                ],
                "total": int
            },
            "status_code": int
        }
    Example:
        >>> from vpc_module import list_vpcs
        >>> result = list_vpcs(limit=10)
        >>> if result['success']:
        ...     for vpc in result['data']['vpcs']:
        ...         print(f"{vpc['name']} ({vpc['id']}): {vpc['cidr']}")
    Related:
        - 查询子网: subnets.list_subnets(vpc_id=vpc_id)
        - 查询安全组: security_groups.list_security_groups(vpc_id=vpc_id)
    """
    def _do_list(session):
        api_path = f"/v1/{session.project_id}/vpcs"
        query_params = {}
        if limit != 2000:
            query_params['limit'] = str(limit)
        if marker:
            query_params['marker'] = marker
        if vpc_id:
            query_params['id'] = vpc_id
        if enterprise_project_id:
            query_params['enterprise_project_id'] = enterprise_project_id
        return vpc_api_call(session, "GET", api_path, query_params)
    return list_vpc_resources("vpcs", "VPC", _do_list)
__all__ = ['list_vpcs']
