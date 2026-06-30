#!/usr/bin/env python3
"""
验证器模块 - URL 和文件验证
"""
import os
from typing import Tuple, Optional
from urllib.parse import urlparse

from .constants import ALLOWED_IMAGE_EXTENSIONS, MAX_FILE_SIZE


class URLValidator:
    """URL 基础验证器"""

    @staticmethod
    def validate(url: str) -> Tuple[bool, Optional[str]]:
        """
        验证 URL 格式

        Args:
            url: 待验证的 URL

        Returns:
            (是否有效, 错误信息)
        """
        if not url or not isinstance(url, str):
            return False, "URL cannot be empty"

        url = url.strip()

        try:
            parsed = urlparse(url)
        except ValueError as e:
            return False, f"Invalid URL format: {str(e)}"

        if parsed.scheme.lower() not in {"http", "https"}:
            return False, f"Protocol '{parsed.scheme}' not allowed."

        return True, None


class FileValidator:
    """文件验证器"""

    @staticmethod
    def validate(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        验证本地文件

        Args:
            file_path: 文件路径

        Returns:
            (是否有效, 错误信息)
        """
        if not file_path or not isinstance(file_path, str):
            return False, "File path cannot be empty"

        file_path = os.path.expanduser(file_path.strip())

        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"

        if not os.path.isfile(file_path):
            return False, f"Not a file: {file_path}"

        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            return False, f"File size exceeds {MAX_FILE_SIZE / 1024 / 1024}MB limit"

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            return False, f"File extension '{ext}' not allowed"

        return True, None
