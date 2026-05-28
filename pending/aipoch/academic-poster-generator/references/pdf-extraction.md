# PDF Extraction Reference

Comprehensive guide for extracting content from research papers for poster creation.

## Advanced Text Extraction

### Section-by-Section Extraction

Extract specific sections systematically:

```python
import pdfplumber
import re

def extract_section(pdf_path, section_name):
    """Extract a specific section from PDF"""
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"

    # Find section start and end
    pattern = rf'(?i){section_name}\s*\n(.*?)(?=\n[A-Z][a-z]+\s*\n|$)'
    match = re.search(pattern, full_text, re.DOTALL)

    if match:
        return match.group(1).strip()
    return None

# Usage
abstract = extract_section("paper.pdf", "abstract")
methods = extract_section("paper.pdf", "methods")
results = extract_section("paper.pdf", "results")
conclusion = extract_section("paper.pdf", "conclusion")
```

### Extracting Title and Authors

```python
def extract_title_authors(pdf_path):
    """Extract title and authors from first page"""
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()

    # Find title (usually first non-empty line)
    lines = text.split('\n')
    title = None
    authors = []

    for i, line in enumerate(lines):
        line = line.strip()
        if line and not title:
            title = line
        elif title and line:
            # Check if author line (contains common author markers)
            if any(marker in line.lower() for marker in ['university', 'institute', 'lab', 'dept']):
                break
            authors.append(line)
        elif title and len(authors) > 0:
            break

    return title, ', '.join(authors)
```

## Table Extraction

### Basic Table Extraction

```python
import pdfplumber

def extract_all_tables(pdf_path):
    """Extract all tables from PDF"""
    all_tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            for table_num, table in enumerate(tables, 1):
                if table:
                    table_data = {
                        'page': page_num,
                        'table_num': table_num,
                        'data': table
                    }
                    all_tables.append(table_data)
    return all_tables

tables = extract_all_tables("paper.pdf")
for table in tables:
    print(f"Table {table['table_num']} on page {table['page']}")
```

### Advanced Table Processing

```python
import pandas as pd

def extract_tables_to_dataframe(pdf_path):
    """Extract tables and convert to pandas DataFrames"""
    dataframes = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            for table_num, table in enumerate(tables, 1):
                if table and len(table) > 1:
                    # First row as header, rest as data
                    df = pd.DataFrame(table[1:], columns=table[0])
                    df['page'] = page_num
                    df['table_num'] = table_num
                    dataframes.append(df)
    return dataframes

# Convert tables to LaTeX format for poster
dfs = extract_tables_to_dataframe("paper.pdf")
for df in dfs:
    print(df.to_latex(index=False))
```

### Table Quality Improvement

```python
def clean_table(table):
    """Clean extracted table data"""
    cleaned = []
    for row in table:
        cleaned_row = []
        for cell in row:
            if cell is None:
                cleaned_row.append('')
            else:
                # Remove extra whitespace
                cleaned_cell = ' '.join(str(cell).split())
                cleaned_row.append(cleaned_cell)
        cleaned.append(cleaned_row)
    return cleaned
```

## Image Extraction

### Using pdfimages

```bash
# Extract all images from PDF
pdfimages -j paper.pdf images/image

# Extract specific page
pdfimages -f 1 -l 1 paper.pdf images/page1
```

### Using pdfplumber for Image Locations

```python
def extract_image_info(pdf_path):
    """Get information about images in PDF"""
    image_info = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            if page.images:
                for img_num, img in enumerate(page.images, 1):
                    info = {
                        'page': page_num,
                        'image_num': img_num,
                        'width': img['width'],
                        'height': img['height'],
                        'x0': img['x0'],
                        'y0': img['y0'],
                        'x1': img['x1'],
                        'y1': img['y1']
                    }
                    image_info.append(info)
    return image_info

images = extract_image_info("paper.pdf")
```

## OCR for Scanned PDFs

### Basic OCR Setup

```python
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

def ocr_pdf(pdf_path, output_txt_path):
    """OCR scanned PDF and save text"""
    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=300)

    full_text = ""
    for i, image in enumerate(images, 1):
        # OCR each page
        text = pytesseract.image_to_string(image)
        full_text += f"--- Page {i} ---\n"
        full_text += text + "\n\n"

    # Save to file
    with open(output_txt_path, 'w', encoding='utf-8') as f:
        f.write(full_text)

    return full_text

text = ocr_pdf("scanned_paper.pdf", "extracted_text.txt")
```

### Enhanced OCR with Page Segmentation

```python
def ocr_with_layout(pdf_path):
    """OCR with layout preservation"""
    images = convert_from_path(pdf_path, dpi=300)

    results = []
    for i, image in enumerate(images, 1):
        # Use different page segmentation modes
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, config=custom_config)

        # Extract data in structured format
        data = pytesseract.image_to_data(image, config=custom_config, output_type='dict')

        results.append({
            'page': i,
            'text': text,
            'data': data
        })

    return results
```

## Metadata Extraction

```python
from pypdf import PdfReader

def extract_metadata(pdf_path):
    """Extract PDF metadata"""
    reader = PdfReader(pdf_path)
    meta = reader.metadata

    metadata = {
        'title': meta.title,
        'author': meta.author,
        'subject': meta.subject,
        'creator': meta.creator,
        'producer': meta.producer,
        'creation_date': meta.get('/CreationDate'),
        'modification_date': meta.get('/ModDate'),
        'num_pages': len(reader.pages)
    }

    return metadata

metadata = extract_metadata("paper.pdf")
```

## Content Summarization for Poster

### Extract Key Sentences

```python
import re

def extract_key_sentences(text, num_sentences=5):
    """Extract key sentences using simple heuristics"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # Score sentences by length and keywords
    keywords = ['important', 'significant', 'key', 'result', 'finding', 'conclusion']
    scored = []

    for sentence in sentences:
        score = len(sentence.split())
        for keyword in keywords:
            if keyword in sentence.lower():
                score += 2
        scored.append((sentence, score))

    # Sort by score and return top N
    scored.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in scored[:num_sentences]]

# Usage
results_text = extract_section("paper.pdf", "results")
key_points = extract_key_sentences(results_text, 5)
```

### Extract Statistics and Numbers

```python
def extract_numbers_with_context(text, window_size=20):
    """Extract numbers with surrounding context"""
    pattern = r'\b\d+(?:\.\d+)?%?\b'
    matches = list(re.finditer(pattern, text))

    results = []
    for match in matches:
        start = max(0, match.start() - window_size)
        end = min(len(text), match.end() + window_size)
        context = text[start:end].strip()
        results.append({
            'number': match.group(),
            'context': context
        })

    return results

# Usage to find key statistics
results_text = extract_section("paper.pdf", "results")
stats = extract_numbers_with_context(results_text)
```

## Troubleshooting Extraction Issues

### Problem: Text extraction returns empty strings

**Solution:** Try different extraction methods:
```python
# Method 1: extract_text()
text = page.extract_text()

# Method 2: extract_words() and reconstruct
words = page.extract_words()
text = ' '.join([w['text'] for w in words])

# Method 3: Use pdfminer.six
from pdfminer.high_level import extract_text
text = extract_text("paper.pdf")
```

### Problem: Tables split across multiple pages

**Solution:** Merge tables from consecutive pages:
```python
def merge_split_tables(tables, max_gap=0.1):
    """Merge tables that span multiple pages"""
    merged = []
    current_table = None

    for table in tables:
        if current_table is None:
            current_table = table['data']
        else:
            # Check if this is a continuation
            if len(current_table[0]) == len(table['data'][0]):
                # Same number of columns - likely continuation
                # Remove header row if present
                if current_table[0] == table['data'][0]:
                    table['data'].pop(0)
                current_table.extend(table['data'])
            else:
                # Different structure - start new table
                merged.append(current_table)
                current_table = table['data']

    if current_table:
        merged.append(current_table)

    return merged
```

### Problem: OCR produces garbled text

**Solution:** Improve image preprocessing:
```python
import cv2
import numpy as np

def preprocess_image(image):
    """Preprocess image for better OCR"""
    # Convert to grayscale
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

    # Apply threshold
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(binary, h=10)

    return Image.fromarray(denoised)

# Use in OCR
images = convert_from_path("scanned.pdf", dpi=300)
for image in images:
    processed = preprocess_image(image)
    text = pytesseract.image_to_string(processed)
```

## Best Practices

1. **Always verify extraction quality** - Check extracted content against original PDF
2. **Handle edge cases** - Empty pages, missing sections, malformed tables
3. **Preserve structure** - Keep track of page numbers and section boundaries
4. **Log extraction process** - Save what was extracted from where
5. **Test on sample papers** - Develop extraction patterns on known-good PDFs
