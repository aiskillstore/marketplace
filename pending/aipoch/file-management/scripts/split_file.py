#!/usr/bin/env python3
"""
Split a file into fixed-size parts.
"""

import argparse
import os
from pathlib import Path


def split_file(input_path, output_dir, part_size_bytes, prefix, pad_width, overwrite):
    input_path = Path(input_path)
    output_dir = Path(output_dir)

    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    part_index = 1

    with input_path.open("rb") as src:
        while True:
            chunk = src.read(part_size_bytes)
            if not chunk:
                break

            part_name = f"{prefix}.part{part_index:0{pad_width}d}"
            part_path = output_dir / part_name

            if part_path.exists() and not overwrite:
                raise FileExistsError(f"Part already exists: {part_path}")

            with part_path.open("wb") as out:
                out.write(chunk)

            part_index += 1


def main():
    parser = argparse.ArgumentParser(description="Split a file into fixed-size parts.")
    parser.add_argument("input", help="Path to the input file")
    parser.add_argument("--part-size-mb", type=int, default=100, help="Part size in MB")
    parser.add_argument("--output-dir", default=None, help="Directory for output parts")
    parser.add_argument("--prefix", default=None, help="Prefix for part filenames")
    parser.add_argument("--pad-width", type=int, default=3, help="Zero padding for part index")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing parts")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir) if args.output_dir else input_path.parent
    prefix = args.prefix if args.prefix else input_path.name

    part_size_bytes = args.part_size_mb * 1024 * 1024
    if part_size_bytes <= 0:
        raise ValueError("Part size must be greater than 0")

    split_file(input_path, output_dir, part_size_bytes, prefix, args.pad_width, args.overwrite)


if __name__ == "__main__":
    main()
