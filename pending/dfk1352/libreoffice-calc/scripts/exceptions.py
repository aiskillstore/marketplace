"""Top-level exceptions for LibreOffice skills."""


class UnoBridgeError(Exception):
    """Error related to UNO bridge operations."""


class SessionClosedError(UnoBridgeError):
    """Error raised when a session is used after it has closed."""
