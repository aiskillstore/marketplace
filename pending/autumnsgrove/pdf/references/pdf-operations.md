# PDF Operations Reference

## Forms

### Fill PDF Forms (PyMuPDF)

```python
import fitz

def fill_pdf_form(input_pdf, output_pdf, field_values):
    """
    Fill PDF form fields.

    Args:
        input_pdf: Path to input PDF with form fields
        output_pdf: Path to save filled PDF
        field_values: Dictionary of {field_name: value}
    """
    doc = fitz.open(input_pdf)

    for page_num in range(len(doc)):
        page = doc[page_num]

        for widget in page.widgets():
            if widget.field_name in field_values:
                widget.field_value = field_values[widget.field_name]
                widget.update()

    doc.save(output_pdf)
    doc.close()

# Usage
form_data = {
    "name": "John Doe",
    "email": "john@example.com",
    "date": "2025-10-25",
    "signature": "John Doe"
}
fill_pdf_form("form_template.pdf", "filled_form.pdf", form_data)
```

### Extract Form Field Names

```python
import fitz

def get_form_fields(pdf_path):
    """Extract all form field names and their current values."""
    doc = fitz.open(pdf_path)
    fields = []

    for page_num in range(len(doc)):
        page = doc[page_num]

        for widget in page.widgets():
            fields.append({
                'page': page_num + 1,
                'name': widget.field_name,
                'type': widget.field_type_string,
                'value': widget.field_value
            })

    doc.close()
    return fields

# Usage
fields = get_form_fields("form.pdf")
for field in fields:
    print(f"{field['name']}: {field['type']} = {field['value']}")
```

### Debug Form Fields

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

### Flatten PDF Forms

```python
import fitz

def flatten_pdf_form(input_pdf, output_pdf):
    """Flatten form fields to make them non-editable."""
    doc = fitz.open(input_pdf)

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Get all widgets (form fields)
        for widget in page.widgets():
            # This makes the field non-editable
            widget.update()

    # Save with form fields flattened
    doc.save(output_pdf, garbage=4, deflate=True)
    doc.close()
```

## Merging

### Basic Merge

```python
from pypdf import PdfMerger

def merge_pdfs(pdf_list, output_path):
    """Merge multiple PDFs into one."""
    merger = PdfMerger()

    for pdf in pdf_list:
        merger.append(pdf)

    merger.write(output_path)
    merger.close()

# Usage
pdfs = ["file1.pdf", "file2.pdf", "file3.pdf"]
merge_pdfs(pdfs, "merged_output.pdf")
```

### Merge with Page Ranges

```python
from pypdf import PdfMerger

def merge_pdfs_with_ranges(pdf_configs, output_path):
    """
    Merge PDFs with specific page ranges.

    Args:
        pdf_configs: List of dicts with 'path', 'pages' keys
        output_path: Output file path

    Example:
        configs = [
            {'path': 'doc1.pdf', 'pages': (0, 3)},  # First 3 pages
            {'path': 'doc2.pdf', 'pages': (5, 10)}, # Pages 6-10
        ]
    """
    merger = PdfMerger()

    for config in pdf_configs:
        path = config['path']
        pages = config.get('pages')

        if pages:
            merger.append(path, pages=pages)
        else:
            merger.append(path)

    merger.write(output_path)
    merger.close()

# Usage
configs = [
    {'path': 'intro.pdf', 'pages': (0, 2)},
    {'path': 'content.pdf'},  # All pages
    {'path': 'appendix.pdf', 'pages': (10, 15)}
]
merge_pdfs_with_ranges(configs, "compiled.pdf")
```

### Merge with Bookmarks

```python
from pypdf import PdfMerger

def merge_with_bookmarks(pdf_list, output_path, bookmark_names=None):
    """Merge PDFs and add bookmarks for each document."""
    merger = PdfMerger()

    if bookmark_names is None:
        bookmark_names = [f"Document {i+1}" for i in range(len(pdf_list))]

    for pdf, bookmark in zip(pdf_list, bookmark_names):
        merger.append(pdf, outline_item=bookmark)

    merger.write(output_path)
    merger.close()

# Usage
pdfs = ["chapter1.pdf", "chapter2.pdf", "chapter3.pdf"]
bookmarks = ["Introduction", "Methods", "Results"]
merge_with_bookmarks(pdfs, "thesis.pdf", bookmarks)
```

## Splitting

### Split into Individual Pages

```python
from pypdf import PdfReader, PdfWriter
import os

def split_pdf_pages(input_pdf, output_dir):
    """Split PDF into individual pages."""
    reader = PdfReader(input_pdf)

    os.makedirs(output_dir, exist_ok=True)

    for page_num, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)

        output_path = os.path.join(output_dir, f"page_{page_num + 1}.pdf")
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

    print(f"Split {len(reader.pages)} pages into {output_dir}")

# Usage
split_pdf_pages("document.pdf", "split_pages/")
```

### Split by Page Ranges

```python
from pypdf import PdfReader, PdfWriter

def split_pdf_ranges(input_pdf, ranges, output_paths):
    """
    Split PDF into multiple files by page ranges.

    Args:
        input_pdf: Input PDF path
        ranges: List of tuples (start, end) - pages are 0-indexed
        output_paths: List of output file paths
    """
    reader = PdfReader(input_pdf)

    for (start, end), output_path in zip(ranges, output_paths):
        writer = PdfWriter()

        for page_num in range(start, end):
            writer.add_page(reader.pages[page_num])

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

# Usage
ranges = [(0, 5), (5, 10), (10, 15)]
outputs = ["part1.pdf", "part2.pdf", "part3.pdf"]
split_pdf_ranges("document.pdf", ranges, outputs)
```

### Split by Size

```python
from pypdf import PdfReader, PdfWriter
import os

def split_pdf_by_size(input_pdf, max_size_mb, output_dir):
    """Split PDF into chunks not exceeding max size."""
    reader = PdfReader(input_pdf)

    os.makedirs(output_dir, exist_ok=True)

    current_writer = PdfWriter()
    current_size = 0
    file_count = 1

    for page in reader.pages:
        current_writer.add_page(page)

        # Estimate size (approximate)
        temp_path = f"/tmp/temp_check.pdf"
        with open(temp_path, 'wb') as f:
            current_writer.write(f)

        current_size = os.path.getsize(temp_path) / (1024 * 1024)  # MB

        if current_size >= max_size_mb:
            output_path = os.path.join(output_dir, f"part_{file_count}.pdf")
            with open(output_path, 'wb') as f:
                current_writer.write(f)

            current_writer = PdfWriter()
            current_size = 0
            file_count += 1

        os.remove(temp_path)

    # Write remaining pages
    if len(current_writer.pages) > 0:
        output_path = os.path.join(output_dir, f"part_{file_count}.pdf")
        with open(output_path, 'wb') as f:
            current_writer.write(f)
```

## Page Operations

### Rotate Pages

```python
from pypdf import PdfReader, PdfWriter

def rotate_pages(input_pdf, output_pdf, rotation=90, pages=None):
    """
    Rotate specific pages in PDF.

    Args:
        rotation: Degrees to rotate (90, 180, 270)
        pages: List of page numbers (0-indexed), or None for all pages
    """
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page_num, page in enumerate(reader.pages):
        if pages is None or page_num in pages:
            page.rotate(rotation)
        writer.add_page(page)

    with open(output_pdf, 'wb') as output_file:
        writer.write(output_file)

# Usage
rotate_pages("document.pdf", "rotated.pdf", rotation=90, pages=[0, 2, 4])
```

### Extract Images

```python
import fitz
import os

def extract_images(pdf_path, output_dir):
    """Extract all images from PDF."""
    doc = fitz.open(pdf_path)
    os.makedirs(output_dir, exist_ok=True)

    image_count = 0

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

            image_count += 1

    print(f"Extracted {image_count} images to {output_dir}")
    doc.close()

# Usage
extract_images("document.pdf", "extracted_images/")
```

### Convert Images to PDF

```python
from PIL import Image
from reportlab.pdfgen import canvas

def images_to_pdf(image_paths, output_pdf):
    """Convert multiple images to a single PDF."""
    c = canvas.Canvas(output_pdf)

    for img_path in image_paths:
        img = Image.open(img_path)
        width, height = img.size

        # Set page size to image size
        c.setPageSize((width, height))

        # Draw image
        c.drawImage(img_path, 0, 0, width=width, height=height)
        c.showPage()

    c.save()

# Usage
images = ["scan1.jpg", "scan2.jpg", "scan3.jpg"]
images_to_pdf(images, "scanned_document.pdf")
```
