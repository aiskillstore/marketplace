"""Range operations for Calc."""

from pathlib import Path

from calc.cells import _cell_result
from uno_bridge import uno_context


def set_range(
    path: str,
    sheet: str | int,
    start_row: int,
    start_col: int,
    data: list[list[object]],
) -> None:
    """Set a rectangular range of values.

    Args:
        path: Path to the spreadsheet file.
        sheet: Sheet name or index.
        start_row: Zero-based start row.
        start_col: Zero-based start column.
        data: 2D array of values.
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
            for row_offset, row_values in enumerate(data):
                for col_offset, value in enumerate(row_values):
                    cell = target_sheet.getCellByPosition(
                        start_col + col_offset,
                        start_row + row_offset,
                    )
                    if isinstance(value, (int, float)):
                        cell.Value = float(value)
                    else:
                        cell.String = str(value)
            doc.store()
        finally:
            doc.close(True)


def get_range(
    path: str,
    sheet: str | int,
    start_row: int,
    start_col: int,
    end_row: int,
    end_col: int,
) -> list[list[dict[str, object]]]:
    """Get a rectangular range of cell results.

    Args:
        path: Path to the spreadsheet file.
        sheet: Sheet name or index.
        start_row: Zero-based start row.
        start_col: Zero-based start column.
        end_row: Zero-based end row.
        end_col: Zero-based end column.

    Returns:
        2D array of cell result dictionaries.
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
            results = []
            for row in range(start_row, end_row + 1):
                row_results = []
                for col in range(start_col, end_col + 1):
                    cell = target_sheet.getCellByPosition(col, row)
                    row_results.append(_cell_result(cell))
                results.append(row_results)
            return results
        finally:
            doc.close(True)
