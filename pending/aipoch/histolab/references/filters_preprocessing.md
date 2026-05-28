# Filters and Preprocessing

## Overview

Histolab provides a comprehensive set of filters for Whole Slide Images (WSI) and Tiles. Filters can be applied for visualization, quality control, tissue detection, and artifact removal. They are composable and can be chained together to create complex preprocessing pipelines.

## Filter Categories

### Image Filters
Includes color space conversions, thresholding, and intensity adjustments.

### Morphological Filters
Includes structural operations such as dilation, erosion, opening, and closing.

### Composition Filters
Utilities for combining multiple filters.

## Image Filters

### RgbToGrayscale

Converts an RGB image to grayscale.

```python
from histolab.filters.image_filters import RgbToGrayscale

gray_filter = RgbToGrayscale()
gray_image = gray_filter(rgb_image)
```

**Use Cases:**
- Preprocessing for intensity-based operations
- Simplifying color complexity
- Input for morphological operations

### RgbToHsv

Converts RGB to the HSV (Hue, Saturation, Value) color space.

```python
from histolab.filters.image_filters import RgbToHsv

hsv_filter = RgbToHsv()
hsv_image = hsv_filter(rgb_image)
```

**Use Cases:**
- Color-based tissue segmentation
- Detecting pen marks via hue
- Separating chromatic and achromatic content

### RgbToHed

Converts RGB to the HED (Hematoxylin-Eosin-DAB) color space for stain deconvolution.

```python
from histolab.filters.image_filters import RgbToHed

hed_filter = RgbToHed()
hed_image = hed_filter(rgb_image)
```

**Use Cases:**
- Separating H&E stain components
- Analyzing nuclei (Hematoxylin) vs. cytoplasm (Eosin) staining
- Quantifying stain intensity

### OtsuThreshold

Applies Otsu's automatic thresholding method to create a binary image.

```python
from histolab.filters.image_filters import OtsuThreshold

otsu_filter = OtsuThreshold()
binary_image = otsu_filter(grayscale_image)
```

**How it Works:**
- Automatically determines the optimal threshold
- Separates foreground from background
- Minimizes intra-class variance

**Use Cases:**
- Tissue detection
- Nuclei segmentation
- Binary mask creation

### AdaptiveThreshold

Applies adaptive thresholding based on local intensity variations.

```python
from histolab.filters.image_filters import AdaptiveThreshold

adaptive_filter = AdaptiveThreshold(
    block_size=11,      # Size of the local neighborhood
    offset=2            # Constant subtracted from the mean
)
binary_image = adaptive_filter(grayscale_image)
```

**Use Cases:**
- Situations with uneven illumination
- Local contrast enhancement
- Handling varying stain intensities

### Invert

Inverts image intensity values.

```python
from histolab.filters.image_filters import Invert

invert_filter = Invert()
inverted_image = invert_filter(image)
```

**Use Cases:**
- Preprocessing for specific segmentation algorithms
- Visualization adjustments

### StretchContrast

Enhances image contrast by stretching the intensity range.

```python
from histolab.filters.image_filters import StretchContrast

contrast_filter = StretchContrast()
enhanced_image = contrast_filter(image)
```

**Use Cases:**
- Improving visibility of low-contrast features
- Visualization preprocessing
- Enhancing faint structures

### HistogramEqualization

Performs histogram equalization to enhance contrast.

```python
from histolab.filters.image_filters import HistogramEqualization

hist_eq_filter = HistogramEqualization()
equalized_image = hist_eq_filter(grayscale_image)
```

**Use Cases:**
- Standardizing image contrast
- Revealing hidden details
- Preprocessing for feature extraction

## Morphological Filters

### BinaryDilation

Expands the white regions in a binary image.

```python
from histolab.filters.morphological_filters import BinaryDilation

dilation_filter = BinaryDilation(disk_size=5)
dilated_image = dilation_filter(binary_image)
```

**Parameters:**
- `disk_size`: Size of the structural element (default: 5)

**Use Cases:**
- Connecting adjacent tissue regions
- Filling small gaps
- Expanding tissue masks

### BinaryErosion

Shrinks the white regions in a binary image.

```python
from histolab.filters.morphological_filters import BinaryErosion

erosion_filter = BinaryErosion(disk_size=5)
eroded_image = erosion_filter(binary_image)
```

**Use Cases:**
- Removing small protrusions
- Separating connected objects
- Shrinking tissue boundaries

### BinaryOpening

Erosion followed by dilation (removes small objects).

```python
from histolab.filters.morphological_filters import BinaryOpening

opening_filter = BinaryOpening(disk_size=3)
opened_image = opening_filter(binary_image)
```

**Use Cases:**
- Removing small artifacts
- Smoothing object boundaries
- Noise reduction

### BinaryClosing

Dilation followed by erosion (fills small holes).

```python
from histolab.filters.morphological_filters import BinaryClosing

closing_filter = BinaryClosing(disk_size=5)
closed_image = closing_filter(binary_image)
```

**Use Cases:**
- Filling small holes in tissue regions
- Connecting neighboring objects
- Smoothing internal boundaries

### RemoveSmallObjects

Removes connected components smaller than a specified threshold.

```python
from histolab.filters.morphological_filters import RemoveSmallObjects

remove_small_filter = RemoveSmallObjects(
    area_threshold=500  # Minimum area (pixels)
)
cleaned_image = remove_small_filter(binary_image)
```

**Use Cases:**
- Removing dust and artifacts
- Filtering noise
- Cleaning tissue masks

### RemoveSmallHoles

Fills holes smaller than a specified threshold.

```python
from histolab.filters.morphological_filters import RemoveSmallHoles

fill_holes_filter = RemoveSmallHoles(
    area_threshold=1000  # Maximum size of holes to fill
)
filled_image = fill_holes_filter(binary_image)
```

**Use Cases:**
- Filling tiny gaps in tissue
- Creating continuous tissue regions
- Removing internal artifacts

## Filter Compositions

### Chaining Filters

Combine multiple filters in sequence:

```python
from histolab.filters.image_filters import RgbToGrayscale, OtsuThreshold
from histolab.filters.morphological_filters import BinaryDilation, RemoveSmallObjects
from histolab.filters.compositions import Compose

# Create a filter pipeline
tissue_detection_pipeline = Compose([
    RgbToGrayscale(),
    OtsuThreshold(),
    BinaryDilation(disk_size=5),
    RemoveSmallHoles(area_threshold=1000),
    RemoveSmallObjects(area_threshold=500)
])

# Apply the pipeline
result = tissue_detection_pipeline(rgb_image)
```

### Lambda Filters

Create custom filters on the fly:

```python
from histolab.filters.image_filters import Lambda
import numpy as np

# Custom brightness adjustment
brightness_filter = Lambda(lambda img: np.clip(img * 1.2, 0, 255).astype(np.uint8))

# Custom channel extraction
red_channel_filter = Lambda(lambda img: img[:, :, 0])
```

## Common Preprocessing Pipelines

### Standard Tissue Detection

```python
from histolab.filters.compositions import Compose
from histolab.filters.image_filters import RgbToGrayscale, OtsuThreshold
from histolab.filters.morphological_filters import (
    BinaryDilation, RemoveSmallHoles, RemoveSmallObjects
)

tissue_detection = Compose([
    RgbToGrayscale(),
    OtsuThreshold(),
    BinaryDilation(disk_size=5),
    RemoveSmallHoles(area_threshold=1000),
    RemoveSmallObjects(area_threshold=500)
])
```

### Pen Mark Removal

```python
from histolab.filters.image_filters import RgbToHsv, Lambda
import numpy as np

def remove_pen_marks(hsv_image):
    """Remove blue/green pen marks."""
    h, s, v = hsv_image[:, :, 0], hsv_image[:, :, 1], hsv_image[:, :, 2]
    # Mask for blue/green hues (common pen colors)
    pen_mask = ((h > 0.45) & (h < 0.7) & (s > 0.3))
    # Set pen mark areas to white
    hsv_image[pen_mask] = [0, 0, 1]
    return hsv_image

pen_removal = Compose([
    RgbToHsv(),
    Lambda(remove_pen_marks)
])
```

### Nuclei Enhancement

```python
from histolab.filters.image_filters import RgbToHed, HistogramEqualization
from histolab.filters.compositions import Compose

nuclei_enhancement = Compose([
    RgbToHed(),
    Lambda(lambda hed: hed[:, :, 0]),  # Extract Hematoxylin channel
    HistogramEqualization()
])
```

### Contrast Normalization

```python
from histolab.filters.image_filters import StretchContrast, HistogramEqualization

contrast_normalization = Compose([
    RgbToGrayscale(),
    StretchContrast(),
    HistogramEqualization()
])
```

## Applying Filters to Tiles

Filters can be applied to individual tiles:

```python
from histolab.tile import Tile
from histolab.filters.image_filters import RgbToGrayscale

# Load or extract a tile
tile = Tile(image=pil_image, coords=(x, y))

# Apply a filter
gray_filter = RgbToGrayscale()
filtered_tile = tile.apply_filters(gray_filter)

# Chain multiple filters
from histolab.filters.compositions import Compose
from histolab.filters.image_filters import StretchContrast

filter_chain = Compose([
    RgbToGrayscale(),
    StretchContrast()
])
processed_tile = tile.apply_filters(filter_chain)
```

## Custom Mask Filters

Integrate custom filters with tissue masks:

```python
from histolab.masks import TissueMask
from histolab.filters.compositions import Compose
from histolab.filters.image_filters import RgbToGrayscale, OtsuThreshold
from histolab.filters.morphological_filters import BinaryDilation

# Custom aggressive tissue detection
aggressive_filters = Compose([
    RgbToGrayscale(),
    OtsuThreshold(),
    BinaryDilation(disk_size=10),  # Larger dilation size
    RemoveSmallObjects(area_threshold=5000)  # Only remove large artifacts
])

# Create a mask using custom filters
custom_mask = TissueMask(filters=aggressive_filters)
```

## Stain Normalization

While histolab does not have built-in stain normalization, you can use filters for basic normalization:

```python
from histolab.filters.image_filters import RgbToHed, Lambda
import numpy as np

def normalize_hed(hed_image, target_means=[0.65, 0.70], target_stds=[0.15, 0.13]):
    """Simple H&E normalization."""
    h_channel = hed_image[:, :, 0]
    e_channel = hed_image[:, :, 1]

    # Normalize Hematoxylin
    h_normalized = (h_channel - h_channel.mean()) / h_channel.std()
    h_normalized = h_normalized * target_stds[0] + target_means[0]

    # Normalize Eosin
    e_normalized = (e_channel - e_channel.mean()) / e_channel.std()
    e_normalized = e_normalized * target_stds[1] + target_means[1]

    hed_image[:, :, 0] = h_normalized
    hed_image[:, :, 1] = e_normalized

    return hed_image

normalization_pipeline = Compose([
    RgbToHed(),
    Lambda(normalize_hed)
    # Convert back to RGB if needed
])
```

## Best Practices

1. **Preview Filters**: Visualize filter outputs on thumbnails before applying them to tiles.
2. **Efficient Chaining**: Arrange filter order logically (e.g., color conversion before thresholding).
3. **Tune Parameters**: Adjust thresholds and structural element sizes for specific tissues.
4. **Use Compositions**: Build reusable filter pipelines using `Compose`.
5. **Consider Performance**: Complex filter chains increase processing time.
6. **Validate on Diverse Slides**: Test filters across different scanners, stains, and tissue types.
7. **Document Custom Filters**: Clearly describe the purpose and parameters of custom pipelines.

## Quality Control Filters

### Blur Detection

```python
from histolab.filters.image_filters import Lambda
import cv2
import numpy as np

def laplacian_blur_score(gray_image):
    """Calculate Laplacian variance (blurriness metric)."""
    return cv2.Laplacian(np.array(gray_image), cv2.CV_64F).var()

blur_detector = Lambda(lambda img: laplacian_blur_score(
    RgbToGrayscale()(img)
))
```

### Tissue Coverage

```python
from histolab.filters.image_filters import RgbToGrayscale, OtsuThreshold
from histolab.filters.compositions import Compose

def tissue_coverage(image):
    """Calculate the percentage of tissue in an image."""
    tissue_mask = Compose([
        RgbToGrayscale(),
        OtsuThreshold()
    ])(image)
    return tissue_mask.sum() / tissue_mask.size * 100

coverage_filter = Lambda(tissue_coverage)
```

## Troubleshooting

### Problem: Tissue detection misses valid tissue
**Solution:**
- Decrease `area_threshold` in `RemoveSmallObjects`.
- Decrease the disk size for erosion/opening.
- Try using `AdaptiveThreshold` instead of Otsu.

### Problem: Too many artifacts included
**Solution:**
- Increase `area_threshold` in `RemoveSmallObjects`.
- Increase opening/closing operations.
- Use color-based custom filtering for specific artifacts.

### Problem: Tissue boundaries are too rough
**Solution:**
- Add `BinaryClosing` or `BinaryOpening` for smoothing.
- Adjust the `disk_size` of morphological operations.

### Problem: Large variations in stain quality
**Solution:**
- Apply histogram equalization.
- Use adaptive thresholding.
- Implement a stain normalization pipeline.