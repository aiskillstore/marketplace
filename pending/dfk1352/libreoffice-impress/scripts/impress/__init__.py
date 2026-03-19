"""Impress skill package."""

from impress.core import create_presentation, export_presentation, get_slide_count
from impress.patch import (
    PatchApplyMode,
    PatchApplyResult,
    PatchOperationResult,
    patch,
)
from impress.session import ImpressSession, open_impress_session
from impress.snapshot import snapshot_slide
from impress.targets import (
    ImpressTarget,
    ListItem,
    ShapePlacement,
    TextFormatting,
)

__all__ = [
    "ImpressSession",
    "ImpressTarget",
    "ListItem",
    "PatchApplyMode",
    "PatchApplyResult",
    "PatchOperationResult",
    "ShapePlacement",
    "TextFormatting",
    "create_presentation",
    "export_presentation",
    "get_slide_count",
    "open_impress_session",
    "patch",
    "snapshot_slide",
]
