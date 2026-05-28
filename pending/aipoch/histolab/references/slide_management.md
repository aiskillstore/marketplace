# Slide Management

## Overview

The `Slide` class is the main interface for handling Whole Slide Images (WSI) in histolab. It provides methods for loading, inspecting, and processing large histopathological images stored in various formats.

## Initialization

```python
from histolab.slide import Slide

# Initialize Slide object with WSI file and output directory
slide = Slide(processed_path="path/to/processed/output",
              slide_path="path/to/slide.svs")
```

**Parameters:**
- `slide_path`: Path to the Whole Slide Image file (supports multiple formats: SVS, TIFF, NDPI, etc.)
- `processed_path`: Directory to save processed output results (tiles, thumbnails, etc.)

## Loading Sample Data

Histolab provides built-in TCGA sample datasets for testing and demonstration:

```python
from histolab.data import prostate_tissue, ovarian_tissue, breast_tissue, heart_tissue, kidney_tissue

# Load prostate tissue sample
prostate_svs, prostate_path = prostate_tissue()
slide = Slide(prostate_path, processed_path="output/")
```

Available sample datasets:
- `prostate_tissue()`: Prostate tissue sample
- `ovarian_tissue()`: Ovarian tissue sample
- `breast_tissue()`: Breast tissue sample
- `heart_tissue()`: Heart tissue sample
- `kidney_tissue()`: Kidney tissue sample

## Key Properties

### Slide Dimensions
```python
# Get slide dimensions at level 0 (highest resolution)
width, height = slide.dimensions

# Get dimensions for specific pyramid levels
level_dimensions = slide.level_dimensions
# Returns a (width, height) tuple for each level
```

### Magnification Information
```python
# Get base magnification (e.g., 40x, 20x)
base_mag = slide.base_mpp  # Microns per pixel (MPP) at level 0

# Get all available levels
num_levels = slide.levels  # Number of pyramid levels
```

### Slide Properties
```python
# Access OpenSlide properties dictionary
properties = slide.properties

# Common properties include:
# - slide.properties['openslide.objective-power']: Objective power
# - slide.properties['openslide.mpp-x']: Microns per pixel in X-axis
# - slide.properties['openslide.mpp-y']: Microns per pixel in Y-axis
# - slide.properties['openslide.vendor']: Scanner vendor
```

## Thumbnail Generation

```python
# Get thumbnail of a specific size
thumbnail = slide.thumbnail

# Save thumbnail to disk
slide.save_thumbnail()  # Saved to processed_path

# Get scaled thumbnail
scaled_thumbnail = slide.scaled_image(scale_factor=32)
```

## Slide Visualization

```python
# Display slide thumbnail using matplotlib
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 10))
plt.imshow(slide.thumbnail)
plt.title(f"Slide: {slide.name}")
plt.axis('off')
plt.show()
```

## Extracting Regions

```python
# Extract region at specific coordinates and level
region = slide.extract_region(
    location=(x, y),  # Top-left corner coordinates at level 0
    size=(width, height),  # Region size
    level=0  # Pyramid level
)
```

## Working with Pyramid Levels

WSI files use a pyramid structure with multiple resolution levels:
- Level 0: Highest resolution (native scan resolution)
- Level 1 and above: Progressively lower resolution for fast access

```python
# Check available levels
for level in range(slide.levels):
    dims = slide.level_dimensions[level]
    downsample = slide.level_downsamples[level]
    print(f"Level {level}: {dims}, downsample: {downsample}x")
```

## Slide Name and Path

```python
# Get slide filename without extension
slide_name = slide.name

# Get full path of the slide file
slide_path = slide.scaled_image
```

## Best Practices

1. **Always specify processed_path**: Manage output results in a dedicated directory.
2. **Check dimensions before processing**: Extremely large slides may exceed memory limits.
3. **Use appropriate pyramid levels**: Extract tiles at the corresponding level based on analysis resolution.
4. **Preview via thumbnails**: Use thumbnails for quick visualization before performing heavy processing.
5. **Monitor memory usage**: Operating at level 0 of very large slides requires significant RAM.

## Common Workflows

### Slide Inspection Workflow
```python
from histolab.slide import Slide

# Load slide
slide = Slide("slide.svs", processed_path="output/")

# Check properties
print(f"Dimensions: {slide.dimensions}")
print(f"Levels: {slide.levels}")
print(f"Magnification: {slide.properties.get('openslide.objective-power', 'N/A')}")

# Save thumbnail for viewing
slide.save_thumbnail()
```

### Multi-slide Processing
```python
import os
from pathlib import Path

slide_dir = Path("slides/")
output_dir = Path("processed/")

for slide_path in slide_dir.glob("*.svs"):
    slide = Slide(slide_path, processed_path=output_dir / slide_path.stem)
    # Process each slide
    print(f"Processing: {slide.name}")
```