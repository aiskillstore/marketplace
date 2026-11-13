#!/usr/bin/env python3
"""Create a visual review sheet for LUT candidates on user-selected images."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError as exc:
    raise SystemExit("Pillow is required for LUT review sheets. Install Pillow or use the single-image preview script.") from exc

from apply_lut_preview import apply_lut, parse_cube
from image_color import open_for_lut, save_for_lut


def safe_label(path: Path) -> str:
    """Use an ASCII label so the built-in fallback font works on every platform."""
    label = f"{path.parent.name}/{path.name}" if path.parent.name else path.name
    return label.encode("ascii", "replace").decode("ascii")


def load_preview(path: Path, max_size: int, color_mode="srgb-photo") -> Image.Image:
    image, _ = open_for_lut(path, color_mode)
    image = image.convert("RGB")
    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    return image


def choose_font(size: int):
    for font_name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_review_sheet(
    input_paths: list[Path],
    lut_paths: list[Path],
    output_path: Path,
    max_size: int,
    color_mode: str = "srgb-photo",
) -> None:
    if not input_paths:
        raise ValueError("Provide at least one input image.")
    if not lut_paths:
        raise ValueError("Provide at least one candidate LUT.")

    if output_path.suffix.lower() != ".png":
        raise ValueError("Review sheet output path must end with .png.")
    resolved_output = output_path.resolve()
    if any(resolved_output == path.resolve() for path in [*input_paths, *lut_paths]):
        raise ValueError("Output path must not overwrite an input image or LUT.")

    inputs = [(path, load_preview(path, max_size, color_mode)) for path in input_paths]
    luts = [(path, *parse_cube(path)) for path in lut_paths]

    padding = 24
    title_height = 54
    column_header_height = 42
    row_header_height = 34
    column_gap = 16
    row_gap = 16
    panel_width = max_size
    pair_width = panel_width * 2
    row_height = row_header_height + max_size

    sheet_width = padding * 2 + len(inputs) * pair_width + max(0, len(inputs) - 1) * column_gap
    sheet_height = (
        padding * 2
        + title_height
        + column_header_height
        + len(luts) * row_height
        + max(0, len(luts) - 1) * row_gap
    )
    sheet = Image.new("RGB", (sheet_width, sheet_height), (26, 29, 35))
    draw = ImageDraw.Draw(sheet)
    title_font = choose_font(22)
    label_font = choose_font(15)

    draw.text((padding, padding), "LUT CANDIDATES | LEFT=BEFORE | RIGHT=AFTER", font=title_font, fill=(245, 246, 248))
    columns_y = padding + title_height
    for input_index, (input_path, _) in enumerate(inputs):
        x = padding + input_index * (pair_width + column_gap)
        draw.text(
            (x, columns_y),
            f"INPUT {input_index + 1}: {safe_label(input_path)}",
            font=label_font,
            fill=(205, 211, 220),
        )

    rows_y = columns_y + column_header_height
    for lut_index, (lut_path, lut_size, values) in enumerate(luts):
        row_y = rows_y + lut_index * (row_height + row_gap)
        draw.text(
            (padding, row_y),
            f"LUT {lut_index + 1}: {safe_label(lut_path)}  |  {lut_size}^3",
            font=label_font,
            fill=(255, 210, 120),
        )
        image_y = row_y + row_header_height

        for input_index, (_, before) in enumerate(inputs):
            x = padding + input_index * (pair_width + column_gap)
            after = apply_lut(before, lut_size, values)
            draw.rectangle((x, image_y, x + pair_width - 1, image_y + max_size - 1), fill=(40, 44, 52))

            for panel_index, image in enumerate((before, after)):
                panel_x = x + panel_index * panel_width
                paste_x = panel_x + (panel_width - image.width) // 2
                paste_y = image_y + (max_size - image.height) // 2
                sheet.paste(image, (paste_x, paste_y))

            draw.line((x + panel_width, image_y, x + panel_width, image_y + max_size), fill=(235, 238, 242), width=2)
            draw.rectangle((x, image_y, x + pair_width - 1, image_y + max_size - 1), outline=(94, 101, 114), width=1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite {output_path}")
    save_for_lut(sheet, output_path, color_mode, format="PNG")
    print(f"Wrote {output_path} ({len(luts)} LUT candidates across {len(inputs)} selected image(s)).")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare candidate .cube LUTs on the same user-selected images; this creates previews, not automatic shot matches."
    )
    parser.add_argument("--input", action="append", required=True, help="Selected image to preview; repeat for additional representative frames.")
    parser.add_argument("--lut", action="append", required=True, help="Candidate .cube LUT; repeat for additional candidates.")
    parser.add_argument("--output", required=True, help="Output PNG review sheet.")
    parser.add_argument("--max-size", type=int, default=420, help="Maximum preview edge in pixels (default: 420).")
    parser.add_argument("--color-mode", choices=("srgb-photo", "encoded-rgb"), default="srgb-photo")
    args = parser.parse_args()
    if args.max_size < 64:
        parser.error("--max-size must be at least 64")
    return args


def main() -> None:
    args = parse_args()
    try:
        make_review_sheet(
            [Path(value) for value in args.input],
            [Path(value) for value in args.lut],
            Path(args.output),
            args.max_size,
            args.color_mode,
        )
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Could not create LUT review sheet: {exc}") from exc


if __name__ == "__main__":
    main()
