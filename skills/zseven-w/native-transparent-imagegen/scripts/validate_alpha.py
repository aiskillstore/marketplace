#!/usr/bin/env python3
"""Read-only validation for native-alpha PNG and WebP assets."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, UnidentifiedImageError


SUPPORTED_FORMATS = {"PNG", "WEBP"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect(path: Path, require_transparent_corners: bool) -> dict[str, object]:
    failures: list[str] = []
    result: dict[str, object] = {
        "path": str(path),
        "verdict": "fail",
        "failures": failures,
    }

    if not path.is_file():
        failures.append("file-not-found")
        return result

    result["bytes"] = path.stat().st_size
    result["sha256"] = sha256(path)

    try:
        with Image.open(path) as image:
            image.load()
            image_format = (image.format or "").upper()
            result["format"] = image_format
            result["dimensions"] = [image.width, image.height]
            result["mode"] = image.mode
            result["bands"] = list(image.getbands())

            if image_format not in SUPPORTED_FORMATS:
                failures.append("format-must-be-png-or-webp")

            encoded_alpha = "A" in image.getbands() or "transparency" in image.info
            result["encoded_alpha"] = encoded_alpha
            if not encoded_alpha:
                failures.append("missing-alpha-channel")
                return result

            alpha = image.convert("RGBA").getchannel("A")
            alpha_min, alpha_max = alpha.getextrema()
            histogram = alpha.histogram()
            total_pixels = image.width * image.height
            corners = [
                alpha.getpixel((0, 0)),
                alpha.getpixel((image.width - 1, 0)),
                alpha.getpixel((0, image.height - 1)),
                alpha.getpixel((image.width - 1, image.height - 1)),
            ]

            result["alpha_extrema"] = [alpha_min, alpha_max]
            result["fully_transparent_pixels"] = histogram[0]
            result["partially_transparent_pixels"] = sum(histogram[1:255])
            result["fully_opaque_pixels"] = histogram[255]
            result["transparent_percent"] = round(
                histogram[0] * 100.0 / total_pixels, 4
            )
            result["corner_alpha"] = corners

            if alpha_min != 0 or histogram[0] == 0:
                failures.append("no-fully-transparent-pixels")
            if alpha_max == 0:
                failures.append("image-is-fully-transparent")
            if require_transparent_corners and any(value != 0 for value in corners):
                failures.append("corners-are-not-fully-transparent")
    except (UnidentifiedImageError, OSError) as error:
        failures.append(f"decode-error:{error.__class__.__name__}")

    if not failures:
        result["verdict"] = "pass"
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify native alpha without modifying the input asset."
    )
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument(
        "--require-transparent-corners",
        action="store_true",
        help="Require all four corner pixels to have alpha 0.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit one JSON array instead of one JSON object per line.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = [inspect(path, args.require_transparent_corners) for path in args.paths]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if all(result["verdict"] == "pass" for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
