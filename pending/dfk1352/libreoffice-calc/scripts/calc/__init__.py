"""Calc skill package."""

from calc.core import create_spreadsheet, export_spreadsheet
from calc.patch import PatchApplyResult, PatchOperationResult, patch
from calc.session import CalcSession, open_calc_session
from calc.snapshot import snapshot_area
from calc.targets import CalcTarget, CellFormatting, ChartSpec, ValidationRule

__all__ = [
    "create_spreadsheet",
    "export_spreadsheet",
    "snapshot_area",
    "open_calc_session",
    "CalcSession",
    "CalcTarget",
    "CellFormatting",
    "ValidationRule",
    "ChartSpec",
    "patch",
    "PatchApplyResult",
    "PatchOperationResult",
]
