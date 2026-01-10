---
name: file-converter
description: This skill handles file format conversions across documents (PDF, DOCX,
  Markdown, HTML, TXT), data files (JSON, CSV, YAML, XML, TOML), and images (PNG,
  JPG, WebP, SVG, GIF). Use when the user requests converting, transforming, or exporting
  files between formats. Generates conversion code dynamically based on the specific
  request.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# File Converter

## Overview

Convert files between formats across three categories: documents, data files, and images. Generate Python code dynamically for each conversion request, selecting appropriate libraries and handling edge cases.

## Conversion Categories

### Documents

| From | To | Recommended Library |
|------|-----|---------------------|
| Markdown | HTML | `markdown` or `mistune` |
| HTML | Markdown | `markdownify` or `html2text` |
| HTML | PDF | `weasyprint` or `pdfkit` (requires wkhtmltopdf) |
| PDF | Text | `pypdf` or `pdfplumber` |
| DOCX | Markdown | `mammoth` |
| DOCX | PDF | `docx2pdf` (Windows/macOS) or LibreOffice CLI |
| Markdown | PDF | Convert via HTML first, then to PDF |

### Data Files

| From | To | Recommended Library |
|------|-----|---------------------|
| JSON | YAML | `pyyaml` |
| YAML | JSON | `pyyaml` |
| JSON | CSV | `pandas` or stdlib `csv` + `json` |
| CSV | JSON | `pandas` or stdlib `csv` + `json` |
| JSON | TOML | `tomli`/`tomllib` (read) + `tomli-w` (write) |
| XML | JSON | `xmltodict` |
| JSON | XML | `dicttoxml` or `xmltodict.unparse` |

### Images

| From | To | Recommended Library |
|------|-----|---------------------|
| PNG/JPG/WebP/GIF | Any raster | `Pillow` (PIL) |
| SVG | PNG/JPG | `cairosvg` or `svglib` + `reportlab` |
| PNG | SVG | `potrace` (CLI) for tracing, limited fidelity |

## Workflow

1. Identify source format (from file extension or user statement)
2. Identify target format
3. Check `references/` for format-specific guidance
4. Generate conversion code using recommended library
5. Handle edge cases (encoding, transparency, nested structures)
6. Execute conversion and report results

## Quick Patterns

### Data: JSON to YAML

```python
import json
import yaml

with open("input.json") as f:
    data = json.load(f)

with open("output.yaml", "w") as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
```

### Data: CSV to JSON

```python
import csv
import json

with open("input.csv") as f:
    reader = csv.DictReader(f)
    data = list(reader)

with open("output.json", "w") as f:
    json.dump(data, f, indent=2)
```

### Document: Markdown to HTML

```python
import markdown

with open("input.md") as f:
    md_content = f.read()

html = markdown.markdown(md_content, extensions=["tables", "fenced_code"])

with open("output.html", "w") as f:
    f.write(html)
```

### Image: PNG to WebP

```python
from PIL import Image

img = Image.open("input.png")
img.save("output.webp", "WEBP", quality=85)
```

### Image: SVG to PNG

```python
import cairosvg

cairosvg.svg2png(url="input.svg", write_to="output.png", scale=2)
```

## Resources

Detailed guidance for complex conversions is in `references/`:

- `references/document-conversions.md` - PDF handling, encoding issues, styling preservation
- `references/data-conversions.md` - Schema handling, type coercion, nested structures
- `references/image-conversions.md` - Quality settings, transparency, color profiles

Consult these references when handling edge cases or when the user has specific quality/fidelity requirements.
