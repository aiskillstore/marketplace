"""Custom exceptions for Writer skill."""

from exceptions import UnoBridgeError


class WriterSkillError(Exception):
    """Base error for Writer skill."""


class DocumentNotFoundError(WriterSkillError):
    """Error when document file is not found."""


class InvalidFormattingError(WriterSkillError):
    """Error for invalid formatting parameters."""


class InvalidTableError(WriterSkillError):
    """Error for invalid table parameters."""


class ImageNotFoundError(WriterSkillError):
    """Error when image file is not found."""


class InvalidMetadataError(WriterSkillError):
    """Error for invalid metadata parameters."""


# Re-export for compatibility
__all__ = [
    "WriterSkillError",
    "UnoBridgeError",
    "DocumentNotFoundError",
    "InvalidFormattingError",
    "InvalidTableError",
    "ImageNotFoundError",
    "InvalidMetadataError",
]
