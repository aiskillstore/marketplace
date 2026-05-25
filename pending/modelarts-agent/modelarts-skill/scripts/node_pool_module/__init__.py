#!/usr/bin/env python3
"""
NodePool模块 - 节点池管理
"""

from .list_node_pools import list_node_pools
from .get_node_pool import get_node_pool
from .create_node_pool import create_node_pool
from .update_node_pool import update_node_pool, scale_node_pool
from .delete_node_pool import delete_node_pool
from .list_node_pool_nodes import list_node_pool_nodes
from .list_pool_plugins import list_pool_plugins
from .create_pool_plugin import create_pool_plugin
from .get_config_template import get_config_template


__all__ = [
    'list_node_pools',
    'get_node_pool',
    'create_node_pool',
    'update_node_pool',
    'delete_node_pool',
    'scale_node_pool',
    'list_node_pool_nodes',
    'list_pool_plugins',
    'create_pool_plugin',
    'get_config_template',
]