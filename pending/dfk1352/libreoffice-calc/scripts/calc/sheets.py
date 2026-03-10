"""Sheet management helpers for Calc."""

from pathlib import Path

from uno_bridge import uno_context


def _get_sheet(doc, sheet: str | int):
    if isinstance(sheet, int):
        return doc.Sheets.getByIndex(sheet)
    return doc.Sheets.getByName(sheet)


def add_sheet(path: str, name: str, index: int | None = None) -> None:
    """Add a sheet to a spreadsheet.

    Args:
        path: Path to the spreadsheet file.
        name: Name for the new sheet.
        index: Optional index to insert the sheet at.
    """
    file_path = Path(path)
    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            if index is None:
                index = doc.Sheets.getCount()
            doc.Sheets.insertNewByName(name, index)
            doc.store()
        finally:
            doc.close(True)


def list_sheets(path: str) -> list[dict[str, object]]:
    """List sheets and metadata for a spreadsheet.

    Args:
        path: Path to the spreadsheet file.

    Returns:
        List of dictionaries with sheet metadata.
    """
    file_path = Path(path)
    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            sheets = []
            for idx in range(doc.Sheets.getCount()):
                sheet = doc.Sheets.getByIndex(idx)
                sheets.append(
                    {
                        "name": sheet.Name,
                        "index": idx,
                        "visible": sheet.IsVisible,
                    }
                )
            return sheets
        finally:
            doc.close(True)


def rename_sheet(path: str, old_name: str, new_name: str) -> None:
    """Rename an existing sheet.

    Args:
        path: Path to the spreadsheet file.
        old_name: Current sheet name.
        new_name: New sheet name.
    """
    file_path = Path(path)
    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            sheet = doc.Sheets.getByName(old_name)
            sheet.Name = new_name
            doc.store()
        finally:
            doc.close(True)


def remove_sheet(path: str, name: str) -> None:
    """Remove a sheet by name.

    Args:
        path: Path to the spreadsheet file.
        name: Sheet name to remove.
    """
    file_path = Path(path)
    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            doc.Sheets.removeByName(name)
            doc.store()
        finally:
            doc.close(True)
