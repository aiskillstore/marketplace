# PDF Manipulation Skill

Comprehensive PDF manipulation, extraction, and generation with support for text extraction, form filling, merging, splitting, annotations, and creation.

## Overview

Work with PDF files in Python for extracting text and tables, filling PDF forms, merging/splitting PDFs, creating PDFs programmatically, adding watermarks/annotations, and managing PDF metadata. This skill covers everything from basic text extraction to advanced operations like OCR and PDF creation.

## Installation

Install the required Python libraries:

```bash
pip install pypdf pdfplumber reportlab PyMuPDF pdf2image pytesseract pillow
```

For detailed installation instructions including system dependencies, see [Library Installation Guide](./references/library-installation.md).

## What's Included

### SKILL.md
Comprehensive guide covering all PDF operations with progressive disclosure for efficiency. Includes quick start examples, detailed workflows for text/table extraction, form operations, merging/splitting, PDF creation, metadata management, and OCR.

### scripts/
- `pdf_helper.py` - Utility functions for common PDF operations

### examples/
- `invoice-generator.md` - Professional invoice template generation
- `report-automation.md` - Automated report generation workflows

### references/
- `library-installation.md` - Setup guide and dependencies
- `text-extraction.md` - All text extraction methods including OCR fallback
- `table-extraction.md` - Table detection strategies and data cleaning
- `pdf-operations.md` - Forms, merge, split, page operations
- `pdf-creation.md` - Creating PDFs from scratch with reportlab
- `metadata-security-ocr.md` - Advanced operations
- `best-practices.md` - Pitfalls and solutions

## Quick Start

### Extract Text from PDF

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
for page in reader.pages:
    text = page.extract_text()
    print(text)
```

### Extract Tables

```python
import pdfplumber

with pdfplumber.open("report.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            print(table)
```

### Create a Simple PDF

```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

c = canvas.Canvas("output.pdf", pagesize=letter)
c.setFont("Helvetica", 12)
c.drawString(50, 750, "Hello, World!")
c.save()
```

### Fill PDF Forms

```python
import fitz

doc = fitz.open("form.pdf")
for page in doc:
    for widget in page.widgets():
        if widget.field_name == "name":
            widget.field_value = "John Doe"
            widget.update()
doc.save("filled.pdf")
doc.close()
```

## Key Features

- **Text Extraction**: Simple and layout-aware extraction with OCR fallback
- **Table Extraction**: Advanced table detection and parsing
- **Form Operations**: Fill, extract, and flatten PDF forms
- **Merging & Splitting**: Combine PDFs or extract specific pages
- **PDF Creation**: Generate PDFs with text, images, tables, and graphics
- **Watermarks & Annotations**: Add text/image watermarks and annotations
- **Metadata Management**: Extract and modify PDF metadata
- **Security**: Password protection and encryption
- **OCR Support**: Extract text from scanned documents
- **Optimization**: Compress and optimize PDF files

## Python Libraries Overview

- **pypdf**: Basic operations (merge, split, rotate, metadata)
- **pdfplumber**: Advanced text/table extraction with layout awareness
- **reportlab**: Create PDFs from scratch (reports, invoices, documents)
- **PyMuPDF (fitz)**: Advanced manipulation, annotations, compression
- **pdf2image**: Convert PDF pages to images (requires poppler)
- **pytesseract**: OCR for scanned documents (requires tesseract)

## Common Use Cases

### Extract Data from Invoices
Use pdfplumber to extract tables and structured data from PDF invoices for automated processing.

### Generate Reports Programmatically
Create professional PDF reports with reportlab including charts, tables, and formatted text.

### Fill PDF Forms in Bulk
Automate form filling using PyMuPDF for contracts, applications, or surveys.

### Merge Multiple PDFs
Combine multiple PDF files into a single document with pypdf.

### OCR Scanned Documents
Use pytesseract to extract text from scanned PDFs and create searchable PDFs.

## Best Practices

1. **Choose the right library** - Use pypdf for basic operations, pdfplumber for extraction, reportlab for creation
2. **Handle errors** - Always use try-except blocks for PDF operations
3. **Check for encryption** - Decrypt PDFs before processing
4. **Use OCR fallback** - Detect scanned documents and apply OCR when needed
5. **Process in chunks** - Handle large PDFs in chunks to manage memory
6. **Validate inputs** - Check file existence and format before processing
7. **Close documents** - Always close PyMuPDF documents to free resources

## Common Pitfalls

- **Scanned Documents**: Text extraction returns empty - use OCR (pytesseract)
- **Table Detection**: Tables not detected - adjust table_settings strategies
- **Encrypted PDFs**: Operations fail - check and decrypt with password first
- **Memory Issues**: Large PDFs cause crashes - process in chunks with garbage collection
- **Encoding Issues**: Special characters corrupted - handle with UTF-8 encoding

For detailed solutions, see [Best Practices and Common Pitfalls](./references/best-practices.md).

## Documentation

See `SKILL.md` for comprehensive documentation, detailed workflows, and advanced techniques.

## Requirements

- Python 3.7+
- pypdf
- pdfplumber
- reportlab
- PyMuPDF (fitz)
- pdf2image (optional, for image conversion)
- pytesseract (optional, for OCR)
- Pillow

System dependencies:
- poppler (for pdf2image)
- tesseract (for OCR)
