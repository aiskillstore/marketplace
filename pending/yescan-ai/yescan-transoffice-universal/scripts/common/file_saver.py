#!/usr/bin/env python3
"""
FileSaver - 通用文件保存器
用于保存扫描王服务返回的结果到文件（图片、Word、Excel 等）。

Security audit notes
--------------------
- Output files are written to ``tempfile.gettempdir()`` by default
  (``/tmp`` on POSIX, ``%TEMP%`` on Windows). This is intentional and
  documented in ``../../SECURITY.md`` § "Output file storage". Callers
  may pass an explicit ``filepath`` / ``default_dir`` to redirect output.
- Filenames are generated with ``os.urandom(8)`` to prevent predictable
  paths / symlink races in the shared temp directory.
- Magic-byte detection (``_detect_format_from_magic_bytes``) is a
  **defensive check** — it ensures the decoded payload really is the
  image format we expect before naming the file with that extension. It
  is NOT a binary-execution path; we never run, parse, or interpret the
  bytes beyond this header inspection.
- ``base64.b64decode`` is used purely as the transport-decoding step for
  the JSON API response, not as obfuscation.
"""
import os
import base64
import time
import tempfile
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Set
from pathlib import Path

from .messages import BASE64_CONTENT_EMPTY, FILE_SAVE_SUCCESS, FILE_SAVE_FAILED, UNSUPPORTED_IMAGE_FORMAT

logger = logging.getLogger(__name__)


# ============== 常量定义 ==============
class ResponseCode:
    """响应状态码"""
    SUCCESS = 0
    ERROR = -1


class FileExtension:
    """支持的文件扩展名"""
    DOCX = ".docx"
    XLSX = ".xlsx"
    PDF = ".pdf"
    PNG = ".png"
    JPG = ".jpg"
    WEBP = ".webp"
    GIF = ".gif"
    BMP = ".bmp"
    TIFF = ".tiff"
    WBMP = ".wbmp"


class SubDirectory:
    """子目录常量"""
    IMAGES = "imgs"
    DOCUMENTS = "documents"


# 支持的图片格式集合
SUPPORTED_IMAGE_FORMATS: Set[str] = {"png", "jpg", "jpeg", "gif", "bmp", "webp", "tiff", "tif", "wbmp"}

# 默认保存目录（使用系统临时目录）
DEFAULT_SAVE_DIR = tempfile.gettempdir()


@dataclass
class SaveResult:
    """文件保存结果（类型安全的返回值）"""
    code: int
    msg: str
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {"code": self.code, "msg": self.msg, "data": self.data}

    @classmethod
    def success(cls, path: str) -> "SaveResult":
        """创建成功结果"""
        return cls(code=ResponseCode.SUCCESS, msg="success", data={"path": path})

    @classmethod
    def error(cls, msg: str) -> "SaveResult":
        """创建错误结果"""
        return cls(code=ResponseCode.ERROR, msg=msg, data={})


class FileSaver:
    """文件保存器，支持保存 Base64 编码的二进制文件到指定目录"""

    def __init__(self, default_dir: Optional[str] = None):
        """
        初始化文件保存器

        Args:
            default_dir: 默认保存目录，如果为 None 则使用 /tmp
        """
        self.default_dir = default_dir or DEFAULT_SAVE_DIR
        Path(self.default_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f"FileSaver initialized with default directory: {self.default_dir}")

    def _generate_filepath(self, extension: str, subdir: Optional[str] = None) -> str:
        """
        生成带时间戳的随机文件路径

        Args:
            extension: 文件扩展名（如 .docx, .xlsx, .png）
            subdir: 子目录名（可选）

        Returns:
            完整的文件路径
        """
        save_dir = os.path.join(self.default_dir, subdir) if subdir else self.default_dir
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        filename = f"{int(time.time())}_{os.urandom(8).hex()}{extension}"
        return os.path.join(save_dir, filename)

    @staticmethod
    def _clean_base64(base64_content: str) -> str:
        """清理 Base64 字符串，移除 data URL 前缀"""
        if base64_content and base64_content.strip().startswith("data:"):
            try:
                return base64_content.split(",", 1)[1].strip()
            except (IndexError, ValueError):
                pass
        return base64_content

    @staticmethod
    def _detect_format_from_data_url(base64_content: str) -> Optional[str]:
        """从 data URL 前缀提取图片格式，如 data:image/png;base64,..."""
        if not base64_content or not base64_content.strip().startswith("data:image/"):
            return None
        try:
            # 提取 data:image/png;base64 中的 png
            mime_part = base64_content.split(",", 1)[0]  # data:image/png;base64
            mime_type = mime_part.split(";")[0]  # data:image/png
            fmt = mime_type.split("/")[1]  # png
            return fmt.lower() if fmt else None
        except (IndexError, ValueError):
            return None

    @staticmethod
    def _detect_format_from_magic_bytes(base64_content: str) -> Optional[str]:
        """通过魔术字节检测图片格式"""
        try:
            # 解码前 24 字符（约18字节）足够判断各种格式
            header = base64.b64decode(base64_content[:24])
            # PNG: 89 50 4E 47 0D 0A 1A 0A
            if header[:8] == b'\x89PNG\r\n\x1a\n':
                return "png"
            # JPEG: FF D8 FF
            if header[:3] == b'\xff\xd8\xff':
                return "jpg"
            # GIF: GIF87a 或 GIF89a
            if header[:6] in (b'GIF87a', b'GIF89a'):
                return "gif"
            # BMP: 42 4D ("BM")
            if header[:2] == b'BM':
                return "bmp"
            # WebP: RIFF....WEBP
            if header[:4] == b'RIFF' and header[8:12] == b'WEBP':
                return "webp"
            # TIFF: II 2A 00 (little-endian) 或 MM 00 2A (big-endian)
            if header[:4] in (b'II\x2a\x00', b'MM\x00\x2a'):
                return "tiff"
            # WBMP: 00 00 开头（简单检测，可能不够准确）
            if header[:2] == b'\x00\x00' and len(header) >= 4:
                return "wbmp"
        except Exception:
            pass
        return None

    @staticmethod
    def _validate_base64(base64_content: str) -> Optional[str]:
        """验证 Base64 字符串合法性，返回 None 表示通过"""
        if not base64_content:
            return BASE64_CONTENT_EMPTY
        try:
            if len(base64_content) % 4 != 0:
                raise ValueError("Base64 string length not multiple of 4")
            base64.b64decode(base64_content, validate=True)
        except (ValueError, base64.binascii.Error) as e:
            return f"Invalid Base64: {e}"
        return None

    def save_file_from_base64(
        self,
        base64_content: str,
        extension: str,
        subdir: Optional[str] = None,
        filepath: Optional[str] = None,
        _skip_clean: bool = False
    ) -> Dict[str, Any]:
        """
        通用的 Base64 文件保存方法
    
        Args:
            base64_content: BASE64 编码的内容
            extension: 文件扩展名（如 .docx, .xlsx, .png）
            subdir: 子目录名（可选，如 "imgs"）
            filepath: 指定文件路径（可选，优先级最高）
            _skip_clean: 内部参数，跳过 base64 清理（已清理过时使用）
    
        Returns:
            {"code": 0, "msg": "success", "data": {"path": "/path/to/file"}}
        """
        if not _skip_clean:
            base64_content = self._clean_base64(base64_content)
        error = self._validate_base64(base64_content)
        if error:
            logger.error(error)
            return SaveResult.error(error).to_dict()
    
        if filepath is None:
            filepath = self._generate_filepath(extension, subdir)
    
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(base64.b64decode(base64_content))
            logger.info(FILE_SAVE_SUCCESS.format(path=filepath))
            return SaveResult.success(filepath).to_dict()
        except (IOError, OSError) as e:
            error_msg = FILE_SAVE_FAILED.format(error=e)
            logger.error(error_msg)
            return SaveResult.error(error_msg).to_dict()

    def save_word_from_base64(self, base64_content: str, filepath: Optional[str] = None) -> Dict[str, Any]:
        """从 BASE64 保存 Word 文档"""
        return self.save_file_from_base64(base64_content, FileExtension.DOCX, subdir=SubDirectory.DOCUMENTS, filepath=filepath)

    def save_excel_from_base64(self, base64_content: str, filepath: Optional[str] = None) -> Dict[str, Any]:
        """从 BASE64 保存 Excel 文档"""
        return self.save_file_from_base64(base64_content, FileExtension.XLSX, subdir=SubDirectory.DOCUMENTS, filepath=filepath)

    def save_pdf_from_base64(self, base64_content: str, filepath: Optional[str] = None) -> Dict[str, Any]:
        """从 BASE64 保存 PDF 文档"""
        return self.save_file_from_base64(base64_content, FileExtension.PDF, subdir=SubDirectory.DOCUMENTS, filepath=filepath)

    def save_image_from_base64(self, base64_content: str, image_format: Optional[str] = None) -> Dict[str, Any]:
        """
        从 BASE64 保存图片（支持自动检测格式）

        Args:
            base64_content: BASE64 编码的图片内容
            image_format: 图片格式（可选），支持 png/jpg/jpeg/webp，不指定则自动检测
        """
        # 1. 优先从 data URL 前缀提取格式
        if image_format is None:
            image_format = self._detect_format_from_data_url(base64_content)

        # 2. 清理 base64 内容
        clean_content = self._clean_base64(base64_content)

        # 3. 仍未知则通过魔术字节检测
        if image_format is None:
            image_format = self._detect_format_from_magic_bytes(clean_content)

        # 4. 最终兜底默认 png
        fmt = (image_format or "png").lower()
        if fmt not in SUPPORTED_IMAGE_FORMATS:
            error_msg = UNSUPPORTED_IMAGE_FORMAT.format(format=image_format, supported=SUPPORTED_IMAGE_FORMATS)
            logger.error(error_msg)
            return SaveResult.error(error_msg).to_dict()

        # jpeg -> jpg, tif -> tiff 统一扩展名
        ext = "." + fmt.replace("jpeg", "jpg").replace("tif", "tiff")
        return self.save_file_from_base64(clean_content, ext, subdir=SubDirectory.IMAGES, _skip_clean=True)
