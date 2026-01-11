# Image Handling Examples

Complete examples for working with images in PowerPoint presentations.

## Basic Image Insertion

```python
from pptx.util import Inches

slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank

# Add image with auto-scaled height
img_path = 'company_logo.png'
left = Inches(1)
top = Inches(1)
height = Inches(2)  # Width will auto-scale to maintain aspect ratio

pic = slide.shapes.add_picture(img_path, left, top, height=height)

# Access image properties
print(f"Image size: {pic.width} x {pic.height}")
print(f"Image position: ({pic.left}, {pic.top})")
```

## Image with Specific Dimensions

```python
from pptx.util import Inches

slide = prs.slides.add_slide(prs.slide_layouts[6])

# Add with both width and height (may distort aspect ratio)
pic = slide.shapes.add_picture(
    'chart_screenshot.png',
    Inches(0.5),  # left
    Inches(2),    # top
    Inches(9),    # width
    Inches(5)     # height
)
```

## Center Image on Slide

```python
from pptx.util import Inches

img_path = 'hero_image.jpg'
slide = prs.slides.add_slide(prs.slide_layouts[6])

# Add image first
pic = slide.shapes.add_picture(img_path, Inches(0), Inches(0), height=Inches(4))

# Calculate centered position
slide_width = prs.slide_width
slide_height = prs.slide_height

pic.left = int((slide_width - pic.width) / 2)
pic.top = int((slide_height - pic.height) / 2)
```

## Image Preprocessing with Pillow

### Resize Before Adding

```python
from PIL import Image
from io import BytesIO
from pptx.util import Inches

# Resize image before adding to presentation
img = Image.open('large_photo.jpg')
img.thumbnail((1920, 1080))  # Resize to max 1920x1080

# Save to bytes
img_bytes = BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

# Add to slide
pic = slide.shapes.add_picture(img_bytes, Inches(1), Inches(1), height=Inches(5))
```

### Maintain Aspect Ratio

```python
from PIL import Image
from pptx.util import Inches

def add_image_with_aspect_ratio(slide, img_path, left, top, max_width, max_height):
    """Add image maintaining aspect ratio within max dimensions."""
    with Image.open(img_path) as img:
        img_width, img_height = img.size
        aspect_ratio = img_width / img_height

        # Calculate dimensions
        if aspect_ratio > max_width / max_height:
            # Width-constrained
            width = max_width
            height = width / aspect_ratio
        else:
            # Height-constrained
            height = max_height
            width = height * aspect_ratio

        # Add image
        pic = slide.shapes.add_picture(img_path, left, top, width, height)
        return pic

# Usage
slide = prs.slides.add_slide(prs.slide_layouts[6])
pic = add_image_with_aspect_ratio(
    slide, 'photo.jpg',
    Inches(1), Inches(1),
    Inches(8), Inches(5.5)
)
```

## Image Gallery Presentation

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from PIL import Image
import os

def create_image_gallery(image_folder, output_file="image_gallery.pptx"):
    """Create a presentation with one image per slide."""

    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    # Get all image files
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    image_files = [
        f for f in os.listdir(image_folder)
        if f.lower().endswith(image_extensions)
    ]

    # Title slide
    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_slide.shapes.title.text = "Image Gallery"
    title_slide.placeholders[1].text = f"{len(image_files)} Images"

    # Add one slide per image
    for img_file in image_files:
        img_path = os.path.join(image_folder, img_file)

        # Get image dimensions
        with Image.open(img_path) as img:
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height

        # Create slide
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank

        # Calculate dimensions to fit slide
        max_width = Inches(9)
        max_height = Inches(6.5)

        if aspect_ratio > max_width / max_height:
            # Width-constrained
            width = max_width
            height = width / aspect_ratio
        else:
            # Height-constrained
            height = max_height
            width = height * aspect_ratio

        # Center image
        left = (prs.slide_width - width) / 2
        top = (prs.slide_height - height) / 2

        # Add image
        slide.shapes.add_picture(img_path, left, top, width, height)

        # Add caption
        caption_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(6.8), Inches(9), Inches(0.5)
        )
        tf = caption_box.text_frame
        tf.text = os.path.splitext(img_file)[0]  # Filename without extension
        tf.paragraphs[0].font.size = Pt(14)
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    prs.save(output_file)
    print(f"✅ Gallery created: {output_file} ({len(image_files)} images)")

# Usage
create_image_gallery('/path/to/images')
```

## Image Compression

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
compressed = compress_image('large_photo.jpg', max_size_mb=0.5)
slide.shapes.add_picture(compressed, Inches(1), Inches(1))
```

## Batch Image Optimization

```python
import os
from PIL import Image

def optimize_images_for_presentation(image_folder, output_folder, max_size=(1920, 1080)):
    """Optimize all images in folder for presentation use."""
    os.makedirs(output_folder, exist_ok=True)

    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')

    for filename in os.listdir(image_folder):
        if filename.lower().endswith(image_extensions):
            input_path = os.path.join(image_folder, filename)
            output_path = os.path.join(output_folder, filename)

            with Image.open(input_path) as img:
                # Resize if larger than max_size
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

                # Save with optimization
                img.save(output_path, optimize=True, quality=85)

            print(f"✅ Optimized: {filename}")

# Usage
optimize_images_for_presentation('original_images/', 'optimized_images/')
```

## Image with Background Removal

```python
from PIL import Image
from io import BytesIO
from pptx.util import Inches

def add_image_with_transparency(slide, img_path, left, top, height):
    """Add image with transparency support (PNG)."""
    # Ensure image is PNG for transparency
    img = Image.open(img_path)

    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # Save to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    # Add to slide
    pic = slide.shapes.add_picture(img_bytes, left, top, height=height)
    return pic

# Usage
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_image_with_transparency(slide, 'logo_transparent.png', Inches(1), Inches(1), Inches(2))
```

## Multiple Images on One Slide

```python
from pptx.util import Inches

slide = prs.slides.add_slide(prs.slide_layouts[6])

# Add title
title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.5))
title_box.text_frame.text = "Product Comparison"

# Define image positions (2x2 grid)
positions = [
    (Inches(0.5), Inches(1.2), Inches(4.5), Inches(3)),   # Top-left
    (Inches(5), Inches(1.2), Inches(4.5), Inches(3)),     # Top-right
    (Inches(0.5), Inches(4.5), Inches(4.5), Inches(3)),   # Bottom-left
    (Inches(5), Inches(4.5), Inches(4.5), Inches(3))      # Bottom-right
]

images = ['product1.jpg', 'product2.jpg', 'product3.jpg', 'product4.jpg']

for img_path, (left, top, width, height) in zip(images, positions):
    slide.shapes.add_picture(img_path, left, top, width, height)
```

## Image Quality Validation

```python
from PIL import Image

def validate_image_quality(img_path, min_dpi=150, min_width=800, min_height=600):
    """Validate image meets quality standards."""
    with Image.open(img_path) as img:
        # Check dimensions
        width, height = img.size
        if width < min_width or height < min_height:
            print(f"⚠️  Warning: Image resolution too low ({width}x{height})")
            return False

        # Check DPI
        dpi = img.info.get('dpi', (72, 72))
        if dpi[0] < min_dpi:
            print(f"⚠️  Warning: Image DPI too low ({dpi[0]})")
            return False

        print(f"✅ Image quality OK: {width}x{height} @ {dpi[0]} DPI")
        return True

# Validate before adding
if validate_image_quality('photo.jpg'):
    slide.shapes.add_picture('photo.jpg', Inches(1), Inches(1))
```
