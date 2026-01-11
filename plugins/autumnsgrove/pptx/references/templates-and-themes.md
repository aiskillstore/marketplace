# Templates and Themes

## Using Templates as Base

```python
# Start with template
prs = Presentation('corporate_template.pptx')

# Template already has master slides and layouts
print(f"Available layouts: {len(prs.slide_layouts)}")
for idx, layout in enumerate(prs.slide_layouts):
    print(f"{idx}: {layout.name}")

# Use specific layout
title_slide = prs.slides.add_slide(prs.slide_layouts[0])
content_slide = prs.slides.add_slide(prs.slide_layouts[1])

# Layouts inherit formatting from master
prs.save('presentation_from_template.pptx')
```

## Accessing Master Slides

```python
# Access slide master
slide_master = prs.slide_master

# Access master shapes (logo, footer, etc.)
for shape in slide_master.shapes:
    if shape.name == "Company Logo":
        # Update logo
        shape.image = 'new_logo.png'
```

## Creating Custom Color Scheme

```python
from pptx.dml.color import RGBColor

# Define brand colors
BRAND_COLORS = {
    'primary': RGBColor(0, 51, 102),      # Dark Blue
    'secondary': RGBColor(0, 153, 204),   # Light Blue
    'accent': RGBColor(255, 102, 0),      # Orange
    'text': RGBColor(51, 51, 51),         # Dark Gray
    'background': RGBColor(255, 255, 255) # White
}

# Apply to text
shape.text_frame.paragraphs[0].font.color.rgb = BRAND_COLORS['primary']

# Apply to fill
shape.fill.solid()
shape.fill.fore_color.rgb = BRAND_COLORS['secondary']
```

## Layout Compatibility

### Checking Available Placeholders

```python
# Always check available placeholders
for shape in slide.placeholders:
    print(f"{shape.placeholder_format.idx} - {shape.name}")

# Use try-except when accessing placeholders
try:
    body = slide.placeholders[1]
except KeyError:
    # Placeholder doesn't exist, create text box instead
    body = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(8), Inches(5))
```

## Font Embedding

### Using Safe Fonts

```python
# Use standard fonts that are widely available
SAFE_FONTS = [
    'Arial',
    'Calibri',
    'Georgia',
    'Times New Roman',
    'Verdana',
    'Tahoma'
]
```

### Manual Font Embedding

1. Open presentation in PowerPoint
2. File → Options → Save
3. Check "Embed fonts in the file"
4. Select "Embed all characters"

## Speaker Notes

```python
slide = prs.slides.add_slide(prs.slide_layouts[1])

# Add speaker notes
notes_slide = slide.notes_slide
text_frame = notes_slide.notes_text_frame

text_frame.text = "Key talking points:\n"
text_frame.text += "- Emphasize 35% revenue growth\n"
text_frame.text += "- Mention customer testimonials\n"
text_frame.text += "- Time: 2 minutes"
```

## Hyperlinks

### External Links

```python
# Add hyperlink to text
text_frame = shape.text_frame
p = text_frame.paragraphs[0]
run = p.add_run()
run.text = "Click here for more info"
run.hyperlink.address = "https://example.com"
```

### Internal Slide Links

```python
# Link to another slide
run.hyperlink.address = f"slide{slide_number}"
```

## Custom Slide Layouts

```python
from pptx import Presentation
from pptx.util import Inches

# Start with blank presentation
prs = Presentation()

# Access slide master
slide_master = prs.slide_master

# Create custom layout (requires XML manipulation)
# Note: python-pptx has limited support for creating new layouts
# Recommended: Create template in PowerPoint, then use in python-pptx
```

**Note:** For advanced layout customization, create templates in PowerPoint and load them programmatically rather than creating layouts from scratch in code.
