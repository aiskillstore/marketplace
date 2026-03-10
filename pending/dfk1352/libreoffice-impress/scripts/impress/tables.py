"""Table operations for Impress."""

from pathlib import Path

from colors import resolve_color
from impress._util import _cm_to_hmm
from impress.exceptions import DocumentNotFoundError
from uno_bridge import uno_context


def add_table(
    path: str,
    slide_index: int,
    rows: int,
    cols: int,
    x_cm: float,
    y_cm: float,
    width_cm: float,
    height_cm: float,
    data: list[list[str]] | None = None,
) -> int:
    """Add a table shape to a slide.

    Args:
        path: Path to the presentation file.
        slide_index: Zero-based slide index.
        rows: Number of rows.
        cols: Number of columns.
        x_cm: X position in centimetres.
        y_cm: Y position in centimetres.
        width_cm: Width in centimetres.
        height_cm: Height in centimetres.
        data: Optional 2D list of cell values.

    Returns:
        Shape index of the new table.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    with uno_context() as desktop:
        import uno  # type: ignore[import-not-found]

        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            slide = doc.DrawPages.getByIndex(slide_index)

            table_shape = doc.createInstance("com.sun.star.drawing.TableShape")

            size = uno.createUnoStruct("com.sun.star.awt.Size")
            size.Width = _cm_to_hmm(width_cm)
            size.Height = _cm_to_hmm(height_cm)
            table_shape.Size = size

            slide.add(table_shape)

            pos = uno.createUnoStruct("com.sun.star.awt.Point")
            pos.X = _cm_to_hmm(x_cm)
            pos.Y = _cm_to_hmm(y_cm)
            table_shape.Position = pos

            # Expand the default 1x1 table to the requested dimensions
            model = table_shape.Model
            if rows > 1:
                model.Rows.insertByIndex(1, rows - 1)
            if cols > 1:
                model.Columns.insertByIndex(1, cols - 1)

            if data is not None:
                for r_idx, row_data in enumerate(data):
                    for c_idx, cell_value in enumerate(row_data):
                        if r_idx < rows and c_idx < cols:
                            cell = model.getCellByPosition(c_idx, r_idx)
                            cell.setString(str(cell_value))

            shape_index = slide.Count - 1
            doc.store()
            return shape_index
        finally:
            doc.close(True)


def set_table_cell(
    path: str,
    slide_index: int,
    shape_index: int,
    row: int,
    col: int,
    text: str,
) -> None:
    """Set text in a specific table cell.

    Args:
        path: Path to the presentation file.
        slide_index: Zero-based slide index.
        shape_index: Shape index of the table.
        row: Zero-based row index.
        col: Zero-based column index.
        text: Text to set.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            slide = doc.DrawPages.getByIndex(slide_index)
            table_shape = slide.getByIndex(shape_index)
            model = table_shape.Model
            cell = model.getCellByPosition(col, row)
            cell.setString(text)
            doc.store()
        finally:
            doc.close(True)


def format_table_cell(
    path: str,
    slide_index: int,
    shape_index: int,
    row: int,
    col: int,
    bold: bool = False,
    font_size: int | None = None,
    fill_color: int | str | None = None,
) -> None:
    """Format a table cell.

    Args:
        path: Path to the presentation file.
        slide_index: Zero-based slide index.
        shape_index: Shape index of the table.
        row: Zero-based row index.
        col: Zero-based column index.
        bold: Whether to make text bold.
        font_size: Font size in points.
        fill_color: Background colour as 0xRRGGBB integer or name.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            slide = doc.DrawPages.getByIndex(slide_index)
            table_shape = slide.getByIndex(shape_index)
            model = table_shape.Model
            cell = model.getCellByPosition(col, row)

            cursor = cell.getText().createTextCursor()
            cursor.gotoStart(False)
            cursor.gotoEnd(True)

            if bold:
                cursor.CharWeight = 150  # BOLD
            if font_size is not None:
                cursor.CharHeight = font_size
            if fill_color is not None:
                cell.FillStyle = 1  # SOLID
                cell.FillColor = resolve_color(fill_color)

            doc.store()
        finally:
            doc.close(True)
