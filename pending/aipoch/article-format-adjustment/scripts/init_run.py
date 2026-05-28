#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Academic paper formatting tool
Adjust the paper format according to the journal or school requirements"""

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Dict, Optional

from format_converter import FormatConverter
from format_adjuster import FormatAdjuster, FormatConfig
from template_downloader import TemplateDownloader


class FormatAdjusterApp:
    """Formatting application"""

    def __init__(self):
        self.converter = FormatConverter()
        self.downloader = TemplateDownloader()

    def run(
        self,
        input_path: str,
        output_path: str = None,
        config: FormatConfig = None,
        journal: str = None,
        config_path: str = None,
    ) -> Dict:
        """Run the formatting process"""
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"Input file does not exist: {input_path}")

        input_format = self.converter.get_format(input_path)
        output_format = input_format

        if output_path:
            output_file = Path(output_path)
            output_format = self.converter.get_format(output_path)
        else:
            output_file = (
                input_file.parent / f"{input_file.stem}_formatted{input_file.suffix}"
            )

        adjuster = FormatAdjuster(config=config)

        if journal:
            try:
                adjuster.load_builtin_format(journal)
                print(f"Journal format loaded: {journal}")
            except ValueError:
                template_result = self.downloader.download_template(journal)
                if template_result["status"] == "success":
                    if template_result.get("path"):
                        adjuster.load_config(template_result["path"])
                else:
                    print(f"Unable to automatically download journal template，Please use --config Parameter specified configuration file")

        if config_path:
            adjuster.load_config(config_path)
            print(f"Configuration file loaded: {config_path}")

        print(f"Processing: {input_file.name}")
        print(f"English: {input_format.upper()}")
        print(f"Output format: {output_format.upper()}")
        print("-" * 50)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            md_path = temp_path / "intermediate.md"

            if input_format != "md":
                md_text = self.converter.to_markdown(input_path)
                md_path.write_text(md_text, encoding="utf-8")
                print(f"converted to Markdown: {md_path}")
            else:
                md_text = input_file.read_text(encoding="utf-8")

            print("Applying format...")
            formatted_text = adjuster.apply_format(md_text)

            print("Verifying format...")
            validation = adjuster.validate_format(formatted_text)
            print(f"Verification results: {'pass' if validation['is_valid'] else 'There is a warning'}")

            if output_format != "md":
                final_path = self.converter.from_markdown(
                    formatted_text, str(output_file), output_format
                )
            else:
                output_file.write_text(formatted_text, encoding="utf-8")
                final_path = output_file

            report = {
                "input": str(input_file),
                "output": str(final_path),
                "input_format": input_format,
                "output_format": output_format,
                "format_config": adjuster.generate_format_report(),
                "validation": validation,
            }

            return report


def load_config(config_path: str) -> Dict:
    """Load configuration file"""
    path = Path(config_path)
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    elif path.suffix.lower() in [".yaml", ".yml"]:
        import yaml

        return yaml.safe_load(path.read_text(encoding="utf-8"))
    else:
        raise ValueError(f"Unsupported configuration file format: {path.suffix}")


def main():
    """main function"""
    parser = argparse.ArgumentParser(
        description="Academic paper formatting tool - format your paper according to journal or school requirements"
    )

    parser.add_argument("--input", "-i", help="input file path")

    parser.add_argument(
        "--output", "-o", help="Output file path (default: original file directory to generate new file)"
    )

    parser.add_argument("--config", "-c", help="Format configuration file path (JSON/YAML)")

    parser.add_argument("--journal", "-j", help="Journal name (use built-in or downloadable template)")

    parser.add_argument("--download-template", "-d", help="Download journal template")

    parser.add_argument("--list-formats", action="store_true", help="List built-in journal formats")

    parser.add_argument("--format", choices=["docx", "md", "tex"], help="Specify output format")

    parser.add_argument("--verbose", "-v", action="store_true", help="Show details")

    args = parser.parse_args()

    try:
        app = FormatAdjusterApp()

        if args.list_formats:
            formats = app.downloader.list_builtin_formats()
            print("Built-in journal formats:")
            for fmt in formats:
                print(f"  - {fmt['name']} ({fmt['key']})")
            return 0

        if args.download_template:
            print(f"Downloading journal template: {args.download_template}")
            result = app.downloader.download_template(args.download_template)
            print(f"Download results: {result['status']}")
            if result.get("path"):
                print(f"template path: {result['path']}")
            else:
                print(
                    f"hint: {result.get('suggestions', ['Unable to download, please obtain the template manually'])}"
                )
            return 0

        config = None
        if args.config:
            config_data = load_config(args.config)
            config = FormatConfig.from_dict(config_data)
            print(f"Configuration loaded: {args.config}")

        output_path = args.output
        if output_path and args.format:
            output_path = str(Path(output_path).with_suffix(f".{args.format}"))

        report = app.run(
            input_path=args.input,
            output_path=output_path,
            config=config,
            journal=args.journal,
            config_path=args.config,
        )

        print("-" * 50)
        print(f"Processing completed!")
        print(f"output file: {report['output']}")
        print(f"Format configuration: {report['format_config']['name']}")
        print(f"English: {'pass' if report['validation']['is_valid'] else 'There is a warning'}")

        if args.verbose and report["validation"]["issues"]:
            print("Validation warning:")
            for issue in report["validation"]["issues"]:
                print(f"  - {issue}")

        return 0

    except Exception as e:
        print(f"mistake: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
