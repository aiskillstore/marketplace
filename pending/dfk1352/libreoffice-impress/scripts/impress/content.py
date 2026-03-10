"""Content placement operations for Impress."""

from pathlib import Path

from colors import resolve_color
from impress._util import _cm_to_hmm
from impress.exceptions import (
    DocumentNotFoundError,
    InvalidShapeError,
    MediaNotFoundError,
)
from uno_bridge import uno_context


SHAPE_TYPE_MAP = {
    "rectangle": "com.sun.star.drawing.RectangleShape",
    "ellipse": "com.sun.star.drawing.EllipseShape",
    "line": "com.sun.star.drawing.LineShape",
    "triangle": "com.sun.star.drawing.CustomShape",
    "arrow": "com.sun.star.drawing.CustomShape",
}


def set_title(path: str, slide_index: int, text: str) -> None:
    """Set the title placeholder text on a slide.

    Args:
        path: Path to the presentation file.
        slide_index: Zero-based slide index.
        text: Title text to set.
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
            for i in range(slide.Count):
                shape = slide.getByIndex(i)
                if shape.supportsService("com.sun.star.presentation.TitleTextShape"):
                    shape.setString(text)
                    break
            doc.store()
        finally:
            doc.close(True)


def set_body(path: str, slide_index: int, text: str) -> None:
    """Set the body/subtitle placeholder text on a slide.

    Args:
        path: Path to the presentation file.
        slide_index: Zero-based slide index.
        text: Body text to set.
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
            for i in range(slide.Count):
                shape = slide.getByIndex(i)
                if shape.supportsService(
                    "com.sun.star.presentation.SubtitleTextShape"
                ) or shape.supportsService(
                    "com.sun.star.drawing.plugin.presentation.PlaceholderText"
                ):
                    shape.setString(text)
                    break
            else:
                # Fallback: find any non-title presentation shape
                for i in range(slide.Count):
                    shape = slide.getByIndex(i)
                    if shape.supportsService(
                        "com.sun.star.presentation.TitleTextShape"
                    ):
                        continue
                    if shape.supportsService("com.sun.star.drawing.Text"):
                        shape.setString(text)
                        break
            doc.store()
        finally:
            doc.close(True)


def add_text_box(
    path: str,
    slide_index: int,
    text: str,
    x_cm: float,
    y_cm: float,
    width_cm: float,
    height_cm: float,
) -> int:
    """Add a text box to a slide.

    Args:
        path: Path to the presentation file.
        slide_index: Zero-based slide index.
        text: Text content for the box.
        x_cm: X position in centimetres.
        y_cm: Y position in centimetres.
        width_cm: Width in centimetres.
        height_cm: Height in centimetres.

    Returns:
        Shape index of the new text box.
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

            shape = doc.createInstance("com.sun.star.drawing.TextShape")
            pos = uno.createUnoStruct("com.sun.star.awt.Point")
            pos.X = _cm_to_hmm(x_cm)
            pos.Y = _cm_to_hmm(y_cm)
            shape.Position = pos

            size = uno.createUnoStruct("com.sun.star.awt.Size")
            size.Width = _cm_to_hmm(width_cm)
            size.Height = _cm_to_hmm(height_cm)
            shape.Size = size

            slide.add(shape)
            shape.setString(text)

            shape_index = slide.Count - 1
            doc.store()
            return shape_index
        finally:
            doc.close(True)


def add_image(
    path: str,
    slide_index: int,
    image_path: str,
    x_cm: float,
    y_cm: float,
    width_cm: float = 10.0,
    height_cm: float = 10.0,
) -> int:
    """Insert an image onto a slide.

    Args:
        path: Path to the presentation file.
        slide_index: Zero-based slide index.
        image_path: Path to the image file.
        x_cm: X position in centimetres.
        y_cm: Y position in centimetres.
        width_cm: Width in centimetres.
        height_cm: Height in centimetres.

    Returns:
        Shape index of the new image.

    Raises:
        MediaNotFoundError: If image file does not exist.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    img_file = Path(image_path)
    if not img_file.exists():
        raise MediaNotFoundError(f"Image not found: {image_path}")

    with uno_context() as desktop:
        import uno  # type: ignore[import-not-found]

        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            slide = doc.DrawPages.getByIndex(slide_index)

            shape = doc.createInstance("com.sun.star.drawing.GraphicObjectShape")
            pos = uno.createUnoStruct("com.sun.star.awt.Point")
            pos.X = _cm_to_hmm(x_cm)
            pos.Y = _cm_to_hmm(y_cm)
            shape.Position = pos

            size = uno.createUnoStruct("com.sun.star.awt.Size")
            size.Width = _cm_to_hmm(width_cm)
            size.Height = _cm_to_hmm(height_cm)
            shape.Size = size

            slide.add(shape)
            shape.GraphicURL = img_file.resolve().as_uri()

            shape_index = slide.Count - 1
            doc.store()
            return shape_index
        finally:
            doc.close(True)


def add_shape(
    path: str,
    slide_index: int,
    shape_type: str,
    x_cm: float,
    y_cm: float,
    width_cm: float,
    height_cm: float,
    fill_color: int | str | None = None,
    line_color: int | str | None = None,
) -> int:
    """Add a geometric shape to a slide.

    Args:
        path: Path to the presentation file.
        slide_index: Zero-based slide index.
        shape_type: Shape type: rectangle, ellipse, triangle, line, arrow.
        x_cm: X position in centimetres.
        y_cm: Y position in centimetres.
        width_cm: Width in centimetres.
        height_cm: Height in centimetres.
        fill_color: Optional fill colour as 0xRRGGBB integer or name.
        line_color: Optional line colour as 0xRRGGBB integer or name.

    Returns:
        Shape index of the new shape.

    Raises:
        InvalidShapeError: If shape_type is unknown.
    """
    if shape_type not in SHAPE_TYPE_MAP:
        raise InvalidShapeError(
            f"Unknown shape type: {shape_type}. "
            f"Valid types: {list(SHAPE_TYPE_MAP.keys())}"
        )

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

            uno_type = SHAPE_TYPE_MAP[shape_type]
            shape = doc.createInstance(uno_type)

            pos = uno.createUnoStruct("com.sun.star.awt.Point")
            pos.X = _cm_to_hmm(x_cm)
            pos.Y = _cm_to_hmm(y_cm)
            shape.Position = pos

            size = uno.createUnoStruct("com.sun.star.awt.Size")
            size.Width = _cm_to_hmm(width_cm)
            size.Height = _cm_to_hmm(height_cm)
            shape.Size = size

            slide.add(shape)

            if shape_type == "triangle":
                _set_custom_shape_geometry(shape, "isosceles-triangle")
            elif shape_type == "arrow":
                _set_custom_shape_geometry(shape, "right-arrow")

            if fill_color is not None:
                fill_color = resolve_color(fill_color)
                shape.FillStyle = 1  # SOLID
                shape.FillColor = fill_color

            if line_color is not None:
                shape.LineColor = resolve_color(line_color)

            shape_index = slide.Count - 1
            doc.store()
            return shape_index
        finally:
            doc.close(True)


def _set_custom_shape_geometry(shape: object, preset_type: str) -> None:
    """Set CustomShape geometry for triangle/arrow shapes.

    Args:
        shape: UNO CustomShape object.
        preset_type: The EnhancedCustomShapeType preset name.
    """
    import uno  # type: ignore[import-not-found]

    geom = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    geom.Name = "Type"
    geom.Value = "non-primitive"

    geom2 = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    geom2.Name = "ViewBox"
    rect = uno.createUnoStruct("com.sun.star.awt.Rectangle")
    rect.X = 0
    rect.Y = 0
    rect.Width = 21600
    rect.Height = 21600
    geom2.Value = rect

    geom3 = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    geom3.Name = "Coordinates"

    if preset_type == "isosceles-triangle":
        # Triangle: three points
        p1 = uno.createUnoStruct(
            "com.sun.star.drawing.EnhancedCustomShapeParameterPair"
        )
        p1.First.Value = 10800
        p1.First.Type = 0
        p1.Second.Value = 0
        p1.Second.Type = 0

        p2 = uno.createUnoStruct(
            "com.sun.star.drawing.EnhancedCustomShapeParameterPair"
        )
        p2.First.Value = 21600
        p2.First.Type = 0
        p2.Second.Value = 21600
        p2.Second.Type = 0

        p3 = uno.createUnoStruct(
            "com.sun.star.drawing.EnhancedCustomShapeParameterPair"
        )
        p3.First.Value = 0
        p3.First.Type = 0
        p3.Second.Value = 21600
        p3.Second.Type = 0

        geom3.Value = (p1, p2, p3)
    else:
        # Arrow: simple right-pointing arrow
        p1 = uno.createUnoStruct(
            "com.sun.star.drawing.EnhancedCustomShapeParameterPair"
        )
        p1.First.Value = 0
        p1.First.Type = 0
        p1.Second.Value = 5400
        p1.Second.Type = 0

        p2 = uno.createUnoStruct(
            "com.sun.star.drawing.EnhancedCustomShapeParameterPair"
        )
        p2.First.Value = 16200
        p2.First.Type = 0
        p2.Second.Value = 5400
        p2.Second.Type = 0

        p3 = uno.createUnoStruct(
            "com.sun.star.drawing.EnhancedCustomShapeParameterPair"
        )
        p3.First.Value = 16200
        p3.First.Type = 0
        p3.Second.Value = 0
        p3.Second.Type = 0

        p4 = uno.createUnoStruct(
            "com.sun.star.drawing.EnhancedCustomShapeParameterPair"
        )
        p4.First.Value = 21600
        p4.First.Type = 0
        p4.Second.Value = 10800
        p4.Second.Type = 0

        p5 = uno.createUnoStruct(
            "com.sun.star.drawing.EnhancedCustomShapeParameterPair"
        )
        p5.First.Value = 16200
        p5.First.Type = 0
        p5.Second.Value = 21600
        p5.Second.Type = 0

        p6 = uno.createUnoStruct(
            "com.sun.star.drawing.EnhancedCustomShapeParameterPair"
        )
        p6.First.Value = 16200
        p6.First.Type = 0
        p6.Second.Value = 16200
        p6.Second.Type = 0

        p7 = uno.createUnoStruct(
            "com.sun.star.drawing.EnhancedCustomShapeParameterPair"
        )
        p7.First.Value = 0
        p7.First.Type = 0
        p7.Second.Value = 16200
        p7.Second.Type = 0

        geom3.Value = (p1, p2, p3, p4, p5, p6, p7)

    shape.CustomShapeGeometry = (geom, geom2, geom3)  # type: ignore[attr-defined]
