# Advanced Techniques

## Copying Slides Between Presentations

```python
from pptx import Presentation
import copy

source_prs = Presentation('source.pptx')
target_prs = Presentation('target.pptx')

# Get slide to copy
source_slide = source_prs.slides[0]

# Copy slide layout
slide_layout = target_prs.slide_layouts[source_slide.slide_layout.slide_layout_index]

# Add new slide
copied_slide = target_prs.slides.add_slide(slide_layout)

# Copy shapes (simplified; full copy requires deep cloning)
for shape in source_slide.shapes:
    el = shape.element
    newel = copy.deepcopy(el)
    copied_slide.shapes._spTree.insert_element_before(newel, 'p:extLst')

target_prs.save('target_with_copied_slide.pptx')
```

## Advanced Table Cell Borders

```python
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

# Apply border to all cells
for row in table.rows:
    for cell in row.cells:
        set_cell_border(cell, "000000", "12700")
```

## Merging Table Cells

```python
# Merge cells
cell1 = table.cell(0, 0)
cell2 = table.cell(0, 1)
merged_cell = cell1.merge(cell2)
merged_cell.text = "Product Information"

# Cell alignment
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

cell = table.cell(1, 1)
cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
cell.vertical_anchor = MSO_ANCHOR.MIDDLE
```

## Image Processing with Pillow

### Checking Image DPI

```python
from PIL import Image

# Check image DPI before adding
with Image.open('photo.jpg') as img:
    dpi = img.info.get('dpi', (72, 72))
    print(f"Image DPI: {dpi}")

    if dpi[0] < 150:
        print("⚠️  Warning: Low resolution image")
        # Resize or replace with higher quality version

# Calculate appropriate size
img_width_inches = img.width / dpi[0]
img_height_inches = img.height / dpi[1]

print(f"Image will be {img_width_inches:.2f}\" x {img_height_inches:.2f}\" at native resolution")
```

### Compressing Images

```python
import os
from PIL import Image

def compress_image(img_path, max_size_mb=1):
    """Compress image to target file size."""
    img = Image.open(img_path)

    quality = 95
    while quality > 10:
        output = f"compressed_{os.path.basename(img_path)}"
        img.save(output, optimize=True, quality=quality)

        size_mb = os.path.getsize(output) / (1024 * 1024)
        if size_mb <= max_size_mb:
            return output

        quality -= 5

    return output

# Use compressed images
compressed = compress_image('large_photo.jpg')
slide.shapes.add_picture(compressed, Inches(1), Inches(1))
```

## Advanced Chart Data Handling

### Handling Missing Data

```python
from pptx.chart.data import CategoryChartData

# Handle missing data with None
chart_data = CategoryChartData()
chart_data.categories = ['Q1', 'Q2', 'Q3', 'Q4']
values_with_none = [10, 20, None, 25]  # None for missing data point
chart_data.add_series('Sales', values_with_none)
```

### Multi-Series Charts

```python
chart_data = CategoryChartData()
chart_data.categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
chart_data.add_series('Website Traffic', (25000, 28000, 31000, 29000, 33000, 36000))
chart_data.add_series('Conversions', (1250, 1400, 1550, 1450, 1650, 1800))
chart_data.add_series('Revenue', (125000, 140000, 155000, 145000, 165000, 180000))

x, y, cx, cy = Inches(1), Inches(2), Inches(8), Inches(4.5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.LINE, x, y, cx, cy, chart_data
).chart

chart.has_legend = True
chart.legend.position = XL_LEGEND_POSITION.RIGHT
```

## Animations (Limited Support)

**Note:** python-pptx has limited animation support. Recommended approaches:

1. Apply animations in PowerPoint after generation
2. Use VBA/COM for Windows automation
3. Use third-party libraries for advanced animation control

## Position and Size Calculations

### Centering Elements

```python
from pptx.util import Inches, Pt, Cm

# Center element horizontally
element_width = Inches(5)
slide_width = prs.slide_width
left = (slide_width - element_width) / 2

# Center element vertically
element_height = Inches(3)
slide_height = prs.slide_height
top = (slide_height - element_height) / 2
```

### Aligning Multiple Elements

```python
# Align multiple elements with consistent spacing
spacing = Inches(0.5)
top = Inches(2)

for i, item in enumerate(items):
    shape = slide.shapes.add_textbox(Inches(1), top, Inches(8), Inches(0.5))
    shape.text_frame.text = item
    top += Inches(0.5) + spacing  # Move down for next item
```

### Using Consistent Units

```python
# Always use consistent units
left = Inches(1)      # Not: left = 914400 (EMUs)
top = Inches(2)
width = Inches(8)
height = Inches(4)

# Convert if needed
from pptx.util import Emu
emu_value = Emu(914400)  # Convert EMUs to Inches internally
```
