#!/usr/bin/env python3
"""Try Yingse on a credited sample photograph without a network request."""
import argparse
from pathlib import Path
import subprocess
import sys

CASES = {
    "portrait": ("portrait.png", "soft-portrait", "0.8"),
    "still-life": ("still-life.png", "warm-film", "0.8"),
    "twilight": ("twilight.jpg", "cinematic-teal-orange", "0.8"),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--example", choices=CASES, default="portrait")
    parser.add_argument("--output-dir", required=True, help="New delivery folder; an existing folder/ZIP is never overwritten.")
    args = parser.parse_args()
    scripts = Path(__file__).resolve().parent
    filename, look, strength = CASES[args.example]
    source = scripts.parent / "examples" / "inputs" / filename
    if not source.is_file():
        raise SystemExit("Bundled sample is missing. Install the complete generate-lut folder, including examples/.")
    completed = subprocess.run([sys.executable, str(scripts / "create_lut_package.py"),
        "--look", look, "--strength", strength, "--input", str(source),
        "--description", f"Yingse reproducible demo: {args.example}; source credited in examples/SOURCES.md",
        "--output-dir", args.output_dir])
    raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
