#!/usr/bin/env python3
"""Create a tiled contact sheet from a video for cheap Live Photo QA."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def probe_duration(video: Path) -> float:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(video),
        ]
    )
    data = json.loads(result.stdout)
    duration = float(data["format"]["duration"])
    if duration <= 0:
        raise SystemExit(f"invalid duration for {video}: {duration}")
    return duration


def main() -> None:
    parser = argparse.ArgumentParser(description="Make a tiled frame strip for video QA.")
    parser.add_argument("video", type=Path, help="Input video path.")
    parser.add_argument("output", type=Path, help="Output JPG/PNG contact sheet path.")
    parser.add_argument("--frames", type=int, default=12, help="Number of frames to sample.")
    parser.add_argument("--cols", type=int, default=4, help="Tile columns.")
    parser.add_argument("--start", type=float, default=0.0, help="Start time in seconds.")
    parser.add_argument("--duration", type=float, help="Inspection window duration in seconds.")
    parser.add_argument("--thumb-width", type=int, default=320, help="Thumbnail width in pixels.")
    parser.add_argument("--padding", type=int, default=12, help="Padding between tiles.")
    parser.add_argument("--margin", type=int, default=12, help="Outer tile margin.")
    parser.add_argument("--color", default="white", help="Tile background color.")
    args = parser.parse_args()

    video = args.video.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not video.exists():
        raise SystemExit(f"missing video: {video}")
    if args.frames < 1:
        raise SystemExit("--frames must be >= 1")
    if args.cols < 1:
        raise SystemExit("--cols must be >= 1")

    source_duration = probe_duration(video)
    window = args.duration if args.duration is not None else max(0.1, source_duration - args.start)
    if window <= 0:
        raise SystemExit("--duration must be > 0")

    output.parent.mkdir(parents=True, exist_ok=True)
    rows = math.ceil(args.frames / args.cols)
    fps_expr = f"{args.frames}/{window:.6f}"
    vf = (
        f"fps={fps_expr},"
        f"scale={args.thumb_width}:-1:flags=lanczos,"
        f"tile={args.cols}x{rows}:padding={args.padding}:margin={args.margin}:color={args.color}"
    )

    cmd = ["ffmpeg", "-y"]
    if args.start > 0:
        cmd += ["-ss", f"{args.start:.6f}"]
    cmd += ["-t", f"{window:.6f}", "-i", str(video), "-vf", vf, "-frames:v", "1", str(output)]
    run(cmd)
    print(output)


if __name__ == "__main__":
    main()
