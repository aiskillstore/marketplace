---
name: neuropixels-analysis
description: End-to-end Neuropixels extracellular electrophysiology analysis (SpikeGLX/Open Ephys/NWB) including preprocessing, motion correction, Kilosort4 spike sorting, QC metrics, and Allen/IBL-style curation; use when processing Neuropixels recordings or when users mention Neuropixels, SpikeGLX, Open Ephys, Kilosort, quality metrics, drift/motion correction, or unit curation.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

Use this skill in any of the following situations:

1. **You need to load and standardize Neuropixels recordings** from SpikeGLX (`.ap.bin/.lf.bin/.meta`), Open Ephys (`.continuous/.oebin`), or NWB (`.nwb`) into a consistent analysis pipeline.
2. **You are preparing raw extracellular data for spike sorting**, including high-pass filtering, phase shift correction (NP1.0), bad channel detection/removal, and common average referencing (CAR).
3. **You suspect probe drift or tissue motion** and need to estimate and correct motion before sorting (especially when drift is > ~10 µm).
4. **You want to run spike sorting** (Kilosort4 recommended; CPU alternatives supported) and then compute post-processing products (waveforms, templates, amplitudes, correlograms, unit locations).
5. **You need quality control and curation** using Allen/IBL-style thresholds, plus optional AI-assisted visual review for borderline units, and exports to Phy/NWB.

## Key Features

- **Multi-format ingestion**: SpikeGLX, Open Ephys, and NWB readers via SpikeInterface.
- **Neuropixels-aware preprocessing**:
  - High-pass filtering for spike band
  - **Phase shift correction for Neuropixels 1.0**
  - Bad channel detection and removal
  - Median CAR / referencing
- **Motion/drift workflow**:
  - Motion estimation presets (e.g., “Kilosort-like”)
  - Optional rigid/non-rigid correction presets
  - Drift visualization outputs
- **Spike sorting orchestration**:
  - Kilosort4 (GPU) recommended
  - CPU alternatives (e.g., SpykingCircus2, Mountainsort5, Tridesclous2)
- **Post-processing and QC**:
  - SortingAnalyzer-based computation of waveforms, templates, amplitudes, correlograms, unit locations, and quality metrics
- **Curation**:
  - Allen/IBL-style automated labeling
  - Optional AI-assisted visual analysis for uncertain units
- **Reporting and export**:
  - HTML report generation
  - Export to **Phy** and **NWB**
  - Save metrics tables (CSV)

Reference guides (if present in the repository) can be used for deeper explanations:
- `reference/standard_workflow.md`
- `reference/api_reference.md`
- `reference/plotting_guide.md`
- `reference/PREPROCESSING.md`, `reference/MOTION_CORRECTION.md`, `reference/SPIKE_SORTING.md`
- `reference/QUALITY_METRICS.md`, `reference/AUTOMATED_CURATION.md`, `reference/AI_CURATION.md`

## Dependencies

Python dependencies (typical versions known to work; adjust to your environment):

- `python >= 3.9`
- `spikeinterface[full] >= 0.99`
- `probeinterface >= 0.2`
- `neo >= 0.13`
- Spike sorters (optional, depending on what you run):
  - `kilosort >= 4.0` (Kilosort4; GPU required)
  - `spykingcircus >= 1.1` (SpykingCircus2; CPU)
  - `mountainsort5 >= 0.5` (CPU)
- Optional (AI-assisted curation):
  - `anthropic >= 0.20`
- Optional (IBL tooling):
  - `ibllib >= 2.0`
  - `ibl-neuropixel >= 1.0`

## Example Usage

The following example is designed to be a complete, runnable script (assuming dependencies and a valid dataset path). It loads SpikeGLX data, preprocesses, estimates/corrects motion, runs Kilosort4, computes metrics, curates units, generates a report, and exports to Phy and NWB.

```python
import spikeinterface.full as si
import neuropixels_analysis as npa

def main():
    # Parallelization / chunking settings used by SpikeInterface functions
    job_kwargs = dict(n_jobs=-1, chunk_duration="1s", progress_bar=True)

    # 1) Load data (SpikeGLX example)
    # For Open Ephys: si.read_openephys("/path/to/Record_Node_101/")
    # For NWB:        si.read_nwb("/path/to/file.nwb")
    recording = si.read_spikeglx("/path/to/spikeglx_folder", stream_id="imec0.ap")

    # Optional: slice first 60 seconds for a quick test
    fs = recording.get_sampling_frequency()
    recording = recording.frame_slice(0, int(60 * fs))

    # 2) Preprocess (recommended chain; wrapper may include the same steps)
    # Note: phase_shift is mandatory for Neuropixels 1.0 and not needed for 2.0.
    rec = npa.preprocess(recording)

    # 3) Estimate drift/motion and correct if needed
    motion_info = npa.estimate_motion(rec, preset="kilosort_like", **job_kwargs)
    npa.plot_drift(rec, motion_info, output="drift_map.png")

    # Example threshold: correct if max drift exceeds 10 µm
    if float(motion_info["motion"].max()) > 10.0:
        rec = npa.correct_motion(rec, preset="nonrigid_accurate", **job_kwargs)

    # 4) Spike sorting (Kilosort4 recommended; requires GPU)
    sorting = si.run_sorter("kilosort4", rec, folder="ks4_output", **job_kwargs)

    # 5) Post-processing + metrics
    analyzer = si.create_sorting_analyzer(sorting, rec, sparse=True)

    analyzer.compute("random_spikes", max_spikes_per_unit=500, **job_kwargs)
    analyzer.compute("waveforms", ms_before=1.0, ms_after=2.0, **job_kwargs)
    analyzer.compute("templates", operators=["average", "std"], **job_kwargs)
    analyzer.compute("spike_amplitudes", **job_kwargs)
    analyzer.compute("correlograms", window_ms=50.0, bin_ms=1.0, **job_kwargs)
    analyzer.compute("unit_locations", method="monopolar_triangulation", **job_kwargs)
    analyzer.compute("quality_metrics", **job_kwargs)

    metrics = analyzer.get_extension("quality_metrics").get_data()
    metrics.to_csv("quality_metrics.csv")

    # 6) Automated curation (Allen/IBL-style)
    labels = npa.curate(metrics, method="allen")  # e.g., "allen", "ibl", "strict"

    # 7) Report
    results = {"sorting": sorting, "metrics": metrics, "labels": labels, "analyzer": analyzer}
    npa.generate_analysis_report(results, "output_report/")
    npa.print_analysis_summary(results)

    # 8) Export
    si.export_to_phy(
        analyzer,
        output_folder="phy_export/",
        compute_pc_features=True,
        compute_amplitudes=True,
    )

    from spikeinterface.exporters import export_to_nwb
    export_to_nwb(rec, sorting, "output.nwb")

if __name__ == "__main__":
    main()
```

## Implementation Details

### 1) Data I/O and supported formats

- **SpikeGLX**: `si.read_spikeglx(path, stream_id="imec0.ap")`
- **Open Ephys**: `si.read_openephys(path)`
- **NWB**: `si.read_nwb(path)`

Neuropixels probe types commonly encountered:
- **Neuropixels 1.0**: requires **phase shift correction** to align channels.
- **Neuropixels 2.0**: denser geometries; phase shift correction typically not required.

### 2) Preprocessing chain (typical)

A standard spike-band preprocessing sequence is:

1. **High-pass filter** (commonly 300–400 Hz) to isolate spikes.
2. **Phase shift correction** (`si.phase_shift`) for **NP1.0**.
3. **Bad channel detection** (`si.detect_bad_channels`) and removal.
4. **Common reference** (often median CAR) to reduce shared noise.

Key parameters:
- `freq_min` (high-pass cutoff): typical **300–400 Hz**
- bad channel detection sensitivity (implementation-dependent; often exposed as thresholds/presets)

### 3) Motion estimation and correction

- Motion/drift can strongly degrade sorting quality; a practical rule is to **inspect drift before sorting**.
- Presets:
  - `preset="kilosort_like"`: faster estimation aligned with common sorter assumptions
  - `preset="nonrigid_accurate"`: more robust correction for severe drift

Operational threshold often used in practice:
- If estimated drift exceeds **~10 µm**, apply correction before sorting.

### 4) Spike sorting

- **Kilosort4** is recommended for Neuropixels due to speed and quality, but requires a GPU.
- CPU alternatives can be used when GPU is unavailable (at the cost of runtime and sometimes quality).

Sorter parameters to tune (Kilosort4 examples):
- `batch_size`: samples per batch (often ~30000 by default)
- `nblocks`: number of drift blocks (increase for long recordings)
- `Th_learned`: detection threshold (lower → more spikes, potentially more false positives)

### 5) Post-processing and quality metrics

Using `SortingAnalyzer`, the pipeline typically computes:
- waveforms (window: `ms_before`, `ms_after`)
- templates (average/std)
- spike amplitudes
- correlograms (e.g., `window_ms=50`, `bin_ms=1`)
- unit locations (e.g., `monopolar_triangulation`)
- quality metrics (e.g., SNR, ISI violations, presence ratio, amplitude cutoff)

Common QC thresholds (dataset-dependent; document your choices):
- `snr_threshold`: often **3–5**
- `isi_violations_ratio`: often **0.01–0.5**
- `presence_ratio`: often **0.5–0.95**

### 6) Curation logic (Allen/IBL-style)

A conservative “good unit” selection often combines:
- high presence ratio (stable across recording)
- low ISI violations (refractory period respected)
- low amplitude cutoff (less truncation / missed spikes)

Example rule (illustrative):
- `presence_ratio > 0.9`
- `isi_violations_ratio < 0.5`
- `amplitude_cutoff < 0.1`

### 7) AI-assisted visual analysis (optional)

For borderline units (e.g., moderate SNR), AI-assisted review can be used to interpret:
- waveform shape consistency
- refractory period evidence in autocorrelograms
- amplitude stability and drift effects
- multi-unit contamination indicators

If your repository provides `npa.analyze_unit_visually(...)`, it can be integrated with an API client (e.g., `anthropic`) to generate structured curation suggestions.