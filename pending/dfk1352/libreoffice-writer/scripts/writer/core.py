"""Core document lifecycle operations for Writer."""

from pathlib import Path

from uno_bridge import uno_context
from writer.exceptions import WriterSkillError


EXPORT_FILTERS = {
    "pdf": "writer_pdf_Export",
    "docx": "MS Word 2007 XML",
}


def create_document(path: str) -> None:
    """Create a new Writer document at the specified path.

    Args:
        path: Output path for the new document.

    Raises:
        WriterSkillError: If document creation fails.
    """
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())

        try:
            file_url = Path(path).resolve().as_uri()
            doc.storeAsURL(file_url, ())
        finally:
            doc.close(True)


def read_document_text(path: str) -> str:
    """Read all text content from a Writer document.

    Args:
        path: Path to the document file.

    Returns:
        Text content of the document.

    Raises:
        WriterSkillError: If document cannot be read.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise WriterSkillError(f"Document not found: {path}")

    with uno_context() as desktop:
        file_url = file_path.resolve().as_uri()

        doc = desktop.loadComponentFromURL(file_url, "_blank", 0, ())

        try:
            text = doc.Text.getString()
            return text
        finally:
            doc.close(True)


def export_document(path: str, output_path: str, format: str) -> None:
    """Export a Writer document to another format.

    Args:
        path: Path to the document file.
        output_path: Destination file path.
        format: Export format key.

    Raises:
        WriterSkillError: If the export format is unsupported.
    """
    if format not in EXPORT_FILTERS:
        raise WriterSkillError(f"Unsupported export format: {format}")
    file_path = Path(path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(),
            "_blank",
            0,
            (),
        )
        try:
            import uno  # type: ignore[import-not-found]

            filter_name = EXPORT_FILTERS[format]
            filter_prop = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
            filter_prop.Name = "FilterName"
            filter_prop.Value = filter_name
            doc.storeToURL(output.resolve().as_uri(), (filter_prop,))
        finally:
            doc.close(True)
