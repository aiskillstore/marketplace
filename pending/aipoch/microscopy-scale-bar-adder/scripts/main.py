#!/usr/bin/env python3
"""
Microscopy Scale Bar Adder
Add calibrated scale bars to microscopy images using Pillow.
"""

import argparse
import sys
import os
from PIL import Image, ImageDraw, ImageFont


VALID_UNITS = ("um", "nm", "mm")
VALID_POSITIONS = ("bottom-right", "bottom-left", "top-right", "top-left")


def check_path_traversal(path: str) -> None:
    """Reject paths containing directory traversal sequences."""
    if "../" in path or path.startswith(".."):
        print(f"Error: path traversal detected in '{path}'. Absolute or traversal paths are not allowed.", file=sys.stderr)
        sys.exit(1)


def read_tiff_pixels_per_unit(image: Image.Image):  # -> Optional[float]
    """
    Try to read XResolution from TIFF tag 282.
    Returns pixels-per-unit as float, or None if unavailable.
    """
    try:
        tag_info = image.tag_v2 if hasattr(image, "tag_v2") else getattr(image, "tag", None)
        if tag_info and 282 in tag_info:
            xres = tag_info[282]
            # IFDRational or tuple (numerator, denominator)
            if hasattr(xres, "numerator"):
                return float(xres.numerator) / float(xres.denominator) if xres.denominator else None
            if isinstance(xres, tuple) and len(xres) == 2:
                return float(xres[0]) / float(xres[1]) if xres[1] else None
            if not isinstance(xres, tuple):
                return float(xres)  # type: ignore[arg-type]
    except Exception:
        pass
    return None


def compute_bar_pixel_length(scale_length: float, pixels_per_unit: float) -> int:
    """Return the scale bar length in pixels."""
    return max(1, round(scale_length * pixels_per_unit))


def get_bar_position(image_width: int, image_height: int, bar_px: int,
                     bar_thickness: int, position: str, margin: int = 20):
    """Return (x0, y0, x1, y1) rectangle coords for the scale bar."""
    if position == "bottom-right":
        x1 = image_width - margin
        x0 = x1 - bar_px
        y1 = image_height - margin
        y0 = y1 - bar_thickness
    elif position == "bottom-left":
        x0 = margin
        x1 = x0 + bar_px
        y1 = image_height - margin
        y0 = y1 - bar_thickness
    elif position == "top-right":
        x1 = image_width - margin
        x0 = x1 - bar_px
        y0 = margin
        y1 = y0 + bar_thickness
    else:  # top-left
        x0 = margin
        x1 = x0 + bar_px
        y0 = margin
        y1 = y0 + bar_thickness
    return x0, y0, x1, y1


def add_scale_bar(
    input_path: str,
    output_path: str,
    scale_length: float,
    scale_unit: str,
    pixels_per_unit: float,
    bar_color: str = "white",
    label_color: str = "white",
    bar_thickness: int = 8,
    position: str = "bottom-right",
) -> None:
    """Draw a scale bar and label onto the image and save it."""
    image = Image.open(input_path).convert("RGBA")
    draw = ImageDraw.Draw(image)

    bar_px = compute_bar_pixel_length(scale_length, pixels_per_unit)
    w, h = image.size
    x0, y0, x1, y1 = get_bar_position(w, h, bar_px, bar_thickness, position)

    # Draw filled rectangle for the bar
    draw.rectangle([x0, y0, x1, y1], fill=bar_color)

    # Draw label below (or above) the bar
    label = f"{scale_length} {scale_unit}"
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except (IOError, OSError):
        font = ImageFont.load_default()

    # Use textbbox for accurate sizing (Pillow ≥ 9.2)
    try:
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except AttributeError:
        text_w, text_h = draw.textsize(label, font=font)  # type: ignore[attr-defined]

    text_x = x0 + (bar_px - text_w) // 2
    if "top" in position:
        text_y = y1 + 4
    else:
        text_y = y0 - text_h - 4

    draw.text((text_x, text_y), label, fill=label_color, font=font)

    # Save — convert back to RGB for JPEG compatibility
    if output_path.lower().endswith((".jpg", ".jpeg")):
        image = image.convert("RGB")
    image.save(output_path)
    print(f"Saved: {output_path}  (bar={bar_px}px, {scale_length} {scale_unit})")


def main():
    parser = argparse.ArgumentParser(
        description="Add a calibrated scale bar to a microscopy image.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py --input slide.tif --scale-length 10 --pixels-per-unit 5.2\n"
            "  python main.py --input img.png --scale-length 50 --scale-unit nm "
            "--pixels-per-unit 2.0 --position bottom-left --bar-color yellow\n"
        ),
    )
    parser.add_argument("--input", required=True, help="Input image path (TIFF/PNG/JPG)")
    parser.add_argument("--output", default="output_with_scalebar.png", help="Output image path")
    parser.add_argument("--scale-length", type=float, required=True,
                        help="Physical length of the scale bar (e.g. 10)")
    parser.add_argument("--scale-unit", default="um", choices=VALID_UNITS,
                        help="Unit for scale bar label (default: um)")
    parser.add_argument("--pixels-per-unit", type=float, default=None,
                        help="Pixels per physical unit (required if TIFF XResolution absent)")
    parser.add_argument("--bar-color", default="white", help="Scale bar fill color (default: white)")
    parser.add_argument("--label-color", default="white", help="Label text color (default: white)")
    parser.add_argument("--bar-thickness", type=int, default=8,
                        help="Bar thickness in pixels (default: 8)")
    parser.add_argument("--position", default="bottom-right", choices=VALID_POSITIONS,
                        help="Scale bar position (default: bottom-right)")

    args = parser.parse_args()

    # Security: reject path traversal
    check_path_traversal(args.input)
    check_path_traversal(args.output)

    if not os.path.isfile(args.input):
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Resolve pixels-per-unit
    pixels_per_unit = args.pixels_per_unit
    if pixels_per_unit is None:
        # Try TIFF XResolution
        try:
            img_probe = Image.open(args.input)
            pixels_per_unit = read_tiff_pixels_per_unit(img_probe)
            img_probe.close()
        except Exception:
            pixels_per_unit = None

        if pixels_per_unit is None:
            print(
                "Error: --pixels-per-unit is required. "
                "No XResolution tag found in the image. "
                "Please provide calibration via --pixels-per-unit (pixels per "
                f"{args.scale_unit}).",
                file=sys.stderr,
            )
            sys.exit(1)

    add_scale_bar(
        input_path=args.input,
        output_path=args.output,
        scale_length=args.scale_length,
        scale_unit=args.scale_unit,
        pixels_per_unit=pixels_per_unit,
        bar_color=args.bar_color,
        label_color=args.label_color,
        bar_thickness=args.bar_thickness,
        position=args.position,
    )


if __name__ == "__main__":
    main()
