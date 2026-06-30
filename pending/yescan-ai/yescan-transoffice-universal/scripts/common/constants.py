#!/usr/bin/env python3
"""
公共常量定义
"""


# 文件配置
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif", ".wbmp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# 请求配置
REQUEST_TIMEOUT = 120  # 秒

# HTTP 状态码
HTTP_OK = 200

# 错误消息最大截取长度
ERROR_MSG_MAX_LENGTH = 200

# API 成功响应码
SUCCESS_CODE = "00000"

# 配额不足错误码
QUOTA_ERROR_CODE = "A0211"

