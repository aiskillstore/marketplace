---
name: histolab
description: Lightweight Whole Slide Image (WSI) tiling and preprocessing for digital pathology; use when you need fast tissue detection and tile extraction to prepare datasets or run quick tile-based analysis.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to **tile gigapixel Whole Slide Images (WSI)** into manageable patches for downstream analysis.
- You want **automatic tissue detection** to avoid background-heavy tiles during dataset preparation.
- You are building a **simple, fast preprocessing pipeline** (e.g., thresholding + morphology) for H&E slides.
- You need **random sampling, grid coverage, or score-based selection** of tiles for exploratory analysis or model training.
- You want to **preview masks and tile locations** before running extraction to validate parameters quickly.

> Note: For advanced multiplex/spatial workflows or complex deep learning pipelines, consider more specialized frameworks (e.g., PathML).

## Key Features

- **Slide management** via `Slide`: load WSI formats (SVS, TIFF, NDPI, etc.), access metadata, thumbnails, pyramid levels, and regions.
- **Tissue masking** via `TissueMask`, `BiggestTissueBoxMask`, and custom `BinaryMask` implementations.
- **Tile extraction strategies**:
  - `RandomTiler` (random sampling with reproducible seeds)
  - `GridTiler` (systematic coverage with optional overlap)
  - `ScoreTiler` (top-N tiles by a scoring function such as nuclei density)
- **Preprocessing filters** (image + morphology) and **filter pipelines** via `Compose`.
- **Visualization helpers** to preview masks (`locate_mask`) and tile locations (`locate_tiles`) and to review extracted tiles.

Reference docs (optional, for deeper detail):  
- `references/slide_management.md`  
- `references/tissue_masks.md`  
- `references/tile_extraction.md`  
- `references/filters_preprocessing.md`  
- `references/visualization.md`

## Dependencies

- `histolab` (install via pip/uv; version depends on your environment)

Installation:

```bash
uv pip install histolab
```

## Example Usage

A complete, runnable example that loads a slide, builds a tissue mask, previews tile locations, and extracts tiles.

```python
from pathlib import Path

from histolab.slide import Slide
from histolab.masks import TissueMask
from histolab.tiler import RandomTiler

def main():
    slide_path = "slide.svs"  # replace with your WSI path
    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) Load slide
    slide = Slide(slide_path, processed_path=str(out_dir))

    # 2) Build/preview tissue mask
    tissue_mask = TissueMask()
    slide.locate_mask(tissue_mask)  # writes a visualization into processed_path

    # 3) Configure tiler
    tiler = RandomTiler(
        tile_size=(512, 512),
        n_tiles=100,
        level=0,
        seed=42,
        check_tissue=True,
        tissue_percent=80.0,
    )

    # 4) Preview tile locations (recommended before extraction)
    tiler.locate_tiles(slide, n_tiles=20)

    # 5) Extract tiles (restricted to tissue mask)
    tiler.extract(slide, extraction_mask=tissue_mask)

    print("Done. Check the output directory for thumbnails, mask previews, and tiles.")

if __name__ == "__main__":
    main()
```

## Implementation Details

### Slide and pyramid levels
- WSIs are typically stored as **pyramids** (multiple resolutions).
- `level=0` usually means **highest resolution** (slowest, largest output).
- Using `level=1` or `level=2` can significantly improve throughput for dataset prototyping.

### Tissue masking
- `TissueMask` generally segments **all tissue regions** (useful when multiple fragments exist).
- `BiggestTissueBoxMask` focuses on the **largest tissue region** (often faster and cleaner for single-section slides).
- Masks can be customized by passing a filter pipeline (see `references/tissue_masks.md` and `references/filters_preprocessing.md`).

### Tile extraction strategies and key parameters
- **Common parameters**
  - `tile_size=(w, h)`: output tile dimensions in pixels at the chosen pyramid level.
  - `check_tissue=True`: enables tissue-content filtering.
  - `tissue_percent`: minimum tissue coverage required for a tile to be accepted (commonly 70–90).
  - `extraction_mask`: restricts candidate tile locations to a mask-defined ROI.
- **RandomTiler**
  - `n_tiles`: number of tiles to sample.
  - `seed`: ensures reproducibility across runs.
- **GridTiler**
  - `pixel_overlap`: overlap between adjacent tiles (0 for non-overlapping grids).
- **ScoreTiler**
  - `scorer`: ranks tiles (e.g., `NucleiScorer`) and selects top tiles.
  - Often used with a CSV report (`report_path`) for auditability.

### Filters and preprocessing pipelines
- Filters are typically chained using `Compose` to build repeatable pipelines (e.g., grayscale → threshold → morphology).
- These pipelines can be used to:
  - improve tissue segmentation robustness,
  - remove small artifacts/holes,
  - tailor detection to staining variability.

For concrete filter recipes and parameter guidance, see `references/filters_preprocessing.md`.