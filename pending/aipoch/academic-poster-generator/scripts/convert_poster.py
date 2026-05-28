#!/usr/bin/env python3
"""
LaTeX Poster Converter
Automatically converts .tex files to PDF and HTML formats.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


class PosterConverter:
    def __init__(
        self,
        tex_file,
        output_dir=None,
        latex_engine="pdflatex",
        create_html=True,
        skip_pdf=False,
        html_mode="render",
    ):
        self.tex_file = Path(tex_file)
        self.output_dir = Path(output_dir) if output_dir else self.tex_file.parent
        self.latex_engine = latex_engine
        self.create_html = create_html
        self.skip_pdf = skip_pdf
        self.html_mode = html_mode
        self.base_name = self.tex_file.stem

    def convert_to_pdf(self):
        """Convert LaTeX to PDF using specified LaTeX engine."""
        print(f"Converting {self.tex_file.name} to PDF using {self.latex_engine}...")
        
        try:
            # Run LaTeX engine multiple times to resolve references
            for i in range(3):
                cmd = [
                    self.latex_engine,
                    "-interaction=nonstopmode",
                    "-output-directory", str(self.output_dir),
                    str(self.tex_file)
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"LaTeX compilation failed (attempt {i+1}):")
                    print(result.stderr)
                    return False
            
            pdf_path = self.output_dir / f"{self.base_name}.pdf"
            if pdf_path.exists():
                print(f"PDF created: {pdf_path}")
                return True
            else:
                print(f"PDF not found after compilation")
                return False
                
        except FileNotFoundError:
            print(f"Error: {self.latex_engine} not found. Please install LaTeX.")
            return False
        except Exception as e:
            print(f"Error converting to PDF: {e}")
            return False

    def convert_to_html(self):
        """Convert LaTeX to HTML using pdf2htmlEX or pandoc."""
        if not self.create_html:
            return True

        if self.html_mode == "render":
            return self.convert_pdf_to_html()

        return self.convert_tex_to_html()

    def convert_pdf_to_html(self):
        """Convert compiled PDF to HTML using pdf2htmlEX."""
        pdf_path = self.output_dir / f"{self.base_name}.pdf"
        if not pdf_path.exists():
            print("Error: PDF not found for HTML rendering. Compile PDF first or use --html-mode pandoc.")
            return False

        print(f"Converting {pdf_path.name} to HTML using pdf2htmlEX...")

        try:
            html_path = self.output_dir / f"{self.base_name}.html"
            cmd = [
                "pdf2htmlEX",
                "--dest-dir", str(self.output_dir),
                str(pdf_path),
                str(html_path.name),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print("pdf2htmlEX conversion failed:")
                print(result.stderr)
                return False

            if html_path.exists():
                print(f"HTML created: {html_path}")
                return True
            print("HTML not found after conversion")
            return False

        except FileNotFoundError:
            print("Error: pdf2htmlEX not found. Please install pdf2htmlEX.")
            return False
        except Exception as e:
            print(f"Error converting PDF to HTML: {e}")
            return False

    def convert_tex_to_html(self):
        """Convert LaTeX to HTML using pandoc (non-rendered)."""
        print(f"Converting {self.tex_file.name} to HTML using pandoc...")

        try:
            html_path = self.output_dir / f"{self.base_name}.html"
            cmd = [
                "pandoc",
                "-s",
                str(self.tex_file),
                "-o", str(html_path),
                "--mathjax",
                "--standalone",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print("Pandoc conversion failed:")
                print(result.stderr)
                return False

            if html_path.exists():
                print(f"HTML created: {html_path}")
                return True
            print("HTML not found after conversion")
            return False

        except FileNotFoundError:
            print("Error: pandoc not found. Please install pandoc.")
            print("Install from: https://pandoc.org/installing.html")
            return False
        except Exception as e:
            print(f"Error converting to HTML: {e}")
            return False

    def clean_auxiliary_files(self):
        """Clean up auxiliary LaTeX files."""
        print("Cleaning auxiliary files...")
        extensions = ['.aux', '.log', '.out', '.toc', '.bbl', '.blg', '.fls', '.fdb_latexmk']
        
        for ext in extensions:
            file_path = self.output_dir / f"{self.base_name}{ext}"
            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"Removed: {file_path.name}")
                except Exception as e:
                    print(f"Could not remove {file_path.name}: {e}")

    def convert(self, clean=True):
        """Perform full conversion process."""
        if not self.tex_file.exists():
            print(f"Error: File not found: {self.tex_file}")
            return False

        print(f"\n{'='*60}")
        print(f"Converting: {self.tex_file.name}")
        print(f"Output directory: {self.output_dir}")
        print(f"{'='*60}\n")

        success = True

        # Convert to PDF
        if not self.skip_pdf:
            if not self.convert_to_pdf():
                success = False
        elif self.html_mode == "render" and self.create_html:
            print("Error: --html-mode render requires PDF generation.")
            return False

        # Convert to HTML
        if success and self.create_html:
            if not self.convert_to_html():
                if self.skip_pdf:
                    success = False
                else:
                    print("Warning: HTML conversion failed, but PDF was created successfully")

        # Clean auxiliary files
        if clean and success:
            self.clean_auxiliary_files()

        if success:
            print(f"\n[*] Conversion completed successfully!")
            if not self.skip_pdf:
                print(f"  PDF: {self.output_dir / f'{self.base_name}.pdf'}")
            if self.create_html:
                print(f"  HTML: {self.output_dir / f'{self.base_name}.html'}")
        else:
            print(f"\n[X] Conversion failed")

        return success


def batch_convert(
    tex_files,
    output_dir=None,
    latex_engine="pdflatex",
    create_html=True,
    skip_pdf=False,
    html_mode="render",
):
    """Convert multiple .tex files."""
    files = []
    
    for pattern in tex_files:
        path = Path(pattern)
        if path.exists() and path.is_file():
            files.append(path)
        else:
            # Glob pattern
            matched = list(Path(path.parent).glob(path.name))
            files.extend(matched)
    
    if not files:
        print("No .tex files found")
        return False

    print(f"Found {len(files)} file(s) to convert\n")

    results = []
    for tex_file in files:
        converter = PosterConverter(
            tex_file,
            output_dir,
            latex_engine,
            create_html,
            skip_pdf,
            html_mode,
        )
        result = converter.convert()
        results.append((tex_file.name, result))
        print()

    # Summary
    print(f"\n{'='*60}")
    print("Batch Conversion Summary:")
    print(f"{'='*60}")
    success_count = sum(1 for _, success in results if success)
    for name, success in results:
        status = "[*]" if success else "[X]"
        print(f"{status} {name}")
    print(f"\nTotal: {success_count}/{len(results)} successful")

    return success_count > 0


def main():
    parser = argparse.ArgumentParser(
        description="Convert LaTeX poster files to PDF and HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single file conversion
  python scripts/convert_poster.py poster.tex
  
  # Custom output directory
  python scripts/convert_poster.py poster.tex -o output/
  
  # Use xelatex for better font support
  python scripts/convert_poster.py poster.tex -e xelatex
  
  # PDF only (no HTML)
  python scripts/convert_poster.py poster.tex --no-html

  # Rendered HTML (PDF -> HTML)
  python scripts/convert_poster.py poster.tex --html-mode render

  # HTML only (skip PDF, non-rendered)
  python scripts/convert_poster.py poster.tex --html-only
  
  # Batch convert all .tex files
  python scripts/convert_poster.py *.tex
  
  # Batch convert with custom settings
  python scripts/convert_poster.py "posters/*.tex" -e lualatex -o build/
        """
    )

    parser.add_argument(
        "tex_files",
        nargs="+",
        help="LaTeX file(s) to convert"
    )

    parser.add_argument(
        "-o", "--output-dir",
        help="Output directory (default: same as input file)"
    )

    parser.add_argument(
        "-e", "--latex-engine",
        choices=["pdflatex", "xelatex", "lualatex"],
        default="pdflatex",
        help="LaTeX engine to use (default: pdflatex)"
    )

    parser.add_argument(
        "--no-html",
        action="store_true",
        help="Skip HTML conversion, only generate PDF"
    )

    parser.add_argument(
        "--html-only",
        action="store_true",
        help="Generate HTML only (skip PDF conversion, uses pandoc)"
    )

    parser.add_argument(
        "--html-mode",
        choices=["render", "pandoc"],
        default="render",
        help="HTML conversion mode (default: render via pdf2htmlEX)"
    )

    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Keep auxiliary LaTeX files (.aux, .log, etc.)"
    )

    args = parser.parse_args()

    if args.html_only and args.no_html:
        print("Error: --html-only and --no-html cannot be used together")
        sys.exit(1)

    if args.html_only and args.html_mode == "render":
        print("Error: --html-only cannot be used with --html-mode render")
        sys.exit(1)

    create_html = not args.no_html
    html_mode = args.html_mode
    if args.html_only:
        create_html = True
        html_mode = "pandoc"

    # Check if batch conversion
    if len(args.tex_files) > 1:
        success = batch_convert(
            args.tex_files,
            args.output_dir,
            args.latex_engine,
            create_html,
            args.html_only,
            html_mode
        )
        sys.exit(0 if success else 1)
    else:
        # Single file conversion
        converter = PosterConverter(
            args.tex_files[0],
            args.output_dir,
            args.latex_engine,
            create_html,
            args.html_only,
            html_mode
        )
        success = converter.convert(clean=not args.no_clean)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
