#!/usr/bin/env python3
"""
PDF Helper Script - Comprehensive PDF Manipulation Utilities

This script provides a collection of functions for common PDF operations including:
- Text and table extraction
- PDF merging and splitting
- Form filling
- PDF creation
- Watermarking and annotations
- Metadata management
- Encryption and security
- OCR processing

Dependencies:
    pip install pypdf pdfplumber reportlab PyMuPDF pdf2image pytesseract pillow

Author: Claude
Date: 2025-10-25
"""

import os
import logging
from typing import List, Dict, Tuple, Optional, Union
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# TEXT EXTRACTION
# ============================================================================

def extract_text(pdf_path: str, method: str = 'pdfplumber') -> str:
    """
    Extract all text from a PDF file.

    Args:
        pdf_path: Path to the PDF file
        method: Extraction method ('pdfplumber' or 'pypdf')

    Returns:
        Extracted text as a string

    Example:
        >>> text = extract_text("document.pdf")
        >>> print(text[:100])
    """
    try:
        if method == 'pdfplumber':
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                text_parts = []
                for page_num, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"--- Page {page_num} ---\n{page_text}")

                return "\n\n".join(text_parts)

        elif method == 'pypdf':
            from pypdf import PdfReader

            reader = PdfReader(pdf_path)
            text_parts = []

            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- Page {page_num} ---\n{page_text}")

            return "\n\n".join(text_parts)

        else:
            raise ValueError(f"Unknown method: {method}. Use 'pdfplumber' or 'pypdf'")

    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {e}")
        raise


def extract_text_by_page(pdf_path: str) -> List[Dict[str, Union[int, str]]]:
    """
    Extract text from PDF, organized by page.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List of dictionaries with page number and text

    Example:
        >>> pages = extract_text_by_page("document.pdf")
        >>> for page in pages:
        ...     print(f"Page {page['page']}: {len(page['text'])} characters")
    """
    import pdfplumber

    pages_data = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                pages_data.append({
                    'page': page_num,
                    'text': text,
                    'char_count': len(text),
                    'word_count': len(text.split())
                })

        logger.info(f"Extracted text from {len(pages_data)} pages")
        return pages_data

    except Exception as e:
        logger.error(f"Error extracting text by page from {pdf_path}: {e}")
        raise


# ============================================================================
# TABLE EXTRACTION
# ============================================================================

def extract_tables(pdf_path: str, page_numbers: Optional[List[int]] = None) -> List[Dict]:
    """
    Extract tables from PDF.

    Args:
        pdf_path: Path to the PDF file
        page_numbers: Specific pages to extract from (1-indexed), or None for all

    Returns:
        List of dictionaries containing table data

    Example:
        >>> tables = extract_tables("report.pdf")
        >>> for t in tables:
        ...     print(f"Page {t['page']}: {len(t['data'])} rows")
    """
    import pdfplumber
    import pandas as pd

    all_tables = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages_to_process = pdf.pages

            if page_numbers:
                # Convert to 0-indexed
                pages_to_process = [pdf.pages[p - 1] for p in page_numbers if 0 < p <= len(pdf.pages)]

            for page in pages_to_process:
                tables = page.extract_tables()

                for table_num, table in enumerate(tables, start=1):
                    if table and len(table) > 0:
                        # Convert to DataFrame
                        df = pd.DataFrame(table[1:], columns=table[0])

                        all_tables.append({
                            'page': page.page_number,
                            'table_number': table_num,
                            'data': df,
                            'raw_data': table
                        })

        logger.info(f"Extracted {len(all_tables)} tables from {pdf_path}")
        return all_tables

    except Exception as e:
        logger.error(f"Error extracting tables from {pdf_path}: {e}")
        raise


def save_tables_to_csv(pdf_path: str, output_dir: str) -> List[str]:
    """
    Extract tables from PDF and save each as CSV.

    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save CSV files

    Returns:
        List of created CSV file paths

    Example:
        >>> csv_files = save_tables_to_csv("report.pdf", "output/")
        >>> print(f"Created {len(csv_files)} CSV files")
    """
    tables = extract_tables(pdf_path)
    os.makedirs(output_dir, exist_ok=True)

    csv_files = []

    for t in tables:
        filename = f"page{t['page']}_table{t['table_number']}.csv"
        filepath = os.path.join(output_dir, filename)

        t['data'].to_csv(filepath, index=False)
        csv_files.append(filepath)

        logger.info(f"Saved table to {filepath}")

    return csv_files


# ============================================================================
# PDF MERGING
# ============================================================================

def merge_pdfs(pdf_list: List[str], output_path: str, add_bookmarks: bool = False) -> None:
    """
    Merge multiple PDF files into one.

    Args:
        pdf_list: List of PDF file paths to merge
        output_path: Path for the output merged PDF
        add_bookmarks: Whether to add bookmarks for each source file

    Example:
        >>> merge_pdfs(["file1.pdf", "file2.pdf"], "merged.pdf")
    """
    from pypdf import PdfMerger

    try:
        merger = PdfMerger()

        for pdf_path in pdf_list:
            if not os.path.exists(pdf_path):
                logger.warning(f"File not found: {pdf_path}, skipping")
                continue

            if add_bookmarks:
                bookmark_name = Path(pdf_path).stem
                merger.append(pdf_path, outline_item=bookmark_name)
            else:
                merger.append(pdf_path)

            logger.info(f"Added {pdf_path} to merge")

        merger.write(output_path)
        merger.close()

        logger.info(f"Successfully merged {len(pdf_list)} PDFs into {output_path}")

    except Exception as e:
        logger.error(f"Error merging PDFs: {e}")
        raise


def merge_pdfs_with_ranges(
    pdf_configs: List[Dict[str, Union[str, Tuple[int, int]]]],
    output_path: str
) -> None:
    """
    Merge PDFs with specific page ranges.

    Args:
        pdf_configs: List of dicts with 'path' and optional 'pages' (tuple)
        output_path: Path for the output merged PDF

    Example:
        >>> configs = [
        ...     {'path': 'doc1.pdf', 'pages': (0, 3)},
        ...     {'path': 'doc2.pdf'},  # All pages
        ... ]
        >>> merge_pdfs_with_ranges(configs, "output.pdf")
    """
    from pypdf import PdfMerger

    try:
        merger = PdfMerger()

        for config in pdf_configs:
            path = config['path']
            pages = config.get('pages')

            if not os.path.exists(path):
                logger.warning(f"File not found: {path}, skipping")
                continue

            if pages:
                merger.append(path, pages=pages)
                logger.info(f"Added {path} (pages {pages[0]}-{pages[1]})")
            else:
                merger.append(path)
                logger.info(f"Added {path} (all pages)")

        merger.write(output_path)
        merger.close()

        logger.info(f"Successfully created merged PDF: {output_path}")

    except Exception as e:
        logger.error(f"Error merging PDFs with ranges: {e}")
        raise


# ============================================================================
# PDF SPLITTING
# ============================================================================

def split_pdf(input_pdf: str, output_dir: str, pages_per_file: int = 1) -> List[str]:
    """
    Split a PDF into multiple files.

    Args:
        input_pdf: Path to the input PDF
        output_dir: Directory to save split PDFs
        pages_per_file: Number of pages per output file

    Returns:
        List of created file paths

    Example:
        >>> files = split_pdf("document.pdf", "output/", pages_per_file=2)
        >>> print(f"Created {len(files)} files")
    """
    from pypdf import PdfReader, PdfWriter

    try:
        reader = PdfReader(input_pdf)
        total_pages = len(reader.pages)

        os.makedirs(output_dir, exist_ok=True)

        output_files = []
        file_count = 1

        for start_page in range(0, total_pages, pages_per_file):
            writer = PdfWriter()

            end_page = min(start_page + pages_per_file, total_pages)

            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])

            output_filename = f"split_{file_count}.pdf"
            output_path = os.path.join(output_dir, output_filename)

            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            output_files.append(output_path)
            logger.info(f"Created {output_filename} (pages {start_page + 1}-{end_page})")

            file_count += 1

        logger.info(f"Split {input_pdf} into {len(output_files)} files")
        return output_files

    except Exception as e:
        logger.error(f"Error splitting PDF {input_pdf}: {e}")
        raise


def extract_page_range(input_pdf: str, output_pdf: str, start_page: int, end_page: int) -> None:
    """
    Extract a specific range of pages from a PDF.

    Args:
        input_pdf: Path to the input PDF
        output_pdf: Path for the output PDF
        start_page: Starting page number (1-indexed)
        end_page: Ending page number (1-indexed, inclusive)

    Example:
        >>> extract_page_range("document.pdf", "excerpt.pdf", 5, 10)
    """
    from pypdf import PdfReader, PdfWriter

    try:
        reader = PdfReader(input_pdf)
        writer = PdfWriter()

        # Convert to 0-indexed
        start_idx = start_page - 1
        end_idx = end_page

        if start_idx < 0 or end_idx > len(reader.pages):
            raise ValueError(f"Page range out of bounds (1-{len(reader.pages)})")

        for page_num in range(start_idx, end_idx):
            writer.add_page(reader.pages[page_num])

        with open(output_pdf, 'wb') as output_file:
            writer.write(output_file)

        logger.info(f"Extracted pages {start_page}-{end_page} to {output_pdf}")

    except Exception as e:
        logger.error(f"Error extracting page range: {e}")
        raise


# ============================================================================
# PDF CREATION
# ============================================================================

def create_pdf_from_text(output_path: str, content: List[str], title: str = "") -> None:
    """
    Create a simple PDF from text content.

    Args:
        output_path: Path for the output PDF
        content: List of text lines
        title: Optional title for the document

    Example:
        >>> content = ["Line 1", "Line 2", "Line 3"]
        >>> create_pdf_from_text("output.pdf", content, "My Document")
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    try:
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica", 12)

        y_position = height - 50

        if title:
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, y_position, title)
            y_position -= 40
            c.setFont("Helvetica", 12)

        for line in content:
            if y_position < 50:  # Start new page
                c.showPage()
                c.setFont("Helvetica", 12)
                y_position = height - 50

            c.drawString(50, y_position, str(line))
            y_position -= 20

        c.save()
        logger.info(f"Created PDF: {output_path}")

    except Exception as e:
        logger.error(f"Error creating PDF from text: {e}")
        raise


def create_pdf_report(
    output_path: str,
    title: str,
    sections: List[Dict[str, Union[str, List[str]]]]
) -> None:
    """
    Create a formatted PDF report with sections.

    Args:
        output_path: Path for the output PDF
        title: Report title
        sections: List of dicts with 'heading' and 'content' keys

    Example:
        >>> sections = [
        ...     {'heading': 'Introduction', 'content': ['Paragraph 1', 'Paragraph 2']},
        ...     {'heading': 'Results', 'content': ['Result 1', 'Result 2']}
        ... ]
        >>> create_pdf_report("report.pdf", "Monthly Report", sections)
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER

    try:
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        # Custom title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='darkblue',
            alignment=TA_CENTER,
            spaceAfter=30
        )

        # Add title
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.5 * inch))

        # Add sections
        for section in sections:
            # Section heading
            story.append(Paragraph(section['heading'], styles['Heading2']))
            story.append(Spacer(1, 0.2 * inch))

            # Section content
            content_list = section.get('content', [])
            if isinstance(content_list, str):
                content_list = [content_list]

            for paragraph in content_list:
                p = Paragraph(str(paragraph), styles['BodyText'])
                story.append(p)
                story.append(Spacer(1, 0.1 * inch))

            story.append(Spacer(1, 0.3 * inch))

        doc.build(story)
        logger.info(f"Created PDF report: {output_path}")

    except Exception as e:
        logger.error(f"Error creating PDF report: {e}")
        raise


# ============================================================================
# WATERMARKS AND ANNOTATIONS
# ============================================================================

def add_watermark(
    input_pdf: str,
    output_pdf: str,
    watermark_text: str,
    opacity: float = 0.3
) -> None:
    """
    Add a text watermark to all pages of a PDF.

    Args:
        input_pdf: Path to the input PDF
        output_pdf: Path for the output PDF
        watermark_text: Text to use as watermark
        opacity: Watermark opacity (0.0 to 1.0)

    Example:
        >>> add_watermark("document.pdf", "watermarked.pdf", "CONFIDENTIAL")
    """
    import fitz

    try:
        doc = fitz.open(input_pdf)

        for page in doc:
            rect = page.rect

            # Add watermark centered and rotated
            page.insert_textbox(
                rect,
                watermark_text,
                fontsize=50,
                align=fitz.TEXT_ALIGN_CENTER,
                rotate=45,
                opacity=opacity,
                color=(0.7, 0.7, 0.7)
            )

        doc.save(output_pdf)
        doc.close()

        logger.info(f"Added watermark to {output_pdf}")

    except Exception as e:
        logger.error(f"Error adding watermark: {e}")
        raise


def add_page_numbers(input_pdf: str, output_pdf: str, position: str = 'bottom-center') -> None:
    """
    Add page numbers to a PDF.

    Args:
        input_pdf: Path to the input PDF
        output_pdf: Path for the output PDF
        position: Position of page numbers ('bottom-center', 'bottom-right', etc.)

    Example:
        >>> add_page_numbers("document.pdf", "numbered.pdf")
    """
    import fitz

    try:
        doc = fitz.open(input_pdf)

        for page_num, page in enumerate(doc, start=1):
            rect = page.rect

            # Determine position
            if position == 'bottom-center':
                text_rect = fitz.Rect(rect.width / 2 - 20, rect.height - 30, rect.width / 2 + 20, rect.height - 10)
            elif position == 'bottom-right':
                text_rect = fitz.Rect(rect.width - 60, rect.height - 30, rect.width - 10, rect.height - 10)
            else:  # bottom-left
                text_rect = fitz.Rect(10, rect.height - 30, 60, rect.height - 10)

            page.insert_textbox(
                text_rect,
                str(page_num),
                fontsize=10,
                align=fitz.TEXT_ALIGN_CENTER,
                color=(0, 0, 0)
            )

        doc.save(output_pdf)
        doc.close()

        logger.info(f"Added page numbers to {output_pdf}")

    except Exception as e:
        logger.error(f"Error adding page numbers: {e}")
        raise


# ============================================================================
# METADATA MANAGEMENT
# ============================================================================

def get_pdf_metadata(pdf_path: str) -> Dict[str, Union[str, int, bool]]:
    """
    Extract metadata from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary containing metadata

    Example:
        >>> metadata = get_pdf_metadata("document.pdf")
        >>> print(metadata['title'])
    """
    from pypdf import PdfReader

    try:
        reader = PdfReader(pdf_path)
        metadata = reader.metadata

        info = {
            'title': metadata.get('/Title', '') if metadata else '',
            'author': metadata.get('/Author', '') if metadata else '',
            'subject': metadata.get('/Subject', '') if metadata else '',
            'creator': metadata.get('/Creator', '') if metadata else '',
            'producer': metadata.get('/Producer', '') if metadata else '',
            'creation_date': metadata.get('/CreationDate', '') if metadata else '',
            'modification_date': metadata.get('/ModDate', '') if metadata else '',
            'page_count': len(reader.pages),
            'is_encrypted': reader.is_encrypted
        }

        return info

    except Exception as e:
        logger.error(f"Error extracting metadata from {pdf_path}: {e}")
        raise


def update_pdf_metadata(input_pdf: str, output_pdf: str, metadata: Dict[str, str]) -> None:
    """
    Update PDF metadata.

    Args:
        input_pdf: Path to the input PDF
        output_pdf: Path for the output PDF
        metadata: Dictionary of metadata fields to update

    Example:
        >>> metadata = {'/Title': 'New Title', '/Author': 'John Doe'}
        >>> update_pdf_metadata("document.pdf", "updated.pdf", metadata)
    """
    from pypdf import PdfReader, PdfWriter

    try:
        reader = PdfReader(input_pdf)
        writer = PdfWriter()

        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)

        # Update metadata
        writer.add_metadata(metadata)

        with open(output_pdf, 'wb') as output_file:
            writer.write(output_file)

        logger.info(f"Updated metadata in {output_pdf}")

    except Exception as e:
        logger.error(f"Error updating metadata: {e}")
        raise


# ============================================================================
# SECURITY AND ENCRYPTION
# ============================================================================

def encrypt_pdf(
    input_pdf: str,
    output_pdf: str,
    user_password: str,
    owner_password: Optional[str] = None
) -> None:
    """
    Encrypt a PDF with password protection.

    Args:
        input_pdf: Path to the input PDF
        output_pdf: Path for the output encrypted PDF
        user_password: Password to open the document
        owner_password: Password for full permissions (optional)

    Example:
        >>> encrypt_pdf("document.pdf", "secure.pdf", "user123", "owner456")
    """
    from pypdf import PdfReader, PdfWriter

    try:
        reader = PdfReader(input_pdf)
        writer = PdfWriter()

        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)

        # Encrypt
        if owner_password is None:
            owner_password = user_password

        writer.encrypt(
            user_password=user_password,
            owner_password=owner_password,
            algorithm="AES-256"
        )

        with open(output_pdf, 'wb') as output_file:
            writer.write(output_file)

        logger.info(f"Encrypted PDF saved to {output_pdf}")

    except Exception as e:
        logger.error(f"Error encrypting PDF: {e}")
        raise


def decrypt_pdf(input_pdf: str, output_pdf: str, password: str) -> None:
    """
    Remove password protection from a PDF.

    Args:
        input_pdf: Path to the encrypted PDF
        output_pdf: Path for the output decrypted PDF
        password: Password to decrypt the PDF

    Example:
        >>> decrypt_pdf("secure.pdf", "unlocked.pdf", "user123")
    """
    from pypdf import PdfReader, PdfWriter

    try:
        reader = PdfReader(input_pdf)

        if reader.is_encrypted:
            success = reader.decrypt(password)
            if success == 0:
                raise ValueError("Incorrect password")

        writer = PdfWriter()

        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)

        with open(output_pdf, 'wb') as output_file:
            writer.write(output_file)

        logger.info(f"Decrypted PDF saved to {output_pdf}")

    except Exception as e:
        logger.error(f"Error decrypting PDF: {e}")
        raise


# ============================================================================
# OCR PROCESSING
# ============================================================================

def ocr_pdf(pdf_path: str, output_txt_path: Optional[str] = None, language: str = 'eng') -> str:
    """
    Perform OCR on a scanned PDF.

    Args:
        pdf_path: Path to the PDF file
        output_txt_path: Optional path to save extracted text
        language: OCR language code (default: 'eng')

    Returns:
        Extracted text

    Example:
        >>> text = ocr_pdf("scanned.pdf", "output.txt")
    """
    try:
        from pdf2image import convert_from_path
        import pytesseract

        # Convert PDF to images
        images = convert_from_path(pdf_path)

        all_text = []

        for page_num, image in enumerate(images, start=1):
            logger.info(f"Processing page {page_num}/{len(images)}")

            # Perform OCR
            text = pytesseract.image_to_string(image, lang=language)
            all_text.append(f"--- Page {page_num} ---\n{text}")

        full_text = "\n\n".join(all_text)

        # Save to file if specified
        if output_txt_path:
            with open(output_txt_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            logger.info(f"Saved OCR text to {output_txt_path}")

        return full_text

    except ImportError as e:
        logger.error("Missing dependencies. Install: pip install pdf2image pytesseract")
        raise
    except Exception as e:
        logger.error(f"Error performing OCR on {pdf_path}: {e}")
        raise


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_pdf_info(pdf_path: str) -> Dict[str, Union[str, int, bool, List]]:
    """
    Get comprehensive information about a PDF.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary with PDF information

    Example:
        >>> info = get_pdf_info("document.pdf")
        >>> print(f"Pages: {info['page_count']}")
    """
    import fitz

    try:
        doc = fitz.open(pdf_path)

        info = {
            'file_path': pdf_path,
            'file_size_mb': os.path.getsize(pdf_path) / (1024 * 1024),
            'page_count': doc.page_count,
            'is_encrypted': doc.is_encrypted,
            'metadata': doc.metadata,
            'page_sizes': []
        }

        # Get page sizes
        for page_num in range(doc.page_count):
            page = doc[page_num]
            info['page_sizes'].append({
                'page': page_num + 1,
                'width': page.rect.width,
                'height': page.rect.height
            })

        doc.close()
        return info

    except Exception as e:
        logger.error(f"Error getting PDF info: {e}")
        raise


def compress_pdf(input_pdf: str, output_pdf: str) -> Dict[str, float]:
    """
    Compress a PDF file to reduce size.

    Args:
        input_pdf: Path to the input PDF
        output_pdf: Path for the compressed PDF

    Returns:
        Dictionary with original and compressed sizes

    Example:
        >>> result = compress_pdf("large.pdf", "small.pdf")
        >>> print(f"Reduced by {result['reduction_percent']:.1f}%")
    """
    import fitz

    try:
        doc = fitz.open(input_pdf)

        # Save with compression
        doc.save(
            output_pdf,
            garbage=4,  # Maximum garbage collection
            deflate=True,  # Compress streams
            clean=True  # Clean up content
        )

        doc.close()

        original_size = os.path.getsize(input_pdf) / (1024 * 1024)
        compressed_size = os.path.getsize(output_pdf) / (1024 * 1024)
        reduction = ((original_size - compressed_size) / original_size) * 100

        result = {
            'original_size_mb': original_size,
            'compressed_size_mb': compressed_size,
            'reduction_percent': reduction
        }

        logger.info(f"Compressed {input_pdf}: {original_size:.2f} MB -> {compressed_size:.2f} MB ({reduction:.1f}% reduction)")

        return result

    except Exception as e:
        logger.error(f"Error compressing PDF: {e}")
        raise


def extract_images_from_pdf(pdf_path: str, output_dir: str) -> List[str]:
    """
    Extract all images from a PDF.

    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save extracted images

    Returns:
        List of saved image file paths

    Example:
        >>> images = extract_images_from_pdf("document.pdf", "images/")
        >>> print(f"Extracted {len(images)} images")
    """
    import fitz

    try:
        doc = fitz.open(pdf_path)
        os.makedirs(output_dir, exist_ok=True)

        image_files = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            images = page.get_images()

            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = doc.extract_image(xref)

                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                image_filename = os.path.join(
                    output_dir,
                    f"page{page_num + 1}_img{img_index + 1}.{image_ext}"
                )

                with open(image_filename, "wb") as img_file:
                    img_file.write(image_bytes)

                image_files.append(image_filename)

        doc.close()

        logger.info(f"Extracted {len(image_files)} images to {output_dir}")
        return image_files

    except Exception as e:
        logger.error(f"Error extracting images: {e}")
        raise


def rotate_pdf_pages(
    input_pdf: str,
    output_pdf: str,
    rotation: int = 90,
    pages: Optional[List[int]] = None
) -> None:
    """
    Rotate pages in a PDF.

    Args:
        input_pdf: Path to the input PDF
        output_pdf: Path for the output PDF
        rotation: Degrees to rotate (90, 180, 270)
        pages: List of page numbers to rotate (1-indexed), or None for all

    Example:
        >>> rotate_pdf_pages("document.pdf", "rotated.pdf", 90, [1, 3, 5])
    """
    from pypdf import PdfReader, PdfWriter

    try:
        reader = PdfReader(input_pdf)
        writer = PdfWriter()

        for page_num, page in enumerate(reader.pages):
            if pages is None or (page_num + 1) in pages:
                page.rotate(rotation)
            writer.add_page(page)

        with open(output_pdf, 'wb') as output_file:
            writer.write(output_file)

        logger.info(f"Rotated pages in {output_pdf}")

    except Exception as e:
        logger.error(f"Error rotating pages: {e}")
        raise


# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    # Example usage
    print("PDF Helper Script")
    print("=" * 50)

    # Example 1: Extract text
    # text = extract_text("sample.pdf")
    # print(text[:500])

    # Example 2: Extract tables
    # tables = extract_tables("report.pdf")
    # for t in tables:
    #     print(f"Page {t['page']}: {t['data']}")

    # Example 3: Merge PDFs
    # merge_pdfs(["file1.pdf", "file2.pdf"], "merged.pdf")

    # Example 4: Get PDF info
    # info = get_pdf_info("document.pdf")
    # print(f"Pages: {info['page_count']}")

    print("\nImport this module to use the helper functions.")
    print("Example: from pdf_helper import extract_text, merge_pdfs")
