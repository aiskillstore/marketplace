#!/usr/bin/env python3
"""
Merge split parts into a single file.
"""

import argparse
from pathlib import Path


def collect_parts(inputs, pattern):
    if len(inputs) == 1 and Path(inputs[0]).is_dir():
        parts = sorted(Path(inputs[0]).glob(pattern))
        if not parts:
            raise FileNotFoundError(f"No parts found in {inputs[0]} matching {pattern}")
        return parts

    parts = [Path(p) for p in inputs]
    for part in parts:
        if not part.is_file():
            raise FileNotFoundError(f"Part not found: {part}")
    return parts


def merge_parts(parts, output_path, overwrite):
    output_path = Path(output_path)
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Output already exists: {output_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as out:
        for part in parts:
            with part.open("rb") as src:
                while True:
                    chunk = src.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)


def main():
    parser = argparse.ArgumentParser(description="Merge split parts into a single file.")
    parser.add_argument("inputs", nargs="+", help="Part files or a directory containing parts")
    parser.add_argument("--pattern", default="*.part*", help="Glob pattern when input is a directory")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output file")
    args = parser.parse_args()

    parts = collect_parts(args.inputs, args.pattern)
    merge_parts(parts, args.output, args.overwrite)


if __name__ == "__main__":
    main()
