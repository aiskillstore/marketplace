# Design Best Practices

## Color Palette Selection

### Rule of 60-30-10

- 60% primary color (backgrounds, large areas)
- 30% secondary color (supporting elements)
- 10% accent color (highlights, call-to-action)

### Professional Palettes

**Corporate Blue:**
```python
CORPORATE = {
    'primary': RGBColor(0, 51, 102),      # Navy
    'secondary': RGBColor(240, 243, 245), # Light Gray
    'accent': RGBColor(0, 153, 204)       # Sky Blue
}
```

**Tech Green:**
```python
TECH = {
    'primary': RGBColor(34, 139, 34),     # Forest Green
    'secondary': RGBColor(245, 245, 245), # Off-white
    'accent': RGBColor(255, 165, 0)       # Orange
}
```

**Creative Purple:**
```python
CREATIVE = {
    'primary': RGBColor(106, 27, 154),    # Deep Purple
    'secondary': RGBColor(238, 238, 238), # Light Gray
    'accent': RGBColor(255, 215, 0)       # Gold
}
```

### Accessibility

- Ensure sufficient contrast (WCAG AA: 4.5:1 for text)
- Avoid red-green combinations (colorblind-friendly)
- Test with grayscale preview

## Typography Guidelines

### Font Hierarchy

```python
# Title
title_font_size = Pt(44)
title_font_bold = True

# Heading
heading_font_size = Pt(32)
heading_font_bold = True

# Subheading
subheading_font_size = Pt(24)
subheading_font_bold = False

# Body
body_font_size = Pt(18)
body_font_bold = False

# Caption
caption_font_size = Pt(12)
caption_font_bold = False
```

### Font Recommendations

- **Sans-serif**: Calibri, Arial, Helvetica, Segoe UI (screens)
- **Serif**: Georgia, Times New Roman (formal documents)
- **Limit to 2 fonts**: One for headings, one for body

### Readability

- Minimum font size: 18pt for body text
- Line spacing: 1.2-1.5x font size
- Character spacing: Normal (avoid tight tracking)

## Layout Principles

### Rule of Thirds

```python
# Divide slide into 9 equal sections (3x3 grid)
slide_width = prs.slide_width
slide_height = prs.slide_height

third_width = slide_width / 3
third_height = slide_height / 3

# Place important elements at intersections
focal_points = [
    (third_width, third_height),      # Top-left
    (2 * third_width, third_height),  # Top-right
    (third_width, 2 * third_height),  # Bottom-left
    (2 * third_width, 2 * third_height)  # Bottom-right
]
```

### White Space

- Minimum margins: 0.5 inches on all sides
- Space between elements: 0.25-0.5 inches
- Don't overcrowd slides (5-7 elements maximum)

### Alignment

```python
# Align to grid
grid_size = Inches(0.25)

def snap_to_grid(value, grid_size):
    """Snap position to grid."""
    return round(value / grid_size) * grid_size

left = snap_to_grid(Inches(1.3), grid_size)
top = snap_to_grid(Inches(2.1), grid_size)
```

## Visual Hierarchy

### Size & Scale

```python
# Most important element: Largest
title.text_frame.paragraphs[0].font.size = Pt(44)

# Secondary elements: Medium
heading.text_frame.paragraphs[0].font.size = Pt(28)

# Supporting details: Smallest
body.text_frame.paragraphs[0].font.size = Pt(18)
```

### Color Contrast

```python
# High contrast = high importance
important_text.font.color.rgb = RGBColor(0, 0, 0)  # Black on white

# Low contrast = low importance
caption.font.color.rgb = RGBColor(128, 128, 128)  # Gray on white
```

### Z-Pattern Layout

- Top-left: Logo/branding
- Top-right: Navigation/page number
- Middle: Main content
- Bottom-right: Call-to-action

## Chart Design

### Best Practices

- Choose appropriate chart type (bar for comparison, line for trends, pie for parts of whole)
- Limit colors (3-5 maximum)
- Always label axes
- Include data labels for clarity
- Use gridlines sparingly

### Clean Chart Formatting

```python
# Chart setup
chart.has_legend = True
chart.legend.position = XL_LEGEND_POSITION.RIGHT
chart.legend.font.size = Pt(12)

# Axis formatting
value_axis = chart.value_axis
value_axis.has_major_gridlines = True
value_axis.major_gridlines.format.line.color.rgb = RGBColor(200, 200, 200)
value_axis.tick_labels.font.size = Pt(11)

# Data labels
plot = chart.plots[0]
plot.has_data_labels = True
data_labels = plot.data_labels
data_labels.font.size = Pt(10)
data_labels.font.bold = True
```

## Image Best Practices

### Resolution

- Screen presentations: 1920x1080 (1080p)
- Print presentations: 300 DPI minimum
- Photos: JPEG (smaller file size)
- Graphics/logos: PNG (transparency support)

### Optimization

```python
from PIL import Image

def optimize_image(input_path, output_path, max_size=(1920, 1080), quality=85):
    """Optimize image for presentation."""
    with Image.open(input_path) as img:
        # Resize if larger than max_size
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Save with compression
        img.save(output_path, optimize=True, quality=quality)

    return output_path

# Usage
optimized = optimize_image('large_photo.jpg', 'optimized.jpg')
pic = slide.shapes.add_picture(optimized, Inches(1), Inches(1))
```

### Aspect Ratios

- 16:9 (widescreen): Standard for modern presentations
- 4:3 (standard): Legacy format
- Match slide aspect ratio to avoid black bars
