"""Formatting operations for Impress."""

from pathlib import Path

from colors import resolve_color
from impress.exceptions import DocumentNotFoundError
from uno_bridge import uno_context


ALIGNMENT_MAP = {
    "left": 0,
    "right": 1,
    "center": 3,
    "justify": 2,
}


def format_shape_text(
    path: str,
    slide_index: int,
    shape_index: int,
    bold: bool = False,
    italic: bool = False,
    underline: bool = False,
    font_size: int | None = None,
    font_name: str | None = None,
    color: int | str | None = None,
    alignment: str | None = None,
) -> None:
    """Format all text in a shape.

    Args:
        path: Path to the presentation file.
        slide_index: Zero-based slide index.
        shape_index: Shape index.
        bold: Whether to make text bold.
        italic: Whether to make text italic.
        underline: Whether to underline text.
        font_size: Font size in points.
        font_name: Font family name.
        color: Text colour as 0xRRGGBB integer or name.
        alignment: Paragraph alignment: left, center, right, justify.
            Case-insensitive; unknown values raise ValueError.
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
            shape = slide.getByIndex(shape_index)

            cursor = shape.getText().createTextCursor()
            cursor.gotoStart(False)
            cursor.gotoEnd(True)

            if bold:
                cursor.CharWeight = 150  # BOLD
            if italic:
                cursor.CharPosture = 2  # ITALIC
            if underline:
                cursor.CharUnderline = 1  # SINGLE
            if font_size is not None:
                cursor.CharHeight = font_size
            if font_name is not None:
                cursor.CharFontName = font_name
            if color is not None:
                cursor.CharColor = resolve_color(color)
            if alignment is not None:
                align_key = alignment.strip().lower()
                if align_key in ALIGNMENT_MAP:
                    cursor.ParaAdjust = ALIGNMENT_MAP[align_key]
                else:
                    raise ValueError(f"Unknown alignment: {alignment}")

            doc.store()
        finally:
            doc.close(True)


def set_slide_background(
    path: str,
    slide_index: int,
    color: int | str,
) -> None:
    """Set a solid background colour on a slide.

    Args:
        path: Path to the presentation file.
        slide_index: Zero-based slide index.
        color: Background colour as 0xRRGGBB integer or name.
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

            bg = doc.createInstance("com.sun.star.drawing.Background")
            bg.FillStyle = 1  # SOLID
            bg.FillColor = resolve_color(color)
            slide.Background = bg

            doc.store()
        finally:
            doc.close(True)
