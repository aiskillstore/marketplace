# Preprocessing Pipelines & Transforms

## Overview

PathML provides a modular preprocessing architecture based on composable transforms organized into pipelines. Transforms are individual operations that modify images, create masks, or extract features. Pipelines chain transforms together to create reproducible, scalable preprocessing workflows for computational pathology.

## Pipeline Architecture

### Pipeline Class

The `Pipeline` class combines a series of transforms to be applied sequentially:

```python
from pathml.preprocessing import Pipeline, Transform1, Transform2

# Create pipeline
pipeline = Pipeline([
    Transform1(param1=value1),
    Transform2(param2=value2),
    # ... more transforms
])

# Run on a single slide
pipeline.run(slide_data)

# Run on dataset
pipeline.run(dataset, distributed=True, n_workers=8)
```

**Key features:**
- Sequential execution of transforms
- Automatic handling of tiles and masks
- Support for distributed processing using Dask
- Reproducible workflows through serializable configurations

### Transform Base Class

All transforms inherit from the `Transform` base class and implement:
- `apply()` - Core transform logic
- `input_type` - Expected input (slide, mask, etc.)
- `output_type` - Produced output

## Transform Categories

PathML provides six major categories of transforms:

1. **Image Modification** - Blurring, scaling, histogram equalization
2. **Mask Creation** - Tissue detection, nucleus detection, thresholding
3. **Mask Modification** - Morphological operations on masks
4. **Stain Processing** - H&E stain normalization and separation
5. **Quality Control** - Artifact detection, whitespace labeling
6. **Specialized** - Multiparametric imaging, cell segmentation

## Image Modification Transforms

### Blur Operations

Apply various blur kernels to reduce noise:

**MedianBlur:**
```python
from pathml.preprocessing import MedianBlur

# Apply median filtering
transform = MedianBlur(kernel_size=5)
```
- Effective for salt-and-pepper noise
- Better edge preservation than Gaussian blur

**GaussianBlur:**
```python
from pathml.preprocessing import GaussianBlur

# Apply Gaussian blur
transform = GaussianBlur(kernel_size=5, sigma=1.0)
```
- Smooth noise reduction
- Adjustable sigma controls blur strength

**BoxBlur:**
```python
from pathml.preprocessing import BoxBlur

# Apply box filter
transform = BoxBlur(kernel_size=5)
```
- Fastest blur operation
- Uniform averaging within kernel

### Intensity Adjustments

**RescaleIntensity:**
```python
from pathml.preprocessing import RescaleIntensity

# Rescale intensity to [0, 255]
transform = RescaleIntensity(
    in_range=(0, 1.0),
    out_range=(0, 255)
)
```

**HistogramEqualization:**
```python
from pathml.preprocessing import HistogramEqualization

# Global histogram equalization
transform = HistogramEqualization()
```
- Enhances global contrast
- Expands intensity distribution

**AdaptiveHistogramEqualization (CLAHE):**
```python
from pathml.preprocessing import AdaptiveHistogramEqualization

# Contrast-limited adaptive histogram equalization
transform = AdaptiveHistogramEqualization(
    clip_limit=0.03,
    tile_grid_size=(8, 8)
)
```
- Enhances local contrast
- Prevents over-amplification through clip_limit
- Better suited for images with varying local contrast

### Superpixel Processing

**SuperpixelInterpolation:**
```python
from pathml.preprocessing import SuperpixelInterpolation

# Segment into superpixels using SLIC
transform = SuperpixelInterpolation(
    n_segments=100,
    compactness=10.0
)
```
- Segments image into perceptually meaningful regions
- Useful for feature extraction and segmentation

## Mask Creation Transforms

### H&E Tissue and Nucleus Detection

**TissueDetectionHE:**
```python
from pathml.preprocessing import TissueDetectionHE

# Detect tissue regions in H&E slides
transform = TissueDetectionHE(
    use_saturation=True,  # Use HSV saturation channel
    threshold=10,  # Intensity threshold
    min_region_size=500  # Minimum tissue region size (pixels)
)
```
- Creates binary tissue mask
- Filters small regions and artifacts
- Stores mask in `tile.masks['tissue']`

**NucleusDetectionHE:**
```python
from pathml.preprocessing import NucleusDetectionHE

# Detect nuclei in H&E images
transform = NucleusDetectionHE(
    stain='hematoxylin',  # Use hematoxylin channel
    threshold=0.3,
    min_nucleus_size=10
)
```
- Separates hematoxylin stain
- Creates nucleus mask through thresholding
- Stores mask in `tile.masks['nucleus']`

### Binary Thresholding

**BinaryThreshold:**
```python
from pathml.preprocessing import BinaryThreshold

# Threshold using Otsu's method
transform = BinaryThreshold(
    method='otsu',  # 'otsu' or manual threshold
    invert=False
)

# Or specify manual threshold
transform = BinaryThreshold(threshold=128)
```

### Foreground Detection

**ForegroundDetection:**
```python
from pathml.preprocessing import ForegroundDetection

# Detect foreground regions
transform = ForegroundDetection(
    threshold=0.5,
    min_region_size=1000,  # Minimum pixel size
    use_saturation=True
)
```

## Mask Modification Transforms

Apply morphological operations to clean up masks:

**MorphOpen:**
```python
from pathml.preprocessing import MorphOpen

# Remove small objects and noise
transform = MorphOpen(
    kernel_size=5,
    mask_name='tissue'  # Which mask to modify
)
```
- Erosion followed by dilation
- Removes small objects and noise

**MorphClose:**
```python
from pathml.preprocessing import MorphClose

# Fill small holes
transform = MorphClose(
    kernel_size=5,
    mask_name='tissue'
)
```
- Dilation followed by erosion
- Fills small holes in masks

## Stain Normalization

### StainNormalizationHE

Normalize H&E stain across slides to eliminate variability from staining procedures and scanner differences:

```python
from pathml.preprocessing import StainNormalizationHE

# Normalize to reference slide
transform = StainNormalizationHE(
    target='normalize',  # 'normalize', 'hematoxylin', or 'eosin'
    stain_estimation_method='macenko',  # 'macenko' or 'vahadane'
    tissue_mask_name=None  # Optional tissue mask for better estimation
)
```

**Target modes:**
- `'normalize'` - Normalize both stains to reference standard
- `'hematoxylin'` - Extract only hematoxylin channel
- `'eosin'` - Extract only eosin channel

**Stain estimation methods:**
- `'macenko'` - Macenko et al. (2009) method (faster, more stable)
- `'vahadane'` - Vahadane et al. (2016) method (more accurate, slower)

**Advanced parameters:**
```python
transform = StainNormalizationHE(
    target='normalize',
    stain_estimation_method='macenko',
    target_od=None,  # Reference optical density matrix (optional)
    target_concentrations=None,  # Target stain concentrations (optional)
    regularizer=0.1,  # Regularization term for vahadane method
    background_intensity=240  # Background intensity level
)
```

**Workflow:**
1. Convert RGB to optical density (OD)
2. Estimate stain matrix (H&E vectors)
3. Decompose into stain concentrations
4. Normalize to reference stain distribution
5. Reconstruct normalized RGB image

**Example with tissue mask:**
```python
from pathml.preprocessing import Pipeline, TissueDetectionHE, StainNormalizationHE

pipeline = Pipeline([
    TissueDetectionHE(),  # Create tissue mask first
    StainNormalizationHE(
        target='normalize',
        stain_estimation_method='macenko',
        tissue_mask_name='tissue'  # Use tissue mask for better estimation
    )
])
```

## Quality Control Transforms

### Artifact Detection

**LabelArtifactTileHE:**
```python
from pathml.preprocessing import LabelArtifactTileHE

# Label tile regions containing artifacts
transform = LabelArtifactTileHE(
    pen_threshold=0.5,  # Pen mark detection threshold
    bubble_threshold=0.5  # Bubble detection threshold
)
```
- Detects pen marks, bubbles, and other artifacts
- Labels affected tile regions for subsequent filtering

**LabelWhiteSpaceHE:**
```python
from pathml.preprocessing import LabelWhiteSpaceHE

# Label tile regions with excessive whitespace
transform = LabelWhiteSpaceHE(
    threshold=0.9,  # White pixel proportion
    mask_name='white_space'
)
```
- Identifies tile regions that are mostly background
- Useful for filtering uninformative tiles

## Multiparametric Imaging Transforms

### Cell Segmentation

**SegmentMIF:**
```python
from pathml.preprocessing import SegmentMIF

# Segment cells using Mesmer deep learning model
transform = SegmentMIF(
    nuclear_channel='DAPI',  # Nuclear marker channel name
    cytoplasm_channel='CD45',  # Cytoplasmic marker channel name
    model='mesmer',  # Deep learning segmentation model
    image_resolution=0.5,  # Microns per pixel
    compartment='whole-cell'  # 'nuclear', 'cytoplasm', or 'whole-cell'
)
```
- Cell segmentation using DeepCell Mesmer model
- Requires specifying nuclear and cytoplasmic channels
- Produces instance segmentation masks

**SegmentMIFRemote:**
```python
from pathml.preprocessing import SegmentMIFRemote

# Use DeepCell API for remote inference
transform = SegmentMIFRemote(
    nuclear_channel='DAPI',
    cytoplasm_channel='CD45',
    model='mesmer',
    api_url='https://deepcell.org/api'
)
```
- Same functionality as SegmentMIF but uses remote API
-
- Suitable for batch processing

### No local GPU required Marker Quantification

**QuantifyMIF:**
```python
from pathml.preprocessing import QuantifyMIF

# Quantify marker expression for each cell
transform = QuantifyMIF(
    segmentation_mask_name='cell_segmentation',
    markers=['CD3', 'CD4', 'CD8', 'CD20', 'CD45'],
    output_format='anndata'  # or 'dataframe'
)
```
- Extracts mean marker intensity for each segmented cell
- Computes morphological features (area, perimeter, etc.)
- Outputs AnnData object for downstream single-cell analysis

### CODEX/Vectra Specific Transforms

**CollapseRunsCODEX:**
```python
from pathml.preprocessing import CollapseRunsCODEX

# Collapse multi-run CODEX data
transform = CollapseRunsCODEX(
    z_slice=2,  # Select specific z-axis slice
    run_order=[0, 1, 2]  # Order of acquisition runs
)
```
- Combines channels from multiple CODEX acquisition runs
- Selects focused plane from z-stacks

**CollapseRunsVectra:**
```python
from pathml.preprocessing import CollapseRunsVectra

# Process Vectra multiplexed immunofluorescence (mIF) data
transform = CollapseRunsVectra(
    wavelengths=[520, 570, 620, 670, 780]  # Emission wavelengths
)
```

## Building Comprehensive Pipelines

### Basic H&E Preprocessing Pipeline

```python
from pathml.preprocessing import (
    Pipeline,
    TissueDetectionHE,
    StainNormalizationHE,
    NucleusDetectionHE,
    MedianBlur,
    LabelWhiteSpaceHE
)

pipeline = Pipeline([
    # 1. Quality control
    LabelWhiteSpaceHE(threshold=0.9),

    # 2. Denoising
    MedianBlur(kernel_size=3),

    # 3. Tissue detection
    TissueDetectionHE(min_region_size=500),

    # 4. Stain normalization
    StainNormalizationHE(
        target='normalize',
        stain_estimation_method='macenko',
        tissue_mask_name='tissue'
    ),

    # 5. Nucleus detection
    NucleusDetectionHE(threshold=0.3)
])
```

### CODEX Multiparametric Pipeline

```python
from pathml.preprocessing import (
    Pipeline,
    CollapseRunsCODEX,
    SegmentMIF,
    QuantifyMIF
)

codex_pipeline = Pipeline([
    # 1. Collapse multi-run data
    CollapseRunsCODEX(z_slice=2),

    # 2. Cell segmentation
    SegmentMIF(
        nuclear_channel='DAPI',
        cytoplasm_channel='CD45',
        model='mesmer',
        image_resolution=0.377
    ),

    # 3. Marker quantification
    QuantifyMIF(
        segmentation_mask_name='cell_segmentation',
        markers=['CD3', 'CD4', 'CD8', 'CD20', 'PD1', 'PDL1'],
        output_format='anndata'
    )
])
```

### Advanced Pipeline with Quality Control

```python
from pathml.preprocessing import (
    Pipeline,
    LabelWhiteSpaceHE,
    LabelArtifactTileHE,
    TissueDetectionHE,
    MorphOpen,
    MorphClose,
    StainNormalizationHE,
    AdaptiveHistogramEqualization
)

advanced_pipeline = Pipeline([
    # Stage 1: Quality control
    LabelWhiteSpaceHE(threshold=0.85),
    LabelArtifactTileHE(pen_threshold=0.5, bubble_threshold=0.5),

    # Stage 2: Tissue detection
    TissueDetectionHE(threshold=10, min_region_size=1000),
    MorphOpen(kernel_size=5, mask_name='tissue'),
    MorphClose(kernel_size=7, mask_name='tissue'),

    # Stage 3: Stain normalization
    StainNormalizationHE(
        target='normalize',
        stain_estimation_method='vahadane',
        tissue_mask_name='tissue'
    ),

    # Stage 4: Contrast enhancement
    AdaptiveHistogramEqualization(clip_limit=0.03, tile_grid_size=(8, 8))
])
```

## Running Pipelines

### Single Slide Processing

```python
from pathml.core import SlideData

# Load slide
wsi = SlideData.from_slide("slide.svs")

# Generate tiles
wsi.generate_tiles(level=1, tile_size=256, stride=256)

# Run pipeline
pipeline.run(wsi)

# Access processed data
for tile in wsi.tiles:
    normalized_image = tile.image
    tissue_mask = tile.masks.get('tissue')
    nucleus_mask = tile.masks.get('nucleus')
```

### Batch Processing with Distributed Execution

```python
from pathml.core import SlideDataset
from dask.distributed import Client
import glob

# Start Dask client
client = Client(n_workers=8, threads_per_worker=2, memory_limit='4GB')

# Create dataset
slide_paths = glob.glob("data/*.svs")
dataset = SlideDataset(
    slide_paths,
    tile_size=512,
    stride=512,
    level=1
)

# Run pipeline in parallel
dataset.run(
    pipeline,
    distributed=True,
    client=client
)

# Save results
dataset.to_hdf5("processed_dataset.h5")

client.close()
```

### Conditional Pipeline Execution

Execute transforms only on tiles meeting specific criteria:

```python
# Generate tiles before processing
wsi.generate_tiles(level=1, tile_size=256)

# Run pipeline only on tissue tiles
for tile in wsi.tiles:
    if tile.masks.get('tissue') is not None:
        pipeline.run(tile)
```

## Performance Optimization

### Memory Management

```python
# Process large datasets in batches
batch_size = 100
for i in range(0, len(slide_paths), batch_size):
    batch_paths = slide_paths[i:i+batch_size]
    batch_dataset = SlideDataset(batch_paths)
    batch_dataset.run(pipeline, distributed=True)
    batch_dataset.to_hdf5(f"batch_{i}.h5")
```

### GPU Acceleration

Some transforms leverage GPU acceleration when available:

```python
import torch

# Check GPU availability
print(f"CUDA available: {torch.cuda.is_available()}")

# Transforms that benefit from GPU:
# - SegmentMIF (Mesmer deep learning model)
# - StainNormalizationHE (Matrix operations)
```

### Parallel Worker Configuration

```python
from dask.distributed import Client

# CPU-intensive tasks (image processing)
client = Client(
    n_workers=8,
    threads_per_worker=1,  # Use processes instead of threads
    memory_limit='8GB'
)

# GPU tasks (deep learning inference)
client = Client(
    n_workers=2,  # Fewer workers for GPU tasks
    threads_per_worker=4,
    processes=True
)
```

## Custom Transforms

Create custom preprocessing operations by subclassing `Transform`:

```python
from pathml.preprocessing.transforms import Transform
import numpy as np

class CustomTransform(Transform):
    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2

    def apply(self, tile):
        # Access tile image
        image = tile.image

        # Apply custom operation
        processed = self.custom_operation(image, self.param1, self.param2)

        # Update tile
        tile.image = processed

        return tile

    def custom_operation(self, image, param1, param2):
        # Implement custom logic
        return processed_image

# Use in pipeline
pipeline = Pipeline([
    CustomTransform(param1=10, param2=0.5),
    # ... other transforms
])
```

## Best Practices

1. **Order transforms appropriately:**
   - Quality control first (LabelWhiteSpace, LabelArtifact)
   - Denoising early (Blur)
   - Tissue detection before stain normalization
   - Stain normalization before color-related operations

2. **Use tissue masks for stain normalization:**
   - Improves accuracy by excluding background
   - Run `TissueDetectionHE()` first, then `StainNormalizationHE(tissue_mask_name='tissue')`

3. **Apply morphological operations to clean masks:**
   - Use `MorphOpen` to remove tiny false positives
   - Use `MorphClose` to fill tiny gaps

4. **Use distributed processing for large datasets:**
   - Use Dask for parallel execution
   - Configure workers based on available resources

5. **Save intermediate results:**
   - Store processed data as HDF5 for reuse
   - Avoid reprocessing computationally expensive transforms

6. **Validate preprocessing on sample images:**
   - Visualize intermediate steps
   - Adjust parameters on representative samples before batch processing

7. **Handle edge cases:**
   - Check if masks are empty before downstream operations
   - Validate slide quality before expensive computations

## Common Issues and Solutions

**Problem: Stain normalization produces artifacts**
- Use tissue mask to exclude background
- Try different stain estimation methods (macenko vs. vahadane)
- Verify optical density parameters match your images

**Problem: Out of memory during pipeline execution**
- Reduce number of Dask workers
- Reduce tile size
- Process images at lower pyramid levels
- Enable memory_limit parameter in Dask client

**Problem: Tissue detection misses tissue regions**
- Adjust threshold parameter
- Use saturation channel: `use_saturation=True`
- Reduce min_region_size to capture smaller tissue fragments

**Problem: Nucleus detection is inaccurate**
- Verify stain separation quality (visualize hematoxylin channel)
- Adjust threshold parameter
- Apply stain normalization before nucleus detection

## Additional Resources

- **PathML Preprocessing API Docs:** https://pathml.readthedocs.io/en/latest/api_preprocessing_reference.html
- **Stain normalization methods:**
  - Macenko et al. (2009): "A method for normalizing histology slides for quantitative analysis"
  - Vahadane et al. (2016): "Structure-Preserving Color Normalization and Sparse Stain Separation"
- **DeepCell Mesmer:** https://www.deepcell.org/ (Cell segmentation models)
