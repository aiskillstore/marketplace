"""Custom exceptions for the Impress skill."""

from exceptions import SessionClosedError, UnoBridgeError


class ImpressSkillError(Exception):
    """Base error for Impress skill."""


class ImpressSessionError(ImpressSkillError):
    """Error for Impress session lifecycle misuse."""


class PatchSyntaxError(ImpressSkillError):
    """Error for malformed Impress patch input."""


class PatchOperationError(ImpressSkillError):
    """Base error for parsed Impress patch operations."""


class InvalidTargetError(PatchOperationError):
    """Error for malformed or contradictory targets."""


class TargetNoMatchError(PatchOperationError):
    """Error when a valid target matches no Impress content."""


class TargetAmbiguousError(PatchOperationError):
    """Error when a valid target matches more than one Impress result."""


class InvalidFormattingError(PatchOperationError):
    """Error for empty or unsupported formatting payloads."""


class InvalidListError(PatchOperationError):
    """Error for malformed or unsupported list payloads."""


class InvalidPayloadError(PatchOperationError):
    """Error for invalid operation payload data."""


class DocumentNotFoundError(ImpressSkillError):
    """Error when presentation file does not exist."""


class MediaNotFoundError(PatchOperationError):
    """Error when media or image file is not found."""


class InvalidSlideIndexError(InvalidTargetError):
    """Compatibility error for invalid slide indices."""


class InvalidLayoutError(InvalidPayloadError):
    """Compatibility error for unsupported slide layouts."""


class InvalidShapeError(InvalidPayloadError):
    """Compatibility error for unsupported shape types."""


class MasterNotFoundError(TargetNoMatchError):
    """Compatibility error when a master page name is not found."""


__all__ = [
    "ImpressSkillError",
    "ImpressSessionError",
    "PatchSyntaxError",
    "PatchOperationError",
    "InvalidTargetError",
    "TargetNoMatchError",
    "TargetAmbiguousError",
    "InvalidFormattingError",
    "InvalidListError",
    "InvalidPayloadError",
    "DocumentNotFoundError",
    "MediaNotFoundError",
    "InvalidSlideIndexError",
    "InvalidLayoutError",
    "InvalidShapeError",
    "MasterNotFoundError",
    "UnoBridgeError",
    "SessionClosedError",
]
