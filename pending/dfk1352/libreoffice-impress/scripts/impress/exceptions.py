"""Custom exceptions for Impress skill."""


class ImpressSkillError(Exception):
    """Base error for Impress skill."""


class DocumentNotFoundError(ImpressSkillError):
    """Error when document file is not found."""


class InvalidSlideIndexError(ImpressSkillError):
    """Error when slide index is out of range."""


class InvalidLayoutError(ImpressSkillError):
    """Error for unknown slide layout names."""


class InvalidShapeError(ImpressSkillError):
    """Error for unknown shape types."""


class MediaNotFoundError(ImpressSkillError):
    """Error when media file is not found."""


class MasterNotFoundError(ImpressSkillError):
    """Error when master page name is not found."""


__all__ = [
    "ImpressSkillError",
    "DocumentNotFoundError",
    "InvalidSlideIndexError",
    "InvalidLayoutError",
    "InvalidShapeError",
    "MediaNotFoundError",
    "MasterNotFoundError",
]
