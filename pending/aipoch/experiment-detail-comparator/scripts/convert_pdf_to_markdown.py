#!/usr/bin/env python3
"""
Convert PDF to Markdown using mistral-pdf-to-markdown skill.
This is a wrapper script for convenience.
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path

def get_mistral_api_key():
    """
    Read Mistral API key from .env file.

    Returns:
        API key string, or None if not found
    """
    env_file = Path("Notes/.env")

    if not env_file.exists():
        print("Error: .env file not found at Notes/.env", file=sys.stderr)
        return None

    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith("MISTRAL_API_KEY="):
                return line.split("=", 1)[1]

    print("Error: MISTRAL_API_KEY not found in .env file", file=sys.stderr)
    return None

def get_output_dir():
    """
    Get appropriate output directory for downloaded files.
    Cross-platform compatible (Windows/Linux/Mac).

    Returns:
        Path object for output directory
    """
    # Try temp directory first
    try:
        temp_dir = Path(tempfile.gettempdir())
        if temp_dir.exists():
            return temp_dir
    except:
        pass

    # Fallback to current directory
    return Path(".")

def convert_pdf_to_markdown(pdf_path, output_path):
    """
    Convert PDF to Markdown using mistral-pdf-to-markdown skill.

    Args:
        pdf_path: Path to input PDF
        output_path: Path to output markdown

    Returns:
        True if successful, False otherwise
    """
    # Get mistral-pdf-to-markdown skill path
    skill_path = Path.home() / ".claude" / "skills" / "mistral-pdf-to-markdown" / "scripts" / "convert_pdf_to_markdown.py"

    if not skill_path.exists():
        # Try alternative paths
        skill_path = Path.home() / ".agents" / "skills" / "mistral-pdf-to-markdown" / "scripts" / "convert_pdf_to_markdown.py"

    if not skill_path.exists():
        print("Error: mistral-pdf-to-markdown skill not found", file=sys.stderr)
        print("Please install it first: npx skills add mistral-pdf-to-markdown", file=sys.stderr)
        return False

    # Run conversion
    cmd = ["python", str(skill_path), str(pdf_path), str(output_path)]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting PDF: {e}", file=sys.stderr)
        print(f"STDERR: {e.stderr}", file=sys.stderr)
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python convert_pdf_to_markdown.py <input_pdf> <output_markdown>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert
    if convert_pdf_to_markdown(pdf_path, output_path):
        print(f"Successfully converted to: {output_path}")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
