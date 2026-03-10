"""Speaker notes operations for Impress."""

from pathlib import Path

from impress.exceptions import DocumentNotFoundError, InvalidSlideIndexError
from uno_bridge import uno_context


def set_notes(path: str, slide_index: int, text: str) -> None:
    """Set speaker notes text on a slide.

    Args:
        path: Path to the presentation file.
        slide_index: Zero-based slide index.
        text: Notes text to set.

    Raises:
        InvalidSlideIndexError: If slide index is out of range.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            pages = doc.DrawPages
            if slide_index < 0 or slide_index >= pages.Count:
                raise InvalidSlideIndexError(
                    f"Slide index {slide_index} out of range "
                    f"(presentation has {pages.Count} slides)"
                )

            slide = pages.getByIndex(slide_index)
            notes_page = slide.getNotesPage()
            notes_shape = _find_notes_text_shape(notes_page)
            if notes_shape is None:
                raise ValueError("Notes text shape not found")
            notes_shape.setString(text)  # type: ignore[attr-defined]

            doc.store()
        finally:
            doc.close(True)


def get_notes(path: str, slide_index: int) -> str:
    """Get speaker notes text from a slide.

    Args:
        path: Path to the presentation file.
        slide_index: Zero-based slide index.

    Returns:
        Notes text, or empty string if none set.

    Raises:
        InvalidSlideIndexError: If slide index is out of range.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            pages = doc.DrawPages
            if slide_index < 0 or slide_index >= pages.Count:
                raise InvalidSlideIndexError(
                    f"Slide index {slide_index} out of range "
                    f"(presentation has {pages.Count} slides)"
                )

            slide = pages.getByIndex(slide_index)
            notes_page = slide.getNotesPage()
            notes_shape = _find_notes_text_shape(notes_page)
            if notes_shape is None:
                return ""
            return notes_shape.getString()  # type: ignore[attr-defined]
        finally:
            doc.close(True)


def _find_notes_text_shape(notes_page: object) -> object | None:
    """Find the first text shape on a notes page."""
    for i in range(notes_page.Count):  # type: ignore[attr-defined]
        shape = notes_page.getByIndex(i)  # type: ignore[attr-defined]
        try:
            if shape.supportsService("com.sun.star.drawing.Text"):
                return shape
        except Exception:
            continue
    return None
