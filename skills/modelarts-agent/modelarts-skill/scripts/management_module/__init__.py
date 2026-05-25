#!/usr/bin/env python3
"""
Management模块 - 初始化文件

功能：整合管理相关的所有函数
"""

import sys
sys.path.insert(0, '.')

__version__ = "1.0.0"
__author__ = "OpenClaw Team"

from .authmode import ma_authmode_show, ma_authmode_update
from .workspace import (
    ma_workspace_show,
    ma_workspace_update,
    ma_workspace_delete,
    ma_workspace_show_quotas,
    ma_workspace_update_quotas,
    ma_workspace_list,
    ma_workspace_create,
    ma_workspace_validate_auth
)
from .authorization import (
    ma_authorization_list,
    ma_authorization_add,
    ma_authorization_delete,
    ma_authorization_agency_create
)
from .quota import ma_quota_list
from .tag import ma_tag_list_pool, ma_tag_get_pool
from .scheduled_event import ma_scheduled_event_accept, ma_scheduled_event_list

__all__ = [
    'ma_authmode_show',
    'ma_authmode_update',
    'ma_workspace_show',
    'ma_workspace_update',
    'ma_workspace_delete',
    'ma_workspace_show_quotas',
    'ma_workspace_update_quotas',
    'ma_workspace_list',
    'ma_workspace_create',
    'ma_workspace_validate_auth',
    'ma_authorization_list',
    'ma_authorization_add',
    'ma_authorization_delete',
    'ma_authorization_agency_create',
    'ma_quota_list',
    'ma_tag_list_pool',
    'ma_tag_get_pool',
    'ma_scheduled_event_accept',
    'ma_scheduled_event_list',
]
