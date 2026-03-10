"""Cell operations for Calc."""

from pathlib import Path
from typing import Any

from calc.exceptions import InvalidCellReferenceError
from uno_bridge import uno_context


FORMULA_ERRORS = {"#DIV/0!", "#REF!", "#VALUE!", "#NAME?", "#N/A"}


def _cell_result(cell) -> dict[str, object]:
    formula = cell.Formula
    if formula and formula.startswith("="):
        value = cell.Value
        raw = cell.String if cell.String in FORMULA_ERRORS else value
        error = cell.String if cell.String in FORMULA_ERRORS else None
        return {
            "value": None if error else value,
            "formula": formula,
            "error": error,
            "type": "formula",
            "raw": raw,
        }
    if cell.Type.value == "TEXT" or cell.Type.value == 2:
        return {
            "value": cell.String,
            "formula": None,
            "error": None,
            "type": "text",
            "raw": cell.String,
        }
    return {
        "value": cell.Value,
        "formula": None,
        "error": None,
        "type": "number",
        "raw": cell.Value,
    }


def set_cell(
    path: str,
    sheet: str | int,
    row: int,
    col: int,
    value: Any,
    type: str = "auto",
) -> None:
    """Set a cell value in a spreadsheet.

    Args:
        path: Path to the spreadsheet file.
        sheet: Sheet name or index.
        row: Zero-based row index.
        col: Zero-based column index.
        value: Value to set.
        type: Value type: auto, number, text, date, formula.
    """
    if row < 0 or col < 0:
        raise InvalidCellReferenceError("Row and column must be non-negative")
    file_path = Path(path)
    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            if isinstance(sheet, int):
                target_sheet = doc.Sheets.getByIndex(sheet)
            else:
                target_sheet = doc.Sheets.getByName(sheet)
            cell = target_sheet.getCellByPosition(col, row)
            if type == "formula":
                cell.Formula = str(value)
            elif type == "text":
                cell.String = str(value)
            elif type == "date":
                cell.Value = float(value) if value is not None else 0.0
            elif type == "number":
                cell.Value = float(value) if value is not None else 0.0
            else:
                if isinstance(value, (int, float)):
                    cell.Value = float(value)
                else:
                    cell.String = str(value)
            doc.store()
        finally:
            doc.close(True)


def get_cell(
    path: str,
    sheet: str | int,
    row: int,
    col: int,
) -> dict[str, object]:
    """Get a cell value and metadata.

    Args:
        path: Path to the spreadsheet file.
        sheet: Sheet name or index.
        row: Zero-based row index.
        col: Zero-based column index.

    Returns:
        Cell result dictionary.
    """
    if row < 0 or col < 0:
        raise InvalidCellReferenceError("Row and column must be non-negative")
    file_path = Path(path)
    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            if isinstance(sheet, int):
                target_sheet = doc.Sheets.getByIndex(sheet)
            else:
                target_sheet = doc.Sheets.getByName(sheet)
            cell = target_sheet.getCellByPosition(col, row)
            return _cell_result(cell)
        finally:
            doc.close(True)
