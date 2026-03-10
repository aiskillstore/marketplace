"""Table operations for Writer documents."""

from pathlib import Path
from typing import Any, Optional

from uno_bridge import uno_context
from writer.exceptions import (
    DocumentNotFoundError,
    InvalidTableError,
)


def add_table(
    path: str,
    rows: int,
    cols: int,
    data: Optional[list[list[Any]]] = None,
    position: int | None = None,
) -> None:
    """Add a table to a Writer document.

    Args:
        path: Path to the document file.
        rows: Number of table rows.
        cols: Number of table columns.
        data: Optional 2D list of cell values. Should be rows x cols.
        position: Character index where insertion starts. If None, inserts at
            the end of the document.

    Raises:
        DocumentNotFoundError: If the document does not exist.
        InvalidTableError: If rows or cols are less than 1, or data
            dimensions don't match.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    if rows < 1 or cols < 1:
        raise InvalidTableError("Rows and cols must be >= 1")

    if data is not None:
        if len(data) != rows:
            raise InvalidTableError(f"Data has {len(data)} rows but table needs {rows}")
        for i, row in enumerate(data):
            if len(row) != cols:
                raise InvalidTableError(
                    f"Data row {i} has {len(row)} cols but table needs {cols}"
                )

    with uno_context() as desktop:
        file_url = file_path.resolve().as_uri()
        doc = desktop.loadComponentFromURL(file_url, "_blank", 0, ())

        try:
            table = doc.createInstance("com.sun.star.text.TextTable")
            table.initialize(rows, cols)

            text_obj = doc.Text
            cursor = text_obj.createTextCursor()

            if position is None:
                cursor.gotoEnd(False)
            else:
                cursor.gotoStart(False)
                if position > 0:
                    cursor.goRight(int(position), False)

            text_obj.insertTextContent(cursor, table, False)

            if data is not None:
                for row_idx, row_data in enumerate(data):
                    for col_idx, cell_value in enumerate(row_data):
                        cell_name = get_cell_name(row_idx, col_idx)
                        cell = table.getCellByName(cell_name)
                        cell.setString(str(cell_value))

            doc.store()
        finally:
            doc.close(True)


def get_cell_name(row: int, col: int) -> str:
    """Convert row/col indices to cell name (e.g., 0, 0 -> 'A1').

    Args:
        row: Zero-based row index.
        col: Zero-based column index.

    Returns:
        Cell name like 'A1', 'B2', etc.
    """
    col_name = ""
    col_num = col + 1
    while col_num > 0:
        col_num -= 1
        col_name = chr(65 + (col_num % 26)) + col_name
        col_num //= 26

    return f"{col_name}{row + 1}"
