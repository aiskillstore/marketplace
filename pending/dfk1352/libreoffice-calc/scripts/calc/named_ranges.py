"""Named range helpers for Calc."""

from pathlib import Path

from uno_bridge import uno_context


def define_named_range(
    path: str,
    name: str,
    sheet: str | int,
    start_row: int,
    start_col: int,
    end_row: int | None = None,
    end_col: int | None = None,
) -> None:
    """Define a named range.

    Args:
        path: Path to the spreadsheet file.
        name: Named range name.
        sheet: Sheet name or index.
        start_row: Zero-based start row.
        start_col: Zero-based start column.
        end_row: Zero-based end row (optional).
        end_col: Zero-based end column (optional).
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
            if end_row is None:
                end_row = start_row
            if end_col is None:
                end_col = start_col
            cell_range = target_sheet.getCellRangeByPosition(
                start_col,
                start_row,
                end_col,
                end_row,
            )
            base_address = target_sheet.getCellByPosition(
                start_col,
                start_row,
            ).getCellAddress()
            doc.NamedRanges.addNewByName(
                name,
                cell_range.AbsoluteName,
                base_address,
                0,
            )
            doc.store()
        finally:
            doc.close(True)


def get_named_range(path: str, name: str) -> dict[str, object]:
    """Get a named range definition.

    Args:
        path: Path to the spreadsheet file.
        name: Named range name.

    Returns:
        Named range metadata.
    """
    file_path = Path(path)
    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            named = doc.NamedRanges.getByName(name)
            return {"name": name, "formula": named.Content}
        finally:
            doc.close(True)
