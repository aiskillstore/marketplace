# File I/O Reference

PyOpenMS supports reading and writing various mass spectrometry file formats.

## Supported Formats
*   **mzML**: Standard XML-based format (Preferred).
*   **mzXML**: Older XML format.
*   **MGF**: Mascot Generic Format (Peak lists).

## Usage Examples

### Reading a File
```python
import pyopenms as ms

exp = ms.MSExperiment()
# Detect file type automatically or use specific class like MzMLFile
ms.MzMLFile().load("data.mzML", exp)
```

### Writing a File
```python
# Save experiment to mzML
ms.MzMLFile().store("output.mzML", exp)
```
