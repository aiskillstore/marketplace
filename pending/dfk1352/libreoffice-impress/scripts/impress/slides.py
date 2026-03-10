"""Slide management operations for Impress."""

from pathlib import Path

from impress.exceptions import (
    DocumentNotFoundError,
    InvalidLayoutError,
    InvalidSlideIndexError,
)
from uno_bridge import uno_context


LAYOUT_MAP = {
    "BLANK": 0,
    "TITLE_SLIDE": 19,
    "TITLE_AND_CONTENT": 1,
    "TITLE_ONLY": 20,
    "TWO_CONTENT": 3,
    "CENTERED_TEXT": 2,
}


def add_slide(
    path: str,
    index: int | None = None,
    layout: str = "BLANK",
) -> None:
    """Add a slide to the presentation.

    Args:
        path: Path to the presentation file.
        index: Position to insert at. None appends at end.
        layout: Layout name. One of BLANK, TITLE_SLIDE,
            TITLE_AND_CONTENT, TITLE_ONLY, TWO_CONTENT, CENTERED_TEXT.

    Raises:
        InvalidLayoutError: If layout name is unknown.
    """
    if layout not in LAYOUT_MAP:
        raise InvalidLayoutError(
            f"Unknown layout: {layout}. Valid layouts: {list(LAYOUT_MAP.keys())}"
        )

    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            pages = doc.DrawPages
            insert_idx = pages.Count if index is None else index
            pages.insertNewByIndex(insert_idx)
            slide = pages.getByIndex(insert_idx)
            slide.Layout = LAYOUT_MAP[layout]
            doc.store()
        finally:
            doc.close(True)


def delete_slide(path: str, index: int) -> None:
    """Remove a slide at the given index.

    Args:
        path: Path to the presentation file.
        index: Zero-based slide index.

    Raises:
        InvalidSlideIndexError: If index is out of range.
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
            if index < 0 or index >= pages.Count:
                raise InvalidSlideIndexError(
                    f"Slide index {index} out of range "
                    f"(presentation has {pages.Count} slides)"
                )
            slide = pages.getByIndex(index)
            pages.remove(slide)
            doc.store()
        finally:
            doc.close(True)


def move_slide(path: str, from_index: int, to_index: int) -> None:
    """Move a slide from one position to another.

    Inserts a new blank slide at the target, copies layout, master page,
    and non-placeholder shapes from the source, then removes the source.

    Args:
        path: Path to the presentation file.
        from_index: Current zero-based slide index.
        to_index: Target zero-based slide index.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    if from_index == to_index:
        return

    with uno_context() as desktop:
        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            pages = doc.DrawPages
            count = pages.Count

            if from_index < 0 or from_index >= count:
                raise InvalidSlideIndexError(f"from_index {from_index} out of range")
            if to_index < 0 or to_index >= count:
                raise InvalidSlideIndexError(f"to_index {to_index} out of range")

            _copy_slide_to_position(doc, pages, from_index, to_index)

            doc.store()
        finally:
            doc.close(True)


def _copy_slide_to_position(
    doc: object, pages: object, src_idx: int, dst_idx: int
) -> None:
    """Copy slide content to a new slide at dst_idx, then remove the source.

    Creates a new slide at dst_idx, copies layout, master page, and
    all non-placeholder shapes from the source. The source slide is
    then removed.

    For leftward moves (dst_idx < src_idx): inserting a blank at
    dst_idx shifts the source to src_idx + 1.

    For rightward moves (dst_idx > src_idx): insert at dst_idx + 1
    so the target ends up at dst_idx after the source is removed.

    Args:
        doc: UNO document object (for createInstance).
        pages: UNO DrawPages object.
        src_idx: Source slide index.
        dst_idx: Destination slide index.
    """
    source = pages.getByIndex(src_idx)  # type: ignore[attr-defined]
    layout = source.Layout
    master = source.MasterPage

    if dst_idx < src_idx:
        # Leftward: insert at dst_idx, source shifts to src_idx + 1
        insert_at = dst_idx
        actual_src = src_idx + 1
    else:
        # Rightward: insert at dst_idx + 1, source stays at src_idx
        insert_at = dst_idx + 1
        actual_src = src_idx

    pages.insertNewByIndex(insert_at)  # type: ignore[attr-defined]
    target = pages.getByIndex(insert_at)  # type: ignore[attr-defined]
    target.Layout = layout
    target.MasterPage = master

    source = pages.getByIndex(actual_src)  # type: ignore[attr-defined]

    for i in range(source.Count):
        src_shape = source.getByIndex(i)

        # Skip auto-created presentation placeholders
        if src_shape.IsPresentationObject:
            continue

        shape_type = src_shape.ShapeType
        new_shape = doc.createInstance(shape_type)  # type: ignore[attr-defined]
        new_shape.Position = src_shape.Position
        new_shape.Size = src_shape.Size
        target.add(new_shape)

        if src_shape.supportsService("com.sun.star.drawing.Text"):
            new_shape.setString(src_shape.getString())

    pages.remove(source)  # type: ignore[attr-defined]


def duplicate_slide(path: str, index: int) -> None:
    """Duplicate the slide at the given index.

    Args:
        path: Path to the presentation file.
        index: Zero-based slide index to duplicate.
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
            slide = pages.getByIndex(index)
            doc.duplicate(slide)
            doc.store()
        finally:
            doc.close(True)


def get_slide_inventory(path: str, index: int) -> dict:
    """Get an inventory of all shapes on a slide.

    Args:
        path: Path to the presentation file.
        index: Zero-based slide index.

    Returns:
        Dict with slide_index, layout, shape_count, and shapes list.
        Each shape has index, type, text, x_cm, y_cm, width_cm, height_cm.
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
            if index < 0 or index >= pages.Count:
                raise InvalidSlideIndexError(
                    f"Slide index {index} out of range "
                    f"(presentation has {pages.Count} slides)"
                )
            slide = pages.getByIndex(index)

            shapes = []
            for i in range(slide.Count):
                shape = slide.getByIndex(i)
                pos = shape.Position
                size = shape.Size
                text = ""
                if shape.supportsService("com.sun.star.drawing.Text"):
                    text = shape.getString()
                else:
                    try:
                        text = shape.getString()
                    except Exception:
                        text = ""

                shapes.append(
                    {
                        "index": i,
                        "type": shape.ShapeType,
                        "text": text,
                        "x_cm": pos.X / 1000.0,
                        "y_cm": pos.Y / 1000.0,
                        "width_cm": size.Width / 1000.0,
                        "height_cm": size.Height / 1000.0,
                    }
                )

            return {
                "slide_index": index,
                "layout": slide.Layout,
                "shape_count": slide.Count,
                "shapes": shapes,
            }
        finally:
            doc.close(True)
