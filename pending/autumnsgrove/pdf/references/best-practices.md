# PDF Best Practices and Common Pitfalls

## Best Practices

### 1. Memory Management for Large PDFs

Process large PDFs in chunks to avoid memory issues:

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

### 2. Handle Text Encoding Issues

Always handle potential encoding problems:

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

### 3. Preserve Document Structure

Extract content while maintaining document structure:

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

### 4. Error Handling Template

Always implement proper error handling:

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

### 5. Optimize PDF Size

Compress and optimize PDFs when file size matters:

```python
import fitz

def optimize_pdf(input_pdf, output_pdf, image_quality=50):
    """Compress and optimize PDF file size."""
    doc = fitz.open(input_pdf)

    # Compress with optimization
    doc.save(
        output_pdf,
        garbage=4,  # Maximum garbage collection
        deflate=True,  # Compress streams
        clean=True,  # Clean up content
        pretty=False  # No pretty-printing
    )

    doc.close()

    import os
    original_size = os.path.getsize(input_pdf) / (1024 * 1024)
    optimized_size = os.path.getsize(output_pdf) / (1024 * 1024)

    print(f"Original: {original_size:.2f} MB")
    print(f"Optimized: {optimized_size:.2f} MB")
    print(f"Reduction: {((original_size - optimized_size) / original_size * 100):.1f}%")

# Usage
optimize_pdf("large_file.pdf", "optimized.pdf")
```

## Common Pitfalls

### 1. Scanned Documents Without OCR

**Problem**: Text extraction returns empty strings for scanned PDFs.

**Solution**: Use OCR (pytesseract + pdf2image)

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

### 2. Table Detection Accuracy

**Problem**: Tables not detected or extracted incorrectly.

**Solution**: Adjust table detection settings

```python
import pdfplumber

def extract_tables_robust(pdf_path):
    """Extract tables with multiple strategies."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]

        # Try different strategies
        strategies = [
            {"vertical_strategy": "lines", "horizontal_strategy": "lines"},
            {"vertical_strategy": "text", "horizontal_strategy": "text"},
            {"vertical_strategy": "lines", "horizontal_strategy": "text"}
        ]

        for strategy in strategies:
            tables = page.extract_tables(table_settings=strategy)
            if tables:
                return tables

        return []
```

### 3. Form Field Identification

**Problem**: Can't find form field names.

**Solution**: Inspect and list all fields first

```python
import fitz

def debug_form_fields(pdf_path):
    """Debug helper to see all form fields."""
    doc = fitz.open(pdf_path)

    print("=== Form Fields ===")
    for page_num in range(len(doc)):
        page = doc[page_num]
        widgets = page.widgets()

        if widgets:
            print(f"\nPage {page_num + 1}:")
            for widget in widgets:
                print(f"  Name: {widget.field_name}")
                print(f"  Type: {widget.field_type_string}")
                print(f"  Value: {widget.field_value}")
                print(f"  Rect: {widget.rect}")
                print("  ---")

    doc.close()
```

### 4. Encrypted PDFs

**Problem**: Operations fail on encrypted PDFs.

**Solution**: Check and handle encryption

```python
from pypdf import PdfReader

def handle_encrypted_pdf(pdf_path, password=None):
    """Safely handle encrypted PDFs."""
    reader = PdfReader(pdf_path)

    if reader.is_encrypted:
        if password:
            success = reader.decrypt(password)
            if success == 0:
                print("Incorrect password")
                return None
        else:
            print("PDF is encrypted, password required")
            return None

    # Now safe to process
    return reader
```

### 5. Page Rotation Issues

**Problem**: Extracted text appears rotated or out of order.

**Solution**: Check and handle page rotation

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

### 6. Memory Issues with Large Files

**Problem**: Out of memory errors when processing large PDFs.

**Solution**: Process in chunks and manage resources

```python
from pypdf import PdfReader
import gc

def process_large_pdf_safe(pdf_path):
    """Process large PDF with memory management."""
    reader = PdfReader(pdf_path)

    for i, page in enumerate(reader.pages):
        # Process one page at a time
        text = page.extract_text()

        # Do something with text
        yield i, text

        # Free memory periodically
        if i % 10 == 0:
            gc.collect()

# Usage
for page_num, text in process_large_pdf_safe("huge.pdf"):
    print(f"Page {page_num}: {len(text)} characters")
```

### 7. Unicode and Special Characters

**Problem**: Special characters or non-ASCII text appears corrupted.

**Solution**: Handle encoding properly

```python
import pdfplumber

def extract_text_unicode_safe(pdf_path):
    """Extract text with proper Unicode handling."""
    with pdfplumber.open(pdf_path) as pdf:
        all_text = []

        for page in pdf.pages:
            text = page.extract_text()

            if text:
                # Normalize Unicode
                import unicodedata
                text = unicodedata.normalize('NFKC', text)

                # Handle encoding issues
                text = text.encode('utf-8', errors='replace').decode('utf-8')

                all_text.append(text)

        return "\n\n".join(all_text)
```

### 8. Missing Dependencies

**Problem**: Import errors or missing system libraries.

**Solution**: Verify all dependencies are installed

```python
def check_dependencies():
    """Check if all required dependencies are available."""
    dependencies = {
        'pypdf': 'pip install pypdf',
        'pdfplumber': 'pip install pdfplumber',
        'reportlab': 'pip install reportlab',
        'fitz': 'pip install PyMuPDF',
        'pdf2image': 'pip install pdf2image (requires poppler)',
        'pytesseract': 'pip install pytesseract (requires tesseract)'
    }

    for module, install_cmd in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {module} is installed")
        except ImportError:
            print(f"✗ {module} is missing. Install with: {install_cmd}")

check_dependencies()
```

## Performance Tips

### 1. Use Appropriate Library for Task

- **Text extraction**: Use `pdfplumber` for layout-aware extraction, `pypdf` for simple extraction
- **Table extraction**: Always use `pdfplumber`
- **PDF creation**: Use `reportlab`
- **Advanced manipulation**: Use `PyMuPDF (fitz)`
- **OCR**: Use `pytesseract` + `pdf2image`

### 2. Batch Processing

Process multiple PDFs efficiently:

```python
from pathlib import Path
import concurrent.futures

def process_pdf_batch(pdf_directory, process_function):
    """Process multiple PDFs in parallel."""
    pdf_files = list(Path(pdf_directory).glob("*.pdf"))

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(process_function, pdf_files)

    return list(results)
```

### 3. Cache Results

Cache expensive operations:

```python
import functools
import hashlib

@functools.lru_cache(maxsize=128)
def extract_text_cached(pdf_path):
    """Cache text extraction results."""
    with open(pdf_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()

    # Actual extraction logic here
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    return ''.join(page.extract_text() for page in reader.pages)
```

## Security Considerations

### 1. Validate Input Files

Always validate PDFs before processing:

```python
import fitz

def validate_pdf(pdf_path):
    """Validate that file is a legitimate PDF."""
    try:
        doc = fitz.open(pdf_path)
        is_valid = doc.is_pdf
        page_count = doc.page_count
        doc.close()

        if not is_valid:
            raise ValueError("File is not a valid PDF")

        if page_count == 0:
            raise ValueError("PDF has no pages")

        return True
    except Exception as e:
        print(f"Validation failed: {e}")
        return False
```

### 2. Sanitize Form Input

When filling forms, sanitize user input:

```python
import re

def sanitize_form_data(data):
    """Sanitize form input to prevent injection."""
    sanitized = {}

    for key, value in data.items():
        if isinstance(value, str):
            # Remove potentially dangerous characters
            value = re.sub(r'[<>\"\'%;()&+]', '', value)
            # Limit length
            value = value[:500]

        sanitized[key] = value

    return sanitized
```

### 3. Handle Temporary Files Securely

Use secure temporary file handling:

```python
import tempfile
import os

def process_pdf_secure(pdf_path):
    """Process PDF with secure temporary file handling."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, "temp.pdf")

        # Do processing
        # ...

        # Temporary files are automatically cleaned up
```
