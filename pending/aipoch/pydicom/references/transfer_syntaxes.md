# DICOM Transfer Syntaxes Reference

This document provides a comprehensive reference for DICOM transfer syntaxes and compression formats. Transfer syntax defines the encoding of DICOM data, including byte ordering, compression methods, and other encoding rules.

## Overview

Transfer Syntax UID specifies:
1. **Byte ordering**: Little Endian or Big Endian
2. **Value Representation (VR)**: Implicit or Explicit
3. **Compression**: None, or specific compression algorithms

## Uncompressed Transfer Syntaxes

### Implicit VR Little Endian (1.2.840.10008.1.2)
- **Default** transfer syntax
- Value Representation is implicit (no explicit encoding)
- Little Endian byte ordering
- **Pydicom constant**: `pydicom.uid.ImplicitVRLittleEndian`

**Usage:**
```python
import pydicom
ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
```

### Explicit VR Little Endian (1.2.840.10008.1.2.1)
- **Most commonly used** transfer syntax
- Value Representation is explicit
- Little Endian byte ordering
- **Pydicom constant**: `pydicom.uid.ExplicitVRLittleEndian`

**Usage:**
```python
ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
```

### Explicit VR Big Endian (1.2.840.10008.1.2.2) - Deprecated
- Value Representation is explicit
- Big Endian byte ordering
- **Deprecated** - Not recommended for new implementations
- **Pydicom constant**: `pydicom.uid.ExplicitVRBigEndian`

## JPEG Compression

### JPEG Baseline (Process 1) (1.2.840.10008.1.2.4.50)
- **Lossy** compression
- Supports only 8-bit samples
- Most widely supported JPEG format
- **Pydicom constant**: `pydicom.uid.JPEGBaseline8Bit`

**Dependencies:** Requires `pylibjpeg` or `pillow`

**Usage:**
```python
# Compress
ds.compress(pydicom.uid.JPEGBaseline8Bit)

# Decompress
ds.decompress()
```

### JPEG Extended (Process 2 & 4) (1.2.840.10008.1.2.4.51)
- **Lossy** compression
- Supports 8-bit and 12-bit samples
- **Pydicom constant**: `pydicom.uid.JPEGExtended12Bit`

### JPEG Lossless, Non-hierarchical (Process 14) (1.2.840.10008.1.2.4.57)
- **Lossless** compression
- First-Order Prediction
- **Pydicom constant**: `pydicom.uid.JPEGLossless`

**Dependencies:** Requires `pylibjpeg-libjpeg` or `gdcm`

### JPEG Lossless, Non-hierarchical, First-Order Prediction (1.2.840.10008.1.2.4.70)
- **Lossless** compression
- Uses Process 14 Selection Value 1
- **Pydicom constant**: `pydicom.uid.JPEGLosslessSV1`

**Usage:**
```python
# Compress to JPEG Lossless
ds.compress(pydicom.uid.JPEGLossless)
```

### JPEG-LS Lossless (1.2.840.10008.1.2.4.80)
- **Lossless** compression
- Low complexity, good compression ratio
- **Pydicom constant**: `pydicom.uid.JPEGLSLossless`

**Dependencies:** Requires `pylibjpeg-libjpeg` or `gdcm`

### JPEG-LS Lossy (Near Lossless) (1.2.840.10008.1.2.4.81)
- **Near lossless** compression
- Allows controlled precision loss
- **Pydicom constant**: `pydicom.uid.JPEGLSNearLossless`

## JPEG 2000 Compression

### JPEG 2000 Lossless (1.2.840.10008.1.2.4.90)
- **Lossless** compression
- Wavelet-based compression
- Better compression ratio than JPEG Lossless
- **Pydicom constant**: `pydicom.uid.JPEG2000Lossless`

**Dependencies:** Requires `pylibjpeg-openjpeg`, `gdcm`, or `pillow`

**Usage:**
```python
# Compress to JPEG 2000 Lossless
ds.compress(pydicom.uid.JPEG2000Lossless)
```

### JPEG 2000 (1.2.840.10008.1.2.4.91)
- **Lossy or Lossless** compression
- Wavelet-based compression
- High quality at low bit rates
- **Pydicom constant**: `pydicom.uid.JPEG2000`

**Dependencies:** Requires `pylibjpeg-openjpeg`, `gdcm`, or `pillow`

### JPEG 2000 Part 2 Multicomponent Lossless (1.2.840.10008.1.2.4.92)
- **Lossless** compression
- Supports multicomponent images
- **Pydicom constant**: `pydicom.uid.JPEG2000MCLossless`

### JPEG 2000 Part 2 Multicomponent (1.2.840.10008.1.2.4.93)
- **Lossy or Lossless** compression
- Supports multicomponent images
- **Pydicom constant**: `pydicom.uid.JPEG2000MC`

## RLE Compression

### RLE Lossless (1.2.840.10008.1.2.5)
- **Lossless** compression
- Run-Length Encoding
- Simple, fast algorithm
- Suitable for images with repeated values
- **Pydicom constant**: `pydicom.uid.RLELossless`

**Dependencies:** Built-in to Pydicom (no extra packages required)

**Usage:**
```python
# Compress with RLE
ds.compress(pydicom.uid.RLELossless)

# Decompress
ds.decompress()
```

## Deflated Transfer Syntaxes

### Deflated Explicit VR Little Endian (1.2.840.10008.1.2.1.99)
- Uses ZLIB compression on the entire dataset
- Not commonly used
- **Pydicom constant**: `pydicom.uid.DeflatedExplicitVRLittleEndian`

## MPEG Compression

### MPEG2 Main Profile @ Main Level (1.2.840.10008.1.2.4.100)
- **Lossy** video compression
- Used for multi-frame images/video
- **Pydicom constant**: `pydicom.uid.MPEG2MPML`

### MPEG2 Main Profile @ High Level (1.2.840.10008.1.2.4.101)
- **Lossy** video compression
- Higher resolution than MPML
- **Pydicom constant**: `pydicom.uid.MPEG2MPHL`

### MPEG-4 AVC/H.264 High Profile (1.2.840.10008.1.2.4.102-106)
- **Lossy** video compression
- Various levels (BD, 2D, 3D, Stereo)
- Modern video codec

## Checking Transfer Syntax

### Identifying Current Transfer Syntax
```python
import pydicom

ds = pydicom.dcmread('image.dcm')

# Get transfer syntax UID
ts_uid = ds.file_meta.TransferSyntaxUID
print(f"Transfer Syntax UID: {ts_uid}")

# Get human-readable name
print(f"Transfer Syntax Name: {ts_uid.name}")

# Check if compressed
print(f"Is compressed: {ts_uid.is_compressed}")
```

### Common Checks
```python
# Check if Little Endian
if ts_uid.is_little_endian:
    print("Little Endian")

# Check if Implicit VR
if ts_uid.is_implicit_VR:
    print("Implicit VR")

# Check compression type
if 'JPEG' in ts_uid.name:
    print("JPEG compressed")
elif 'JPEG2000' in ts_uid.name:
    print("JPEG 2000 compressed")
elif 'RLE' in ts_uid.name:
    print("RLE compressed")
```

## Decompression

### Automatic Decompression
Pydicom can automatically decompress pixel data when accessing `pixel_array`:

```python
import pydicom

# Read compressed DICOM
ds = pydicom.dcmread('compressed.dcm')

# Pixel data will be automatically decompressed
pixel_array = ds.pixel_array  # Automatically decompresses if needed
```

### Manual Decompression
```python
import pydicom

ds = pydicom.dcmread('compressed.dcm')

# Decompress in place
ds.decompress()

# Save as uncompressed format
ds.save_as('uncompressed.dcm', write_like_original=False)
```

## Compression

### Compressing DICOM Files
```python
import pydicom

ds = pydicom.dcmread('uncompressed.dcm')

# Compress with JPEG 2000 Lossless
ds.compress(pydicom.uid.JPEG2000Lossless)
ds.save_as('compressed_j2k.dcm')

# Compress with RLE Lossless (no extra dependencies)
ds.compress(pydicom.uid.RLELossless)
ds.save_as('compressed_rle.dcm')

# Compress with JPEG Baseline (lossy)
ds.compress(pydicom.uid.JPEGBaseline8Bit)
ds.save_as('compressed_jpeg.dcm')
```

### Compressing with Custom Encoding Parameters
```python
import pydicom
from pydicom.encoders import JPEGLSLosslessEncoder

ds = pydicom.dcmread('uncompressed.dcm')

# Compress with custom parameters
ds.compress(pydicom.uid.JPEGLSLossless, encoding_plugin='pylibjpeg')
```

## Installing Compression Handlers

Different transfer syntaxes require different Python packages:

### JPEG Baseline/Extended
```bash
pip install pylibjpeg pylibjpeg-libjpeg
# or
pip install pillow
```

### JPEG Lossless/JPEG-LS
```bash
pip install pylibjpeg pylibjpeg-libjpeg
# or
pip install python-gdcm
```

### JPEG 2000
```bash
pip install pylibjpeg pylibjpeg-openjpeg
# or
pip install python-gdcm
# or
pip install pillow
```

### RLE
No extra packages required - Pydicom has it built-in

### Full Installation
```bash
# Install all common handlers
pip install pylibjpeg pylibjpeg-libjpeg pylibjpeg-openjpeg python-gdcm
```

## Checking Available Handlers

```python
import pydicom

# List available pixel data handlers
from pydicom.pixel_data_handlers.util import get_pixel_data_handlers
handlers = get_pixel_data_handlers()

print("Available handlers:")
for handler in handlers:
    print(f"  - {handler.__name__}")
```

## Best Practices

1. **Use Explicit VR Little Endian** when creating new files for maximum compatibility.
2. **Use JPEG 2000 Lossless** for good compression without quality loss.
3. If you cannot install extra dependencies, **use RLE Lossless** compression.
4. **Check transfer syntax** before processing to ensure the correct handlers are installed.
5. **Test decompression** before deployment to ensure all required packages are installed.
6. When possible, **preserve original** transfer syntax using `write_like_original=True`.
7. When using lossy compression, **balance file size vs. quality**.
8. Diagnostic images should **use lossless** compression to maintain clinical quality.

## Common Issues

### Issue: "Unable to decode pixel data"
**Cause:** Missing compression handler
**Solution:** Install the corresponding package (see "Installing Compression Handlers" above)

### Issue: "Unsupported Transfer Syntax"
**Cause:** Rare or unsupported compression format
**Solution:** Try installing `python-gdcm` which supports more formats

### Issue: "Pixel data decompressed but looks wrong"
**Cause:** May need to apply VOI LUT or Rescale
**Solution:** Use `apply_voi_lut()` or apply `RescaleSlope`/`RescaleIntercept`

## References

- DICOM Standard Part 5 (Data Structures and Encoding): https://dicom.nema.org/medical/dicom/current/output/chtml/part05/PS3.5.html
- Pydicom Transfer Syntax Documentation: https://pydicom.github.io/pydicom/stable/guides/user/transfer_syntaxes.html
- Pydicom Compression Guide: https://pydicom.github.io/pydicom/stable/old/image_data_compression.html
