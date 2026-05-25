#!/usr/bin/env python3
"""
ModelArts KMS 模块
提供KMS（密钥管理服务）功能：
- 查询SSH密钥对列表（ListKeypairs）
"""

from .keypairs import list_keypairs

__all__ = [
    'list_keypairs'
]
