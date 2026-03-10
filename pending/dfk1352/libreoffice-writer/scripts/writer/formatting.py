"""Formatting operations for Writer documents."""

from pathlib import Path
from typing import Any

from colors import resolve_color
from uno_bridge import uno_context
from writer.exceptions import (
    DocumentNotFoundError,
    InvalidFormattingError,
)


def apply_formatting(
    path: str, formatting: dict[str, Any], selection: str = "all"
) -> None:
    """Apply formatting to text in a Writer document.

    Args:
        path: Path to the document file.
        formatting: Dictionary of formatting properties.
            Character properties: bold, italic, underline, font_name,
            font_size, color
            Paragraph properties: align, line_spacing, spacing_before,
            spacing_after
        selection: Which text to format. Options: "all", "last_paragraph"
            Default is "all".

    Raises:
        DocumentNotFoundError: If the document does not exist.
        InvalidFormattingError: If unknown formatting keys are provided or
            alignment is invalid.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    allowed = {
        "bold",
        "italic",
        "underline",
        "font_name",
        "font_size",
        "color",
        "align",
        "line_spacing",
        "spacing_before",
        "spacing_after",
    }
    if any(key not in allowed for key in formatting.keys()):
        unknown = [k for k in formatting.keys() if k not in allowed]
        raise InvalidFormattingError(f"Unknown formatting keys: {unknown}")

    with uno_context() as desktop:
        file_url = file_path.resolve().as_uri()
        doc = desktop.loadComponentFromURL(file_url, "_blank", 0, ())

        try:
            text_obj = doc.Text
            cursor = text_obj.createTextCursor()

            if selection == "all":
                cursor.gotoStart(False)
                cursor.gotoEnd(True)
            elif selection == "last_paragraph":
                cursor.gotoEnd(False)
                cursor.gotoStartOfParagraph(True)
            else:
                cursor.gotoStart(False)
                cursor.gotoEnd(True)

            if "bold" in formatting:
                # Use numeric constants instead of enums
                # BOLD = 150, NORMAL = 100
                cursor.CharWeight = 150 if formatting["bold"] else 100

            if "italic" in formatting:
                # Use numeric constants: ITALIC = 2, NONE = 0
                cursor.CharPosture = 2 if formatting["italic"] else 0

            if "underline" in formatting:
                # Use numeric constants: SINGLE = 1, NONE = 0
                cursor.CharUnderline = 1 if formatting["underline"] else 0

            if "font_name" in formatting:
                cursor.CharFontName = formatting["font_name"]

            if "font_size" in formatting:
                cursor.CharHeight = formatting["font_size"]

            if "color" in formatting:
                cursor.CharColor = resolve_color(formatting["color"])

            if "align" in formatting:
                # Use numeric constants for paragraph alignment
                # LEFT = 0, RIGHT = 1, BLOCK = 3, CENTER = 2
                align_map = {
                    "left": 0,
                    "center": 2,
                    "right": 1,
                    "justify": 3,
                }
                align_key = str(formatting["align"]).strip().lower()
                if align_key in align_map:
                    cursor.ParaAdjust = align_map[align_key]
                else:
                    raise InvalidFormattingError(
                        f"Unknown align value: {formatting['align']}"
                    )

            if "line_spacing" in formatting:
                import uno  # type: ignore[import-not-found]

                line_spacing = uno.createUnoStruct("com.sun.star.style.LineSpacing")
                line_spacing.Mode = 0  # PROP mode
                line_spacing.Height = int(formatting["line_spacing"] * 100)
                cursor.ParaLineSpacing = line_spacing

            if "spacing_before" in formatting:
                cursor.ParaTopMargin = formatting["spacing_before"]

            if "spacing_after" in formatting:
                cursor.ParaBottomMargin = formatting["spacing_after"]

            doc.store()
        finally:
            doc.close(True)
