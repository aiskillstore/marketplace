#!/usr/bin/env python3
"""
Poster Quality Checker
Automatically validates poster PDF for printing requirements.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


class PosterQualityChecker:
    """Check quality of poster PDF files."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.issues = []
        self.warnings = []
    
    def _run_command(self, command: list) -> tuple:
        """Run command and return output and return code."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout, result.returncode
        except subprocess.TimeoutExpired:
            return "", -1
        except FileNotFoundError:
            return "", -2
        except Exception as e:
            return "", -3
    
    def check_file_exists(self) -> bool:
        """Check if PDF file exists."""
        if not self.pdf_path.exists():
            self.issues.append(f"File not found: {self.pdf_path}")
            return False
        return True
    
    def check_page_size(self):
        """Check PDF page dimensions."""
        stdout, returncode = self._run_command(['pdfinfo', str(self.pdf_path)])
        
        if returncode != 0:
            self.warnings.append("Could not check page size (pdfinfo not installed)")
            return
        
        # Parse page size
        for line in stdout.split('\n'):
            if 'Page size:' in line:
                print(f"✓ {line.strip()}")
                
                # Extract dimensions
                parts = line.split()
                if len(parts) >= 5:
                    width = parts[2]
                    height = parts[4]
                    
                    # Check common poster sizes
                    if width == '2384' and height == '3370':
                        print("  ✓ Detected: A0 Portrait")
                    elif width == '3370' and height == '2384':
                        print("  ✓ Detected: A0 Landscape")
                    elif width == '1684' and height == '2384':
                        print("  ✓ Detected: A1 Portrait")
                    elif width == '2592' and height == '3456':
                        print("  ✓ Detected: 36×48 inches Portrait")
                    else:
                        self.warnings.append(f"Non-standard size: {width}×{height}")
                break
    
    def check_page_count(self):
        """Check that poster is single page."""
        stdout, returncode = self._run_command(['pdfinfo', str(self.pdf_path)])
        
        if returncode != 0:
            self.warnings.append("Could not check page count")
            return
        
        for line in stdout.split('\n'):
            if 'Pages:' in line:
                parts = line.split()
                if len(parts) >= 2:
                    page_count = int(parts[1])
                    if page_count == 1:
                        print("✓ Single page (correct for poster)")
                    else:
                        self.issues.append(f"Multiple pages detected: {page_count} (should be 1)")
                break
    
    def check_file_size(self):
        """Check PDF file size."""
        file_size = self.pdf_path.stat().st_size
        size_mb = file_size / (1024 * 1024)
        
        print(f"✓ File size: {size_mb:.2f} MB")
        
        if file_size > 52428800:  # 50 MB
            self.warnings.append(f"Large file (>50MB) - may need compression for email")
        elif file_size < 1048576:  # 1 MB
            self.warnings.append("Small file - check image quality")
    
    def check_font_embedding(self):
        """Check that fonts are embedded."""
        stdout, returncode = self._run_command(['pdffonts', str(self.pdf_path)])
        
        if returncode != 0:
            self.warnings.append("Could not check fonts (pdffonts not installed)")
            return
        
        print("Checking font embedding...")
        lines = stdout.split('\n')
        
        if len(lines) > 3:
            print("  Fonts:")
            for line in lines[2:22]:  # Show first 20 fonts
                print(f"    {line}")
        
        # Check for non-embedded fonts
        non_embedded = []
        for line in lines[2:]:
            if 'no' in line.split():
                non_embedded.append(line)
        
        if non_embedded:
            self.issues.append(f"{len(non_embedded)} fonts are NOT embedded (printing may fail)")
            print("  ✗ Some fonts are not embedded")
        else:
            print("  ✓ All fonts appear to be embedded")
    
    def check_images(self):
        """Check image quality."""
        stdout, returncode = self._run_command(['pdfimages', '-list', str(self.pdf_path)])
        
        if returncode != 0:
            self.warnings.append("Could not check images (pdfimages not installed)")
            return
        
        lines = stdout.split('\n')
        if len(lines) > 2:
            image_count = len(lines) - 2
            print(f"✓ Found {image_count} image(s)")
            
            if image_count > 0:
                print("  Image details:")
                for line in lines[1:12]:  # Show first 10 images
                    print(f"    {line}")
                
                self.warnings.append("Verify images are at least 300 DPI for printing")
        else:
            self.warnings.append("No images found")
    
    def generate_manual_checklist(self):
        """Generate manual checklist items."""
        print("\n" + "="*60)
        print("MANUAL VISUAL INSPECTION REQUIRED")
        print("="*60)
        
        checklist = [
            ("Layout and Spacing", [
                "Content fills entire page (no large white margins)",
                "Consistent spacing between columns",
                "Consistent spacing between blocks/sections",
                "All elements aligned properly",
                "No overlapping text or figures"
            ]),
            ("Typography", [
                "Title visible and large (72pt+)",
                "Section headers readable (48-72pt)",
                "Body text readable (24-36pt minimum)",
                "No text cutoff or running off edges",
                "Consistent font usage"
            ]),
            ("Visual Elements", [
                "All figures display correctly",
                "No pixelated or blurry images",
                "Figure captions present and readable",
                "Colors render as expected",
                "QR codes visible and scannable"
            ]),
            ("Content", [
                "All sections present (Intro, Methods, Results, Conclusions)",
                "References included",
                "Contact information visible",
                "No placeholder text (Lorem ipsum, TODO, etc.)"
            ])
        ]
        
        for category, items in checklist:
            print(f"\n{category}:")
            for item in items:
                print(f"  [ ] {item}")
        
        print("\n" + "="*60)
        print("RECOMMENDED NEXT STEPS")
        print("="*60)
        print("\nTest Print:")
        print("  • Print at 25% scale (A0→A4, 36×48→Letter)")
        print("  • Check readability from 2-3 feet")
        print("  • Verify colors printed accurately")
        print("\nDigital Checks:")
        print("  • View at 100% zoom in PDF viewer")
        print("  • Test on different screens/devices")
        print("  • Verify QR codes work with scanner app")
    
    def run_all_checks(self):
        """Run all quality checks."""
        print("="*60)
        print("POSTER PDF QUALITY CHECK")
        print("="*60)
        print(f"\nFile: {self.pdf_path}\n")
        
        if not self.check_file_exists():
            return False
        
        # Run automated checks
        print("[1] Page Dimensions:")
        self.check_page_size()
        print()
        
        print("[2] Page Count:")
        self.check_page_count()
        print()
        
        print("[3] File Size:")
        self.check_file_size()
        print()
        
        print("[4] Font Embedding:")
        self.check_font_embedding()
        print()
        
        print("[5] Image Quality:")
        self.check_images()
        print()
        
        # Print issues and warnings
        if self.issues:
            print("\n" + "="*60)
            print("ISSUES FOUND (must fix before printing):")
            print("="*60)
            for issue in self.issues:
                print(f"  ✗ {issue}")
        
        if self.warnings:
            print("\n" + "="*60)
            print("WARNINGS (review recommended):")
            print("="*60)
            for warning in self.warnings:
                print(f"  ⚠ {warning}")
        
        # Generate manual checklist
        self.generate_manual_checklist()
        
        # Summary
        print("\n" + "="*60)
        print("QUALITY CHECK COMPLETE")
        print("="*60)
        
        if self.issues:
            print(f"\n✗ Found {len(self.issues)} issue(s) that must be fixed")
            return False
        else:
            print("\n✓ Automated checks passed")
            return True


def main():
    parser = argparse.ArgumentParser(
        description="Check quality of poster PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check poster PDF
  python scripts/check_poster_quality.py poster.pdf
  
  # Check and save report
  python scripts/check_poster_quality.py poster.pdf --output report.txt
        """
    )
    
    parser.add_argument(
        "pdf_file",
        help="PDF file to check"
    )
    
    parser.add_argument(
        "--output",
        help="Save report to file"
    )
    
    args = parser.parse_args()
    
    # Run checks
    checker = PosterQualityChecker(args.pdf_file)
    
    if args.output:
        # Capture output to file
        import io
        from contextlib import redirect_stdout, redirect_stderr
        
        output_buffer = io.StringIO()
        
        with redirect_stdout(output_buffer), redirect_stderr(output_buffer):
            success = checker.run_all_checks()
        
        # Save to file
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_buffer.getvalue())
        
        print(f"Report saved to {args.output}")
        sys.exit(0 if success else 1)
    else:
        success = checker.run_all_checks()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
