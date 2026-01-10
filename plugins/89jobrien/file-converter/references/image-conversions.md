---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: file-converter
---

# Image Conversion Reference

## Quality Settings

### JPEG Quality

Range: 1-100 (higher = better quality, larger file)

```python
from PIL import Image

img = Image.open("input.png")
img = img.convert("RGB")  # JPEG requires RGB, not RGBA
img.save("output.jpg", "JPEG", quality=85, optimize=True)
```

Recommendations:

- 95: Near-lossless, large files
- 85: Good balance (default recommendation)
- 75: Noticeable compression, smaller files
- 60: Web thumbnails

### WebP Quality

```python
img.save("output.webp", "WEBP", quality=80, method=6)
```

- `quality`: 0-100 (80 recommended)
- `method`: 0-6 (compression effort, 6 = slowest/smallest)
- `lossless=True`: For lossless compression

### PNG Optimization

PNG is lossless, but compression level affects file size:

```python
img.save("output.png", "PNG", optimize=True, compress_level=9)
```

## Transparency Handling

### RGBA to RGB (for JPEG)

```python
from PIL import Image

img = Image.open("input.png")

if img.mode == "RGBA":
    background = Image.new("RGB", img.size, (255, 255, 255))
    background.paste(img, mask=img.split()[3])
    img = background

img.save("output.jpg", "JPEG", quality=85)
```

### Preserving Transparency

Formats supporting transparency: PNG, WebP, GIF

```python
img = Image.open("input.png")
img.save("output.webp", "WEBP", quality=80)  # Preserves alpha
```

## Color Profiles

### Converting Color Modes

```python
from PIL import Image

img = Image.open("input.png")

if img.mode == "P":  # Palette mode
    img = img.convert("RGBA")
elif img.mode == "L":  # Grayscale
    img = img.convert("RGB")
elif img.mode == "CMYK":
    img = img.convert("RGB")
```

### Preserving ICC Profiles

```python
img = Image.open("input.jpg")
icc_profile = img.info.get("icc_profile")

img.save("output.jpg", "JPEG", quality=85, icc_profile=icc_profile)
```

## SVG Conversion

### SVG to Raster (PNG/JPG)

**cairosvg** (recommended):

```python
import cairosvg

cairosvg.svg2png(
    url="input.svg",
    write_to="output.png",
    output_width=1024,  # or use scale=2
)
```

**svglib + reportlab**:

```python
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

drawing = svg2rlg("input.svg")
renderPM.drawToFile(drawing, "output.png", fmt="PNG")
```

### Raster to SVG (Tracing)

Limited fidelity - converts to vector paths:

```bash
potrace input.bmp -s -o output.svg
```

For photographs, this produces stylized results, not faithful reproduction.

## Resizing

### Maintain Aspect Ratio

```python
from PIL import Image

img = Image.open("input.png")
img.thumbnail((800, 600), Image.Resampling.LANCZOS)
img.save("output.png")
```

### Exact Dimensions (with padding)

```python
from PIL import Image

def resize_with_padding(img, target_size, fill_color=(255, 255, 255)):
    img.thumbnail(target_size, Image.Resampling.LANCZOS)
    new_img = Image.new("RGB", target_size, fill_color)
    offset = ((target_size[0] - img.size[0]) // 2,
              (target_size[1] - img.size[1]) // 2)
    new_img.paste(img, offset)
    return new_img
```

## Batch Processing

```python
from pathlib import Path
from PIL import Image

input_dir = Path("input_images")
output_dir = Path("output_images")
output_dir.mkdir(exist_ok=True)

for img_path in input_dir.glob("*.png"):
    img = Image.open(img_path)
    output_path = output_dir / f"{img_path.stem}.webp"
    img.save(output_path, "WEBP", quality=80)
```

## GIF Handling

### Extracting Frames

```python
from PIL import Image

img = Image.open("input.gif")
frames = []

try:
    while True:
        frames.append(img.copy())
        img.seek(img.tell() + 1)
except EOFError:
    pass
```

### Creating GIF from Images

```python
from PIL import Image

images = [Image.open(f"frame_{i}.png") for i in range(10)]
images[0].save(
    "output.gif",
    save_all=True,
    append_images=images[1:],
    duration=100,  # milliseconds per frame
    loop=0  # 0 = infinite loop
)
```
