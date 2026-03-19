"""Custom exceptions for Writer skill."""

from exceptions import SessionClosedError, UnoBridgeError


class WriterSkillError(Exception):
    """Base error for Writer skill."""


class WriterSessionError(WriterSkillError):
    """Error for Writer session lifecycle misuse."""


class DocumentNotFoundError(WriterSkillError):
    """Error when document file is not found."""


class InvalidMetadataError(WriterSkillError):
    """Error for invalid metadata parameters."""


class PatchSyntaxError(WriterSkillError):
    """Error for malformed Writer patch input."""


class PatchOperationError(WriterSkillError):
    """Base error for parsed Writer patch operations."""


class InvalidTargetError(PatchOperationError):
    """Error for malformed or unsupported targets."""


class TargetNoMatchError(PatchOperationError):
    """Error when a target matches no document content."""


class TargetAmbiguousError(PatchOperationError):
    """Error when a target matches more than one element."""


class InvalidFormattingError(PatchOperationError):
    """Error for invalid formatting parameters."""


class InvalidListError(PatchOperationError):
    """Error for invalid list parameters."""


class InvalidTableError(PatchOperationError):
    """Error for invalid table parameters."""


class ImageNotFoundError(PatchOperationError):
    """Error when image file is not found."""


class InvalidPayloadError(PatchOperationError):
    """Error when patch payload data is invalid for the target."""


__all__ = [
    "WriterSkillError",
    "WriterSessionError",
    "UnoBridgeError",
    "SessionClosedError",
    "DocumentNotFoundError",
    "InvalidMetadataError",
    "PatchSyntaxError",
    "PatchOperationError",
    "InvalidTargetError",
    "TargetNoMatchError",
    "TargetAmbiguousError",
    "InvalidFormattingError",
    "InvalidListError",
    "InvalidTableError",
    "ImageNotFoundError",
    "InvalidPayloadError",
]
