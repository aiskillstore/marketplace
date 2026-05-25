#!/usr/bin/env python3
"""
Pool模块 - get_os_config函数
功能：获取 OS 配置
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, List


@authenticated_api_call
def get_os_config(access) -> Dict[str, Any]:
    """
    获取 OS 配置

    Args:
        无

    Returns:
        OS 配置信息，包含:
        - clusterFlavorSpecs: 集群规格列表
        - defaultClusterFlavor: 默认集群规格
        - networkCidrs: 网络 CIDR 范围
        - networkQuota: 网络配额
        - nodeOSVersionSupport: 支持的 OS 版本和服务截止时间
        - poolHighAvailable: 资源池高可用开关
        - poolQuota: 资源池配额
        - poolScopePlugins: 各 scope 支持的插件
        - volumeTypes: 支持的磁盘类型
    
    调用经验:
        - 无需参数，直接调用
        - 返回全局配置信息，创建资源池和网络时需要参考
    """
    

    result = access_api_call(
        access,
        "GET",
        "/v1/{project_id}/os-user-config",
        query={}
    )

    return format_api_result(True, data=result)


__all__ = ["get_os_config"]