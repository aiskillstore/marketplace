#!/usr/bin/env python3
"""Compose an image-based PDF with invisible and debug text layers."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

try:
    import fitz
    from PIL import Image
except ImportError as exc:
    raise SystemExit(
        "Missing dependency. Install with: uv pip install PyMuPDF Pillow"
    ) from exc


ALIGN = {
    "left": fitz.TEXT_ALIGN_LEFT,
    "center": fitz.TEXT_ALIGN_CENTER,
    "right": fitz.TEXT_ALIGN_RIGHT,
}


def has_non_latin(text: str) -> bool:
    return any(ord(ch) > 255 for ch in text)


def image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as im:
        return im.size


def load_layout(path: Path, fallback_size: tuple[int, int]) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        data = {"items": data}
    if not isinstance(data, dict):
        raise ValueError("layout JSON must be an object or list of items")
    data.setdefault("image_width", fallback_size[0])
    data.setdefault("image_height", fallback_size[1])
    data.setdefault("units", "px")
    if "items" not in data or not isinstance(data["items"], list):
        raise ValueError("layout JSON must contain an items list")
    return data


def bbox_from_item(item: dict[str, Any]) -> list[float]:
    if "bbox" in item:
        bbox = item["bbox"]
    elif {"x", "y", "width", "height"} <= set(item):
        bbox = [item["x"], item["y"], item["x"] + item["width"], item["y"] + item["height"]]
    elif "polygon" in item:
        xs: list[float] = []
        ys: list[float] = []
        for point in item["polygon"]:
            if isinstance(point, dict):
                xs.append(float(point.get("x", 0)))
                ys.append(float(point.get("y", 0)))
            else:
                xs.append(float(point[0]))
                ys.append(float(point[1]))
        bbox = [min(xs), min(ys), max(xs), max(ys)]
    else:
        raise ValueError(f"layout item is missing bbox: {item!r}")

    if not isinstance(bbox, list) or len(bbox) != 4:
        raise ValueError(f"bbox must be [x0, y0, x1, y1]: {item!r}")
    x0, y0, x1, y1 = [float(v) for v in bbox]
    if x1 <= x0 or y1 <= y0:
        raise ValueError(f"bbox has non-positive size: {bbox!r}")
    return [x0, y0, x1, y1]


def rect_from_bbox(
    bbox: list[float],
    *,
    units: str,
    image_width: float,
    image_height: float,
    page_width: float,
    page_height: float,
) -> fitz.Rect:
    x0, y0, x1, y1 = bbox
    if units == "relative":
        x0 *= image_width
        x1 *= image_width
        y0 *= image_height
        y1 *= image_height
    elif units != "px":
        raise ValueError(f"unsupported units: {units}")
    sx = page_width / image_width
    sy = page_height / image_height
    return fitz.Rect(x0 * sx, y0 * sy, x1 * sx, y1 * sy)


def estimate_font_size(text: str, rect: fitz.Rect) -> float:
    stripped = text.strip()
    if not stripped:
        return max(1.0, rect.height * 0.65)
    cjk = sum(1 for ch in stripped if ord(ch) > 255)
    latin = max(0, len(stripped) - cjk)
    width_units = cjk * 0.95 + latin * 0.52
    by_width = rect.width / max(width_units, 1.0)
    by_height = rect.height * 0.72
    return max(4.0, min(by_width, by_height))


def insert_fitting_textbox(
    page: fitz.Page,
    rect: fitz.Rect,
    text: str,
    *,
    font_size: float,
    align: int,
    fontfile: str | None,
    render_mode: int,
    color: tuple[float, float, float],
    fill_opacity: float = 1.0,
) -> float:
    fontname = "imagetextfont" if fontfile else "helv"
    size = max(1.0, font_size)
    last_result = 0.0
    for _ in range(18):
        last_result = page.insert_textbox(
            rect,
            text,
            fontsize=size,
            fontname=fontname,
            fontfile=fontfile,
            align=align,
            color=color,
            render_mode=render_mode,
            fill_opacity=fill_opacity,
            overlay=True,
        )
        if last_result >= 0:
            return size
        size *= 0.92
    raise RuntimeError(
        f"text did not fit after shrinking to {size:.2f} pt: {text[:80]!r}; "
        f"last result={last_result:.2f}, rect={tuple(rect)}"
    )


def add_page_with_layers(
    doc: fitz.Document,
    image_path: Path,
    layout: dict[str, Any],
    *,
    page_width: float,
    page_height: float,
    fontfile: str | None,
    debug: bool,
) -> None:
    page = doc.new_page(width=page_width, height=page_height)
    page.insert_image(page.rect, filename=str(image_path), keep_proportion=False)

    image_width = float(layout["image_width"])
    image_height = float(layout["image_height"])
    units = str(layout.get("units", "px"))

    for index, raw_item in enumerate(layout["items"], 1):
        if not isinstance(raw_item, dict):
            raise ValueError(f"layout item {index} must be an object")
        text = str(raw_item.get("text", ""))
        if not text.strip():
            continue
        rect = rect_from_bbox(
            bbox_from_item(raw_item),
            units=units,
            image_width=image_width,
            image_height=image_height,
            page_width=page_width,
            page_height=page_height,
        )
        inset = float(raw_item.get("inset", 0))
        if inset:
            rect = rect + (inset, inset, -inset, -inset)
        align = ALIGN.get(str(raw_item.get("align", "left")).lower(), fitz.TEXT_ALIGN_LEFT)
        font_size = float(raw_item.get("font_size") or estimate_font_size(text, rect))

        if debug:
            page.draw_rect(
                rect,
                color=(1, 0, 0.6),
                fill=(1, 1, 0),
                width=1.0,
                stroke_opacity=0.9,
                fill_opacity=0.18,
                overlay=True,
            )
            insert_fitting_textbox(
                page,
                rect,
                text,
                font_size=font_size,
                align=align,
                fontfile=fontfile,
                render_mode=2,
                color=(0.85, 0, 0.65),
                fill_opacity=0.95,
            )
        else:
            insert_fitting_textbox(
                page,
                rect,
                text,
                font_size=font_size,
                align=align,
                fontfile=fontfile,
                render_mode=3,
                color=(0, 0, 0),
            )


def extract_text(path: Path) -> str:
    doc = fitz.open(path)
    try:
        return "\n".join(page.get_text("text") for page in doc)
    finally:
        doc.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, type=Path, help="Poster image path")
    parser.add_argument("--layout", required=True, type=Path, help="Layout JSON path")
    parser.add_argument("--output", required=True, type=Path, help="Final PDF path")
    parser.add_argument("--debug-output", type=Path, help="Visible text-layer inspection PDF")
    parser.add_argument("--font-file", type=Path, help="Unicode font file for embedded text")
    parser.add_argument("--page-width", type=float, help="PDF page width in points")
    parser.add_argument("--page-height", type=float, help="PDF page height in points")
    parser.add_argument(
        "--check-text",
        action="store_true",
        help="Print extracted text from the final PDF after saving",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.image.exists():
        raise SystemExit(f"image not found: {args.image}")
    if not args.layout.exists():
        raise SystemExit(f"layout not found: {args.layout}")
    fontfile = str(args.font_file) if args.font_file else None
    if args.font_file and not args.font_file.exists():
        raise SystemExit(f"font file not found: {args.font_file}")

    size = image_size(args.image)
    layout = load_layout(args.layout, size)
    page_width = float(args.page_width or size[0])
    page_height = float(args.page_height or size[1])

    if not fontfile and any(has_non_latin(str(item.get("text", ""))) for item in layout["items"]):
        print(
            "warning: layout contains non-Latin text but no --font-file was supplied; "
            "PDF text extraction may fail if the default font lacks glyphs.",
            file=sys.stderr,
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    add_page_with_layers(
        doc,
        args.image,
        layout,
        page_width=page_width,
        page_height=page_height,
        fontfile=fontfile,
        debug=False,
    )
    doc.save(args.output, deflate=True, garbage=4)
    doc.close()

    if args.debug_output:
        args.debug_output.parent.mkdir(parents=True, exist_ok=True)
        debug_doc = fitz.open()
        add_page_with_layers(
            debug_doc,
            args.image,
            layout,
            page_width=page_width,
            page_height=page_height,
            fontfile=fontfile,
            debug=True,
        )
        debug_doc.save(args.debug_output, deflate=True, garbage=4)
        debug_doc.close()

    if args.check_text:
        print(extract_text(args.output).strip())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
