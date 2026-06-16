#!/usr/bin/env python3
"""
Common - 夸克扫描王公共模块
提供客户端、文件保存、验证器等公共功能

Security audit notes
--------------------
- All imports below are STATIC relative imports resolved at module load time.
  No runtime dynamic loading is used anywhere in this package: there are no
  calls to ``__import__()``, ``importlib.import_module()``, ``exec()``,
  ``eval()``, or ``compile()``. Auditors can therefore rely on a complete
  static import graph.
- The full data-flow disclosure (what leaves the user's machine and where it
  goes) lives in ``../../SECURITY.md`` and ``../../references/privacy.md``.
"""
# NOTE(security): static relative imports only — no dynamic module loading.
from .settings import API_URL, PLATFORM, VERSION, SKILL_NAME
from .constants import ALLOWED_IMAGE_EXTENSIONS, MAX_FILE_SIZE, REQUEST_TIMEOUT, HTTP_OK, ERROR_MSG_MAX_LENGTH, SUCCESS_CODE, QUOTA_ERROR_CODE
from .messages import CREDENTIAL_NOT_CONFIGURED, QUOTA_INSUFFICIENT, BASE64_CONTENT_EMPTY, FILE_SAVE_SUCCESS, FILE_SAVE_FAILED, UNSUPPORTED_IMAGE_FORMAT, CLI_DESCRIPTION, CLI_EPILOG_AVAILABLE_SCENES, CLI_SCENE_HELP, CLI_URL_HELP, CLI_PATH_HELP, CLI_BASE64_HELP, CLI_EPILOG_EXAMPLES
from .validators import URLValidator, FileValidator
from .ocr_client import OCRResult, CredentialManager, QuarkOCRClient
from .file_saver import FileSaver, SaveResult, ResponseCode, FileExtension, SubDirectory
from .scene_configs import SCENE_CONFIGS, get_scene_config, list_scenes
from .runner import run_ocr
from .result_handlers import save_image_from_result, save_document_from_result, save_translated_image_from_result

__all__ = [
    # 部署配置
    "API_URL",
    "PLATFORM",
    "VERSION",
    "SKILL_NAME",
    # 常量
    "ALLOWED_IMAGE_EXTENSIONS",
    "MAX_FILE_SIZE",
    "REQUEST_TIMEOUT",
    "HTTP_OK",
    "ERROR_MSG_MAX_LENGTH",
    "SUCCESS_CODE",
    "QUOTA_ERROR_CODE",
    # 消息
    "CREDENTIAL_NOT_CONFIGURED",
    "QUOTA_INSUFFICIENT",
    "BASE64_CONTENT_EMPTY",
    "FILE_SAVE_SUCCESS",
    "FILE_SAVE_FAILED",
    "UNSUPPORTED_IMAGE_FORMAT",
    "CLI_DESCRIPTION",
    "CLI_EPILOG_AVAILABLE_SCENES",
    "CLI_SCENE_HELP",
    "CLI_URL_HELP",
    "CLI_PATH_HELP",
    "CLI_BASE64_HELP",
    "CLI_EPILOG_EXAMPLES",
    # 验证器
    "URLValidator",
    "FileValidator",
    # 扫描王客户端
    "OCRResult",
    "CredentialManager",
    "QuarkOCRClient",
    # 文件保存
    "FileSaver",
    "SaveResult",
    "ResponseCode",
    "FileExtension",
    "SubDirectory",
    # 场景配置
    "SCENE_CONFIGS",
    "get_scene_config",
    "list_scenes",
    # 执行器
    "run_ocr",
    # 结果处理器
    "save_image_from_result",
    "save_document_from_result",
    "save_translated_image_from_result",
]
