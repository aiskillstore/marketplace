"""Unified error types for academic search operations."""


class AcademicSearchError(Exception):
    """Base exception for academic search operations."""


class DataSourceError(AcademicSearchError):
    """Error from a specific data source."""

    def __init__(self, source: str, message: str, original_error: Exception | None = None):
        self.source = source
        self.original_error = original_error
        super().__init__(f"[{source}] {message}")


class TimeoutError(AcademicSearchError):
    """Request timeout after retries."""


class ConfigError(AcademicSearchError):
    """Configuration error."""
