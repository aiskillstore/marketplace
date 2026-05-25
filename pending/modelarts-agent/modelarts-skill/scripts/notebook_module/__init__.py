#!/usr/bin/env python3
"""
Notebook模块 - 初始化文件
功能：整合Notebook相关的所有函数
"""

import sys
sys.path.insert(0, '.')

from .create_notebook import create_notebook
from .list_notebooks import list_notebooks
from .get_notebook import get_notebook
from .update_notebook import update_notebook
from .delete_notebook import delete_notebook
from .start_notebook import start_notebook
from .stop_notebook import stop_notebook
from .list_all_notebooks import list_all_notebooks
from .list_flavors import list_flavors
from .show_switchable_flavors import show_switchable_flavors
from .list_features import list_features
from .list_clusters import list_clusters
from .get_cluster import get_cluster
from .create_image import create_image
from .image_list import image_list
from .image_register import image_register
from .image_list_groups import image_list_groups
from .image_get import image_get
from .image_delete import image_delete
from .image_sync import image_sync
from .list_attachable_obs import list_attachable_obs
from .attach_obs import attach_obs
from .show_attachable_obs import show_attachable_obs
from .cancel_obs import cancel_obs
from .create_tags import create_tags
from .delete_tags import delete_tags
from .show_tags import show_tags
from .show_lease import show_lease
from .renew_lease import renew_lease
from .list_practices import list_practices
from .list_obs_buckets import list_obs_buckets
from .create_obs_bucket import create_obs_bucket
from .delete_obs_bucket import delete_obs_bucket

__all__ = [
    'create_notebook',
    'list_notebooks',
    'get_notebook',
    'update_notebook',
    'delete_notebook',
    'start_notebook',
    'stop_notebook',
    'list_all_notebooks',
    'list_flavors',
    'show_switchable_flavors',
    'list_features',
    'list_clusters',
    'get_cluster',
    'create_image',
    'image_list',
    'image_register',
    'image_list_groups',
    'image_get',
    'image_delete',
    'image_sync',
    'list_attachable_obs',
    'attach_obs',
    'show_attachable_obs',
    'cancel_obs',
    'create_tags',
    'delete_tags',
    'show_tags',
    'show_lease',
    'renew_lease',
    'list_practices',
    'list_obs_buckets',
    'create_obs_bucket',
    'delete_obs_bucket',
]