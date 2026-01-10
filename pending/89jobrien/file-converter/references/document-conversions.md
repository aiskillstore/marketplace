---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: file-converter
---

# Document Conversion Reference

## PDF Handling

### Reading PDFs

**pypdf** (formerly PyPDF2):

- Best for: Simple text extraction, merging, splitting
- Limitation: Poor handling of complex layouts, tables

**pdfplumber**:

- Best for: Table extraction, precise text positioning
- Provides bounding boxes for text elements

```python
import pdfplumber

with pdfplumber.open("input.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        tables = page.extract_tables()
```

### Creating PDFs

**weasyprint**:

- Best for: HTML/CSS to PDF with good styling support
- Requires: Cairo graphics library

```python
from weasyprint import HTML

HTML("input.html").write_pdf("output.pdf")
```

**reportlab**:

- Best for: Programmatic PDF generation
- More control but more verbose

### PDF Edge Cases

- **Scanned PDFs**: Contain images, not text. Use OCR (pytesseract + pdf2image)
- **Encrypted PDFs**: Must decrypt first with password
- **Form fields**: Use pypdf or pdfrw for filling forms

## Encoding Issues

### Text Files

Always specify encoding explicitly:

```python
with open("input.txt", encoding="utf-8") as f:
    content = f.read()
```

Common encodings:

- `utf-8`: Default for modern files
- `latin-1` / `iso-8859-1`: Legacy Windows/European
- `cp1252`: Windows Western European
- `utf-16`: Some Windows exports

Detection when unknown:

```python
import chardet

with open("input.txt", "rb") as f:
    result = chardet.detect(f.read())
    encoding = result["encoding"]
```

## DOCX Handling

### Reading DOCX

**python-docx**:

- Full access to document structure
- Can read paragraphs, tables, images

**mammoth**:

- Best for converting to HTML/Markdown
- Semantic conversion (headings, lists preserved)

```python
import mammoth

with open("input.docx", "rb") as f:
    result = mammoth.convert_to_markdown(f)
    markdown = result.value
```

### DOCX to PDF

Platform-dependent options:

**macOS/Windows** - docx2pdf:

```python
from docx2pdf import convert
convert("input.docx", "output.pdf")
```

**Linux** - LibreOffice CLI:

```bash
libreoffice --headless --convert-to pdf input.docx
```

## Styling Preservation

When converting between formats, styling fidelity varies:

| Conversion | Styling Preserved |
|------------|-------------------|
| DOCX -> HTML | Partial (basic formatting) |
| DOCX -> Markdown | Minimal (headings, lists, bold/italic) |
| HTML -> PDF | Good (with weasyprint + CSS) |
| Markdown -> HTML | Full (via extensions) |
| PDF -> Text | None (text only) |

For maximum fidelity, prefer intermediate HTML with explicit CSS.
