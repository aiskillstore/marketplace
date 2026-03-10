"""Media operations for Impress."""

import warnings
from pathlib import Path

from impress._util import _cm_to_hmm
from impress.exceptions import DocumentNotFoundError, MediaNotFoundError
from uno_bridge import uno_context


def add_audio(
    path: str,
    slide_index: int,
    media_path: str,
    x_cm: float,
    y_cm: float,
    width_cm: float,
    height_cm: float,
) -> int:
    """Insert an audio shape on a slide.

    Args:
        path: Path to the presentation file.
        slide_index: Zero-based slide index.
        media_path: Path to the audio file.
        x_cm: X position in centimetres.
        y_cm: Y position in centimetres.
        width_cm: Width in centimetres.
        height_cm: Height in centimetres.

    Returns:
        Shape index of the new audio shape.

    Raises:
        MediaNotFoundError: If audio file does not exist.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    media_file = Path(media_path)
    if not media_file.exists():
        raise MediaNotFoundError(f"Audio file not found: {media_path}")

    return _add_media_shape(
        path, slide_index, media_path, x_cm, y_cm, width_cm, height_cm
    )


def add_video(
    path: str,
    slide_index: int,
    media_path: str,
    x_cm: float,
    y_cm: float,
    width_cm: float,
    height_cm: float,
) -> int:
    """Insert a video shape on a slide.

    Args:
        path: Path to the presentation file.
        slide_index: Zero-based slide index.
        media_path: Path to the video file.
        x_cm: X position in centimetres.
        y_cm: Y position in centimetres.
        width_cm: Width in centimetres.
        height_cm: Height in centimetres.

    Returns:
        Shape index of the new video shape.

    Raises:
        MediaNotFoundError: If video file does not exist.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {path}")

    media_file = Path(media_path)
    if not media_file.exists():
        raise MediaNotFoundError(f"Video file not found: {media_path}")

    return _add_media_shape(
        path, slide_index, media_path, x_cm, y_cm, width_cm, height_cm
    )


def _add_media_shape(
    path: str,
    slide_index: int,
    media_path: str,
    x_cm: float,
    y_cm: float,
    width_cm: float,
    height_cm: float,
) -> int:
    """Internal helper to add a media shape.

    Args:
        path: Path to the presentation file.
        slide_index: Zero-based slide index.
        media_path: Path to the media file.
        x_cm: X position in centimetres.
        y_cm: Y position in centimetres.
        width_cm: Width in centimetres.
        height_cm: Height in centimetres.

    Returns:
        Shape index of the new media shape.
    """
    file_path = Path(path)
    media_file = Path(media_path)

    with uno_context() as desktop:
        import uno  # type: ignore[import-not-found]

        doc = desktop.loadComponentFromURL(
            file_path.resolve().as_uri(), "_blank", 0, ()
        )
        try:
            slide = doc.DrawPages.getByIndex(slide_index)

            # Try MediaShape first, fall back to PluginShape
            try:
                shape = doc.createInstance("com.sun.star.presentation.MediaShape")
            except Exception as exc:
                warnings.warn(
                    f"media shape creation fallback triggered: {exc}",
                    stacklevel=2,
                )
                shape = doc.createInstance("com.sun.star.drawing.PluginShape")

            pos = uno.createUnoStruct("com.sun.star.awt.Point")
            pos.X = _cm_to_hmm(x_cm)
            pos.Y = _cm_to_hmm(y_cm)
            shape.Position = pos

            size = uno.createUnoStruct("com.sun.star.awt.Size")
            size.Width = _cm_to_hmm(width_cm)
            size.Height = _cm_to_hmm(height_cm)
            shape.Size = size

            slide.add(shape)

            # Set media URL after adding to slide
            media_url = media_file.resolve().as_uri()
            try:
                shape.MediaURL = media_url
            except Exception as exc:
                warnings.warn(
                    f"MediaURL assignment failed, trying PluginURL: {exc}",
                    stacklevel=2,
                )
                try:
                    shape.PluginURL = media_url
                except Exception as plugin_exc:
                    warnings.warn(
                        f"PluginURL assignment failed: {plugin_exc}",
                        stacklevel=2,
                    )

            shape_index = slide.Count - 1
            doc.store()
            return shape_index
        finally:
            doc.close(True)
