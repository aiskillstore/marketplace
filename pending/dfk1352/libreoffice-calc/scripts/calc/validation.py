"""Data validation helpers for Calc."""

from pathlib import Path
from typing import Mapping


from uno_bridge import uno_context


VALIDATION_TYPES: dict[str, str] = {
    "any": "ANY",
    "whole": "WHOLE",
    "decimal": "DECIMAL",
    "date": "DATE",
    "time": "TIME",
    "text_length": "TEXT_LEN",
    "list": "LIST",
}

CONDITION_OPERATORS: dict[str, str] = {
    "between": "BETWEEN",
    "not_between": "NOT_BETWEEN",
    "equal": "EQUAL",
    "not_equal": "NOT_EQUAL",
    "greater_than": "GREATER",
    "less_than": "LESS",
    "greater_or_equal": "GREATER_EQUAL",
    "less_or_equal": "LESS_EQUAL",
}


def _normalize_validation_type(value: object, uno_module) -> object:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        key = value.strip().lower()
        if key in VALIDATION_TYPES:
            return uno_module.Enum(
                "com.sun.star.sheet.ValidationType",
                VALIDATION_TYPES[key],
            )
    raise ValueError(f"Unsupported validation type: {value}")


def _normalize_condition(value: object, uno_module) -> object:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        key = value.strip().lower()
        if key in CONDITION_OPERATORS:
            return uno_module.Enum(
                "com.sun.star.sheet.ConditionOperator",
                CONDITION_OPERATORS[key],
            )
    raise ValueError(f"Unsupported validation condition: {value}")


def _format_formula(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    return str(value)


def _to_cell_address(doc, sheet: str | int, row: int, col: int):
    if isinstance(sheet, int):
        sheet_index = sheet
    else:
        sheet_index = doc.Sheets.getByName(sheet).getRangeAddress().Sheet
    return (
        doc.Sheets.getByIndex(sheet_index)
        .getCellByPosition(
            col,
            row,
        )
        .getCellAddress()
    )


def add_validation(
    path: str,
    sheet: str | int,
    start_row: int,
    start_col: int,
    end_row: int,
    end_col: int,
    rule: Mapping[str, object],
) -> None:
    """Apply a validation rule to a cell range.

    Args:
        path: Path to the spreadsheet file.
        sheet: Sheet name or index.
        start_row: Zero-based start row.
        start_col: Zero-based start column.
        end_row: Zero-based end row.
        end_col: Zero-based end column.
        rule: Validation rule dictionary.
    """
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
            cell_range = target_sheet.getCellRangeByPosition(
                start_col,
                start_row,
                end_col,
                end_row,
            )
            import uno

            validation = cell_range.Validation
            validation.Type = _normalize_validation_type(
                rule.get("type"),
                uno,
            )
            validation.setOperator(
                _normalize_condition(
                    rule.get("condition"),
                    uno,
                )
            )
            validation.setFormula1(_format_formula(rule.get("value1")))
            validation.setFormula2(_format_formula(rule.get("value2")))
            validation.ShowErrorMessage = bool(rule.get("show_error", False))
            validation.ErrorMessage = str(rule.get("error_message", ""))
            validation.ShowInputMessage = bool(rule.get("show_input", False))
            validation.InputTitle = str(rule.get("input_title", ""))
            validation.InputMessage = str(rule.get("input_message", ""))
            validation.IgnoreBlankCells = bool(rule.get("ignore_blank", True))
            error_style = rule.get("error_style", 0)
            validation.ErrorAlertStyle = (
                int(error_style) if isinstance(error_style, int) else 0
            )
            validation.setSourcePosition(
                _to_cell_address(
                    doc,
                    sheet,
                    start_row,
                    start_col,
                )
            )
            cell_range.Validation = validation
            doc.store()
        finally:
            doc.close(True)
