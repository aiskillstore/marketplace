#!/usr/bin/env python3
"""Create dense review frames, contact sheets, a storyboard, and a frame manifest."""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import subprocess
import sys
import tempfile
import zipfile
from fractions import Fraction
from pathlib import Path
from urllib.parse import urlparse


def run(command: list[str], *, capture: bool = False) -> str:
    result = subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    return result.stdout if capture else ""


def require_binary(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"Required binary not found: {name}")
    return path


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def fraction_to_float(value: str | None) -> float | None:
    if not value or value == "0/0":
        return None
    try:
        return float(Fraction(value))
    except (ValueError, ZeroDivisionError):
        return None


def format_timestamp(seconds: float) -> str:
    milliseconds = int(round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    return f"{minutes:02d}:{secs:02d}.{millis:03d}"


def probe_video(ffprobe: str, source: Path) -> dict:
    raw = run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=index,codec_type,width,height,avg_frame_rate,r_frame_rate",
            "-of",
            "json",
            str(source),
        ],
        capture=True,
    )
    data = json.loads(raw)
    video_stream = next(
        (stream for stream in data.get("streams", []) if stream.get("codec_type") == "video"),
        None,
    )
    if not video_stream:
        raise RuntimeError("No video stream found")
    duration = float(data.get("format", {}).get("duration") or 0)
    if duration <= 0:
        raise RuntimeError("Could not determine video duration")
    native_fps = fraction_to_float(video_stream.get("avg_frame_rate"))
    if not native_fps:
        native_fps = fraction_to_float(video_stream.get("r_frame_rate"))
    return {
        "duration_seconds": duration,
        "width": int(video_stream.get("width") or 0),
        "height": int(video_stream.get("height") or 0),
        "native_fps": native_fps,
    }


def download_source(yt_dlp: str, source: str, output_dir: Path) -> Path:
    template = output_dir / "source.%(ext)s"
    run(
        [
            yt_dlp,
            "--no-playlist",
            "-f",
            "bv*+ba/b",
            "--merge-output-format",
            "mp4",
            "-o",
            str(template),
            source,
        ]
    )
    candidates = sorted(
        path
        for path in output_dir.glob("source.*")
        if path.is_file() and path.suffix not in {".part", ".ytdl"}
    )
    if not candidates:
        raise RuntimeError("yt-dlp completed but no downloaded video was found")
    return candidates[0]


def make_contact_sheet(
    ffmpeg: str,
    frames_dir: Path,
    output: Path,
    start_number: int,
    cols: int,
    rows: int,
    cell_width: int,
) -> None:
    count = cols * rows
    video_filter = (
        f"scale={cell_width}:-2,"
        f"tile={cols}x{rows}:nb_frames={count}:padding=4:margin=4:color=black"
    )
    run(
        [
            ffmpeg,
            "-loglevel",
            "error",
            "-y",
            "-start_number",
            str(start_number),
            "-i",
            str(frames_dir / "frame_%04d.jpg"),
            "-vf",
            video_filter,
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(output),
        ]
    )


def evenly_spaced_indices(total: int, target: int) -> list[int]:
    if total <= target:
        return list(range(1, total + 1))
    if target <= 1:
        return [1]
    result = [round(i * (total - 1) / (target - 1)) + 1 for i in range(target)]
    return list(dict.fromkeys(result))


def build_storyboard(
    ffmpeg: str,
    frames_dir: Path,
    output: Path,
    indices: list[int],
    cell_width: int,
) -> None:
    cols = min(4, len(indices))
    rows = math.ceil(len(indices) / cols)
    with tempfile.TemporaryDirectory(prefix="storyboard-") as temp_name:
        temp_dir = Path(temp_name)
        for position, frame_number in enumerate(indices, start=1):
            shutil.copy2(
                frames_dir / f"frame_{frame_number:04d}.jpg",
                temp_dir / f"frame_{position:04d}.jpg",
            )
        make_contact_sheet(ffmpeg, temp_dir, output, 1, cols, rows, cell_width)


def write_manifest(
    output_dir: Path,
    source: str,
    source_file: Path,
    probe: dict,
    sample_fps: float,
    frame_count: int,
    storyboard_indices: list[int],
) -> None:
    frames = []
    for index in range(1, frame_count + 1):
        seconds = min((index - 1) / sample_fps, probe["duration_seconds"])
        frames.append(
            {
                "number": index,
                "file": f"frames/frame_{index:04d}.jpg",
                "timestamp_seconds": round(seconds, 3),
                "timestamp": format_timestamp(seconds),
            }
        )
    manifest = {
        "source": source,
        "local_source": str(source_file),
        **probe,
        "sample_fps": round(sample_fps, 6),
        "sample_interval_seconds": round(1 / sample_fps, 6),
        "frame_count": frame_count,
        "storyboard_frame_numbers": storyboard_indices,
        "frames": frames,
        "note": "Timestamps are sampling estimates; verify exact cuts against adjacent frames.",
    }
    (output_dir / "frame_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    with (output_dir / "frame_manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["number", "file", "timestamp_seconds", "timestamp"],
        )
        writer.writeheader()
        writer.writerows(frames)


def package_frames(frames_dir: Path, output: Path) -> None:
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        for frame in sorted(frames_dir.glob("frame_*.jpg")):
            archive.write(frame, arcname=frame.name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract dense review frames and storyboard artifacts from a video."
    )
    parser.add_argument("source", help="Local video path or HTTP(S) URL")
    parser.add_argument("--out-dir", required=True, help="New or empty output directory")
    parser.add_argument("--fps", type=float, default=2.0, help="Requested sampling fps (max 2)")
    parser.add_argument("--max-frames", type=int, default=120, help="Maximum review frames")
    parser.add_argument("--width", type=int, default=768, help="Extracted frame width")
    parser.add_argument("--story-frames", type=int, default=12, help="Storyboard frame count")
    parser.add_argument("--sheet-cols", type=int, default=4)
    parser.add_argument("--sheet-rows", type=int, default=3)
    parser.add_argument("--sheet-cell-width", type=int, default=280)
    parser.add_argument("--extract-audio", action="store_true", help="Also write audio.mp3")
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.fps <= 0:
        raise ValueError("--fps must be positive")
    if args.max_frames <= 0 or args.width <= 0 or args.story_frames <= 0:
        raise ValueError("frame and size options must be positive")
    if args.sheet_cols <= 0 or args.sheet_rows <= 0 or args.sheet_cell_width <= 0:
        raise ValueError("contact-sheet options must be positive")


def main() -> int:
    args = parse_args()
    validate_args(args)

    ffmpeg = require_binary("ffmpeg")
    ffprobe = require_binary("ffprobe")
    output_dir = Path(args.out_dir).expanduser().resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise RuntimeError(f"Output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    if is_url(args.source):
        source_file = download_source(require_binary("yt-dlp"), args.source, output_dir)
    else:
        source_file = Path(args.source).expanduser().resolve()
        if not source_file.is_file():
            raise FileNotFoundError(f"Video not found: {source_file}")

    probe = probe_video(ffprobe, source_file)
    requested_fps = min(args.fps, 2.0)
    budget_fps = args.max_frames / probe["duration_seconds"]
    sample_fps = min(requested_fps, budget_fps)
    sample_fps = max(sample_fps, min(1 / probe["duration_seconds"], requested_fps))

    frames_dir = output_dir / "frames"
    sheets_dir = output_dir / "contact_sheets"
    frames_dir.mkdir()
    sheets_dir.mkdir()

    run(
        [
            ffmpeg,
            "-loglevel",
            "error",
            "-i",
            str(source_file),
            "-vf",
            f"fps={sample_fps:.9f},scale={args.width}:-2",
            "-frames:v",
            str(args.max_frames),
            "-q:v",
            "2",
            str(frames_dir / "frame_%04d.jpg"),
        ]
    )
    frame_files = sorted(frames_dir.glob("frame_*.jpg"))
    if not frame_files:
        raise RuntimeError("No frames were extracted")
    frame_count = len(frame_files)

    page_size = args.sheet_cols * args.sheet_rows
    for page, start in enumerate(range(1, frame_count + 1, page_size), start=1):
        make_contact_sheet(
            ffmpeg,
            frames_dir,
            sheets_dir / f"sheet_{page:03d}.jpg",
            start,
            args.sheet_cols,
            args.sheet_rows,
            args.sheet_cell_width,
        )

    storyboard_indices = evenly_spaced_indices(frame_count, min(args.story_frames, frame_count))
    build_storyboard(
        ffmpeg,
        frames_dir,
        output_dir / "storyboard.jpg",
        storyboard_indices,
        args.sheet_cell_width,
    )
    write_manifest(
        output_dir,
        args.source,
        source_file,
        probe,
        sample_fps,
        frame_count,
        storyboard_indices,
    )
    package_frames(frames_dir, output_dir / "frames.zip")

    if args.extract_audio:
        try:
            run(
                [
                    ffmpeg,
                    "-loglevel",
                    "error",
                    "-i",
                    str(source_file),
                    "-vn",
                    "-ac",
                    "1",
                    "-ar",
                    "16000",
                    "-b:a",
                    "64k",
                    str(output_dir / "audio.mp3"),
                ]
            )
        except subprocess.CalledProcessError:
            print("Warning: audio extraction failed; continuing with frames only.", file=sys.stderr)

    summary = {
        "output_dir": str(output_dir),
        "duration_seconds": round(probe["duration_seconds"], 3),
        "sample_fps": round(sample_fps, 6),
        "frame_count": frame_count,
        "storyboard": str(output_dir / "storyboard.jpg"),
        "archive": str(output_dir / "frames.zip"),
        "manifest": str(output_dir / "frame_manifest.json"),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError, FileNotFoundError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
