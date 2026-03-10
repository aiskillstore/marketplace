"""Image operations for Writer documents."""

from pathlib import Path
from typing import Optional

from uno_bridge import uno_context
from writer.exceptions import (
    DocumentNotFoundError,
    ImageNotFoundError,
)


def insert_image(
    path: str,
    image_path: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    position: int | None = None,
) -> None:
    """Insert an image into a Writer document.

    Args:
        path: Path to the document file.
        image_path: Path to the image file to insert.
        width: Optional width in 1/100mm units. If None, uses original size.
        height: Optional height in 1/100mm units. If None, uses original size.
        position: Character index where insertion starts. If None, inserts at
            the end of the document.

    Raises:
        DocumentNotFoundError: If the document does not exist.
        ImageNotFoundError: If the image file does not exist.
    """
    doc_file = Path(path)
    img_file = Path(image_path)

    if not doc_file.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    if not img_file.exists():
        raise ImageNotFoundError(f"Image not found: {image_path}")

    with uno_context() as desktop:
        file_url = doc_file.resolve().as_uri()
        doc = desktop.loadComponentFromURL(file_url, "_blank", 0, ())

        try:
            graphic = doc.createInstance("com.sun.star.text.GraphicObject")

            img_url = img_file.resolve().as_uri()
            graphic.GraphicURL = img_url

            if width is not None and height is not None:
                import uno  # type: ignore[import-not-found]

                size = uno.createUnoStruct("com.sun.star.awt.Size")
                size.Width = width
                size.Height = height
                graphic.setSize(size)

            text_obj = doc.Text
            cursor = text_obj.createTextCursor()

            if position is None:
                cursor.gotoEnd(False)
            else:
                cursor.gotoStart(False)
                if position > 0:
                    cursor.goRight(int(position), False)

            text_obj.insertTextContent(cursor, graphic, False)

            doc.store()
        finally:
            doc.close(True)
