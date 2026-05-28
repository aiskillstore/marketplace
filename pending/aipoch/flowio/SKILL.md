---
name: flowio
description: Parse Flow Cytometry Standard (FCS) files v2.0–3.1 and extract events/metadata for preprocessing workflows (e.g., when you need NumPy arrays, channel info, or CSV/DataFrame export from cytometry files).
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to read FCS v2.0/3.0/3.1 files and extract event matrices for downstream preprocessing.
- You want to inspect or validate FCS metadata (TEXT segment) without loading event data (memory-efficient parsing).
- You need channel definitions (PnN/PnS), ranges (PnR), and automatic identification of scatter/fluorescence/time channels.
- You need to handle problematic FCS files with offset inconsistencies or multi-dataset content.
- You want to export cytometry events to CSV/Pandas DataFrame or write new/modified FCS files.

## Key Features

- **FCS parsing (v2.0–3.1):** Reads HEADER/TEXT/DATA and optional ANALYSIS segments.
- **Event extraction to NumPy:** Returns event data as `ndarray` with shape `(events, channels)`.
- **Optional preprocessing:** Applies standard FCS transformations (gain/log/time scaling) when enabled.
- **Metadata access:** Exposes TEXT keywords and common instrument/acquisition fields.
- **Channel utilities:** Provides PnN/PnS labels, ranges, and indices for scatter/fluorescence/time channels.
- **Robust parsing options:** Flags for offset discrepancy handling and null-channel exclusion.
- **Multi-dataset support:** Detects and reads files containing multiple datasets.
- **FCS writing:** Create new FCS files from arrays and optionally preserve/override metadata.

## Dependencies

- `python >= 3.9`
- `flowio` (install via pip/uv; version depends on your environment)
- Example-only:
  - `numpy >= 1.20`
  - `pandas >= 1.5`

## Example Usage

```python
"""
End-to-end example:
1) Read an FCS file (metadata + events)
2) Convert to a Pandas DataFrame and export CSV
3) Filter events and write a new FCS file
4) Handle multi-dataset files
"""

from pathlib import Path

import numpy as np
import pandas as pd

from flowio import (
    FlowData,
    create_fcs,
    read_multiple_data_sets,
    MultipleDataSetsError,
    FCSParsingError,
    DataOffsetDiscrepancyError,
)

FCS_PATH = "sample.fcs"

def read_fcs_safely(path: str) -> FlowData:
    try:
        return FlowData(path)
    except DataOffsetDiscrepancyError:
        # Common workaround for files with inconsistent offsets
        return FlowData(path, ignore_offset_discrepancy=True)
    except FCSParsingError:
        # Looser mode if the file is malformed
        return FlowData(path, ignore_offset_error=True)

def main() -> None:
    # --- 1) Read file (single dataset) ---
    try:
        flow = read_fcs_safely(FCS_PATH)
    except MultipleDataSetsError:
        # --- 4) Multi-dataset handling ---
        datasets = read_multiple_data_sets(FCS_PATH)
        flow = datasets[0]  # pick the first dataset for this demo

    print("File:", getattr(flow, "name", Path(FCS_PATH).name))
    print("FCS version:", flow.version)
    print("Events:", flow.event_count)
    print("Channels:", flow.channel_count)
    print("PnN labels:", flow.pnn_labels)

    # Metadata (TEXT segment)
    print("Instrument ($CYT):", flow.text.get("$CYT", "N/A"))
    print("Acquisition date ($DATE):", flow.text.get("$DATE", "N/A"))

    # --- 2) Events -> NumPy -> DataFrame -> CSV ---
    events = flow.as_array(preprocess=True)  # default preprocessing behavior
    df = pd.DataFrame(events, columns=flow.pnn_labels)
    df.to_csv("events.csv", index=False)
    print("Wrote CSV:", "events.csv")

    # --- 3) Filter and write a new FCS ---
    # Example: threshold on first scatter channel if available, else channel 0
    fsc_idx = flow.scatter_indices[0] if getattr(flow, "scatter_indices", []) else 0
    threshold = np.percentile(events[:, fsc_idx], 50)  # median threshold
    mask = events[:, fsc_idx] > threshold
    filtered = events[mask]

    create_fcs(
        "filtered.fcs",
        filtered,
        flow.pnn_labels,
        opt_channel_names=flow.pns_labels,
        metadata={**flow.text, "$SRC": "Filtered via FlowIO example"},
    )
    print("Wrote FCS:", "filtered.fcs")

    # --- Metadata-only read (memory efficient) ---
    meta_only = FlowData(FCS_PATH, only_text=True)
    print("Metadata-only read: $DATE =", meta_only.text.get("$DATE", "N/A"))

if __name__ == "__main__":
    main()
```

## Implementation Details

### Data Model and Segments

An FCS file is organized into segments:

- **HEADER:** FCS version and byte offsets for other segments.
- **TEXT:** Keyword/value metadata (e.g., `$DATE`, `$CYT`, `$PnN`, `$PnS`, `$PnR`, `$PnG`, `$PnE`).
- **DATA:** Event matrix encoded as integer/float/double/ASCII depending on file keywords.
- **ANALYSIS (optional):** Post-processing results if present.

In FlowIO, these are exposed via `FlowData` attributes such as:
- `flow.header` (HEADER info)
- `flow.text` (TEXT keyword dictionary)
- `flow.analysis` (ANALYSIS keyword dictionary, if present)
- `flow.as_array(...)` (decoded event matrix)

### Preprocessing (`as_array(preprocess=True)`)

When preprocessing is enabled, FlowIO applies common FCS transformations:

1. **Gain scaling (PnG):** Values are multiplied by the per-parameter gain.
2. **Log/exponential transform (PnE):** If present, applies:
   - `value = a * 10^(b * raw_value)` where `PnE = "a,b"`.
3. **Time scaling:** If a time channel is detected, values may be scaled into appropriate units.

To disable all transformations and obtain raw decoded values:
- `flow.as_array(preprocess=False)`

### Channel Identification

FlowIO provides convenience indices for common channel types:

- `flow.scatter_indices` (e.g., FSC/SSC)
- `flow.fluoro_indices` (fluorescence channels)
- `flow.time_index` (time channel index or `None`)

These indices can be used to slice the event matrix:
- `events[:, flow.scatter_indices]`
- `events[:, flow.fluoro_indices]`

### Handling Problematic Files (Offsets and Null Channels)

Some files contain inconsistent offsets between HEADER and TEXT:

- `ignore_offset_discrepancy=True` to tolerate HEADER/TEXT offset mismatch.
- `use_header_offsets=True` to prefer HEADER offsets.
- `ignore_offset_error=True` to bypass offset-related failures more aggressively.

To exclude known null/empty channels during parsing:
- `FlowData(path, null_channel_list=[...])`

### Multi-Dataset Files

If a file contains multiple datasets, constructing `FlowData(path)` may raise `MultipleDataSetsError`. Use:

- `read_multiple_data_sets(path)` to load all datasets, or
- `FlowData(path, nextdata_offset=...)` to load a specific dataset using `$NEXTDATA` offsets.

### Writing FCS

Two common patterns:

- **Write metadata-only changes:** `flow.write_fcs("out.fcs", metadata={...})`
- **Modify event data:** extract array → modify → `create_fcs(...)` to generate a new file (FlowIO does not modify event data in-place).