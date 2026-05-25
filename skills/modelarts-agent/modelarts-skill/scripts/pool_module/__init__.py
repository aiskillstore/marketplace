#!/usr/bin/env python3
"""
Pool模块 - 专属资源池管理
"""

from .list_pools import list_pools
from .get_pool import get_pool
from .create_pool import create_pool
from .update_pool import update_pool
from .delete_pool import delete_pool
from .list_pool_nodes import list_pool_nodes
from .batch_delete_nodes import batch_delete_nodes
from .batch_reboot_nodes import batch_reboot_nodes
from .batch_lock_nodes import batch_lock_nodes
from .batch_unlock_nodes import batch_unlock_nodes
from .batch_update_nodes import batch_update_nodes
from .batch_reset_nodes import batch_reset_nodes
from .batch_resize_nodes import batch_resize_nodes
from .batch_migrate_nodes import batch_migrate_nodes
from .batch_bind_nodes import batch_bind_nodes
from .list_pool_workloads import list_pool_workloads
from .pool_workload_statistics import pool_workload_statistics
from .list_resource_flavors import list_resource_flavors
from .pool_statistics import pool_statistics
from .pool_monitor import pool_monitor
from .get_pool_runtime_metrics import get_pool_runtime_metrics
from .list_os_networks import list_os_networks
from .get_os_network import get_os_network
from .create_os_network import create_os_network
from .delete_os_network import delete_os_network
from .patch_os_network import patch_os_network
from .get_os_config import get_os_config
from .list_os_events import list_os_events
from .list_plugin_templates import list_plugin_templates
from .get_plugin_template import get_plugin_template


__all__ = [
    'list_pools',
    'get_pool',
    'create_pool',
    'update_pool',
    'delete_pool',
    'list_pool_nodes',
    'batch_delete_nodes',
    'batch_reboot_nodes',
    'batch_lock_nodes',
    'batch_unlock_nodes',
    'batch_update_nodes',
    'batch_reset_nodes',
    'batch_resize_nodes',
    'batch_migrate_nodes',
    'batch_bind_nodes',
    'list_pool_workloads',
    'pool_workload_statistics',
    'list_resource_flavors',
    'pool_statistics',
    'pool_monitor',
    'get_pool_runtime_metrics',
    'list_os_networks',
    'get_os_network',
    'create_os_network',
    'delete_os_network',
    'patch_os_network',
    'get_os_config',
    'list_os_events',
    'list_plugin_templates',
    'get_plugin_template',
]