#!/usr/bin/env python3
"""
PDF to Image Converter
Converts PDF pages to PNG images for analysis and reference.
"""

import os
import sys
import argparse
from pathlib import Path
from pdf2image import convert_from_path


def convert_pdf_to_images(pdf_path, output_dir, dpi=300, max_dim=None):
    """
    Convert PDF pages to PNG images.
    
    Args:
        pdf_path: Path to input PDF file
        output_dir: Directory to save images
        dpi: Resolution for output images (default: 300)
        max_dim: Maximum dimension for resizing (optional)
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Converting {pdf_path} to images...")
    print(f"DPI: {dpi}")
    print(f"Output directory: {output_dir}")
    
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=dpi)
        
        for i, image in enumerate(images, 1):
            # Resize if max_dim specified
            if max_dim:
                width, height = image.size
                if width > max_dim or height > max_dim:
                    scale_factor = min(max_dim / width, max_dim / height)
                    new_width = int(width * scale_factor)
                    new_height = int(height * scale_factor)
                    image = image.resize((new_width, new_height))
                    print(f"  Page {i}: Resized to {new_width}x{new_height}")
            
            # Save image
            image_path = output_path / f"page_{i:03d}.png"
            image.save(image_path, 'PNG')
            print(f"  Saved: {image_path.name} (size: {image.size})")
        
        print(f"\n✓ Successfully converted {len(images)} pages to PNG images")
        return True
        
    except Exception as e:
        print(f"\n✗ Error converting PDF: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF pages to PNG images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic conversion with default DPI (300)
  python scripts/convert_pdf_to_images.py paper.pdf output/
  
  # High quality conversion (600 DPI)
  python scripts/convert_pdf_to_images.py paper.pdf output/ --dpi 600
  
  # Limit image size to 1000px on longest dimension
  python scripts/convert_pdf_to_images.py paper.pdf output/ --max-dim 1000
        """
    )
    
    parser.add_argument(
        "pdf_file",
        help="Input PDF file to convert"
    )
    
    parser.add_argument(
        "output_dir",
        help="Output directory for PNG images"
    )
    
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="Output resolution in DPI (default: 300)"
    )
    
    parser.add_argument(
        "--max-dim",
        type=int,
        help="Maximum dimension (width or height) for resizing"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.pdf_file).exists():
        print(f"Error: File not found: {args.pdf_file}")
        sys.exit(1)
    
    # Convert PDF
    success = convert_pdf_to_images(
        args.pdf_file,
        args.output_dir,
        args.dpi,
        args.max_dim
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
