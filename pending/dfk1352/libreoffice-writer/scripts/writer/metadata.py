"""Metadata operations for Writer documents."""

from pathlib import Path

from uno_bridge import uno_context
from writer.exceptions import (
    DocumentNotFoundError,
    InvalidMetadataError,
)


def set_metadata(path: str, values: dict[str, str]) -> None:
    """Set metadata properties in a Writer document.

    Args:
        path: Path to the document file.
        values: Dictionary of metadata key-value pairs.
            Common keys: title, author, subject, keywords, description

    Raises:
        DocumentNotFoundError: If the document does not exist.
        InvalidMetadataError: If metadata keys are invalid.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    if any(not key for key in values.keys()):
        raise InvalidMetadataError("Metadata keys must be non-empty")

    with uno_context() as desktop:
        file_url = file_path.resolve().as_uri()
        doc = desktop.loadComponentFromURL(file_url, "_blank", 0, ())

        try:
            doc_info = doc.getDocumentProperties()

            if "title" in values:
                doc_info.Title = values["title"]

            if "author" in values:
                doc_info.Author = values["author"]

            if "subject" in values:
                doc_info.Subject = values["subject"]

            if "keywords" in values:
                keywords = values["keywords"]
                if isinstance(keywords, str):
                    keyword_list = [k.strip() for k in keywords.split(",")]
                    doc_info.Keywords = tuple(keyword_list)
                else:
                    doc_info.Keywords = tuple(keywords)

            if "description" in values:
                doc_info.Description = values["description"]

            doc.store()
        finally:
            doc.close(True)


def get_metadata(path: str) -> dict[str, str]:
    """Get metadata properties from a Writer document.

    Args:
        path: Path to the document file.

    Returns:
        Dictionary of metadata key-value pairs.

    Raises:
        DocumentNotFoundError: If the document does not exist.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    with uno_context() as desktop:
        file_url = file_path.resolve().as_uri()
        doc = desktop.loadComponentFromURL(file_url, "_blank", 0, ())

        try:
            doc_info = doc.getDocumentProperties()

            metadata = {
                "title": doc_info.Title or "",
                "author": doc_info.Author or "",
                "subject": doc_info.Subject or "",
                "keywords": ", ".join(doc_info.Keywords) or "",
                "description": doc_info.Description or "",
            }

            return metadata
        finally:
            doc.close(True)
