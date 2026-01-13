# PowerPoint (PPTX) Skill

Professional PowerPoint presentation creation, editing, and automation with support for layouts, templates, charts, images, and formatting.

## Overview

Create and edit professional PowerPoint presentations programmatically using Python's `python-pptx` library. This skill enables you to automate presentation creation, apply templates and themes, add charts and visualizations, and bulk-generate slides from data.

## Installation

Install the required library:

```bash
pip install python-pptx
# or with uv
uv pip install python-pptx
```

Basic imports:

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Cm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
```

For complete library setup and supporting packages, see `references/library-setup.md`.

## What's Included

### SKILL.md
Comprehensive guide covering all PowerPoint operations including creating presentations, adding slides, working with layouts, adding charts and tables, applying themes, and bulk generation workflows.

### scripts/
- `pptx_helper.py` - Utility functions for common presentation operations including:
  - `create_presentation()` - Initialize with defaults
  - `add_title_slide()` - Add formatted title slide
  - `add_bullet_slide()` - Add slide with bullet points
  - `add_image_slide()` - Add slide with centered image
  - `add_chart_slide()` - Add slide with chart
  - `add_table_slide()` - Add formatted table
  - `apply_brand_colors()` - Apply consistent color scheme
  - `optimize_images()` - Batch optimize images

### examples/
- `business-presentation.md` - Complete business presentation workflow
- `chart-examples.md` - All chart types (bar, line, pie)
- `image-handling.md` - Advanced image techniques
- `table-examples.md` - Table formatting
- `editing-presentations.md` - Modifying existing presentations
- `bulk-generation.md` - Bulk slide generation from data

### references/
- `library-setup.md` - Installation and dependencies
- `design-best-practices.md` - Professional design guidelines
- `templates-and-themes.md` - Master slide customization
- `advanced-techniques.md` - Advanced PowerPoint features
- `troubleshooting.md` - Common issues and solutions

## Quick Start

### Create a Simple Presentation

```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()
prs.slide_width = Inches(10)
prs.slide_height = Inches(7.5)

# Title slide
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "Q4 Business Review"
slide.placeholders[1].text = "Prepared by: Jane Doe\nDate: October 25, 2025"

prs.save('presentation.pptx')
```

### Add a Chart

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

chart_data = CategoryChartData()
chart_data.categories = ['Q1', 'Q2', 'Q3', 'Q4']
chart_data.add_series('2025', (9.5, 10.8, 11.2, 13.1))

chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED,
    Inches(1), Inches(2), Inches(8), Inches(4.5),
    chart_data
).chart
```

### Add an Image

```python
# Add image with auto-scaled aspect ratio
pic = slide.shapes.add_picture('logo.png', Inches(1), Inches(1), height=Inches(2))

# Center image on slide
pic.left = int((prs.slide_width - pic.width) / 2)
pic.top = int((prs.slide_height - pic.height) / 2)
```

### Create a Table

```python
table = slide.shapes.add_table(4, 3, Inches(1.5), Inches(2), Inches(7), Inches(3)).table

# Header formatting
cell = table.cell(0, 0)
cell.text = "Product"
cell.text_frame.paragraphs[0].font.bold = True
cell.fill.solid()
cell.fill.fore_color.rgb = RGBColor(0, 51, 102)
```

## Key Features

- **Presentation Creation**: New presentations with custom dimensions and metadata
- **Slide Management**: Add, duplicate, delete, reorder slides with predefined layouts
- **Content Types**: Text, shapes, images, tables, charts, SmartArt, hyperlinks
- **Design & Formatting**: Themes, color schemes, fonts, fills, borders, effects
- **Charts**: Bar, column, line, pie, scatter, area charts with full customization
- **Tables**: Formatted tables with cell styling and merged cells
- **Templates**: Use and create master slide templates for consistent branding
- **Bulk Generation**: Generate multiple slides from data sources (CSV, JSON, databases)
- **Editing**: Modify existing presentations programmatically

## Core Workflows

### Workflow 1: Creating a Business Presentation
1. Initialize presentation with proper dimensions
2. Add title slide with company branding
3. Add content slides using appropriate layouts
4. Insert charts and visualizations
5. Apply consistent formatting and themes
6. Save presentation

See `examples/business-presentation.md` for complete implementation.

### Workflow 2: Bulk Slide Generation
1. Load data from CSV, JSON, or database
2. Create presentation object
3. Iterate through data records
4. Generate one slide per record with data population
5. Apply consistent formatting
6. Save final presentation

See `examples/bulk-generation.md` for complete examples.

## Design Best Practices

### Color & Typography
- Use 60-30-10 color rule (60% primary, 30% secondary, 10% accent)
- Ensure WCAG AA contrast ratios (4.5:1 minimum)
- Limit to 2 font families maximum
- Minimum body text: 18pt for readability

### Layout & Composition
- Follow rule of thirds for element placement
- Maintain minimum 0.5" margins on all sides
- Limit to 5-7 elements per slide
- Use consistent alignment (snap to grid)

### Chart Best Practices
- Choose appropriate chart type (bar for comparison, line for trends, pie for parts-of-whole)
- Limit to 3-5 colors maximum
- Always label axes and include data labels
- Use gridlines sparingly

For complete design guidelines, see `references/design-best-practices.md`.

## Common Use Cases

### Automated Report Generation
Generate monthly business reports from database data with charts and tables.

### Template-Based Presentations
Create presentations using corporate templates for consistent branding.

### Bulk Presentation Creation
Generate individual presentations for multiple clients or products from data.

### Editing Existing Presentations
Update existing presentations with new data or branding changes.

## Helper Script Usage

```python
from scripts.pptx_helper import create_presentation, add_title_slide, add_chart_slide

prs = create_presentation(title="My Presentation")
add_title_slide(prs, "Main Title", "Subtitle")
add_chart_slide(prs, "Sales Data", chart_type='bar',
                categories=['Q1', 'Q2', 'Q3', 'Q4'],
                values=[10, 20, 15, 25])
prs.save('output.pptx')
```

## Best Practices Summary

1. Always use templates for consistent branding
2. Optimize images before adding to presentation
3. Limit text on each slide (5-7 bullet points max)
4. Use high contrast for readability
5. Test on target device before presenting
6. Keep file size manageable (<20MB for email)
7. Use speaker notes for detailed talking points
8. Follow 6x6 rule: Max 6 bullets, max 6 words per bullet
9. Validate data before creating charts
10. Use consistent spacing and alignment

## Troubleshooting Quick Reference

**"ModuleNotFoundError: No module named 'pptx'"**
```bash
pip install python-pptx
```

**"AttributeError: 'NoneType' object has no attribute..."**
- Check placeholder indices: `[p.placeholder_format.idx for p in slide.placeholders]`
- Verify layout has expected placeholders

**Images not found**
- Use absolute paths: `os.path.abspath('image.png')`
- Verify file exists: `os.path.exists(img_path)`

**File size too large**
- Compress images before adding (use Pillow)
- Resize images to presentation dimensions (1920x1080 max)

For complete troubleshooting, see `references/troubleshooting.md`.

## Documentation

See `SKILL.md` for comprehensive documentation, detailed workflows, and advanced techniques.

## Requirements

- Python 3.7+
- python-pptx
- Pillow (optional, for image optimization)
- pandas (optional, for bulk generation from CSV)
