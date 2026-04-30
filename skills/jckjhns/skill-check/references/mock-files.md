# Mock File Generation

## Contents

- [Dependencies](#dependencies)
- [Text-based formats](#text-based-formats) — CSV, JSON, Markdown, Plain text, HTML, XML
- [Spreadsheet formats](#spreadsheet-formats) — Excel, TSV
- [Document formats](#document-formats) — Word, PowerPoint, PDF
- [Image formats](#image-formats) — PNG/JPG/WEBP/GIF, SVG
- [Archive formats](#archive-formats) — ZIP
- [Code files](#code-files)
- [General approach for unlisted types](#general-approach-for-unlisted-types)
- [Matching the skill's schema](#matching-the-skills-schema)

---

When testing a skill's input/output contracts, you need realistic mock files. This reference
covers how to generate them for every file type Claude commonly works with.

The golden rule: **match the skill's spec exactly**. If the skill says "expects a CSV with
columns Name, Date, Amount", your mock CSV must have those exact column names with plausible
data in each. Generic placeholder data ("value_1", "value_2") won't catch bugs where scripts
parse by column name or make assumptions about data types — matching the real schema does.

---

## Dependencies

Mock generation for text-based formats (CSV, JSON, MD, TXT, HTML, XML) uses only Python
built-ins. But generating binary formats requires third-party packages. Before generating
mocks, check what file types you'll need and install the relevant packages.

**Run this at the start of mock generation** — install only what's needed for the file
types the skill actually uses:

```bash
# Check which packages are needed based on the skill's declared I/O types
# Only install what's required — don't install everything unconditionally

# For .xlsx files
pip install openpyxl --break-system-packages -q

# For .docx files
pip install python-docx --break-system-packages -q

# For .pptx files
pip install python-pptx --break-system-packages -q

# For .pdf files
pip install fpdf2 --break-system-packages -q

# For image files (.png, .jpg, .webp, .gif)
pip install Pillow --break-system-packages -q
```

**Quick check before installing** — the package may already be available:

```bash
python3 -c "import openpyxl" 2>/dev/null && echo "openpyxl: available" || echo "openpyxl: needs install"
python3 -c "import docx" 2>/dev/null && echo "python-docx: available" || echo "python-docx: needs install"
python3 -c "import pptx" 2>/dev/null && echo "python-pptx: available" || echo "python-pptx: needs install"
python3 -c "import fpdf" 2>/dev/null && echo "fpdf2: available" || echo "fpdf2: needs install"
python3 -c "import PIL" 2>/dev/null && echo "Pillow: available" || echo "Pillow: needs install"
```

If installation fails (network restrictions, permission issues), fall back to generating
the closest text-based equivalent and note the limitation in the report. For example, if
openpyxl isn't available, generate a CSV instead of an XLSX and note: "Mock was generated
as CSV instead of XLSX because openpyxl couldn't be installed."

---

## Text-based formats

### CSV (.csv)

```python
import csv, io, random, datetime

def generate_mock_csv(columns, num_rows=10, output_path="mock_data.csv"):
    """Generate a CSV with specified columns and realistic data."""
    # Map column names to data generators based on common naming patterns
    generators = {
        "name": lambda: random.choice(["Alice", "Bob", "Charlie", "Diana", "Eve"]),
        "date": lambda: (datetime.date(2024,1,1) + datetime.timedelta(days=random.randint(0,365))).isoformat(),
        "amount": lambda: round(random.uniform(10, 10000), 2),
        "email": lambda: f"{random.choice(['alice','bob','charlie'])}@example.com",
        "id": lambda i=iter(range(1,10000)): next(i),
        "status": lambda: random.choice(["active", "inactive", "pending"]),
        "description": lambda: random.choice(["Widget A", "Service B", "Product C"]),
        "quantity": lambda: random.randint(1, 100),
        "price": lambda: round(random.uniform(1, 500), 2),
        "category": lambda: random.choice(["Electronics", "Clothing", "Food", "Services"]),
    }
    # Default generator for unrecognized columns
    default_gen = lambda: f"value_{random.randint(1, 999)}"

    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for _ in range(num_rows):
            row = []
            for col in columns:
                col_lower = col.lower().strip()
                gen = generators.get(col_lower, default_gen)
                row.append(gen())
            writer.writerow(row)
    return output_path
```

**Edge case variants (Deep Check):**
- Empty: headers only, no rows
- Minimal: headers + 1 row
- Large: 10,000 rows
- Special chars: unicode in values, commas inside quoted fields
- Malformed: inconsistent column counts, mixed delimiters

### JSON (.json)

```python
import json

def generate_mock_json(schema_description, output_path="mock_data.json"):
    """Generate JSON matching a described schema.
    
    Parse the schema_description from the skill's SKILL.md and build
    a matching structure. Common patterns:
    """
    # Example: array of objects with known fields
    mock = [
        {"name": "Alice", "role": "Engineer", "score": 92},
        {"name": "Bob", "role": "Designer", "score": 85},
        {"name": "Charlie", "role": "Manager", "score": 78},
    ]
    with open(output_path, 'w') as f:
        json.dump(mock, f, indent=2)
    return output_path
```

**Edge case variants:**
- Empty: `[]` or `{}`
- Deeply nested: 10+ levels
- Large arrays: 1000+ items
- Special chars: unicode keys, emoji values
- Malformed: trailing commas, single quotes, unquoted keys

### Markdown (.md)

```python
def generate_mock_markdown(sections=3, output_path="mock_doc.md"):
    content = "# Mock Document\n\n"
    for i in range(sections):
        content += f"## Section {i+1}\n\n"
        content += f"This is the content for section {i+1}. "
        content += "It contains enough text to be realistic.\n\n"
        content += "- Point one\n- Point two\n- Point three\n\n"
    with open(output_path, 'w') as f:
        f.write(content)
    return output_path
```

### Plain text (.txt)

Simple — write content appropriate to what the skill expects. If the skill processes logs,
generate fake log lines. If it processes prose, generate paragraphs.

### HTML (.html)

```python
def generate_mock_html(output_path="mock_page.html"):
    html = """<!DOCTYPE html>
<html><head><title>Mock Page</title></head>
<body>
<h1>Mock Document</h1>
<p>This is a paragraph of mock content for testing.</p>
<table>
  <tr><th>Name</th><th>Value</th></tr>
  <tr><td>Alpha</td><td>100</td></tr>
  <tr><td>Beta</td><td>200</td></tr>
</table>
</body></html>"""
    with open(output_path, 'w') as f:
        f.write(html)
    return output_path
```

### XML (.xml)

Similar to HTML — structure it to match whatever schema the skill expects.

---

## Spreadsheet formats

### Excel (.xlsx)

```python
# Requires openpyxl: pip install openpyxl
from openpyxl import Workbook
import random

def generate_mock_xlsx(columns, num_rows=10, output_path="mock_data.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(columns)
    for _ in range(num_rows):
        row = [f"value_{random.randint(1,999)}" for _ in columns]
        ws.append(row)
    wb.save(output_path)
    return output_path
```

**Edge case variants:**
- Multiple sheets
- Merged cells
- Formulas in cells
- Empty sheets
- Very wide (50+ columns)

### TSV (.tsv)

Same as CSV generation but use `\t` as delimiter.

---

## Document formats

### Word (.docx)

```python
# Requires python-docx: pip install python-docx
from docx import Document

def generate_mock_docx(output_path="mock_doc.docx"):
    doc = Document()
    doc.add_heading("Mock Document", 0)
    doc.add_paragraph("This is a mock document for testing purposes.")
    doc.add_heading("Section 1", level=1)
    doc.add_paragraph("Content for section one with enough text to be realistic.")
    table = doc.add_table(rows=3, cols=3)
    table.cell(0,0).text = "Header 1"
    table.cell(0,1).text = "Header 2"
    table.cell(0,2).text = "Header 3"
    for i in range(1, 3):
        for j in range(3):
            table.cell(i,j).text = f"Cell {i},{j}"
    doc.save(output_path)
    return output_path
```

### PowerPoint (.pptx)

```python
# Requires python-pptx: pip install python-pptx
from pptx import Presentation
from pptx.util import Inches

def generate_mock_pptx(num_slides=3, output_path="mock_deck.pptx"):
    prs = Presentation()
    # Title slide
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Mock Presentation"
    slide.placeholders[1].text = "Generated for testing"
    # Content slides
    for i in range(num_slides):
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = f"Slide {i+1}"
        slide.placeholders[1].text = f"Content for slide {i+1}"
    prs.save(output_path)
    return output_path
```

### PDF (.pdf)

```python
# Requires fpdf2: pip install fpdf2
from fpdf import FPDF

def generate_mock_pdf(pages=2, output_path="mock_doc.pdf"):
    pdf = FPDF()
    for i in range(pages):
        pdf.add_page()
        pdf.set_font("Helvetica", size=16)
        pdf.cell(0, 10, f"Mock PDF - Page {i+1}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=12)
        pdf.multi_cell(0, 10, "This is mock content for testing. " * 10)
    pdf.output(output_path)
    return output_path
```

---

## Image formats

### PNG / JPG / WEBP / GIF

```python
# Requires Pillow: pip install Pillow
from PIL import Image, ImageDraw, ImageFont

def generate_mock_image(width=800, height=600, format="PNG", output_path="mock_image.png"):
    img = Image.new('RGB', (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    # Draw a grid and label
    for x in range(0, width, 100):
        draw.line([(x, 0), (x, height)], fill=(200, 200, 200))
    for y in range(0, height, 100):
        draw.line([(0, y), (width, y)], fill=(200, 200, 200))
    draw.text((width//2 - 60, height//2 - 10), "MOCK IMAGE", fill=(100, 100, 100))
    draw.text((10, 10), f"{width}x{height} {format}", fill=(150, 150, 150))
    img.save(output_path, format=format)
    return output_path
```

### SVG (.svg)

```python
def generate_mock_svg(width=800, height=600, output_path="mock_image.svg"):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#f0f0f0"/>
  <text x="{width//2}" y="{height//2}" text-anchor="middle" fill="#999">MOCK SVG</text>
</svg>'''
    with open(output_path, 'w') as f:
        f.write(svg)
    return output_path
```

---

## Archive formats

### ZIP (.zip)

```python
import zipfile

def generate_mock_zip(file_contents: dict, output_path="mock_archive.zip"):
    """file_contents: {"filename.txt": "content", ...}"""
    with zipfile.ZipFile(output_path, 'w') as zf:
        for name, content in file_contents.items():
            zf.writestr(name, content)
    return output_path
```

---

## Code files

For any code file type (.py, .js, .ts, .sh, .sql, etc.), generate syntactically valid
code that matches what the skill expects. If the skill processes Python files, write a
small valid Python module. If it processes SQL, write a few CREATE TABLE / SELECT statements.

---

## General approach for unlisted types

If the skill expects a file type not listed here:

1. Check if it's a text-based format — if so, generate the content as a string and write it
2. Check if there's a Python library for it — search pip
3. If binary and no library, create the simplest valid file of that type you can
4. As a last resort, note in the report that mock generation wasn't possible for that type

## Matching the skill's schema

This reinforces the golden rule from above with a concrete example. If the skill says:
> "Expects a CSV with columns: employee_name, department, salary, start_date"

Then your mock CSV must have those exact column headers with semantically appropriate data:
- employee_name → realistic names (scripts may validate string format)
- department → realistic department names (scripts may use these as group-by keys)
- salary → realistic salary numbers (scripts may do arithmetic on this column)
- start_date → realistic date strings in a common format (scripts may parse dates)

Semantically matched data catches a class of bugs that generic placeholders miss —
type coercion failures, date parsing errors, numeric overflow on realistic values, and
logic that branches on specific column values.
