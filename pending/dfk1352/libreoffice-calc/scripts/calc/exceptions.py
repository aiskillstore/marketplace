"""Custom exceptions for the Calc skill."""

from exceptions import SessionClosedError, UnoBridgeError


class CalcSkillError(Exception):
    """Base error for Calc skill."""


class CalcSessionError(CalcSkillError):
    """Error for Calc session lifecycle misuse."""


class PatchSyntaxError(CalcSkillError):
    """Error for malformed Calc patch input."""


class PatchOperationError(CalcSkillError):
    """Base error for parsed Calc patch operations."""


class InvalidTargetError(PatchOperationError):
    """Error for malformed or contradictory targets."""


class TargetNoMatchError(PatchOperationError):
    """Error when a valid target matches no Calc content."""


class TargetAmbiguousError(PatchOperationError):
    """Error when a valid target matches more than one result."""


class InvalidFormattingError(PatchOperationError):
    """Error for empty or unsupported formatting payloads."""


class InvalidValidationError(PatchOperationError):
    """Error for malformed or unsupported validation payloads."""


class InvalidPayloadError(PatchOperationError):
    """Error for invalid operation payload data."""


class NamedRangeNotFoundError(PatchOperationError):
    """Error when a named range target cannot be resolved."""


class ChartNotFoundError(PatchOperationError):
    """Error when a chart target cannot be resolved."""


class DocumentNotFoundError(CalcSkillError):
    """Error when spreadsheet file does not exist."""


__all__ = [
    "CalcSkillError",
    "CalcSessionError",
    "PatchSyntaxError",
    "PatchOperationError",
    "InvalidTargetError",
    "TargetNoMatchError",
    "TargetAmbiguousError",
    "InvalidFormattingError",
    "InvalidValidationError",
    "InvalidPayloadError",
    "NamedRangeNotFoundError",
    "ChartNotFoundError",
    "DocumentNotFoundError",
    "UnoBridgeError",
    "SessionClosedError",
]
