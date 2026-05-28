#!/usr/bin/env python3
"""
PDF Text Extraction Script for NOS Quality Assessment

Extracts text from PDF files and saves to extracted_text.txt
Usage: python extract_pdf.py <pdf_file_path>
"""

import PyPDF2
import sys
import os
from pathlib import Path


def extract_pdf_text(pdf_path):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file (absolute or relative)
    
    Returns:
        tuple: (full_text, num_pages, extracted_pages)
    """
    # Handle paths with spaces and special characters
    pdf_path = Path(pdf_path).resolve()
    
    print(f"Opening: {pdf_path}")
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            print(f"Total pages: {num_pages}")
            
            all_text = []
            extracted_pages = 0
            
            for i, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        all_text.append(f'--- Page {i+1} ---\n{text}')
                        extracted_pages += 1
                        print(f'[OK] Extracted page {i+1}/{num_pages}')
                    else:
                        print(f'[WARN] Page {i+1}/{num_pages} has no extractable text')
                except Exception as e:
                    print(f'[ERROR] Page {i+1}: {e}')
                    continue
            
            full_text = '\n\n'.join(all_text)
            return full_text, num_pages, extracted_pages
            
    except Exception as e:
        raise Exception(f"Error reading PDF: {e}")


def main():
    """Main function to handle command line arguments and extraction."""
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf.py <pdf_file_path>")
        print("Example: python extract_pdf.py 'my document.pdf'")
        sys.exit(1)
    
    # Get PDF path from command line
    pdf_path = sys.argv[1]
    
    # Remove surrounding quotes if present
    pdf_path = pdf_path.strip('"\'')
    
    try:
        # Extract text
        full_text, num_pages, extracted_pages = extract_pdf_text(pdf_path)
        
        # Save to output file
        output_file = 'extracted_text.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        # Print summary
        print(f'\n{"#"*50}')
        print(f'Extraction complete!')
        print(f'Total pages in PDF: {num_pages}')
        print(f'Pages with text: {extracted_pages}')
        print(f'Characters extracted: {len(full_text)}')
        print(f'Output saved to: {os.path.abspath(output_file)}')
        print(f'{"#"*50}')
        
        # Preview first 500 characters (safely handle encoding)
        if len(full_text) > 0:
            try:
                print(f'\nPreview (first 500 chars):')
                # Try to encode/decode to handle terminal encoding issues
                preview = full_text[:500]
                preview_safe = preview.encode('utf-8', errors='ignore').decode('utf-8')
                print(preview_safe)
                print('...')
            except:
                print(f'\n[Preview skipped due to terminal encoding]')
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check if the file path is correct")
        print("2. If path contains spaces, enclose it in quotes")
        print("3. Ensure you have read permissions for the file")
        sys.exit(1)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
