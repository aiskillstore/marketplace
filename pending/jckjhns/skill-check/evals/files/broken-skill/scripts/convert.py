"""Convert CSV to other formats."""

import argparse
import csv
import json
import sys


def convert(filepath, out_path, fmt):
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if fmt == "json":
        with open(out_path, 'w') as f:
            json.dump(rows, f, indent=2)
    else:
        print(f"Unsupported format: {fmt}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Convert CSV files")
    parser.add_argument("--file", required=True, help="Input CSV path")
    parser.add_argument("--out", required=True, help="Output file path")
    parser.add_argument("--fmt", default="json", help="Output format")
    args = parser.parse_args()

    convert(args.file, args.out, args.fmt)


if __name__ == "__main__":
    main()
