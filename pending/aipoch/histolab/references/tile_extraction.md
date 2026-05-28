# Tile Extraction

## Overview

Tile extraction is the process of cropping smaller, manageable regions from large Whole Slide Images (WSIs). Histolab provides three main extraction strategies, each suited for different analysis needs. All tilers share common parameters and provide methods for previewing and extracting tiles.

## Common Parameters

All tiler classes accept the following parameters:

```python
tile_size: tuple = (512, 512)           # Tile dimensions in pixels (width, height)
level: int = 0                          # Extraction pyramid level (0=highest resolution)
check_tissue: bool = True               # Filter tiles based on tissue content
tissue_percent: float = 80.0            # Minimum tissue coverage (0-100)
pixel_overlap: int = 0                  # Overlapping pixels between adjacent tiles (GridTiler only)
prefix: str = ""                        # Prefix for saved tile filenames
suffix: str = ".png"                    # File extension for saved tiles
extraction_mask: BinaryMask = BiggestTissueBoxMask()  # Mask defining the extraction area
```

## RandomTiler

**Purpose:** Extract a fixed number of tiles from random positions within tissue regions.

```python
from histolab.tiler import RandomTiler

random_tiler = RandomTiler(
    tile_size=(512, 512),
    n_tiles=100,                # Number of random tiles to extract
    level=0,
    seed=42,                    # Random seed for reproducibility
    check_tissue=True,
    tissue_percent=80.0
)

# Extract tiles
random_tiler.extract(slide, extraction_mask=TissueMask())
```

**Key Parameters:**
- `n_tiles`: Number of random tiles to extract.
- `seed`: Random seed for reproducible tile selection.
- `max_iter`: Maximum number of attempts to find valid tiles (default is 1000).

**Usage Scenarios:**
- Exploratory analysis of slide content.
- Sampling diverse regions for training data.
- Rapid assessment of tissue characteristics.
- Creating balanced datasets from multiple slides.

**Pros:**
- Computationally efficient.
- Good for sampling diverse tissue morphologies.
- Reproducible results via the seed parameter.
- Fast execution.

**Cons:**
- May miss rare tissue patterns.
- No guarantee of coverage.
- Random distribution might not capture structural features.

## GridTiler

**Purpose:** Systematically extract tiles across the entire tissue area in a grid pattern.

```python
from histolab.tiler import GridTiler

grid_tiler = GridTiler(
    tile_size=(512, 512),
    level=0,
    check_tissue=True,
    tissue_percent=80.0,
    pixel_overlap=0             # Overlapping pixels between adjacent tiles
)

# Extract tiles
grid_tiler.extract(slide)
```

**Key Parameters:**
- `pixel_overlap`: Number of pixels to overlap between adjacent tiles.
  - `pixel_overlap=0`: Non-overlapping tiles.
  - `pixel_overlap=128`: 128-pixel overlap on each side.
  - Useful for sliding window approaches.

**Usage Scenarios:**
- Comprehensive slide coverage.
- Spatial analysis requiring positional information.
- Image reconstruction from tiles.
- Semantic segmentation tasks.
- Region-based analysis.

**Pros:**
- Complete tissue coverage.
- Preserves spatial relationships.
- Predictable tile locations.
- Suitable for whole-slide analysis.

**Cons:**
- Computationally intensive for large slides.
- May generate many tiles with high background (mitigated by `check_tissue`).
- Large output datasets.

**Grid Pattern:**
```
[Tile 1][Tile 2][Tile 3]
[Tile 4][Tile 5][Tile 6]
[Tile 7][Tile 8][Tile 9]
```

When `pixel_overlap=64`:
```
[Tile 1-overlap-Tile 2-overlap-Tile 3]
[    overlap       overlap       overlap]
[Tile 4-overlap-Tile 5-overlap-Tile 6]
```

## ScoreTiler

**Purpose:** Extract top-ranked tiles based on a custom scoring function.

```python
from histolab.tiler import ScoreTiler
from histolab.scorer import NucleiScorer

score_tiler = ScoreTiler(
    tile_size=(512, 512),
    n_tiles=50,                 # Number of top-scoring tiles to extract
    level=0,
    scorer=NucleiScorer(),      # Scoring function
    check_tissue=True
)

# Extract top-scoring tiles
score_tiler.extract(slide)
```

**Key Parameters:**
- `n_tiles`: Number of top-scoring tiles to extract.
- `scorer`: Scoring function (e.g., `NucleiScorer`, `CellularityScorer`, or a custom scorer).

**Usage Scenarios:**
- Extracting the most informative regions.
- Prioritizing tiles with specific features (nuclei, cells, etc.).
- Quality-based tile selection.
- Focusing on areas with diagnostic relevance.
- Training data curation.

**Pros:**
- Focuses on the most informative tiles.
- Reduces dataset size while maintaining quality.
- Customizable with different scorers.
- Efficient for targeted analysis.

**Cons:**
- Slower than RandomTiler (must score all candidate tiles).
- Requires a suitable scorer for the task.
- May miss low-scoring but relevant regions.

## Available Scorers

### NucleiScorer

Scores tiles based on nuclei detection and density.

```python
from histolab.scorer import NucleiScorer

nuclei_scorer = NucleiScorer()
```

**How it works:**
1. Converts the tile to grayscale.
2. Applies thresholding to detect nuclei.
3. Counts nuclei-like structures.
4. Assigns a score based on nuclei density.

**Best for:**
- Cell-rich tissue areas.
- Tumor detection.
- Mitotic analysis.
- High cellularity regions.

### CellularityScorer

Scores tiles based on overall cellular content.

```python
from histolab.scorer import CellularityScorer

cellularity_scorer = CellularityScorer()
```

**Best for:**
- Distinguishing cellular regions from stroma.
- Tumor cell abundance assessment.
- Isolating dense vs. sparse tissue areas.

### Custom Scorers

Create custom scoring functions for specific needs:

```python
from histolab.scorer import Scorer
import numpy as np

class ColorVarianceScorer(Scorer):
    def __call__(self, tile):
        """Score tile based on color variance."""
        tile_array = np.array(tile.image)
        # Calculate color variance
        variance = np.var(tile_array, axis=(0, 1)).sum()
        return variance

# Use custom scorer
variance_scorer = ColorVarianceScorer()
score_tiler = ScoreTiler(
    tile_size=(512, 512),
    n_tiles=30,
    scorer=variance_scorer
)
```

## Previewing Tiles with locate_tiles()

Preview tile positions before extraction to verify tiler configuration:

```python
# Preview random tile locations
random_tiler.locate_tiles(
    slide=slide,
    extraction_mask=TissueMask(),
    n_tiles=20  # Number of tiles to preview (for RandomTiler)
)
```

This displays a thumbnail of the slide with colored rectangles indicating tile positions.

## Extraction Workflow

### Basic Extraction

```python
from histolab.slide import Slide
from histolab.tiler import RandomTiler

# Load slide
slide = Slide("slide.svs", processed_path="output/tiles/")

# Configure tiler
tiler = RandomTiler(
    tile_size=(512, 512),
    n_tiles=100,
    level=0,
    seed=42
)

# Extract tiles (saves to processed_path)
tiler.extract(slide)
```

### Extraction with Logging

```python
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)

# Extract tiles with progress info
tiler.extract(slide)
# Output: INFO: Tile 1/100 saved...
# Output: INFO: Tile 2/100 saved...
```

### Extraction with Report

```python
# Generate a CSV report with tile information
score_tiler = ScoreTiler(
    tile_size=(512, 512),
    n_tiles=50,
    scorer=NucleiScorer()
)

# Extract and save report
score_tiler.extract(slide, report_path="tiles_report.csv")

# Report contains: tile_name, coordinates, score, tissue percentage
```

Report format:
```csv
tile_name,x_coord,y_coord,level,score,tissue_percent
tile_001.png,10240,5120,0,0.89,95.2
tile_002.png,15360,7680,0,0.85,91.7
...
```

## Advanced Extraction Patterns

### Multi-level Extraction

Extract tiles at different magnification levels:

```python
# High resolution tiles (level 0)
high_res_tiler = RandomTiler(tile_size=(512, 512), n_tiles=50, level=0)
high_res_tiler.extract(slide)

# Medium resolution tiles (level 1)
med_res_tiler = RandomTiler(tile_size=(512, 512), n_tiles=50, level=1)
med_res_tiler.extract(slide)

# Low resolution tiles (level 2)
low_res_tiler = RandomTiler(tile_size=(512, 512), n_tiles=50, level=2)
low_res_tiler.extract(slide)
```

### Hierarchical Extraction

Extract tiles from the same location at multiple scales:

```python
# Extract random positions at level 0
random_tiler_l0 = RandomTiler(
    tile_size=(512, 512),
    n_tiles=30,
    level=0,
    seed=42,
    prefix="level0_"
)
random_tiler_l0.extract(slide)

# Extract same positions at level 1 (using same seed)
random_tiler_l1 = RandomTiler(
    tile_size=(512, 512),
    n_tiles=30,
    level=1,
    seed=42,
    prefix="level1_"
)
random_tiler_l1.extract(slide)
```

### Custom Tile Filtering

Apply additional filtering after extraction:

```python
from PIL import Image
import numpy as np
from pathlib import Path

def filter_blurry_tiles(tile_dir, threshold=100):
    """Remove blurry tiles using Laplacian variance."""
    for tile_path in Path(tile_dir).glob("*.png"):
        img = Image.open(tile_path)
        gray = np.array(img.convert('L'))
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        if laplacian_var < threshold:
            tile_path.unlink()  # Remove blurry tile
            print(f"Removed blurry tile: {tile_path.name}")

# Use after extraction
tiler.extract(slide)
filter_blurry_tiles("output/tiles/")
```

## Best Practices

1. **Preview before extracting**: Always use `locate_tiles()` to verify tile placement.
2. **Use appropriate levels**: Match the extraction level to your analysis resolution requirements.
3. **Set tissue_percent thresholds**: Adjust based on staining and tissue type (typically 70-90%).
4. **Choose the right tiler**:
   - RandomTiler for sampling and exploration.
   - GridTiler for comprehensive coverage.
   - ScoreTiler for targeted, quality-driven extraction.
5. **Enable logging**: Monitor extraction progress for large datasets.
6. **Use seeds for reproducibility**: Set random seeds in RandomTiler.
7. **Consider storage space**: GridTiler can generate thousands of tiles per slide.
8. **Verify tile quality**: Check extracted tiles for artifacts, blur, or focus issues.

## Performance Optimization

1. **Extract at appropriate levels**: Lower levels (1, 2) are faster to extract.
2. **Adjust tissue_percent**: Higher thresholds can reduce attempts for invalid tiles.
3. **Use BiggestTissueBoxMask**: Faster than TissueMask for single tissue sections.
4. **Limit n_tiles**: For RandomTiler and ScoreTiler.
5. **Use pixel_overlap=0**: For non-overlapping GridTiler extraction.

## Troubleshooting

### Issue: No tiles extracted
**Solutions:**
- Lower the `tissue_percent` threshold.
- Verify the WSI contains tissue (check thumbnail).
- Ensure the `extraction_mask` captures the tissue area.
- Check if `tile_size` is appropriate for the slide's resolution.

### Issue: Too many background tiles
**Solutions:**
- Enable `check_tissue=True`.
- Increase the `tissue_percent` threshold.
- Use an appropriate mask (TissueMask vs. BiggestTissueBoxMask).

### Issue: Extraction is very slow
**Solutions:**
- Extract at a lower pyramid level (level=1 or 2).
- Reduce `n_tiles` for RandomTiler/ScoreTiler.
- Use RandomTiler instead of GridTiler for sampling.
- Use BiggestTissueBoxMask instead of TissueMask.

### Issue: Tiles overlap too much (GridTiler)
**Solutions:**
- Set `pixel_overlap` to 0 for non-overlapping tiles.
- Decrease the `pixel_overlap` value.