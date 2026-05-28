#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Text formatting tool - format preserving version
Clean blank lines and spaces, retaining Word document format and content"""

import argparse
import sys
from pathlib import Path

from text_formatter import (
    TextFormatter,
    FormatOptions,
    LineEnding,
    IndentType,
    clean_docx_preserve_format,
)


def parse_args():
    """Parse command line parameters"""
    parser = argparse.ArgumentParser(
        description="Text formatting tool - clean up blank lines and spaces and retain document formatting"
    )

    parser.add_argument("--input", "-i", required=True, help="input file path")

    parser.add_argument("--output", "-o", help="Output file path (default: automatically generated)")

    parser.add_argument(
        "--line-ending",
        "-l",
        choices=["unix", "windows", "mac"],
        default="unix",
        help="newline type (default: unix)",
    )

    parser.add_argument(
        "--preview", "-p", action="store_true", help="Preview mode, no file generated"
    )

    parser.add_argument(
        "--docx-font",
        "-f",
        default="Times New Roman",
        help="Word output font (default: Times New Roman)",
    )

    parser.add_argument(
        "--docx-size",
        type=int,
        default=12,
        help="Word output font size (default: 12)",
    )

    parser.add_argument(
        "--no-clean-empty",
        action="store_true",
        help="Do not clear empty lines",
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Show details")

    parser.add_argument("--stats", "-S", action="store_true", help="Show statistics")

    return parser.parse_args()


def is_docx_file(path: str) -> bool:
    """Check if it is a Word document"""
    return Path(path).suffix.lower() in [".docx", ".doc"]


def main():
    """main function"""
    args = parse_args()

    try:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"mistake: File does not exist: {args.input}")
            return 1

        is_docx = is_docx_file(str(input_path))

        if is_docx:
            print(f"detected Word document: {input_path.name}")
            print(f"font: {args.docx_font} {args.docx_size}pt")

            if args.preview:
                from text_formatter import extract_text_from_docx

                text, para_styles = extract_text_from_docx(str(input_path))
                print("=" * 60)
                print("Preview results (first 50 rows):")
                print("=" * 60)
                lines = text.split("\n")
                for line in lines[:50]:
                    print(line)
                print("=" * 60)
                return 0

            remove_empty = not args.no_clean_empty
            output_file = clean_docx_preserve_format(
                str(input_path),
                args.output,
                font_name=args.docx_font,
                font_size=args.docx_size,
                remove_empty_lines=remove_empty,
            )

            print(f"Processing completed!")
            print(f"output file: {output_file}")
            return 0

        ending_map = {
            "unix": LineEnding.UNIX,
            "windows": LineEnding.WINDOWS,
            "mac": LineEnding.MAC,
        }

        options = FormatOptions(
            remove_empty_lines=not args.no_clean_empty,
            max_empty_lines=2,
            trim_line_end_spaces=True,
            line_ending=ending_map.get(args.line_ending, LineEnding.UNIX),
        )

        formatter = TextFormatter(options)

        original_text = input_path.read_text(encoding="utf-8")

        if args.verbose:
            print(f"input file: {input_path.name}")
            print(f"file size: {len(original_text)} character")
            print(f"English: {len(original_text.splitlines())}")
            print("-" * 50)

        if args.preview:
            print("=" * 60)
            print("Preview results:")
            print("=" * 60)
            formatted = formatter.preview(original_text)
            print(formatted)
            print("=" * 60)
            return 0

        output_path = args.output
        if output_path is None:
            output_path = str(
                input_path.parent / f"{input_path.stem}_clean{input_path.suffix}"
            )

        output_file = formatter.format_file(str(input_path), output_path)

        formatted_text = Path(output_file).read_text(encoding="utf-8")
        stats = {
            "original_lines": len(original_text.splitlines()),
            "formatted_lines": len(formatted_text.splitlines()),
            "lines_removed": len(original_text.splitlines())
            - len(formatted_text.splitlines()),
        }

        if args.stats or args.verbose:
            print(f"Processing completed!")
            print(f"output file: {output_file}")
            print("-" * 50)
            print(f"Original number of rows: {stats['original_lines']}")
            print(f"Number of rows after sorting: {stats['formatted_lines']}")
            print(f"Remove rows: {stats['lines_removed']}")
        else:
            print(f"Finished: {output_file}")

        return 0

    except ImportError as e:
        print(f"mistake: {e}")
        print("Please install the required dependencies: pip install python-docx")
        return 1

    except Exception as e:
        print(f"mistake: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
