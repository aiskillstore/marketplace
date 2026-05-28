#!/usr/bin/env python3
"""
ID Photo Tool
Change background color and add text watermark.
"""

import argparse
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont


COLOR_MAP = {
    "blue": (0, 102, 204),
    "white": (255, 255, 255),
    "red": (204, 0, 0),
}

POS_MAP = {
    "top-left": (0.05, 0.05),
    "top-right": (0.95, 0.05),
    "bottom-left": (0.05, 0.95),
    "bottom-right": (0.95, 0.95),
    "center": (0.5, 0.5),
}


def load_image(path: Path) -> Image.Image:
    img = Image.open(path)
    return img.convert("RGB")


def save_image(img: Image.Image, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)


def sample_border_pixels(img: Image.Image, border: int = 10) -> np.ndarray:
    arr = np.asarray(img)
    h, w, _ = arr.shape
    top = arr[:border, :, :]
    bottom = arr[h - border :, :, :]
    left = arr[:, :border, :]
    right = arr[:, w - border :, :]
    samples = np.concatenate(
        [
            top.reshape(-1, 3),
            bottom.reshape(-1, 3),
            left.reshape(-1, 3),
            right.reshape(-1, 3),
        ],
        axis=0,
    )
    return samples


def dominant_color(samples: np.ndarray) -> np.ndarray:
    return np.median(samples, axis=0)


def replace_background(
    img: Image.Image, target_color: Tuple[int, int, int], tolerance: int
) -> Image.Image:
    arr = np.asarray(img).astype(np.int16)
    samples = sample_border_pixels(img)
    bg = dominant_color(samples)
    diff = np.linalg.norm(arr - bg, axis=2)
    mask = diff <= tolerance
    arr[mask] = np.array(target_color, dtype=np.int16)
    return Image.fromarray(arr.astype(np.uint8))


def add_watermark(
    img: Image.Image,
    text: str,
    position: str,
    opacity: float,
    font_size: int,
    color: Tuple[int, int, int],
    font_path: str | None,
) -> Image.Image:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    if font_path:
        font = ImageFont.truetype(font_path, font_size)
    else:
        font = ImageFont.load_default()

    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
    anchor = POS_MAP[position]
    x = int(img.size[0] * anchor[0])
    y = int(img.size[1] * anchor[1])

    if "right" in position:
        x -= text_width
    if "bottom" in position:
        y -= text_height
    if position == "center":
        x -= text_width // 2
        y -= text_height // 2

    alpha = int(255 * max(0.0, min(opacity, 1.0)))
    draw.text((x, y), text, font=font, fill=(color[0], color[1], color[2], alpha))

    combined = Image.alpha_composite(img.convert("RGBA"), overlay)
    return combined.convert("RGB")


def parse_color(value: str) -> Tuple[int, int, int]:
    if value in COLOR_MAP:
        return COLOR_MAP[value]
    raise ValueError("Unsupported color")


def ensure_output_not_input(input_path: Path, output_path: Path) -> None:
    if input_path.resolve() == output_path.resolve():
        raise ValueError("Output path must be different from input")


def main() -> None:
    parser = argparse.ArgumentParser(description="ID Photo Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    change_bg = subparsers.add_parser("change-bg")
    change_bg.add_argument("--input", required=True)
    change_bg.add_argument("--output", required=True)
    change_bg.add_argument("--color", required=True, choices=list(COLOR_MAP.keys()))
    change_bg.add_argument("--tolerance", type=int, default=40)

    watermark = subparsers.add_parser("add-watermark")
    watermark.add_argument("--input", required=True)
    watermark.add_argument("--output", required=True)
    watermark.add_argument("--text", required=True)
    watermark.add_argument(
        "--position",
        default="bottom-right",
        choices=list(POS_MAP.keys()),
    )
    watermark.add_argument("--opacity", type=float, default=0.3)
    watermark.add_argument("--font-size", type=int, default=24)
    watermark.add_argument("--color", default="white", choices=list(COLOR_MAP.keys()))
    watermark.add_argument("--font-path", default=None)

    args = parser.parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    ensure_output_not_input(input_path, output_path)

    img = load_image(input_path)

    if args.command == "change-bg":
        target = parse_color(args.color)
        result = replace_background(img, target, args.tolerance)
    else:
        color = parse_color(args.color)
        result = add_watermark(
            img,
            args.text,
            args.position,
            args.opacity,
            args.font_size,
            color,
            args.font_path,
        )

    save_image(result, output_path)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
