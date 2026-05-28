# Visualization

## Overview

Histolab provides several built-in visualization methods for inspecting slides, previewing tile positions, visualizing masks, and evaluating extraction quality. Proper visualization is essential for validating preprocessing pipelines, debugging extraction issues, and presenting results.

## Slide Visualization

### Thumbnail Display

```python
from histolab.slide import Slide
import matplotlib.pyplot as plt

slide = Slide("slide.svs", processed_path="output/")

# Display the thumbnail
plt.figure(figsize=(10, 10))
plt.imshow(slide.thumbnail)
plt.title(f"Slide: {slide.name}")
plt.axis('off')
plt.show()
```

### Saving Thumbnails to Disk

```python
# Save the thumbnail as an image file
slide.save_thumbnail()
# The save path is processed_path/thumbnails/slide_name_thumb.png
```

### Scaled Images

```python
# Get a scaled version of the slide at a specific downsampling factor
scaled_img = slide.scaled_image(scale_factor=32)

plt.imshow(scaled_img)
plt.title(f"Slide at 32x downsample")
plt.show()
```

## Mask Visualization

### Using locate_mask()

```python
from histolab.masks import TissueMask, BiggestTissueBoxMask

# Visualize TissueMask
tissue_mask = TissueMask()
slide.locate_mask(tissue_mask)

# Visualize BiggestTissueBoxMask
biggest_mask = BiggestTissueBoxMask()
slide.locate_mask(biggest_mask)
```

This will overlay the mask boundaries in red on the slide thumbnail.

### Manual Mask Visualization

```python
import matplotlib.pyplot as plt
from histolab.masks import TissueMask

slide = Slide("slide.svs", processed_path="output/")
mask = TissueMask()

# Generate the mask
mask_array = mask(slide)

# Create side-by-side comparison
fig, axes = plt.subplots(1, 3, figsize=(20, 7))

# Original thumbnail
axes[0].imshow(slide.thumbnail)
axes[0].set_title("Original Slide")
axes[0].axis('off')

# Binary mask
axes[1].imshow(mask_array, cmap='gray')
axes[1].set_title("Tissue Mask")
axes[1].axis('off')

# Overlay the mask on the thumbnail
from matplotlib.colors import ListedColormap
overlay = slide.thumbnail.copy()
axes[2].imshow(overlay)
axes[2].imshow(mask_array, cmap=ListedColormap(['none', 'red']), alpha=0.3)
axes[2].set_title("Mask Overlay")
axes[2].axis('off')

plt.tight_layout()
plt.show()
```

### Comparing Multiple Masks

```python
from histolab.masks import TissueMask, BiggestTissueBoxMask

masks = {
    'TissueMask': TissueMask(),
    'BiggestTissueBoxMask': BiggestTissueBoxMask()
}

fig, axes = plt.subplots(1, len(masks) + 1, figsize=(20, 6))

# Original
axes[0].imshow(slide.thumbnail)
axes[0].set_title("Original")
axes[0].axis('off')

# Each mask
for idx, (name, mask) in enumerate(masks.items(), 1):
    mask_array = mask(slide)
    axes[idx].imshow(mask_array, cmap='gray')
    axes[idx].set_title(name)
    axes[idx].axis('off')

plt.tight_layout()
plt.show()
```

## Tile Location Preview

### Using locate_tiles()

Preview tile locations before extraction:

```python
from histolab.tiler import RandomTiler, GridTiler, ScoreTiler
from histolab.scorer import NucleiScorer

# RandomTiler preview
random_tiler = RandomTiler(
    tile_size=(512, 512),
    n_tiles=50,
    level=0,
    seed=42
)
random_tiler.locate_tiles(slide, n_tiles=20)

# GridTiler preview
grid_tiler = GridTiler(
    tile_size=(512, 512),
    level=0
)
grid_tiler.locate_tiles(slide)

# ScoreTiler preview
score_tiler = ScoreTiler(
    tile_size=(512, 512),
    n_tiles=30,
    scorer=NucleiScorer()
)
score_tiler.locate_tiles(slide, n_tiles=15)
```

This will display colored rectangles on the slide thumbnail, indicating the locations where tiles will be extracted.

### Custom Tile Location Visualization

```python
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from histolab.tiler import RandomTiler

slide = Slide("slide.svs", processed_path="output/")
tiler = RandomTiler(tile_size=(512, 512), n_tiles=30, seed=42)

# Get thumbnail and scale factor
thumbnail = slide.thumbnail
scale_factor = slide.dimensions[0] / thumbnail.size[0]

# Generate tile coordinates (without extraction)
fig, ax = plt.subplots(figsize=(12, 12))
ax.imshow(thumbnail)
ax.set_title("Tile Locations Preview")
ax.axis('off')

# Manually add a rectangle for each tile location
# Note: This is conceptual - the actual implementation would retrieve coordinates from the tiler
tile_coords = []  # This should be populated by tiler logic
for coord in tile_coords:
    x, y = coord[0] / scale_factor, coord[1] / scale_factor
    w, h = 512 / scale_factor, 512 / scale_factor
    rect = patches.Rectangle((x, y), w, h,
                             linewidth=2, edgecolor='red',
                             facecolor='none')
    ax.add_patch(rect)

plt.show()
```

## Tile Visualization

### Displaying Extracted Tiles

```python
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt

tile_dir = Path("output/tiles/")
tile_paths = list(tile_dir.glob("*.png"))[:16]  # First 16 tiles

fig, axes = plt.subplots(4, 4, figsize=(12, 12))
axes = axes.ravel()

for idx, tile_path in enumerate(tile_paths):
    tile_img = Image.open(tile_path)
    axes[idx].imshow(tile_img)
    axes[idx].set_title(tile_path.stem, fontsize=8)
    axes[idx].axis('off')

plt.tight_layout()
plt.show()
```

### Tile Grid Mosaic

```python
def create_tile_mosaic(tile_dir, grid_size=(4, 4)):
    """Create a tile mosaic."""
    tile_paths = list(Path(tile_dir).glob("*.png"))[:grid_size[0] * grid_size[1]]

    fig, axes = plt.subplots(grid_size[0], grid_size[1], figsize=(16, 16))

    for idx, tile_path in enumerate(tile_paths):
        row = idx // grid_size[1]
        col = idx % grid_size[1]
        tile_img = Image.open(tile_path)
        axes[row, col].imshow(tile_img)
        axes[row, col].axis('off')

    plt.tight_layout()
    plt.savefig("tile_mosaic.png", dpi=150, bbox_inches='tight')
    plt.show()

create_tile_mosaic("output/tiles/", grid_size=(5, 5))
```

### Tiles with Tissue Mask Overlay

```python
from histolab.tile import Tile
import matplotlib.pyplot as plt

# Assuming we have a tile object
tile = Tile(image=pil_image, coords=(x, y))

# Calculate tissue mask
tile.calculate_tissue_mask()

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Original tile
axes[0].imshow(tile.image)
axes[0].set_title("Original Tile")
axes[0].axis('off')

# Tissue mask
axes[1].imshow(tile.tissue_mask, cmap='gray')
axes[1].set_title(f"Tissue Mask ({tile.tissue_ratio:.1%} tissue)")
axes[1].axis('off')

# Overlay display
axes[2].imshow(tile.image)
axes[2].imshow(tile.tissue_mask, cmap='Reds', alpha=0.3)
axes[2].set_title("Overlay")
axes[2].axis('off')

plt.tight_layout()
plt.show()
```

## Quality Assessment Visualization

### Tile Score Distribution

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load tile report from ScoreTiler
report_df = pd.read_csv("tiles_report.csv")

# Histogram of score distribution
plt.figure(figsize=(10, 6))
plt.hist(report_df['score'], bins=30, edgecolor='black', alpha=0.7)
plt.xlabel('Tile Score')
plt.ylabel('Frequency')
plt.title('Distribution of Tile Scores')
plt.grid(axis='y', alpha=0.3)
plt.show()

# Scatter plot of Score vs. Tissue Percentage
plt.figure(figsize=(10, 6))
plt.scatter(report_df['tissue_percent'], report_df['score'], alpha=0.5)
plt.xlabel('Tissue Percentage')
plt.ylabel('Tile Score')
plt.title('Tile Score vs Tissue Coverage')
plt.grid(alpha=0.3)
plt.show()
```

### Comparison of Top and Bottom Scoring Tiles

```python
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt

# Load tile report
report_df = pd.read_csv("tiles_report.csv")
report_df = report_df.sort_values('score', ascending=False)

# Top 8 tiles
top_tiles = report_df.head(8)
# Bottom 8 tiles
bottom_tiles = report_df.tail(8)

fig, axes = plt.subplots(2, 8, figsize=(20, 6))

# Display high-scoring tiles
for idx, (_, row) in enumerate(top_tiles.iterrows()):
    tile_img = Image.open(f"output/tiles/{row['tile_name']}")
    axes[0, idx].imshow(tile_img)
    axes[0, idx].set_title(f"Score: {row['score']:.3f}", fontsize=8)
    axes[0, idx].axis('off')

# Display low-scoring tiles
for idx, (_, row) in enumerate(bottom_tiles.iterrows()):
    tile_img = Image.open(f"output/tiles/{row['tile_name']}")
    axes[1, idx].imshow(tile_img)
    axes[1, idx].set_title(f"Score: {row['score']:.3f}", fontsize=8)
    axes[1, idx].axis('off')

axes[0, 0].set_ylabel('Top Scoring', fontsize=12)
axes[1, 0].set_ylabel('Bottom Scoring', fontsize=12)

plt.tight_layout()
plt.savefig("score_comparison.png", dpi=150, bbox_inches='tight')
plt.show()
```

## Multi-Slide Visualization

### Slide Collection Thumbnails

```python
from pathlib import Path
from histolab.slide import Slide
import matplotlib.pyplot as plt

slide_dir = Path("slides/")
slide_paths = list(slide_dir.glob("*.svs"))[:9]

fig, axes = plt.subplots(3, 3, figsize=(15, 15))
axes = axes.ravel()

for idx, slide_path in enumerate(slide_paths):
    slide = Slide(slide_path, processed_path="output/")
    axes[idx].imshow(slide.thumbnail)
    axes[idx].set_title(slide.name, fontsize=10)
    axes[idx].axis('off')

plt.tight_layout()
plt.savefig("slide_collection.png", dpi=150, bbox_inches='tight')
plt.show()
```

### Tissue Coverage Comparison

```python
from pathlib import Path
from histolab.slide import Slide
from histolab.masks import TissueMask
import matplotlib.pyplot as plt
import numpy as np

slide_paths = list(Path("slides/").glob("*.svs"))
tissue_percentages = []
slide_names = []

for slide_path in slide_paths:
    slide = Slide(slide_path, processed_path="output/")
    mask = TissueMask()(slide)
    tissue_pct = mask.sum() / mask.size * 100
    tissue_percentages.append(tissue_pct)
    slide_names.append(slide.name)

# Bar chart
plt.figure(figsize=(12, 6))
plt.bar(range(len(slide_names)), tissue_percentages)
plt.xticks(range(len(slide_names)), slide_names, rotation=45, ha='right')
plt.ylabel('Tissue Coverage (%)')
plt.title('Tissue Coverage Across Slides')
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.show()
```

## Filter Effect Visualization

### Before and After Filtering

```python
from histolab.filters.image_filters import RgbToGrayscale, HistogramEqualization
from histolab.filters.compositions import Compose

# Define filter pipeline
filter_pipeline = Compose([
    RgbToGrayscale(),
    HistogramEqualization()
])

# Original vs. Filtered
fig, axes = plt.subplots(1, 2, figsize=(12, 6))

axes[0].imshow(slide.thumbnail)
axes[0].set_title("Original")
axes[0].axis('off')

filtered = filter_pipeline(slide.thumbnail)
axes[1].imshow(filtered, cmap='gray')
axes[1].set_title("After Filtering")
axes[1].axis('off')

plt.tight_layout()
plt.show()
```

### Multi-step Filter Visualization

```python
from histolab.filters.image_filters import RgbToGrayscale, OtsuThreshold
from histolab.filters.morphological_filters import BinaryDilation, RemoveSmallObjects

# Individual filter steps
steps = [
    ("Original", None),
    ("Grayscale", RgbToGrayscale()),
    ("Otsu Threshold", Compose([RgbToGrayscale(), OtsuThreshold()])),
    ("After Dilation", Compose([RgbToGrayscale(), OtsuThreshold(), BinaryDilation(disk_size=5)])),
    ("Remove Small Objects", Compose([RgbToGrayscale(), OtsuThreshold(), BinaryDilation(disk_size=5), RemoveSmallObjects(area_threshold=500)]))
]

fig, axes = plt.subplots(1, len(steps), figsize=(20, 4))

for idx, (title, filter_fn) in enumerate(steps):
    if filter_fn is None:
        axes[idx].imshow(slide.thumbnail)
    else:
        result = filter_fn(slide.thumbnail)
        axes[idx].imshow(result, cmap='gray')
    axes[idx].set_title(title, fontsize=10)
    axes[idx].axis('off')

plt.tight_layout()
plt.show()
```

## Exporting Visualization Results

### High-Resolution Export

```python
# Export high-resolution image
fig, ax = plt.subplots(figsize=(20, 20))
ax.imshow(slide.thumbnail)
ax.axis('off')
plt.savefig("slide_high_res.png", dpi=300, bbox_inches='tight', pad_inches=0)
plt.close()
```

### PDF Reports

```python
from matplotlib.backends.backend_pdf import PdfPages

# Create a multi-page PDF report
with PdfPages('slide_report.pdf') as pdf:
    # Page 1: Slide thumbnail
    fig1, ax1 = plt.subplots(figsize=(10, 10))
    ax1.imshow(slide.thumbnail)
    ax1.set_title(f"Slide: {slide.name}")
    ax1.axis('off')
    pdf.savefig(fig1, bbox_inches='tight')
    plt.close()

    # Page 2: Tissue mask
    fig2, ax2 = plt.subplots(figsize=(10, 10))
    mask = TissueMask()(slide)
    ax2.imshow(mask, cmap='gray')
    ax2.set_title("Tissue Mask")
    ax2.axis('off')
    pdf.savefig(fig2, bbox_inches='tight')
    plt.close()

    # Page 3: Tile locations
    fig3, ax3 = plt.subplots(figsize=(10, 10))
    tiler = RandomTiler(tile_size=(512, 512), n_tiles=30)
    tiler.locate_tiles(slide)
    pdf.savefig(fig3, bbox_inches='tight')
    plt.close()
```

## Interactive Visualization (Jupyter)

### IPython Widgets for Exploration

```python
from ipywidgets import interact, IntSlider
import matplotlib.pyplot as plt
from histolab.filters.morphological_filters import BinaryDilation

@interact(disk_size=IntSlider(min=1, max=20, value=5))
def explore_dilation(disk_size):
    """Interactive dilation effect exploration."""
    filter_pipeline = Compose([
        RgbToGrayscale(),
        OtsuThreshold(),
        BinaryDilation(disk_size=disk_size)
    ])
    result = filter_pipeline(slide.thumbnail)

    plt.figure(figsize=(10, 10))
    plt.imshow(result, cmap='gray')
    plt.title(f"Binary Dilation (disk_size={disk_size})")
    plt.axis('off')
    plt.show()
```

## Best Practices

1. **Always preview before processing**: Use thumbnails and `locate_tiles()` to verify settings.
2. **Use side-by-side comparisons**: Show before and after effects of filters.
3. **Label clearly**: Include titles, axis labels, and legends.
4. **High-resolution export**: Use 300 DPI for publication-quality images.
5. **Save intermediate visualizations**: Document processing steps.
6. **Use appropriate colormaps**: Use 'gray' for binary masks and 'viridis' for heatmaps.
7. **Create reusable visualization functions**: Standardize reporting across projects.