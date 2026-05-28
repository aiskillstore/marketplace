---
name: pyopenms-skill
description: Comprehensive tool for computational mass spectrometry using PyOpenMS; use when you need to read/write MS formats (mzML/mzXML/MGF), run signal processing (smoothing/peak picking), detect isotope features, or perform peptide identification in proteomics/metabolomics workflows.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Converting, validating, or batch-processing mass spectrometry files (e.g., mzML, mzXML, MGF) as part of a pipeline.
- Cleaning raw spectra before downstream analysis (smoothing, baseline correction, denoising, peak picking).
- Detecting and linking isotope patterns / features for proteomics or metabolomics feature tables.
- Running identification-oriented steps where peptide/protein identification integration is required.
- Building custom computational MS workflows in Python while leveraging OpenMS algorithms.

## Key Features

- **MS File I/O**: Read/write common MS formats (mzML, mzXML, MGF).
- **Signal Processing**: Smoothing, baseline correction, filtering, and peak picking.
- **Feature Detection**: Isotope pattern detection and feature linking utilities.
- **Identification Support**: Hooks for peptide identification workflows via OpenMS-compatible components.
- **Scripted Workflows**: A ready-to-use “Load → Process → Analyze” workflow entry point.

## Dependencies

Install the following Python packages:

- `pyopenms` (version: compatible with your OpenMS/PyOpenMS distribution)
- `pandas` (version: latest recommended)
- `numpy` (version: latest recommended)

Installation:

```bash
uv pip install pyopenms pandas numpy
```

## Example Usage

A complete runnable example using the provided workflow script (`scripts/process_ms.py`):

```python
# run_example.py
from scripts.process_ms import run_workflow

def main():
    # Load -> Process -> Analyze
    # The script is expected to read the input mzML and apply optional filtering.
    result = run_workflow("data.mzML", apply_filter=True)

    # The returned object depends on the implementation of run_workflow.
    # Common patterns include a processed experiment, a feature map, or a summary dict.
    print("Workflow finished.")
    print(result)

if __name__ == "__main__":
    main()
```

Run:

```bash
python run_example.py
```

For manual/custom workflows, see:
- File operations: `references/file_io.md`
- Signal processing algorithms: `references/signal_processing.md`

## Implementation Details

- **Binding Layer**: This skill uses PyOpenMS, the Python bindings for the OpenMS C++ library, to expose core computational MS algorithms.
- **Workflow Pattern**: The default script follows a standard pipeline structure:
  1. **Load** an MS run from disk (e.g., mzML).
  2. **Process** spectra (optional filtering/smoothing/baseline correction).
  3. **Analyze** results (e.g., peak picking, feature detection, or downstream summaries).
- **Configurable Processing**: The `apply_filter` flag in `run_workflow(...)` is intended to toggle one or more preprocessing steps; exact filters and parameters should be documented in `scripts/process_ms.py` and the referenced guides.
- **Algorithm Reference**: Detailed descriptions of available filters and peak pickers, including parameterization, are maintained in `references/signal_processing.md`.