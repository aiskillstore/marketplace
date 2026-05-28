#!/usr/bin/env python3
"""
Poster PDF Quality Checker - Enhanced Version
Combines features from review_poster.sh with Python cross-platform compatibility.
Provides automated quality checks for academic posters.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


class PosterQualityChecker:
    """Check quality of poster PDF files."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.issues = []
        self.warnings = []
        self.checks_passed = 0
        self.checks_failed = 0
    
    def _run_command(self, command: list) -> tuple:
        """Run command and return output and return code."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,
                shell=True
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
            print("⚠ pdfinfo not installed (install: brew install poppler or apt-get install poppler-utils)")
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
                    
                    # Check against common poster sizes
                    if width == '2384' and height == '3370':
                        print("  ✓ Detected: A0 Portrait")
                    elif width == '3370' and height == '2384':
                        print("  ✓ Detected: A0 Landscape")
                    elif width == '1684' and height == '2384':
                        print("  ✓ Detected: A1 Portrait")
                    elif width == '2592' and height == '3456':
                        print("  ✓ Detected: 36×48 inches Portrait")
                    else:
                        print(f"  ⚠ Non-standard size: {width}×{height}")
                break
        else:
            print("✗ Could not extract page size")
    
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
                        self.checks_passed += 1
                    else:
                        self.issues.append(f"Multiple pages detected: {page_count}")
                        print(f"✗ Multiple pages detected: {page_count}")
                        self.checks_failed += 1
                break
    
    def check_file_size(self):
        """Check PDF file size."""
        file_size = self.pdf_path.stat().st_size
        size_mb = file_size / (1024 * 1024)
        size_str = f"{size_mb:.2f} MB"
        
        print(f"✓ File size: {size_str}")
        
        # Check if file is too large for email
        if file_size > 52428800:  # 50 MB
            self.warnings.append(f"Large file (>50MB) - may need compression for email")
            print(f"  ⚠ Large file (>50MB) - may need compression for email")
            print(f"  💡 Compress with: gs -sDEVICE=pdfwrite -dPDFSETTINGS=/printer -dNOPAUSE -dQUIET -dBATCH -sOutputFile=compressed.pdf {self.pdf_path}")
        elif file_size < 1048576:  # 1 MB
            self.warnings.append("Small file - check image quality")
            print(f"  ⚠ Small file - check image quality")
    
    def check_font_embedding(self):
        """Check that fonts are embedded."""
        stdout, returncode = self._run_command(['pdffonts', str(self.pdf_path)])
        
        if returncode != 0:
            self.warnings.append("Could not check fonts (pdffonts not installed)")
            return
        
        print("Checking font embedding...")
        lines = stdout.split('\n')
        
        if len(lines) > 3:
            print("  Checking first 20 fonts...")
            for line in lines[2:22]:
                print(f"    {line}")
            
            # Check for non-embedded fonts
            non_embedded = []
            for line in lines[2:]:
                if 'no' in line.split():
                    non_embedded.append(line)
            
            if non_embedded:
                print(f"  ✗ Some fonts are NOT embedded (printing may fail)")
                print(f"  💡 Fix: Recompile with 'pdflatex -dEmbedAllFonts=true poster.tex'")
                self.checks_failed += 1
            else:
                print("  ✓ All fonts appear to be embedded")
                self.checks_passed += 1
    
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
            print("  Image details:")
            for line in lines[1:12]:
                print(f"    {line}")
            
            if image_count > 0:
                print("  💡 Verify images are at least 300 DPI for printing")
                print("  💡 Formula: DPI = pixels / (inches in poster)")
            else:
                self.warnings.append("No images found")
                print("  ⚠ No images found")
        else:
            self.warnings.append("Could not check images")
    
    def generate_manual_checklist(self):
        """Generate manual inspection checklist."""
        print("\n" + "="*60)
        print("MANUAL VISUAL INSPECTION REQUIRED")
        print("="*60)
        print("\nLayout and Spacing:")
        print("  [ ] Content fills entire page (no large white margins)")
        print("  [ ] Consistent spacing between columns (1-2cm)")
        print("  [ ] Consistent spacing between blocks (1-2cm)")
        print("  [ ] All elements aligned to grid")
        print("  [ ] No overlapping text or figures")
        print("  [ ] White space evenly distributed (30-40% total)")
        print("  [ ] Visual balance across poster (no heavy/empty areas)")
        
        print("\nTypography:")
        print("  [ ] Title readable and prominent (72-120pt)")
        print("  [ ] Section headers clear (48-72pt)")
        print("  [ ] Body text large enough (24-36pt minimum)")
        print("  [ ] Captions readable (18-24pt)")
        print("  [ ] No text cutoff or running off edges")
        print("  [ ] Consistent font usage throughout")
        print("  [ ] Line spacing adequate (1.2-1.5×)")
        print("  [ ] No awkward hyphenation or word breaks")
        
        print("\nVisual Elements:")
        print("  [ ] All figures display correctly")
        print("  [ ] No pixelated or blurry images")
        print("  [ ] Figure resolution high (zoom to 200% to verify)")
        print("  [ ] Figure labels large and clear")
        print("  [ ] Graph axes labeled with units")
        print("  [ ] Color schemes consistent across figures")
        print("  [ ] Legends readable and well-positioned")
        print("  [ ] Logos crisp and professional")
        print("  [ ] QR codes sharp and high-contrast (minimum 2×2cm)")
        print("  [ ] No visual artifacts or rendering errors")
        
        print("\nColors:")
        print("  [ ] Colors render as intended (not washed out)")
        print("  [ ] High contrast between text and background (≥4.5:1)")
        print("  [ ] Color scheme harmonious")
        print("  [ ] Colors appropriate for printing (not too bright/neon)")
        print("  [ ] Institutional colors used correctly")
        print("  [ ] Color-blind friendly palette (avoid red-green only)")
        
        print("\nContent:")
        print("  [ ] Title complete and correctly positioned")
        print("  [ ] All author names and affiliations visible")
        print("  [ ] All sections present (Intro, Methods, Results, Conclusions)")
        print("  [ ] Results section has figures/data")
        print("  [ ] Conclusions clearly stated")
        print("  [ ] References formatted consistently")
        print("  [ ] Contact information clearly visible")
        print("  [ ] No missing content")
        
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
        
        print("\nProofreading:")
        print("  • Spell-check all text")
        print("  • Verify author names and affiliations")
        print("  • Confirm all statistics and numbers")
        print("  • Ask colleague to review")
    
    def print_summary(self):
        """Print summary of quality checks."""
        print("\n" + "="*60)
        print("QUALITY CHECK COMPLETE")
        print("="*60)
        print(f"\nFile: {self.pdf_path}")
        
        if self.issues:
            print("\n✗ ISSUES FOUND (must fix before printing):")
            for issue in self.issues:
                print(f"  ✗ {issue}")
        
        if self.warnings:
            print("\n⚠ WARNINGS (review recommended):")
            for warning in self.warnings:
                print(f"  ⚠ {warning}")
        
        print(f"\n✓ Automated checks passed: {self.checks_passed}")
        print(f"✗ Automated checks failed: {self.checks_failed}")
        
        print(f"\n✓ Warnings: {len(self.warnings)}")
        print(f"✗ Issues: {len(self.issues)}")
        
        self.generate_manual_checklist()
    
    def run_all_checks(self):
        """Run all quality checks."""
        print("="*60)
        print("POSTER PDF QUALITY CHECK")
        print("="*60)
        print(f"\nFile: {self.pdf_path}\n")
        
        # Run automated checks
        self.check_file_exists()
        
        if not self.issues or 'File not found' in '\n'.join(self.issues):
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
            
            # Print summary
            self.print_summary()
            
            return len(self.issues) == 0


def main():
    parser = argparse.ArgumentParser(
        description="Check quality of poster PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check poster PDF
  python scripts/review_poster.py poster.pdf
  
  # Check and save report
  python scripts/review_poster.py poster.pdf --output report.txt
  
  # Check and exit with error code
  python scripts/review_poster.py poster.pdf --exit-on-error
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
    
    parser.add_argument(
        "--exit-on-error",
        action="store_true",
        help="Exit with error code if issues found"
    )
    
    args = parser.parse_args()
    
    # Run checks
    checker = PosterQualityChecker(args.pdf_file)
    success = checker.run_all_checks()
    
    # Save report if requested
    if args.output:
        import io
        from contextlib import redirect_stdout, redirect_stderr
        
        output_buffer = io.StringIO()
        
        with redirect_stdout(output_buffer), redirect_stderr(output_buffer):
            checker.run_all_checks()
        
        # Save to file
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_buffer.getvalue())
        
        print(f"Report saved to {args.output}")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
