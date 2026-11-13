#!/usr/bin/env python3
"""Create fallback PNG test charts for LUT previews without bundled binary assets."""

from __future__ import annotations

import argparse
import struct
import zlib
from pathlib import Path


def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    payload = chunk_type + data
    return struct.pack(">I", len(data)) + payload + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF)


def write_png(path: Path, width: int, height: int, pixels: list[tuple[int, int, int]]) -> None:
    if len(pixels) != width * height:
        raise ValueError("Pixel count does not match image size.")
    raw_rows = []
    for y in range(height):
        row = bytearray([0])
        for r, g, b in pixels[y * width : (y + 1) * width]:
            row.extend((r, g, b))
        raw_rows.append(bytes(row))
    data = b"".join(raw_rows)
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", header) + png_chunk(b"IDAT", zlib.compress(data, 9)) + png_chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def make_neutral_ramp(path: Path) -> None:
    width, height = 1024, 256
    pixels: list[tuple[int, int, int]] = []
    for y in range(height):
        for x in range(width):
            value = round(255 * x / (width - 1))
            if y < height * 0.62:
                pixels.append((value, value, value))
            elif y < height * 0.75:
                pixels.append((value, 0, 0))
            elif y < height * 0.88:
                pixels.append((0, value, 0))
            else:
                pixels.append((0, 0, value))
    write_png(path, width, height, pixels)


def make_color_checker(path: Path) -> None:
    swatches = [
        (18, 18, 18), (48, 48, 48), (92, 92, 92), (138, 138, 138), (190, 190, 190), (235, 235, 235),
        (182, 120, 92), (217, 164, 126), (132, 76, 60), (236, 190, 154), (112, 54, 42), (196, 136, 96),
        (196, 28, 38), (236, 112, 40), (246, 202, 48), (82, 168, 76), (38, 122, 196), (92, 62, 150),
        (20, 184, 180), (230, 70, 130), (120, 80, 40), (70, 125, 85), (40, 80, 130), (210, 210, 120),
    ]
    cols, rows = 6, 4
    cell, gap, margin = 120, 12, 24
    width = cols * cell + (cols + 1) * gap + 2 * margin
    height = rows * cell + (rows + 1) * gap + 2 * margin
    pixels = [(24, 24, 24) for _ in range(width * height)]

    for index, color in enumerate(swatches):
        col = index % cols
        row = index // cols
        x0 = margin + gap + col * (cell + gap)
        y0 = margin + gap + row * (cell + gap)
        for y in range(y0, y0 + cell):
            for x in range(x0, x0 + cell):
                pixels[y * width + x] = color
    write_png(path, width, height, pixels)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create neutral-ramp.png and color-checker.png for LUT previews.")
    parser.add_argument("--output-dir", default="assets", help="Directory where PNG test charts should be written.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    make_neutral_ramp(output_dir / "neutral-ramp.png")
    make_color_checker(output_dir / "color-checker.png")
    print(f"Wrote {output_dir / 'neutral-ramp.png'}")
    print(f"Wrote {output_dir / 'color-checker.png'}")


if __name__ == "__main__":
    main()
