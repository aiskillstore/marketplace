"""Text operations for Writer documents."""

from pathlib import Path

from uno_bridge import uno_context
from writer.exceptions import DocumentNotFoundError


def insert_text(path: str, text: str, position: int | None = None) -> None:
    """Insert text into a Writer document at a character index.

    Args:
        path: Path to the document file.
        text: Text content to insert.
        position: Character index where insertion starts. If None, inserts at
            the end of the document.

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
            text_obj = doc.Text
            cursor = text_obj.createTextCursor()

            if position is None:
                cursor.gotoEnd(False)
            else:
                cursor.gotoStart(False)
                if position > 0:
                    cursor.goRight(int(position), False)

            if "\n" in text:
                for idx, part in enumerate(text.split("\n")):
                    if idx > 0:
                        text_obj.insertControlCharacter(cursor, 0, False)
                    if part:
                        text_obj.insertString(cursor, part, False)
            else:
                text_obj.insertString(cursor, text, False)

            doc.store()
        finally:
            doc.close(True)


def replace_text(path: str, old: str, new: str) -> None:
    """Replace all occurrences of text in a Writer document.

    Args:
        path: Path to the document file.
        old: Text to find and replace.
        new: Replacement text.

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
            search = doc.createSearchDescriptor()
            search.SearchString = old

            found = doc.findFirst(search)
            while found:
                found.setString(new)
                found = doc.findNext(found.End, search)

            doc.store()
        finally:
            doc.close(True)
