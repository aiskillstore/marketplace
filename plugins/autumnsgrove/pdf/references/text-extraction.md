# Text Extraction Reference

## Basic Text Extraction (pypdf)

```python
from pypdf import PdfReader

def extract_text_basic(pdf_path):
    """Extract all text from a PDF using pypdf."""
    reader = PdfReader(pdf_path)
    text = ""

    for page_num, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()
        text += f"--- Page {page_num} ---\n{page_text}\n\n"

    return text

# Usage
text = extract_text_basic("document.pdf")
print(text)
```

## Advanced Text Extraction with Layout (pdfplumber)

```python
import pdfplumber

def extract_text_with_layout(pdf_path):
    """Extract text preserving layout information."""
    results = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            # Extract text
            text = page.extract_text()

            # Extract words with positioning
            words = page.extract_words()

            results.append({
                'page': page_num,
                'text': text,
                'words': words,
                'width': page.width,
                'height': page.height
            })

    return results

# Usage
pages = extract_text_with_layout("document.pdf")
for page_data in pages:
    print(f"Page {page_data['page']}:")
    print(page_data['text'])
    print(f"Total words: {len(page_data['words'])}")
```

## Extract Text from Specific Regions

```python
import pdfplumber

def extract_text_from_region(pdf_path, page_num, bbox):
    """
    Extract text from a specific region.

    Args:
        pdf_path: Path to PDF
        page_num: Page number (0-indexed)
        bbox: Tuple (x0, y0, x1, y1) defining the region
    """
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num]

        # Crop to specific region
        cropped = page.crop(bbox)
        text = cropped.extract_text()

        return text

# Usage - Extract header region
header_text = extract_text_from_region(
    "document.pdf",
    page_num=0,
    bbox=(0, 0, 612, 100)  # Top 100 points
)
```

## Handle Text Encoding Issues

```python
import pdfplumber

def extract_text_safe(pdf_path):
    """Extract text with proper encoding handling."""
    with pdfplumber.open(pdf_path) as pdf:
        all_text = []

        for page in pdf.pages:
            text = page.extract_text()

            if text:
                # Handle encoding issues
                text = text.encode('utf-8', errors='ignore').decode('utf-8')
                all_text.append(text)

        return "\n\n".join(all_text)
```

## Extract Text with OCR Fallback

```python
import fitz

def extract_text_with_ocr_fallback(pdf_path):
    """Try text extraction, fall back to OCR if needed."""
    doc = fitz.open(pdf_path)
    page = doc[0]
    text = page.get_text()

    if not text.strip():
        print("No text found, using OCR...")
        from pdf2image import convert_from_path
        import pytesseract

        images = convert_from_path(pdf_path)
        text = pytesseract.image_to_string(images[0])

    return text
```

## Handle Page Rotation

```python
import fitz

def extract_text_handle_rotation(pdf_path):
    """Extract text accounting for page rotation."""
    doc = fitz.open(pdf_path)

    for page in doc:
        # Check rotation
        rotation = page.rotation

        if rotation != 0:
            # Rotate page to 0 degrees
            page.set_rotation(0)

        text = page.get_text()
        print(text)

    doc.close()
```

## Memory-Efficient Processing for Large PDFs

```python
from pypdf import PdfReader
import gc

def process_large_pdf_in_chunks(pdf_path, chunk_size=10):
    """Process large PDFs in chunks to manage memory."""
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    for start in range(0, total_pages, chunk_size):
        end = min(start + chunk_size, total_pages)

        # Process chunk
        for page_num in range(start, end):
            page = reader.pages[page_num]
            text = page.extract_text()

            # Process text here
            yield page_num, text

        # Force garbage collection
        gc.collect()

# Usage
for page_num, text in process_large_pdf_in_chunks("large_file.pdf"):
    print(f"Processing page {page_num}")
```

## Preserve Document Structure

```python
import pdfplumber

def extract_structured_content(pdf_path):
    """Extract content while preserving structure."""
    with pdfplumber.open(pdf_path) as pdf:
        structured_data = []

        for page in pdf.pages:
            page_data = {
                'page_number': page.page_number,
                'text': page.extract_text(),
                'tables': page.extract_tables(),
                'images': len(page.images),
                'width': page.width,
                'height': page.height
            }

            structured_data.append(page_data)

        return structured_data
```

## Count Words in PDF

```python
import pdfplumber

def count_words_in_pdf(pdf_path):
    """Count total words in PDF."""
    total_words = 0

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                words = text.split()
                total_words += len(words)

    return total_words

# Usage
word_count = count_words_in_pdf("document.pdf")
print(f"Total words: {word_count}")
```

## Error Handling Template

```python
from pypdf import PdfReader
import logging

def safe_pdf_operation(pdf_path):
    """Template for safe PDF operations with error handling."""
    try:
        reader = PdfReader(pdf_path)

        # Check if encrypted
        if reader.is_encrypted:
            logging.warning(f"PDF {pdf_path} is encrypted")
            return None

        # Perform operations
        result = []
        for page in reader.pages:
            try:
                text = page.extract_text()
                result.append(text)
            except Exception as e:
                logging.error(f"Error extracting page: {e}")
                result.append("")

        return result

    except FileNotFoundError:
        logging.error(f"File not found: {pdf_path}")
        return None
    except Exception as e:
        logging.error(f"Error processing PDF: {e}")
        return None
```
