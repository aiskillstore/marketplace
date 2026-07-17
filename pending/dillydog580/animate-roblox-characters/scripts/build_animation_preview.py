#!/usr/bin/env python3
"""Encode sequential RGB animation frames as a verified, flicker-resistant GIF."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


def _require_pillow():
    try:
        from PIL import Image, ImageSequence  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Pillow is required; install Pillow>=10,<13") from exc
    return Image, ImageSequence


def natural_key(path: Path) -> list[Any]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", path.name)]


def gif_durations(frame_count: int, fps: float) -> list[int]:
    """Distribute GIF centiseconds while matching the requested rate over time."""
    if frame_count < 1:
        raise ValueError("frame_count must be positive")
    if not math.isfinite(fps) or fps <= 0 or fps > 100:
        raise ValueError("GIF fps must be greater than 0 and no more than 100")
    rate = Fraction(str(fps))
    centiseconds = Fraction(100, 1) / rate
    base = centiseconds.numerator // centiseconds.denominator
    remainder = centiseconds.numerator % centiseconds.denominator
    if base < 1:
        raise ValueError("GIF cannot represent frame durations shorter than 10 ms")
    error = 0
    durations = []
    for _index in range(frame_count):
        duration_cs = base
        error += remainder
        if error >= centiseconds.denominator:
            duration_cs += 1
            error -= centiseconds.denominator
        durations.append(duration_cs * 10)
    return durations


def _load_rgb_frames(paths: Iterable[Path]):
    Image, _ImageSequence = _require_pillow()
    images = []
    for path in paths:
        with Image.open(path) as source:
            source.load()
            images.append(source.convert("RGB"))
    if not images:
        raise ValueError("No input frames were found")
    size = images[0].size
    if any(image.size != size for image in images):
        raise ValueError("Every preview frame must have identical dimensions")
    return images


def _shared_palette(images, colors: int = 254, max_sample_pixels: int = 4_194_304):
    Image, _ImageSequence = _require_pillow()
    thumb_edge = max(32, min(128, int(math.sqrt(max_sample_pixels / len(images)))))
    columns = min(8, max(1, math.ceil(math.sqrt(len(images)))))
    rows = math.ceil(len(images) / columns)
    sheet = Image.new("RGB", (columns * thumb_edge, rows * thumb_edge))
    for index, image in enumerate(images):
        thumbnail = image.resize((thumb_edge, thumb_edge), Image.Resampling.LANCZOS)
        sheet.paste(thumbnail, ((index % columns) * thumb_edge, (index // columns) * thumb_edge))
    return sheet.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)


def _preserve_frame_boundaries(gif_frames) -> None:
    """Prevent Pillow from coalescing intentional identical hold frames.

    Two otherwise-unused palette indices are assigned the same visible color as
    the fixed top-left review background. Alternating those equivalent indices
    changes the encoded data without changing the displayed pixel color.
    """
    if not gif_frames:
        return
    marker = (0, 0)
    for index, frame in enumerate(gif_frames):
        frame_palette = frame.getpalette()
        if frame_palette is None:
            raise ValueError("GIF frame does not have an indexed palette")
        marker_index = int(frame.getpixel(marker))
        marker_rgb = frame_palette[marker_index * 3 : marker_index * 3 + 3]
        padded_palette = list(frame_palette)
        if len(padded_palette) < 768:
            padded_palette.extend([0] * (768 - len(padded_palette)))
        padded_palette[254 * 3 : 254 * 3 + 3] = marker_rgb
        padded_palette[255 * 3 : 255 * 3 + 3] = marker_rgb
        frame.putpalette(padded_palette)
        frame.putpixel(marker, 254 + (index % 2))


def verify_gif(path: str | Path, expected_frames: int, expected_size: tuple[int, int], expected_total_ms: int) -> dict[str, Any]:
    Image, ImageSequence = _require_pillow()
    source = Path(path).expanduser().resolve()
    with Image.open(source) as gif:
        durations = []
        disposals = []
        for frame in ImageSequence.Iterator(gif):
            durations.append(int(frame.info.get("duration", 0)))
            disposals.append(int(getattr(gif, "disposal_method", 0)))
        errors = []
        if gif.n_frames != expected_frames:
            errors.append(f"Expected {expected_frames} GIF frames, found {gif.n_frames}")
        if gif.size != expected_size:
            errors.append(f"Expected GIF size {expected_size}, found {gif.size}")
        if gif.info.get("loop") != 0:
            errors.append("GIF is not configured for infinite looping")
        if sum(durations) != expected_total_ms:
            errors.append(f"Expected {expected_total_ms} ms total duration, found {sum(durations)} ms")
        if any(disposal != 2 for disposal in disposals):
            errors.append(f"GIF disposal metadata is not mode 2: {disposals}")
        total_ms = sum(durations)
        return {
            "ok": not errors,
            "path": str(source),
            "frames": gif.n_frames,
            "width": gif.width,
            "height": gif.height,
            "duration_ms": total_ms,
            "average_fps": round(gif.n_frames * 1000 / total_ms, 6) if total_ms else None,
            "loop": gif.info.get("loop"),
            "durations_ms": durations,
            "disposal_modes": disposals,
            "file_size_bytes": source.stat().st_size,
            "errors": errors,
        }


def build_gif(
    frame_paths: Iterable[str | Path],
    output_path: str | Path,
    fps: float = 30.0,
    expected_frames: int | None = None,
) -> dict[str, Any]:
    Image, _ImageSequence = _require_pillow()
    paths = sorted((Path(path).expanduser().resolve() for path in frame_paths), key=natural_key)
    images = _load_rgb_frames(paths)
    if expected_frames is not None and len(images) != expected_frames:
        raise ValueError(f"Expected {expected_frames} input frames, found {len(images)}")
    palette = _shared_palette(images)
    gif_frames = [
        image.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG)
        for image in images
    ]
    _preserve_frame_boundaries(gif_frames)
    durations = gif_durations(len(gif_frames), fps)
    output = Path(output_path).expanduser().resolve().with_suffix(".gif")
    output.parent.mkdir(parents=True, exist_ok=True)
    gif_frames[0].save(
        output,
        save_all=True,
        append_images=gif_frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=False,
    )
    verification = verify_gif(output, len(gif_frames), images[0].size, sum(durations))
    return {
        **verification,
        "source_frames": [str(path) for path in paths],
        "requested_fps": fps,
        "palette": "shared-adaptive-256-mediancut",
        "dither": "floyd-steinberg",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames-dir", required=True, type=Path)
    parser.add_argument("--glob", default="*.png", dest="pattern")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--fps", default=30.0, type=float)
    parser.add_argument("--exclude-last", action="store_true", help="Exclude a rendered duplicated loop-closing frame")
    parser.add_argument("--expected-frames", type=int)
    args = parser.parse_args(sys.argv[1:])
    paths = sorted(args.frames_dir.expanduser().resolve().glob(args.pattern), key=natural_key)
    if args.exclude_last and paths:
        paths = paths[:-1]
    try:
        result = build_gif(paths, args.output, args.fps, args.expected_frames)
    except Exception as exc:
        result = {"ok": False, "errors": [str(exc)]}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
