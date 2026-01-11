# Troubleshooting and Common Pitfalls

## Installation Issues

### "ModuleNotFoundError: No module named 'pptx'"

**Solution:**
```bash
pip install python-pptx
```

Verify installation:
```python
import pptx
print(pptx.__version__)
```

## Layout Compatibility Issues

### Problem: Layouts from templates don't match expected placeholders

**Solution:**
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

## Image Problems

### Problem: Images appear pixelated or blurry

**Solution:**
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

### Problem: Images not found

**Solution:**
```python
import os

# Use absolute paths
img_path = os.path.abspath('image.png')

# Verify file exists
if not os.path.exists(img_path):
    raise FileNotFoundError(f"Image not found: {img_path}")

# Add to slide
pic = slide.shapes.add_picture(img_path, Inches(1), Inches(1))
```

## Font Issues

### Problem: Fonts not displaying correctly on other computers

**Solution:**

Use standard fonts:
```python
SAFE_FONTS = [
    'Arial',
    'Calibri',
    'Georgia',
    'Times New Roman',
    'Verdana',
    'Tahoma'
]
```

Or embed fonts manually:
1. Open presentation in PowerPoint
2. File → Options → Save
3. Check "Embed fonts in the file"
4. Select "Embed all characters"

## Chart Data Issues

### Problem: Chart data doesn't display as expected

**Solution:**
```python
from pptx.chart.data import CategoryChartData

# Always validate data before creating chart
chart_data = CategoryChartData()

# Categories must be strings
categories = ['Q1', 'Q2', 'Q3', 'Q4']  # ✅ Good
# categories = [1, 2, 3, 4]  # ❌ Bad (numbers)

chart_data.categories = categories

# Series data must be numbers
values = [10, 20, 15, 25]  # ✅ Good
# values = ['10', '20', '15', '25']  # ❌ Bad (strings)

chart_data.add_series('Sales', values)

# Handle missing data
values_with_none = [10, 20, None, 25]  # None for missing
chart_data.add_series('Sales', values_with_none)
```

### Problem: "AttributeError: 'NoneType' object has no attribute..."

**Cause:** Accessing a placeholder that doesn't exist in the layout.

**Solution:**
```python
# Check placeholder indices
print([p.placeholder_format.idx for p in slide.placeholders])

# Verify layout has expected placeholders
for shape in slide.placeholders:
    print(f"Index {shape.placeholder_format.idx}: {shape.name}")
```

## Text Overflow

### Problem: Text doesn't fit in text boxes or placeholders

**Solution:**
```python
from pptx.enum.text import MSO_AUTO_SIZE

# Enable auto-fit
text_frame = shape.text_frame
text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE  # Shrink text
# or
text_frame.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT  # Expand shape

# Check if text fits
text_frame.word_wrap = True

# Truncate long text
max_chars = 500
if len(long_text) > max_chars:
    display_text = long_text[:max_chars] + "..."
else:
    display_text = long_text
```

## File Size Issues

### Problem: Presentation file is too large

**Solution:**

Compress images before adding:
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

Manual compression in PowerPoint:
1. Open presentation in PowerPoint
2. File → Compress Pictures
3. Select resolution (220 ppi for print, 150 ppi for screen)
4. Check "Delete cropped areas of pictures"

## Position and Size Issues

### Problem: Elements not positioned correctly

**Solution:**
```python
from pptx.util import Inches, Pt, Cm

# Use consistent units
left = Inches(1)      # Not: left = 914400 (EMUs)
top = Inches(2)
width = Inches(8)
height = Inches(4)

# Center element horizontally
element_width = Inches(5)
slide_width = prs.slide_width
left = (slide_width - element_width) / 2

# Center element vertically
element_height = Inches(3)
slide_height = prs.slide_height
top = (slide_height - element_height) / 2

# Align multiple elements
spacing = Inches(0.5)
top = Inches(2)

for i, item in enumerate(items):
    shape = slide.shapes.add_textbox(Inches(1), top, Inches(8), Inches(0.5))
    shape.text_frame.text = item
    top += Inches(0.5) + spacing  # Move down for next item
```

## File Corruption

### Problem: File corrupted after generation

**Solutions:**

1. Validate presentation by opening in PowerPoint
2. Check for invalid characters in text
3. Ensure all shapes are properly closed
4. Verify chart data types are correct
5. Test with minimal content to isolate issue

**Prevention:**
```python
# Save incrementally during generation
prs.save('temp_presentation.pptx')

# Verify file can be opened
try:
    test_prs = Presentation('temp_presentation.pptx')
    print("✅ File validation successful")
except Exception as e:
    print(f"❌ File validation failed: {e}")
```

## Common Error Messages

### "KeyError: 'placeholder index not found'"
- Placeholder doesn't exist in the layout
- Check available placeholders before accessing

### "ValueError: slide not in presentation"
- Trying to modify a slide from a different presentation
- Ensure slide belongs to the presentation being modified

### "AttributeError: 'Presentation' object has no attribute..."
- Using incorrect API method
- Check python-pptx documentation for correct method names

### "PIL.UnidentifiedImageError: cannot identify image file"
- Image file is corrupted or unsupported format
- Verify image file is valid (PNG, JPEG, GIF, BMP)

## Performance Issues

### Problem: Slow generation with many slides

**Optimization strategies:**

1. **Batch operations:**
```python
# Add all slides first, then populate
slides = [prs.slides.add_slide(prs.slide_layouts[1]) for _ in range(100)]
for i, slide in enumerate(slides):
    slide.shapes.title.text = f"Slide {i+1}"
```

2. **Optimize images before adding:**
```python
from PIL import Image

def optimize_all_images(image_folder):
    for img_file in os.listdir(image_folder):
        if img_file.endswith(('.png', '.jpg', '.jpeg')):
            optimize_image(os.path.join(image_folder, img_file))
```

3. **Use templates to reduce formatting overhead:**
```python
# Start with pre-formatted template
prs = Presentation('template.pptx')
# Add content without additional formatting
```

## Debugging Tips

### Enable Verbose Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('pptx')
```

### Inspect Slide Structure

```python
def inspect_slide(slide):
    """Print slide structure for debugging."""
    print(f"Slide Layout: {slide.slide_layout.name}")
    print(f"Number of shapes: {len(slide.shapes)}")

    for shape in slide.shapes:
        print(f"  - {shape.name} ({type(shape).__name__})")
        if hasattr(shape, 'text'):
            print(f"    Text: {shape.text[:50]}...")
```

### Validate Chart Data

```python
def validate_chart_data(categories, values):
    """Validate chart data before creating chart."""
    if len(categories) != len(values):
        raise ValueError("Categories and values must have same length")

    if not all(isinstance(c, str) for c in categories):
        raise ValueError("All categories must be strings")

    if not all(isinstance(v, (int, float, type(None))) for v in values):
        raise ValueError("All values must be numbers or None")

    print("✅ Chart data validation passed")
```
