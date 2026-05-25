#!/usr/bin/env python3
"""
ModelArts SWR 模块

提供SWR（软件仓库）镜像查询功能。
"""

from .image_repos import swr_get_train_image_repos

__all__ = [
    'swr_get_train_image_repos'
]
