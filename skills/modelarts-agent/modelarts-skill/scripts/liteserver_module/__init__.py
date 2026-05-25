#!/usr/bin/env python3
"""
Lite Server 模块 - 初始化文件
功能：导出所有 Lite Server API 函数
"""

import sys
from typing import Dict, Any, List, Optional

sys.path.insert(0, '.')
# 版本信息
__version__ = "1.1.0"
__author__ = "OpenClaw Team"
__description__ = "ModelArts Lite Server Management API Module"
# 从各个文件导入函数
from .create_dev_server import ma_liteserver_create
from .list_dev_servers import ma_liteserver_list
from .get_dev_server import ma_liteserver_get
from .update_dev_server import ma_liteserver_update
from .stop_dev_server import ma_liteserver_stop
from .start_dev_server import ma_liteserver_start
from .delete_dev_server import ma_liteserver_delete
# Hyper Cluster 管理
from .create_hyper_cluster import ma_liteserver_create_hyper_cluster
from .list_hyper_clusters import ma_liteserver_list_hyper_clusters
from .get_hyper_cluster import ma_liteserver_get_hyper_cluster
from .delete_hyper_cluster import ma_liteserver_delete_hyper_cluster
from .sync_dev_servers import ma_liteserver_sync
# 标签管理
from .create_hyper_tags import ma_liteserver_create_hyper_tags
from .delete_hyper_tags import ma_liteserver_delete_hyper_tags
from .query_hyper_tags import ma_liteserver_query_hyper_tags
# 操作系统管理
from .reinstall_dev_server_os import ma_liteserver_reinstall_os
from .change_dev_server_os import ma_liteserver_change_os
from .change_hyper_os import ma_liteserver_change_hyper_os
# Hyperinstance 管理
from .list_hyperinstances import ma_liteserver_list_hyperinstances
from .get_hyperinstance import ma_liteserver_get_hyperinstance
from .delete_hyperinstance import ma_liteserver_delete_hyperinstance
from .reboot_dev_server import ma_liteserver_reboot
from .start_hyperinstance import ma_liteserver_start_hyperinstance
from .stop_hyperinstance import ma_liteserver_stop_hyperinstance
# 存储与网络管理
from .attach_volume import ma_liteserver_attach_volume
from .detach_volume import ma_liteserver_detach_volume
from .bind_eip import ma_liteserver_bind_eip
from .list_public_ips import ma_liteserver_list_public_ips
from .list_eips import ma_liteserver_list_eips
from .create_roce_network import ma_liteserver_create_roce_network
# 规格与镜像（增强版支持查询参数和自动选择）
from .list_flavors import ma_liteserver_list_flavors
from .list_resource_flavors import ma_liteserver_list_resource_flavors
from .list_images import ma_liteserver_list_images
from .get_image import ma_liteserver_get_image
# 批量操作
from .list_all_dev_servers import ma_liteserver_list_all
from .list_all_hyperinstances import ma_liteserver_list_all_hyperinstances
# 扩缩容
from .scale_up_hyperinstance import ma_liteserver_scale_up_hyperinstance
from .scale_down_hyperinstance import ma_liteserver_scale_down_hyperinstance
# 操作与拓扑
from .get_dev_server_operation import ma_liteserver_get_operation
from .get_scale_evaluations import ma_liteserver_get_scale_evaluations
from .list_hyper_clusters_capacity import ma_liteserver_list_hyper_clusters_capacity
from .get_topologies import ma_liteserver_get_topologies
from .batch_action import ma_liteserver_batch_action
# 作业管理
from .get_job import ma_liteserver_get_job
from .list_jobs import ma_liteserver_list_jobs
from .delete_jobs import ma_liteserver_delete_jobs
from .create_job import ma_liteserver_create_job
from .list_job_templates import ma_liteserver_list_job_templates
from .get_job_template import ma_liteserver_get_job_template
# 插件与软件
from .list_plugins import ma_liteserver_list_plugins
from .show_software import ma_liteserver_show_software
from .get_job_service import ma_liteserver_get_job_service
# 公共函数（包含自动选择辅助函数）
from .common import (
    validate_dev_server_params,
    format_paginated_result,
    add_api_reference,
    validate_required_params,
    build_request_body,
    build_query_params,
    get_available_flavor,
    get_image_by_flavor
)

__all__ = [
    # 已实现的函数
    'ma_liteserver_create',
    'ma_liteserver_list',
    'ma_liteserver_get',
    'ma_liteserver_update',
    'ma_liteserver_stop',
    'ma_liteserver_start',
    'ma_liteserver_delete',
    'ma_liteserver_reboot',
    'ma_liteserver_sync',
    'ma_liteserver_reinstall_os',
    'ma_liteserver_bind_eip',
    'ma_liteserver_list_public_ips',
    'ma_liteserver_list_all',
    'ma_liteserver_list_flavors',
    'ma_liteserver_list_resource_flavors',
    'ma_liteserver_list_images',
    'ma_liteserver_get_image',
    'ma_liteserver_batch_action',
    'ma_liteserver_list_jobs',
    'ma_liteserver_get_job',
    'ma_liteserver_delete_jobs',
    'ma_liteserver_create_job',
    'ma_liteserver_list_job_templates',
    'ma_liteserver_get_job_template',
    'ma_liteserver_get_job_service',
    'ma_liteserver_show_software',
    'ma_liteserver_list_plugins',
    # Hyper Cluster 管理
    'ma_liteserver_create_hyper_cluster',
    'ma_liteserver_list_hyper_clusters',
    'ma_liteserver_get_hyper_cluster',
    'ma_liteserver_delete_hyper_cluster',
    # 标签管理
    'ma_liteserver_create_hyper_tags',
    'ma_liteserver_delete_hyper_tags',
    'ma_liteserver_query_hyper_tags',
    # 操作系统管理
    'ma_liteserver_change_os',
    'ma_liteserver_change_hyper_os',
    # Hyperinstance 管理
    'ma_liteserver_list_hyperinstances',
    'ma_liteserver_get_hyperinstance',
    'ma_liteserver_delete_hyperinstance',
    'ma_liteserver_start_hyperinstance',
    'ma_liteserver_stop_hyperinstance',
    'ma_liteserver_list_all_hyperinstances',
    'ma_liteserver_scale_up_hyperinstance',
    'ma_liteserver_scale_down_hyperinstance',
    # 存储与网络管理
    'ma_liteserver_attach_volume',
    'ma_liteserver_detach_volume',
    'ma_liteserver_list_eips',
    'ma_liteserver_create_roce_network',
    # 操作与拓扑
    'ma_liteserver_get_operation',
    'ma_liteserver_get_scale_evaluations',
    'ma_liteserver_list_hyper_clusters_capacity',
    'ma_liteserver_get_topologies',
    # 公共辅助函数
    'validate_dev_server_params',
    'format_paginated_result',
    'add_api_reference',
    'validate_required_params',
    'build_request_body',
    'build_query_params',
    'get_available_flavor',
    'get_image_by_flavor',
    # 辅助函数
    'ma_get_liteserver_skill_info',
]
# 模块统计信息
__stats__ = {
    "total_apis": 51,
    "structure": "每个API一个文件，扁平化组织",
    "max_lines_per_file": 150,
    "max_cyclomatic_complexity": 15,
    "api_chapter": "Chapter 22 (Lite Server / Lightweight Computing Node)",
    "enhanced_features": [
        "支持通过 availability_zone, arch 等参数过滤规格",
        "支持自动选择可用规格（优先 resource_flavor）",
        "支持根据规格自动选择镜像",
        "创建时设置 auto_select=False 可禁用自动选择"
    ]
}
# 技能信息函数
def ma_get_liteserver_skill_info() -> Dict[str, Any]:
    """
    Get information about this Lite Server tools skill.
    Returns:
        Skill metadata including version, available functions, API compliance
    """
    return {
        "name": "ModelArts Lite Server Management Tools",
        "version": __version__,
        "description": __description__,
        "api_compliance": "ModelArts API 22.1-22.51 (Lite Server)",
        "security_level": "high",
        "status": "operational",
        "structure": __stats__["structure"],
        "total_functions": 51,
        "implemented_apis": [
            "22.1 CreateDevServer", "22.2 ListDevServers", "22.3 ShowDevServer",
            "22.4 UpdateDevServer", "22.5 StopDevServer", "22.6 StartDevServer",
            "22.7 DeleteDevServer", "22.8 CreateHyperCluster", "22.9 ListHyperCluster",
            "22.10 GetHyperCluster", "22.11 DeleteHyperCluster", "22.12 SyncDevServers",
            "22.13 CreateHyperinstanceTags", "22.14 DeleteHyperinstanceTags",
            "22.15 QueryHyperinstanceTags", "22.16 ReinstallDevServerOS",
            "22.17 ChangeDevServerOS", "22.18 ChangeHyperinstanceOS",
            "22.19 ListHyperinstances", "22.20 GetHyperinstance",
            "22.21 DeleteHyperinstance", "22.22 RebootDevServer",
            "22.23 StartHyperinstance", "22.24 StopHyperinstance",
            "22.25 AttachDevServerVolume", "22.26 DetachDevServerVolume",
            "22.27 BindDevServerPublicIP", "22.28 ListDevServerPublicIP",
            "22.29 ListDevServerFlavors", "22.30 ListDevServerResourceflavors",
            "22.31 CreateRoceNetwork", "22.32 ListAllDevServers",
            "22.33 GetDevServerImage", "22.34 ListDevServerImages",
            "22.35 ListAllHyperinstances", "22.36 ScaleUpHyperinstance",
            "22.37 ScaleDownHyperinstance", "22.38 GetDevServerOperation",
            "22.39 GetScaleEvaluationsDevServer", "22.40 ListHyperinstanceClustersCapacity",
            "22.41 GetTopologies", "22.42 BatchDevServersAction",
            "22.43 GetDevServerJob", "22.44 ListDevServerJobs",
            "22.45 DeleteDevServerJobs", "22.46 CreateDevServerJob",
            "22.47 ListDevServerJobTemplates", "22.48 GetDevServerJobTemplate",
            "22.49 ListPlugins", "22.50 ShowSoftware",
            "22.51 GetDevServerJobService"
        ],
        "enhanced_features": __stats__["enhanced_features"]
    }
# 将技能信息函数也导出
__all__.append('ma_get_liteserver_skill_info')
