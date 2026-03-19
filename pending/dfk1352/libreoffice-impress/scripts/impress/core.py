"""Core document lifecycle operations for Impress."""

from pathlib import Path

from impress.exceptions import DocumentNotFoundError, ImpressSkillError
from uno_bridge import uno_context


EXPORT_FILTERS = {
    "pdf": "impress_pdf_Export",
    "pptx": "Impress MS PowerPoint 2007 XML",
}


def create_presentation(path: str) -> None:
    """Create a new Impress presentation at the specified path.

    Args:
        path: Output path for the new presentation.
    """
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL("private:factory/simpress", "_blank", 0, ())
        try:
            file_url = output.resolve().as_uri()
            doc.storeAsURL(file_url, ())
        finally:
            doc.close(True)


def get_slide_count(path: str) -> int:
    """Return number of slides in a presentation.

    Args:
        path: Path to the presentation file.

    Returns:
        Number of slides.

    Raises:
        DocumentNotFoundError: If file does not exist.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            return doc.DrawPages.Count
        finally:
            doc.close(True)


def export_presentation(path: str, output_path: str, format: str) -> None:
    """Export a presentation to another format.

    Args:
        path: Path to the presentation file.
        output_path: Destination file path.
        format: Export format key ("pdf" or "pptx").

    Raises:
        ImpressSkillError: If the export format is unsupported.
    """
    if format not in EXPORT_FILTERS:
        raise ImpressSkillError(f"Unsupported export format: {format}")

    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            import uno  # type: ignore[import-not-found]

            filter_prop = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
            filter_prop.Name = "FilterName"
            filter_prop.Value = EXPORT_FILTERS[format]
            doc.storeToURL(output.resolve().as_uri(), (filter_prop,))
        finally:
            doc.close(True)
