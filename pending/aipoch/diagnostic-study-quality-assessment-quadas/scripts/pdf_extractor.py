#!/usr/bin/env python3
"""PDF text extraction tool - for QUADAS-2 literature assessment
Extract PDF text content using PyPDF2 library"""

import sys
from pathlib import Path

def extract_pdf_text(pdf_path, start_page=1, end_page=None):
    """Extract text from PDF files
    
    Args:
        pdf_path: PDF file path
        start_page: starting page number (starting from 1)
        end_page: end page number (None means to the last page)
    
    Returns:
        Extracted text content"""
    try:
        import PyPDF2
    except ImportError:
        print("Error: Please install PyPDF2 library first")
        print("pip install PyPDF2")
        sys.exit(1)
    
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"mistake：File not found '{pdf_path}'")
        sys.exit(1)
    
    text_content = []
    
    try:
        with open(pdf_file, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            
            # Adjust page range
            start_idx = max(0, start_page - 1)
            end_idx = end_page if end_page else total_pages
            end_idx = min(end_idx, total_pages)
            
            print(f"Reading PDF: {pdf_file.name}")
            print(f"Total pages: {total_pages}, Reading range: No.{start_page}Page arrive No.{end_idx}Page\n")
            
            for page_num in range(start_idx, end_idx):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text.strip():
                    text_content.append(f"--- No. {page_num + 1} Page ---\n{text}\n")
    
    except Exception as e:
        print(f"read PDF error: {e}")
        sys.exit(1)
    
    return "\n".join(text_content)


def extract_methods_section(pdf_path):
    """Intelligent extraction of Methods section of documents
    For QUADAS-2 evaluation"""
    full_text = extract_pdf_text(pdf_path)
    
    # Common Methods section header variations
    methods_markers = [
        "Methods",
        "METHODS", 
        "Materials and Methods",
        "MATERIALS AND METHODS",
        "Study Design",
        "Experimental Procedures"
    ]
    
    # Find the beginning and end of the Methods section
    methods_start = -1
    for marker in methods_markers:
        idx = full_text.find(marker)
        if idx != -1:
            methods_start = idx
            break
    
    if methods_start == -1:
        print("Warning: Methods section not found, return to full text")
        return full_text
    
    # Find the next main section (usually Results)
    next_section_markers = ["Results", "RESULTS", "Findings", "Discussion", "DISCUSSION"]
    methods_end = len(full_text)
    
    for marker in next_section_markers:
        idx = full_text.find(marker, methods_start + 100)  # +100 to avoid duplicate matches
        if idx != -1 and idx < methods_end:
            methods_end = idx
    
    methods_text = full_text[methods_start:methods_end].strip()
    
    print(f"successfully extracted Methods part (length: {len(methods_text)} character)\n")
    return methods_text


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_extractor.py <pdf file path> [start page] [end page] [output file]")
        print("Example: python pdf_extractor.py paper.pdf")
        print("Example: python pdf_extractor.py paper.pdf 5 15")
        print("Example: python pdf_extractor.py paper.pdf 1 100 output.txt")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    start_page = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    end_page = int(sys.argv[3]) if len(sys.argv) > 3 else None
    output_file = sys.argv[4] if len(sys.argv) > 4 else "extracted_text.txt"
    
    # Extract text
    text = extract_pdf_text(pdf_path, start_page, end_page)
    
    # Save to file (encoded using UTF-8)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"\nText saved to: {output_file}")
