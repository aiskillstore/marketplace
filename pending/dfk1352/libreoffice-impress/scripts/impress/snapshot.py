"""Impress snapshot module for slide-level PNG export."""

import struct
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from impress.exceptions import (
    DocumentNotFoundError,
    ImpressSkillError,
    InvalidSlideIndexError,
)
from uno_bridge import find_libreoffice, uno_context


class SnapshotError(ImpressSkillError):
    """Base error for snapshot operations."""


class FilterError(SnapshotError):
    """Error when PNG export filter fails."""


@dataclass
class SnapshotResult:
    """Result metadata from a snapshot export.

    Attributes:
        file_path: Path to the exported PNG file.
        width: Image width in pixels.
        height: Image height in pixels.
        dpi: Export resolution in dots per inch.
    """

    file_path: str
    width: int
    height: int
    dpi: int


def snapshot_slide(
    doc_path: str,
    slide_index: int,
    output_path: str,
    width: int = 1280,
    height: int = 720,
) -> SnapshotResult:
    """Capture a specific slide as a PNG image.

    Args:
        doc_path: Path to the Impress presentation.
        slide_index: Zero-based slide index.
        output_path: File path for the PNG output.
        width: Pixel width of the output image.
        height: Pixel height of the output image.

    Returns:
        SnapshotResult with file path, dimensions, and dpi (96).

    Raises:
        DocumentNotFoundError: If the document file does not exist.
        InvalidSlideIndexError: If slide index is out of range.
        FilterError: If the PNG export fails.
    """
    file_path = Path(doc_path)
    if not file_path.exists():
        raise DocumentNotFoundError(f"Document not found: {doc_path}")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        temp_doc = temp_dir_path / "snapshot_slide.odp"

        temp_doc.write_bytes(file_path.read_bytes())

        with uno_context() as desktop:
            doc = desktop.loadComponentFromURL(
                temp_doc.resolve().as_uri(), "_blank", 0, ()
            )
            try:
                pages = doc.DrawPages
                if slide_index < 0 or slide_index >= pages.Count:
                    raise InvalidSlideIndexError(
                        f"Slide index {slide_index} out of range "
                        f"(presentation has {pages.Count} slides)"
                    )

                for i in range(pages.Count - 1, -1, -1):
                    if i != slide_index:
                        pages.remove(pages.getByIndex(i))

                doc.store()
            finally:
                doc.close(True)

        png_path = _convert_to_pngs(str(temp_doc), temp_dir_path)[0]
        if width and height:
            try:
                from PIL import Image
            except ImportError as exc:
                raise FilterError("Pillow is required for resizing PNGs") from exc

            with Image.open(png_path) as image:
                resized = image.resize((width, height))
                resized.save(output)
        else:
            output.write_bytes(png_path.read_bytes())

    actual_width, actual_height = _read_png_dimensions(output)

    return SnapshotResult(
        file_path=str(output),
        width=actual_width,
        height=actual_height,
        dpi=96,
    )


def _read_png_dimensions(path: Path) -> tuple[int, int]:
    """Read width and height from a PNG file's IHDR chunk.

    Args:
        path: Path to the PNG file.

    Returns:
        Tuple of (width, height) in pixels.
    """
    with open(path, "rb") as f:
        f.read(8)  # PNG signature
        f.read(4)  # IHDR chunk length
        f.read(4)  # IHDR chunk type
        w, h = struct.unpack(">II", f.read(8))
    return w, h


def _convert_to_pngs(doc_path: str, output_dir: Path) -> list[Path]:
    soffice_path = find_libreoffice()
    if not soffice_path:
        raise FilterError("LibreOffice not found. Please install LibreOffice.")

    output_dir.mkdir(parents=True, exist_ok=True)
    doc = Path(doc_path).resolve()

    result = subprocess.run(
        [
            soffice_path,
            "--headless",
            "--invisible",
            "--nocrashreport",
            "--nodefault",
            "--nofirststartwizard",
            "--nologo",
            "--norestore",
            "--convert-to",
            "png",
            "--outdir",
            str(output_dir),
            str(doc),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise FilterError(
            "LibreOffice PNG conversion failed: "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )

    pngs = [p for p in output_dir.iterdir() if p.suffix.lower() == ".png"]
    pngs.sort(key=lambda path: path.name)
    if not pngs:
        raise FilterError("PNG export failed: no PNGs produced")
    return pngs
