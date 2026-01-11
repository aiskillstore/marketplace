# Table Examples

Complete examples for creating and formatting tables in PowerPoint.

## Basic Table

```python
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

slide = prs.slides.add_slide(prs.slide_layouts[5])  # Title Only
title = slide.shapes.title
title.text = "Product Comparison"

# Define table dimensions
rows, cols = 4, 3
left = Inches(1.5)
top = Inches(2)
width = Inches(7)
height = Inches(3)

# Add table
table = slide.shapes.add_table(rows, cols, left, top, width, height).table

# Set column widths
table.columns[0].width = Inches(3)
table.columns[1].width = Inches(2)
table.columns[2].width = Inches(2)

# Populate headers
headers = ['Product', 'Price', 'Sales']
for col_idx, header in enumerate(headers):
    cell = table.cell(0, col_idx)
    cell.text = header
    cell.text_frame.paragraphs[0].font.bold = True
    cell.text_frame.paragraphs[0].font.size = Pt(14)
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor(0, 51, 102)
    cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

# Populate data
data = [
    ['Widget A', '$299', '1,234'],
    ['Widget B', '$399', '2,456'],
    ['Widget C', '$499', '3,789']
]

for row_idx, row_data in enumerate(data, start=1):
    for col_idx, value in enumerate(row_data):
        cell = table.cell(row_idx, col_idx)
        cell.text = value
        cell.text_frame.paragraphs[0].font.size = Pt(12)
```

## Table with Alternating Row Colors

```python
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

slide = prs.slides.add_slide(prs.slide_layouts[5])
title = slide.shapes.title
title.text = "Sales Report"

# Create table
rows, cols = 11, 4  # 1 header + 10 data rows
table = slide.shapes.add_table(rows, cols, Inches(1), Inches(2), Inches(8), Inches(5)).table

# Headers
headers = ['Month', 'Revenue', 'Costs', 'Profit']
for col_idx, header in enumerate(headers):
    cell = table.cell(0, col_idx)
    cell.text = header
    cell.text_frame.paragraphs[0].font.bold = True
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor(0, 51, 102)
    cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

# Sample data
data = [
    ['January', '$50,000', '$30,000', '$20,000'],
    ['February', '$55,000', '$32,000', '$23,000'],
    ['March', '$60,000', '$35,000', '$25,000'],
    ['April', '$58,000', '$33,000', '$25,000'],
    ['May', '$62,000', '$36,000', '$26,000'],
    ['June', '$65,000', '$38,000', '$27,000'],
    ['July', '$68,000', '$40,000', '$28,000'],
    ['August', '$70,000', '$41,000', '$29,000'],
    ['September', '$72,000', '$42,000', '$30,000'],
    ['October', '$75,000', '$43,000', '$32,000']
]

# Alternating row colors
for row_idx, row_data in enumerate(data, start=1):
    for col_idx, value in enumerate(row_data):
        cell = table.cell(row_idx, col_idx)
        cell.text = value
        cell.text_frame.paragraphs[0].font.size = Pt(11)

        # Alternate row colors
        if row_idx % 2 == 0:
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(240, 240, 240)  # Light gray
```

## Table from pandas DataFrame

```python
import pandas as pd
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

def create_table_from_dataframe(slide, df, left, top, width, height):
    """Create PowerPoint table from pandas DataFrame."""
    rows = len(df) + 1  # +1 for header
    cols = len(df.columns)

    table = slide.shapes.add_table(rows, cols, left, top, width, height).table

    # Set column widths
    col_width = width / cols
    for col in range(cols):
        table.columns[col].width = col_width

    # Headers
    for col_idx in range(cols):
        cell = table.cell(0, col_idx)
        cell.text = str(df.columns[col_idx])
        cell.text_frame.paragraphs[0].font.bold = True
        cell.text_frame.paragraphs[0].font.size = Pt(11)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0, 51, 102)
        cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

    # Data
    for row_idx in range(len(df)):
        for col_idx in range(cols):
            cell = table.cell(row_idx + 1, col_idx)
            cell.text = str(df.iloc[row_idx, col_idx])
            cell.text_frame.paragraphs[0].font.size = Pt(10)

    return table

# Usage
df = pd.read_csv('sales_data.csv')
slide = prs.slides.add_slide(prs.slide_layouts[5])
title = slide.shapes.title
title.text = "Sales Data"

create_table_from_dataframe(slide, df.head(10), Inches(0.5), Inches(2), Inches(9), Inches(4))
```

## Table with Merged Cells

```python
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

slide = prs.slides.add_slide(prs.slide_layouts[5])
title = slide.shapes.title
title.text = "Quarterly Summary"

# Create table
table = slide.shapes.add_table(5, 4, Inches(1.5), Inches(2), Inches(7), Inches(4)).table

# Merge cells for title row
cell1 = table.cell(0, 0)
cell2 = table.cell(0, 3)
merged_cell = cell1.merge(cell2)
merged_cell.text = "Q4 2025 Summary"
merged_cell.text_frame.paragraphs[0].font.bold = True
merged_cell.text_frame.paragraphs[0].font.size = Pt(16)
merged_cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
merged_cell.vertical_anchor = MSO_ANCHOR.MIDDLE
merged_cell.fill.solid()
merged_cell.fill.fore_color.rgb = RGBColor(0, 51, 102)
merged_cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

# Add headers
headers = ['', 'Oct', 'Nov', 'Dec']
for col_idx, header in enumerate(headers):
    if col_idx > 0:  # Skip first column (already merged)
        cell = table.cell(1, col_idx)
        cell.text = header
        cell.text_frame.paragraphs[0].font.bold = True
```

## Table with Cell Borders

```python
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement

def set_cell_border(cell, border_color="000000", border_width='12700'):
    """
    Set cell border properties.
    border_width in EMUs (914400 EMUs = 1 inch)
    12700 = 1pt
    """
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()

    for border_name in ['lnL', 'lnR', 'lnT', 'lnB']:
        ln = OxmlElement(f'a:{border_name}')
        ln.set('w', border_width)
        ln.set('cap', 'flat')
        ln.set('cmpd', 'sng')
        ln.set('algn', 'ctr')

        solidFill = OxmlElement('a:solidFill')
        srgbClr = OxmlElement('a:srgbClr')
        srgbClr.set('val', border_color)
        solidFill.append(srgbClr)
        ln.append(solidFill)

        tcPr.append(ln)

# Create table
slide = prs.slides.add_slide(prs.slide_layouts[5])
table = slide.shapes.add_table(4, 3, Inches(2), Inches(2), Inches(6), Inches(3)).table

# Add borders to all cells
for row in table.rows:
    for cell in row.cells:
        set_cell_border(cell, "000000", "12700")
        cell.text = "Data"
```

## Table with Cell Alignment

```python
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

slide = prs.slides.add_slide(prs.slide_layouts[5])
table = slide.shapes.add_table(4, 3, Inches(2), Inches(2), Inches(6), Inches(3)).table

# Headers (centered)
headers = ['Product', 'Price', 'Quantity']
for col_idx, header in enumerate(headers):
    cell = table.cell(0, col_idx)
    cell.text = header
    cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    cell.text_frame.paragraphs[0].font.bold = True

# Data with different alignments
data = [
    ['Widget A', '$299', '100'],
    ['Widget B', '$399', '250'],
    ['Widget C', '$499', '175']
]

for row_idx, row_data in enumerate(data, start=1):
    # Product name (left-aligned)
    cell = table.cell(row_idx, 0)
    cell.text = row_data[0]
    cell.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    # Price (right-aligned)
    cell = table.cell(row_idx, 1)
    cell.text = row_data[1]
    cell.text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    # Quantity (centered)
    cell = table.cell(row_idx, 2)
    cell.text = row_data[2]
    cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
```

## Summary Table with Totals

```python
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

slide = prs.slides.add_slide(prs.slide_layouts[5])
title = slide.shapes.title
title.text = "Monthly Revenue Summary"

# Create table (5 rows: header, 3 data, totals)
table = slide.shapes.add_table(5, 4, Inches(1.5), Inches(2), Inches(7), Inches(4)).table

# Headers
headers = ['Month', 'Sales', 'Costs', 'Profit']
for col_idx, header in enumerate(headers):
    cell = table.cell(0, col_idx)
    cell.text = header
    cell.text_frame.paragraphs[0].font.bold = True
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor(0, 51, 102)
    cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

# Data
data = [
    ['January', '$50,000', '$30,000', '$20,000'],
    ['February', '$55,000', '$32,000', '$23,000'],
    ['March', '$60,000', '$35,000', '$25,000']
]

for row_idx, row_data in enumerate(data, start=1):
    for col_idx, value in enumerate(row_data):
        cell = table.cell(row_idx, col_idx)
        cell.text = value
        cell.text_frame.paragraphs[0].font.size = Pt(11)

# Totals row
totals = ['Total', '$165,000', '$97,000', '$68,000']
for col_idx, value in enumerate(totals):
    cell = table.cell(4, col_idx)
    cell.text = value
    cell.text_frame.paragraphs[0].font.bold = True
    cell.text_frame.paragraphs[0].font.size = Pt(12)
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor(220, 220, 220)

    # Right-align numbers
    if col_idx > 0:
        cell.text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT
```
