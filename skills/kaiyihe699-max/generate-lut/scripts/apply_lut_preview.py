#!/usr/bin/env python3
"""Apply a .cube LUT to an image and create an adjusted or comparison preview."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError as exc:  # pragma: no cover - exercised only when Pillow is absent.
    raise SystemExit("Pillow is required for image previews. Install Pillow or use validate/generate only.") from exc


from cube_io import read_cube
from image_color import open_for_lut, save_for_lut


def parse_cube(path: Path) -> tuple[int, list[tuple[float, float, float]]]:
    size, values, _ = read_cube(path)
    return size, values


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def lerp(a: float, b: float, amount: float) -> float:
    return a + (b - a) * amount


def lookup(values: list[tuple[float, float, float]], size: int, r: float, g: float, b: float) -> tuple[float, float, float]:
    scale = size - 1
    rf, gf, bf = clamp(r) * scale, clamp(g) * scale, clamp(b) * scale
    r0, g0, b0 = int(math.floor(rf)), int(math.floor(gf)), int(math.floor(bf))
    r1, g1, b1 = min(r0 + 1, scale), min(g0 + 1, scale), min(b0 + 1, scale)
    tr, tg, tb = rf - r0, gf - g0, bf - b0

    def at(ri: int, gi: int, bi: int) -> tuple[float, float, float]:
        return values[((bi * size) + gi) * size + ri]

    c000 = at(r0, g0, b0)
    c100 = at(r1, g0, b0)
    c010 = at(r0, g1, b0)
    c110 = at(r1, g1, b0)
    c001 = at(r0, g0, b1)
    c101 = at(r1, g0, b1)
    c011 = at(r0, g1, b1)
    c111 = at(r1, g1, b1)

    out = []
    for channel in range(3):
        c00 = lerp(c000[channel], c100[channel], tr)
        c10 = lerp(c010[channel], c110[channel], tr)
        c01 = lerp(c001[channel], c101[channel], tr)
        c11 = lerp(c011[channel], c111[channel], tr)
        c0 = lerp(c00, c10, tg)
        c1 = lerp(c01, c11, tg)
        out.append(clamp(lerp(c0, c1, tb)))
    return tuple(out)


def resize_for_preview(image: Image.Image, max_size: int) -> Image.Image:
    if max(image.size) <= max_size:
        return image
    copy = image.copy()
    copy.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    return copy


def apply_lut(
    image: Image.Image,
    size: int,
    values: list[tuple[float, float, float]],
    strength: float = 1.0,
) -> Image.Image:
    if not 0.0 <= strength <= 1.0:
        raise ValueError("LUT strength must be between 0 and 1.")
    has_alpha = image.mode == "RGBA"
    source = image.convert("RGBA" if has_alpha else "RGB")
    output = Image.new(source.mode, source.size)
    result = []
    pixel_data = source.get_flattened_data() if hasattr(source, "get_flattened_data") else source.getdata()
    for pixel in pixel_data:
        r, g, b = pixel[:3]
        rr, gg, bb = lookup(values, size, r / 255.0, g / 255.0, b / 255.0)
        original = (r / 255.0, g / 255.0, b / 255.0)
        mixed = tuple(original[channel] + (graded - original[channel]) * strength for channel, graded in enumerate((rr, gg, bb)))
        mapped = tuple(round(channel * 255) for channel in mixed)
        if has_alpha:
            mapped = mapped + (pixel[3],)
        result.append(mapped)
    output.putdata(result)
    return output


def comparison(before: Image.Image, after: Image.Image) -> Image.Image:
    before_rgb = before.convert("RGB")
    after_rgb = after.convert("RGB")
    canvas = Image.new("RGB", (before_rgb.width * 2, before_rgb.height), "white")
    canvas.paste(before_rgb, (0, 0))
    canvas.paste(after_rgb, (before_rgb.width, 0))
    return canvas


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply a .cube 3D LUT to an image preview.")
    parser.add_argument("--input", required=True, help="Input image path.")
    parser.add_argument("--lut", required=True, help=".cube LUT path.")
    parser.add_argument("--output", required=True, help="Output image path.")
    parser.add_argument("--mode", choices=("adjusted", "comparison"), default="comparison", help="Preview output mode.")
    parser.add_argument("--max-size", type=int, default=1400, help="Resize longest edge before previewing.")
    parser.add_argument("--strength", type=float, default=1.0, help="LUT amount from 0 (identity) to 1 (full effect).")
    parser.add_argument("--color-mode", choices=("srgb-photo", "encoded-rgb"), default="srgb-photo", help="Photo ICC normalization, or explicit raw-code preview for technical LUTs; encoded output has no ICC tag.")
    args = parser.parse_args()
    if args.max_size < 1:
        parser.error("--max-size must be positive")
    if not 0.0 <= args.strength <= 1.0:
        parser.error("--strength must be between 0 and 1")
    return args


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    if output_path.resolve() in {Path(args.input).resolve(), Path(args.lut).resolve()} or output_path.exists():
        raise ValueError("Output must be new and must not overwrite an input.")
    lut_size, values = parse_cube(Path(args.lut))
    image, color_info = open_for_lut(args.input, args.color_mode)
    image = resize_for_preview(image, args.max_size)
    adjusted = apply_lut(image, lut_size, values, args.strength)
    output = comparison(image, adjusted) if args.mode == "comparison" else adjusted
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_for_lut(output, output_path, args.color_mode)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Could not create LUT preview: {exc}") from exc
