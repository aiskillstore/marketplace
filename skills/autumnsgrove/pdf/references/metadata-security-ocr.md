# Metadata, Security, and OCR Reference

## Metadata Management

### Extract Metadata

```python
from pypdf import PdfReader

def extract_metadata(pdf_path):
    """Extract PDF metadata."""
    reader = PdfReader(pdf_path)
    metadata = reader.metadata

    info = {
        'title': metadata.get('/Title', ''),
        'author': metadata.get('/Author', ''),
        'subject': metadata.get('/Subject', ''),
        'creator': metadata.get('/Creator', ''),
        'producer': metadata.get('/Producer', ''),
        'creation_date': metadata.get('/CreationDate', ''),
        'modification_date': metadata.get('/ModDate', ''),
        'pages': len(reader.pages)
    }

    return info

# Usage
metadata = extract_metadata("document.pdf")
for key, value in metadata.items():
    print(f"{key}: {value}")
```

### Modify Metadata

```python
from pypdf import PdfReader, PdfWriter

def modify_metadata(input_pdf, output_pdf, metadata):
    """
    Modify PDF metadata.

    Args:
        metadata: Dict with keys like '/Title', '/Author', '/Subject', etc.
    """
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Copy all pages
    for page in reader.pages:
        writer.add_page(page)

    # Update metadata
    writer.add_metadata(metadata)

    with open(output_pdf, 'wb') as output_file:
        writer.write(output_file)

# Usage
new_metadata = {
    '/Title': 'Updated Title',
    '/Author': 'John Doe',
    '/Subject': 'Research Paper',
    '/Keywords': 'PDF, Python, Automation'
}
modify_metadata("document.pdf", "updated.pdf", new_metadata)
```

### Extract Comprehensive PDF Information

```python
import fitz

def get_pdf_info(pdf_path):
    """Get comprehensive PDF information."""
    doc = fitz.open(pdf_path)

    info = {
        'metadata': doc.metadata,
        'page_count': doc.page_count,
        'is_encrypted': doc.is_encrypted,
        'is_pdf': doc.is_pdf,
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

# Usage
info = get_pdf_info("document.pdf")
print(f"Pages: {info['page_count']}")
print(f"Title: {info['metadata'].get('title', 'N/A')}")
print(f"Encrypted: {info['is_encrypted']}")
```

## Security and Encryption

### Add Password Protection

```python
from pypdf import PdfReader, PdfWriter

def encrypt_pdf(input_pdf, output_pdf, user_password, owner_password=None):
    """
    Add password protection to PDF.

    Args:
        user_password: Password to open the document
        owner_password: Password for full permissions (optional)
    """
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Copy all pages
    for page in reader.pages:
        writer.add_page(page)

    # Encrypt with password
    if owner_password is None:
        owner_password = user_password

    writer.encrypt(
        user_password=user_password,
        owner_password=owner_password,
        algorithm="AES-256"
    )

    with open(output_pdf, 'wb') as output_file:
        writer.write(output_file)

# Usage
encrypt_pdf("document.pdf", "encrypted.pdf", user_password="user123", owner_password="owner456")
```

### Decrypt PDF

```python
from pypdf import PdfReader, PdfWriter

def decrypt_pdf(input_pdf, output_pdf, password):
    """Remove password protection from PDF."""
    reader = PdfReader(input_pdf)

    # Decrypt
    if reader.is_encrypted:
        reader.decrypt(password)

    writer = PdfWriter()

    # Copy all pages
    for page in reader.pages:
        writer.add_page(page)

    with open(output_pdf, 'wb') as output_file:
        writer.write(output_file)

# Usage
decrypt_pdf("encrypted.pdf", "decrypted.pdf", password="user123")
```

### Handle Encrypted PDFs

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

### Set Permissions

```python
from pypdf import PdfWriter, PdfReader

def set_pdf_permissions(input_pdf, output_pdf, password, allow_printing=True, allow_copying=False):
    """Set specific permissions on PDF."""
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Set permissions
    writer.encrypt(
        user_password=password,
        owner_password=password + "_owner",
        permissions_flag=(
            (0b100 if allow_printing else 0) |
            (0b10000 if allow_copying else 0)
        )
    )

    with open(output_pdf, 'wb') as f:
        writer.write(f)
```

## OCR for Scanned Documents

### Basic OCR

```python
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

def ocr_pdf(pdf_path, output_txt_path=None):
    """
    Perform OCR on scanned PDF.

    Returns extracted text from all pages.
    """
    # Convert PDF to images
    images = convert_from_path(pdf_path)

    all_text = []

    for page_num, image in enumerate(images, start=1):
        # Perform OCR
        text = pytesseract.image_to_string(image)
        all_text.append(f"--- Page {page_num} ---\n{text}\n")

    full_text = "\n".join(all_text)

    # Optionally save to file
    if output_txt_path:
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write(full_text)

    return full_text

# Usage
text = ocr_pdf("scanned_document.pdf", "extracted_text.txt")
print(text)
```

### OCR with Language Support

```python
from pdf2image import convert_from_path
import pytesseract

def ocr_pdf_multilang(pdf_path, languages='eng'):
    """
    Perform OCR with multiple language support.

    Args:
        languages: Language codes separated by '+' (e.g., 'eng+fra+deu')
    """
    images = convert_from_path(pdf_path)
    all_text = []

    for image in images:
        text = pytesseract.image_to_string(image, lang=languages)
        all_text.append(text)

    return "\n\n".join(all_text)

# Usage
text = ocr_pdf_multilang("french_document.pdf", languages='fra')
```

### Create Searchable PDF

```python
from pdf2image import convert_from_path
import pytesseract
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import fitz

def create_searchable_pdf(input_pdf, output_pdf):
    """Convert scanned PDF to searchable PDF with OCR layer."""
    # Convert to images
    images = convert_from_path(input_pdf)

    # Create new PDF with OCR text
    temp_pdfs = []

    for i, image in enumerate(images):
        # Perform OCR
        text = pytesseract.image_to_string(image)

        # Create PDF page with invisible text layer
        temp_pdf = f"/tmp/page_{i}.pdf"
        c = canvas.Canvas(temp_pdf, pagesize=letter)

        # Add invisible OCR text
        c.setFillColorRGB(1, 1, 1, alpha=0)  # Transparent
        text_obj = c.beginText(40, 750)
        text_obj.setFont("Helvetica", 10)

        for line in text.split('\n'):
            text_obj.textLine(line)

        c.drawText(text_obj)
        c.save()

        temp_pdfs.append(temp_pdf)

    # Merge all pages
    from pypdf import PdfMerger
    merger = PdfMerger()
    for pdf in temp_pdfs:
        merger.append(pdf)
    merger.write(output_pdf)
    merger.close()

    # Clean up
    import os
    for pdf in temp_pdfs:
        os.remove(pdf)

# Usage
create_searchable_pdf("scanned.pdf", "searchable.pdf")
```

### OCR with Preprocessing

```python
from pdf2image import convert_from_path
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

def ocr_pdf_enhanced(pdf_path):
    """Perform OCR with image preprocessing for better accuracy."""
    images = convert_from_path(pdf_path)
    all_text = []

    for image in images:
        # Preprocess image
        # Convert to grayscale
        image = image.convert('L')

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2)

        # Sharpen
        image = image.filter(ImageFilter.SHARPEN)

        # Perform OCR
        text = pytesseract.image_to_string(image)
        all_text.append(text)

    return "\n\n".join(all_text)

# Usage
text = ocr_pdf_enhanced("low_quality_scan.pdf")
```

## Watermarks and Annotations

### Add Text Watermark

```python
import fitz

def add_text_watermark(input_pdf, output_pdf, watermark_text, opacity=0.3):
    """Add text watermark to all pages."""
    doc = fitz.open(input_pdf)

    for page in doc:
        # Get page dimensions
        rect = page.rect

        # Add watermark
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

# Usage
add_text_watermark("document.pdf", "watermarked.pdf", "CONFIDENTIAL")
```

### Add Annotations

```python
import fitz

def add_annotations(input_pdf, output_pdf, annotations):
    """
    Add various annotations to PDF.

    Args:
        annotations: List of dicts with 'page', 'type', 'rect', 'content'
    """
    doc = fitz.open(input_pdf)

    for annot in annotations:
        page = doc[annot['page']]
        rect = fitz.Rect(annot['rect'])

        if annot['type'] == 'highlight':
            highlight = page.add_highlight_annot(rect)
            highlight.update()

        elif annot['type'] == 'text':
            text_annot = page.add_text_annot(
                rect.top_left,
                annot['content']
            )
            text_annot.update()

        elif annot['type'] == 'underline':
            underline = page.add_underline_annot(rect)
            underline.update()

        elif annot['type'] == 'strikeout':
            strike = page.add_strikeout_annot(rect)
            strike.update()

    doc.save(output_pdf)
    doc.close()

# Usage
annotations = [
    {
        'page': 0,
        'type': 'highlight',
        'rect': (100, 100, 300, 120)
    },
    {
        'page': 0,
        'type': 'text',
        'rect': (400, 400, 450, 450),
        'content': 'Important note here'
    }
]
add_annotations("document.pdf", "annotated.pdf", annotations)
```

### Add Stamp

```python
import fitz

def add_stamp(input_pdf, output_pdf, stamp_text, position="top-right"):
    """Add a stamp (e.g., 'APPROVED', 'DRAFT') to all pages."""
    doc = fitz.open(input_pdf)

    for page in doc:
        rect = page.rect

        # Determine stamp position
        if position == "top-right":
            stamp_rect = fitz.Rect(rect.width - 150, 20, rect.width - 20, 60)
        elif position == "top-left":
            stamp_rect = fitz.Rect(20, 20, 150, 60)
        elif position == "bottom-right":
            stamp_rect = fitz.Rect(rect.width - 150, rect.height - 60, rect.width - 20, rect.height - 20)
        else:  # center
            stamp_rect = fitz.Rect(rect.width/2 - 75, rect.height/2 - 20, rect.width/2 + 75, rect.height/2 + 20)

        # Add stamp
        page.draw_rect(stamp_rect, color=(1, 0, 0), width=2)
        page.insert_textbox(
            stamp_rect,
            stamp_text,
            fontsize=20,
            align=fitz.TEXT_ALIGN_CENTER,
            color=(1, 0, 0)
        )

    doc.save(output_pdf)
    doc.close()

# Usage
add_stamp("document.pdf", "stamped.pdf", "APPROVED", position="top-right")
```

## Optimization

### Optimize PDF Size

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
