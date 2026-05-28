#!/usr/bin/env python3
"""
Run end-to-end poster pipeline with timestamped outputs.
"""

import argparse
import datetime
import json
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(command, cwd):
    result = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.stdout:
        print(result.stdout.rstrip())
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr.rstrip(), file=sys.stderr)
        raise SystemExit(result.returncode)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Run poster pipeline with timestamped outputs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_poster_pipeline.py paper.pdf
  python scripts/run_poster_pipeline.py paper.pdf --template tikzposter
  python scripts/run_poster_pipeline.py paper.pdf --output-root outputs
  python scripts/run_poster_pipeline.py paper.pdf --run-id 20260208_165233
  python scripts/run_poster_pipeline.py paper.pdf --figures-config figures_config.json
  python scripts/run_poster_pipeline.py paper.pdf --html-mode render
  python scripts/run_poster_pipeline.py paper.pdf --html-only
        """
    )

    parser.add_argument("pdf_file", help="Input PDF file")
    parser.add_argument(
        "--template",
        choices=["beamerposter", "tikzposter", "baposter"],
        default="beamerposter",
        help="Template type (default: beamerposter)",
    )
    parser.add_argument(
        "--package",
        choices=["beamerposter", "tikzposter", "baposter"],
        help="LaTeX package for content structuring (default: same as template)",
    )
    parser.add_argument(
        "--output-root",
        default="outputs",
        help="Root output directory (default: outputs)",
    )
    parser.add_argument(
        "--run-id",
        help="Run identifier (default: YYYYMMDD_HHMMSS)",
    )
    parser.add_argument(
        "--skip-images",
        action="store_true",
        help="Skip PDF-to-image conversion",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="DPI for PDF-to-image conversion (default: 300)",
    )
    parser.add_argument(
        "--figures-config",
        help="Use a figures_config.json file for figure generation",
    )
    parser.add_argument(
        "--no-html",
        action="store_true",
        help="Skip HTML conversion (PDF only)",
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="Generate HTML only (skip PDF conversion; uses pandoc)",
    )
    parser.add_argument(
        "--html-mode",
        choices=["render", "pandoc"],
        default="render",
        help="HTML conversion mode (default: render via pdf2htmlEX)",
    )

    args = parser.parse_args()

    if args.no_html and args.html_only:
        print("Error: --no-html and --html-only cannot be used together")
        sys.exit(1)

    pdf_path = Path(args.pdf_file).resolve()
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)

    run_id = args.run_id or datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_root = Path(args.output_root)
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    figures_dir = run_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    images_dir = run_dir / "paper_images"

    scripts_dir = Path(__file__).resolve().parent
    repo_root = scripts_dir.parent
    python = sys.executable
    package = args.package or args.template

    run_command(
        [
            python,
            "-X",
            "utf8",
            str(scripts_dir / "extract_metadata.py"),
            str(pdf_path),
            str(run_dir / "metadata.json"),
        ],
        cwd=repo_root,
    )

    if not args.skip_images:
        run_command(
            [
                python,
                "-X",
                "utf8",
                str(scripts_dir / "convert_pdf_to_images.py"),
                str(pdf_path),
                str(images_dir),
                "--dpi",
                str(args.dpi),
            ],
            cwd=repo_root,
        )

    run_command(
        [
            python,
            "-X",
            "utf8",
            str(scripts_dir / "structure_content.py"),
            str(pdf_path),
            "--json",
            str(run_dir / "poster_content.json"),
            "--latex",
            str(run_dir / "content.tex"),
            "--package",
            package,
        ],
        cwd=repo_root,
    )

    template_map = {
        "beamerposter": repo_root / "assets" / "templates" / "beamerposter-template.tex",
        "tikzposter": repo_root / "assets" / "templates" / "tikzposter-template.tex",
        "baposter": repo_root / "assets" / "templates" / "baposter-template.tex",
    }
    template_path = template_map.get(args.template)
    if template_path is None or not template_path.exists():
        print(f"Error: Template not found: {template_path}")
        sys.exit(1)

    poster_tex = run_dir / "poster.tex"
    shutil.copyfile(template_path, poster_tex)

    figures_config_path = run_dir / "figures_config.json"
    if args.figures_config is not None:
        source_config = Path(args.figures_config)
        if not source_config.exists():
            print(f"Error: Figures config not found: {source_config}")
            sys.exit(1)
        shutil.copyfile(source_config, figures_config_path)
        run_command(
            [
                python,
                "-X",
                "utf8",
                str(scripts_dir / "generate_figures.py"),
                "config",
                str(figures_config_path),
                "--output-dir",
                str(figures_dir),
            ],
            cwd=repo_root,
        )
    else:
        run_command(
            [
                python,
                "-X",
                "utf8",
                str(scripts_dir / "generate_figures.py"),
                "mechanism",
                "Cldn7 loss promotes neutrophil recruitment and immunosuppression",
                "mechanism.png",
                "--output-dir",
                str(figures_dir),
            ],
            cwd=repo_root,
        )
        run_command(
            [
                python,
                "-X",
                "utf8",
                str(scripts_dir / "generate_figures.py"),
                "flowchart",
                "Sample collection;Neutrophil profiling;Metabolic assays;T cell analysis;Therapy response",
                "process.png",
                "--output-dir",
                str(figures_dir),
            ],
            cwd=repo_root,
        )
        data = json.dumps({"Baseline": [1.0], "Cldn7-low": [1.3], "Rescue": [1.1]})
        run_command(
            [
                python,
                "-X",
                "utf8",
                str(scripts_dir / "generate_figures.py"),
                "comparison",
                data,
                "comparison.png",
                "--output-dir",
                str(figures_dir),
            ],
            cwd=repo_root,
        )

        config = {
            "figures": [
                {
                    "path": str(figures_dir / "mechanism.png"),
                    "caption": "Mechanism overview (placeholder)",
                    "position": "methods",
                    "label": "mechanism",
                },
                {
                    "path": str(figures_dir / "process.png"),
                    "caption": "Workflow summary (placeholder)",
                    "position": "results",
                    "label": "workflow",
                },
                {
                    "path": str(figures_dir / "comparison.png"),
                    "caption": "Comparison chart (placeholder)",
                    "position": "results-secondary",
                    "label": "comparison",
                },
            ]
        }
        with open(figures_config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    run_command(
        [
            python,
            "-X",
            "utf8",
            str(scripts_dir / "insert_figures.py"),
            str(poster_tex),
            "--config",
            str(figures_config_path),
        ],
        cwd=repo_root,
    )

    convert_cmd = [
        python,
        "-X",
        "utf8",
        str(scripts_dir / "convert_poster.py"),
        str(poster_tex),
        "-o",
        str(run_dir),
    ]
    if args.no_html:
        convert_cmd.append("--no-html")
    elif args.html_only:
        convert_cmd.append("--html-only")
    else:
        convert_cmd.extend(["--html-mode", args.html_mode])

    run_command(convert_cmd, cwd=repo_root)

    print(f"Outputs saved to: {run_dir}")


if __name__ == "__main__":
    main()
