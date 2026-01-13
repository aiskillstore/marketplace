# PDF Library Installation Guide

## Quick Installation

Install all required libraries:

```bash
pip install pypdf pdfplumber reportlab PyMuPDF pdf2image pytesseract pillow
```

## Individual Libraries

### 1. pypdf (PyPDF2)
**Purpose**: Basic PDF operations (merging, splitting, rotation)

```bash
pip install pypdf
```

```python
from pypdf import PdfReader, PdfWriter, PdfMerger
```

**Use for**: Merging, splitting, rotating pages, extracting metadata

### 2. pdfplumber
**Purpose**: Advanced text and table extraction with layout awareness

```bash
pip install pdfplumber
```

```python
import pdfplumber
```

**Use for**: Extracting text with positioning, table detection, precise layout analysis

### 3. reportlab
**Purpose**: Creating PDFs from scratch

```bash
pip install reportlab
```

```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
```

**Use for**: Generating reports, invoices, certificates, custom PDFs

### 4. PyMuPDF (fitz)
**Purpose**: Advanced PDF manipulation, rendering, and conversion

```bash
pip install PyMuPDF
```

```python
import fitz  # PyMuPDF
```

**Use for**: Advanced operations, image extraction, annotations, rendering, compression

### 5. pdf2image
**Purpose**: Converting PDF pages to images

```bash
pip install pdf2image
```

**Requires poppler:**
```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt-get install poppler-utils

# Windows
# Download from https://github.com/oschwartz10612/poppler-windows/releases/
```

```python
from pdf2image import convert_from_path
```

### 6. pytesseract (for OCR)
**Purpose**: OCR for scanned documents

```bash
pip install pytesseract
```

**Requires tesseract:**
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows
# Download from https://github.com/UB-Mannheim/tesseract/wiki
```

```python
import pytesseract
from PIL import Image
```

## System Dependencies

### macOS
```bash
brew install poppler tesseract
```

### Ubuntu/Debian
```bash
sudo apt-get install poppler-utils tesseract-ocr
```

### Windows
1. Install poppler from: https://github.com/oschwartz10612/poppler-windows/releases/
2. Install tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
3. Add both to system PATH

## Troubleshooting

### Import Errors
If you encounter import errors, ensure you're using the correct package names:
- Use `pypdf` (not `PyPDF2` for newer versions)
- Use `import fitz` for PyMuPDF

### Missing System Dependencies
If pdf2image or pytesseract fail, verify system dependencies are installed:
```bash
# Test poppler
pdftoppm -v

# Test tesseract
tesseract --version
```

### Version Conflicts
For compatibility, use these version ranges:
```bash
pip install 'pypdf>=3.0.0' 'pdfplumber>=0.9.0' 'reportlab>=4.0.0' 'PyMuPDF>=1.23.0'
```
