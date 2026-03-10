"""Custom exceptions for Calc skill."""

from exceptions import UnoBridgeError


class CalcSkillError(Exception):
    """Base error for Calc skill."""


class SheetNotFoundError(CalcSkillError):
    """Error when a sheet is not found."""


class InvalidCellReferenceError(CalcSkillError):
    """Error for invalid cell coordinates."""


class FormulaError(CalcSkillError):
    """Error for formula evaluation issues."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        super().__init__(message)
        self.error_code = error_code


class ChartError(CalcSkillError):
    """Error for chart operations."""


class ValidationError(CalcSkillError):
    """Error for validation rule operations."""


__all__ = [
    "CalcSkillError",
    "UnoBridgeError",
    "SheetNotFoundError",
    "InvalidCellReferenceError",
    "FormulaError",
    "ChartError",
    "ValidationError",
]
