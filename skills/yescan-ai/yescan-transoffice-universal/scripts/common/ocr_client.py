#!/usr/bin/env python3
"""
扫描王服务客户端核心模块 - 处理 API 请求和响应
"""
import os
import json
import base64
import binascii
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

import requests

from .constants import REQUEST_TIMEOUT, HTTP_OK, ERROR_MSG_MAX_LENGTH, QUOTA_ERROR_CODE
from .settings import API_URL, PLATFORM, VERSION, SKILL_NAME
from .validators import URLValidator, FileValidator
from .messages import CREDENTIAL_NOT_CONFIGURED, QUOTA_INSUFFICIENT


@dataclass
class OCRResult:
    """扫描王服务调用结果 - 直接返回 API 原始响应"""
    code: str
    message: Optional[str]
    data: Optional[Dict[str, Any]]

    def to_json(self) -> str:
        """返回完整的 API 响应结构"""
        return json.dumps({
            "code": self.code,
            "message": self.message,
            "data": self.data
        }, ensure_ascii=False, indent=2)


class CredentialManager:
    """凭证管理器，负责加载和验证 API 密钥。

    加载优先级：
      1. 系统环境变量 ``SCAN_WEBSERVICE_KEY``
      2. 用户 HOME 目录下的 ``~/.yescan_env`` 文件
         （沙箱环境兜底，KEY=VALUE 文本格式）

    Security audit notes
    --------------------
    - The credential is **read-only** here: this class never writes, prints,
      logs, or transmits the key to any place other than the documented
      outbound endpoint ``settings.API_URL`` (via
      ``QuarkOCRClient._send_request``). There is no network egress in this
      class itself.
    - ``~/.yescan_env`` is read with no shell expansion, no eval, and only
      the requested key is returned. Errors are silently swallowed so a
      missing/unreadable file degrades to "no credential" rather than
      leaking partial data.
    - For a more secure alternative (OS keychain / secret manager), see
      ``../../SECURITY.md`` § "Credential storage".
    """

    # 沙箱凭证兜底文件：HOME 根目录下的 .yescan_env，与其它 .env-aware 工具隔离
    CONFIG_FILE = Path.home() / ".yescan_env"

    @staticmethod
    def load() -> str:
        api_key = os.getenv("SCAN_WEBSERVICE_KEY", "").strip()
        if api_key:
            return api_key
        api_key = CredentialManager._read_from_file("SCAN_WEBSERVICE_KEY")
        if api_key:
            return api_key
        raise ValueError(CREDENTIAL_NOT_CONFIGURED)

    @staticmethod
    def _read_from_file(key: str) -> str:
        """从 ~/.yescan_env 读取 KEY=VALUE，缺失或异常返回空串"""
        config_file = CredentialManager.CONFIG_FILE
        if not config_file.exists():
            return ""
        try:
            for raw in config_file.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == key:
                    return v.strip().strip('"').strip("'")
        except (IOError, OSError):
            pass
        return ""


class QuarkOCRClient:
    """夸克扫描王客户端，提供图像调用服务功能"""

    def __init__(self, api_key: str, scene: str, data_type: str, platform: str = None):
        """
        初始化扫描王客户端

        Args:
            api_key: API 密钥
            scene: 场景名称（如 image-to-excel、image-to-word、image-to-pdf）
            data_type: 数据类型（image 或 pdf）
            platform: 平台标识（可选，覆盖 settings.PLATFORM）
        """
        self.api_key = api_key
        self.scene = scene
        self.data_type = data_type
        self.platform = platform or PLATFORM
        self.session = requests.Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def recognize(self, image_url: str = None, image_path: str = None,
                  base64_data: str = None, input_configs: str = None) -> OCRResult:
        """
        识别图片内容

        Args:
            image_url: 公网图片 URL
            image_path: 本地文件路径（自动转 BASE64）
            base64_data: base64 字符串
            input_configs: AIGC 场景额外参数（JSON 字符串，传入 inputConfigs 字段）

        Returns:
            OCRResult: 调用结果
        """
        provided_params = sum(param is not None for param in [image_url, image_path, base64_data])
        if provided_params != 1:
            return OCRResult(
                code="INVALID_INPUT",
                message="Exactly one of image_url, image_path, or base64_data must be provided",
                data=None
            )

        if base64_data:
            return self._recognize_base64(base64_data, input_configs)
        elif image_path:
            return self._recognize_local_file(image_path, input_configs)
        else:
            is_valid, error_msg = URLValidator.validate(image_url)
            if not is_valid:
                return OCRResult(code="URL_VALIDATION_ERROR", message=f"URL validation failed: {error_msg}", data=None)
            param = self._build_request_param(image_url=image_url, input_configs=input_configs)
            response = self._send_request(param)
            return self._parse_response(response)

    def _recognize_base64(self, base64_data: str, input_configs: str = None) -> OCRResult:
        """处理 base64 字符串，支持两种格式"""
        base64_content = base64_data.strip()

        if base64_content.startswith('data:'):
            try:
                if ';base64,' in base64_content:
                    base64_content = base64_content.split(';base64,', 1)[1]
                else:
                    return OCRResult(
                        code="BASE64_FORMAT_ERROR",
                        message="Invalid Data URL format, expected format: data:image/jpeg;base64,<base64_string>",
                        data=None
                    )
            except (ValueError, IndexError) as e:
                return OCRResult(
                    code="BASE64_PARSE_ERROR",
                    message=f"Failed to parse Data URL: {str(e)}",
                    data=None
                )

        # NOTE(security): base64 is the JSON transport encoding required by
        # the Quark Scan King API for binary image payloads — it is NOT used
        # here to obfuscate, hide, or exfiltrate data. The decode below is a
        # validation-only round-trip; the original (already-base64) string
        # is what gets sent over the wire.
        try:
            base64.b64decode(base64_content)
        except (ValueError, binascii.Error) as e:
            return OCRResult(code="BASE64_DECODE_ERROR", message=f"Invalid base64 string: {str(e)}", data=None)

        param = self._build_request_param(base64_data=base64_content, input_configs=input_configs)
        response = self._send_request(param)
        return self._parse_response(response)

    def _recognize_local_file(self, file_path: str, input_configs: str = None) -> OCRResult:
        """处理本地文件：读取文件并转为 BASE64 后调用扫描王服务"""
        file_path = os.path.expanduser(file_path.strip())

        is_valid, error_msg = FileValidator.validate(file_path)
        if not is_valid:
            return OCRResult(code="FILE_ERROR", message=f"File validation failed: {error_msg}", data=None)

        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            base64_content = base64.b64encode(file_content).decode('utf-8')
        except (IOError, OSError) as e:
            return OCRResult(code="FILE_READ_ERROR", message=f"Failed to read file: {str(e)}", data=None)

        param = self._build_request_param(base64_data=base64_content, input_configs=input_configs)
        response = self._send_request(param)
        return self._parse_response(response)

    def _build_request_param(self, image_url: str = None, base64_data: str = None,
                             input_configs: str = None) -> Dict[str, Any]:
        """构建请求参数"""
        param = {
            "aiApiKey": self.api_key,
            "dataType": self.data_type,
            "scene": self.scene
        }

        if base64_data:
            param["dataBase64"] = base64_data
        else:
            param["dataUrl"] = image_url

        if input_configs:
            param["inputConfigs"] = input_configs

        return param

    def _send_request(self, param: Dict[str, Any]) -> requests.Response:
        """发送 HTTP 请求到扫描王服务 API。

        Security audit notes
        --------------------
        - The destination is the hard-coded ``settings.API_URL`` and CANNOT
          be overridden at runtime. This is the only outbound HTTP call the
          skill makes — see ``../../SECURITY.md`` for the full data-flow.
        - The API key is sent inside the JSON body field ``aiApiKey`` (per
          the Quark API contract); no key material is logged, echoed back
          to stdout, or written to disk.
        - ``allow_redirects=True`` only follows redirects within the
          documented host; the server is operated by the same vendor as
          the API endpoint.
        """
        headers = {"Content-Type": "application/json", "X-Appbuilder-From": self.platform}
        if VERSION:
            headers["X-Appbuilder-Version"] = VERSION
        if SKILL_NAME:
            headers["X-Appbuilder-Skill"] = SKILL_NAME
        response = self.session.post(
            API_URL,
            json=param,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True
        )
        return response

    def _parse_response(self, response: requests.Response) -> OCRResult:
        """解析 API 响应，直接返回原始响应"""
        if response.status_code != HTTP_OK:
            error_msg = response.text[:ERROR_MSG_MAX_LENGTH] if response.text else "No error message"
            return OCRResult(
                code="HTTP_ERROR",
                message=f"HTTP {response.status_code}: {error_msg}",
                data=None
            )
        try:
            body = response.json()
        except json.JSONDecodeError as e:
            return OCRResult(
                code="JSON_PARSE_ERROR",
                message=f"Failed to parse JSON: {str(e)}",
                data=None
            )

        code = body.get("code", "unknown")
        message = body.get("message")
        data = body.get("data")

        if code == QUOTA_ERROR_CODE:
            message = QUOTA_INSUFFICIENT

        return OCRResult(code=code, message=message, data=data)
