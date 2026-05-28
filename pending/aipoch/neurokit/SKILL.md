---
name: neurokit
description: "Comprehensive biosignal processing for ECG/PPG/EEG/EDA/RSP/EMG/EOG; use when you need to clean, segment, and extract physiological features for HRV, event-related responses, complexity metrics, or multimodal psychophysiology pipelines."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

Use this skill when you need to:

1. **Run end-to-end ECG/PPG pipelines** (cleaning → peak detection → feature extraction) for cardiovascular monitoring and HRV.
2. **Compute HRV metrics** (time/frequency/nonlinear) for autonomic nervous system assessment in resting-state or continuous recordings.
3. **Analyze EEG** for band power, microstates, and complexity measures in cognitive/neuroscience experiments.
4. **Decompose EDA** into tonic/phasic components and quantify SCRs for arousal/stress and psychophysiological paradigms.
5. **Perform multimodal biosignal processing** (e.g., ECG + RSP + EDA + EMG) with unified outputs for integrated analyses.

Reference docs (if available in this skill package): `references/ecg_cardiac.md`, `references/hrv.md`, `references/eeg.md`, `references/eda.md`, `references/rsp.md`, `references/emg.md`, `references/eog.md`, `references/signal_processing.md`, `references/complexity.md`, `references/epochs_events.md`, `references/bio_module.md`.

## Key Features

- **Cardiac (ECG/PPG)**: cleaning, R-peak detection, delineation, quality assessment, ECG-derived respiration, pulse analysis.
- **HRV**: comprehensive indices across time, frequency, and nonlinear domains; RSA and advanced metrics (e.g., RQA where applicable).
- **EEG**: band power, channel utilities, microstate segmentation, and integration patterns commonly used with MNE workflows.
- **EDA**: tonic/phasic decomposition, SCR detection, sympathetic indices, and event-related EDA analysis.
- **Respiration (RSP)**: breathing rate, variability (RRV), and respiratory volume per time (RVT) style features.
- **EMG/EOG**: EMG activation/amplitude processing; EOG blink and eye-movement feature extraction.
- **General utilities**: filtering, peak finding, PSD estimation, resampling/interpolation, and synchronization helpers.
- **Event-related analysis**: event finding, epoching, baseline correction, and averaging across trials.
- **Multimodal integration**: `bio_process()` / `bio_analyze()` for consistent multi-signal pipelines.

## Dependencies

- `neurokit2` (latest; install via pip/uv)
- Python 3.x environment (version depends on your runtime)

Installation:

```bash
uv pip install neurokit2
```

Development version:

```bash
uv pip install https://github.com/neuropsychology/NeuroKit/zipball/dev
```

## Example Usage

A complete, runnable example that simulates signals, processes them, computes features, and performs event-related epoching:

```python
import neurokit2 as nk
import numpy as np

# -----------------------------
# 1) Simulate example signals
# -----------------------------
sampling_rate = 1000
duration = 60  # seconds

ecg = nk.ecg_simulate(duration=duration, sampling_rate=sampling_rate, heart_rate=70)
rsp = nk.rsp_simulate(duration=duration, sampling_rate=sampling_rate, respiratory_rate=15)
eda = nk.eda_simulate(duration=duration, sampling_rate=sampling_rate, scr_number=8)

# Create a simple trigger channel with 5 events
trigger = np.zeros(len(ecg))
event_times_s = [10, 20, 30, 40, 50]
for t in event_times_s:
    trigger[int(t * sampling_rate)] = 1.0

# -----------------------------
# 2) ECG processing + HRV
# -----------------------------
ecg_signals, ecg_info = nk.ecg_process(ecg, sampling_rate=sampling_rate)
rpeaks = ecg_info["ECG_R_Peaks"]
hrv = nk.hrv(rpeaks, sampling_rate=sampling_rate)

# -----------------------------
# 3) Multimodal processing
# -----------------------------
bio_signals, bio_info = nk.bio_process(
    ecg=ecg,
    rsp=rsp,
    eda=eda,
    sampling_rate=sampling_rate
)
bio_results = nk.bio_analyze(bio_signals, sampling_rate=sampling_rate)

# -----------------------------
# 4) Event-related epoching
# -----------------------------
events = nk.events_find(trigger, threshold=0.5)
epochs = nk.epochs_create(
    bio_signals,
    events,
    sampling_rate=sampling_rate,
    epochs_start=-0.5,
    epochs_end=2.0
)
grand_average = nk.epochs_average(epochs)

# -----------------------------
# 5) Minimal outputs
# -----------------------------
print("HRV (first columns):")
print(hrv.iloc[:, :8].round(3))

print("\nBio analysis keys:", list(bio_results.keys())[:10])
print("Grand average shape:", grand_average.shape)
```

## Implementation Details

### Processing pipelines (typical pattern)
Most modalities follow a consistent structure:

1. `*_process(signal, sampling_rate=...)`
   Produces a cleaned signal plus intermediate channels (e.g., peaks, phases) and an `info` dict with indices/metadata.
2. `*_analyze(processed_signals, sampling_rate=...)`
   Computes summary features and automatically selects an analysis mode based on recording length.

Examples:
- ECG: `ecg_process()` → `ecg_analyze()` → `hrv()`
- EDA: `eda_process()` → `eda_analyze()`
- RSP: `rsp_process()` → `rsp_rrv()` / `rsp_rvt()`

### Analysis mode selection (event-related vs interval-related)
Many `*_analyze()` functions implicitly switch modes based on data duration:

- **Event-related** (short segments; commonly < ~10 s): stimulus-locked responses, epoch-based summaries.
- **Interval-related** (longer recordings; commonly ≥ ~10 s): continuous/resting summaries (e.g., HRV over a window).

If you need explicit event-related workflows, use:
- `events_find()` to detect markers
- `epochs_create()` to segment around events
- `epochs_average()` (and modality-specific `*_eventrelated()` where applicable)

### HRV domains and inputs
HRV functions typically require **R-peak indices** (sample positions) and often a `sampling_rate`:

- Time-domain: e.g., SDNN, RMSSD, pNN50
- Frequency-domain: band powers/ratios (requires sampling rate and appropriate interpolation assumptions)
- Nonlinear: Poincaré (SD1/SD2), entropy/fractal-style measures

Common calls:
- `nk.hrv(peaks, sampling_rate=...)` (all-in-one)
- `nk.hrv_time(peaks)`, `nk.hrv_frequency(peaks, sampling_rate=...)`, `nk.hrv_nonlinear(peaks, sampling_rate=...)`

### Filtering and spectral estimation
General utilities (see `references/signal_processing.md`) typically expose parameters such as:
- `sampling_rate`
- cutoff frequencies (`lowcut`, `highcut`)
- method-specific options (e.g., filter order/type)

Example:
```python
filtered = nk.signal_filter(x, sampling_rate=1000, lowcut=0.5, highcut=40)
psd = nk.signal_psd(filtered, sampling_rate=1000)
```

### Complexity/entropy measures
Complexity functions (see `references/complexity.md`) provide:
- Entropy families (approximate, sample, permutation, multiscale, etc.)
- Fractal/DFA variants
- Nonlinear dynamics metrics (e.g., Lyapunov-style measures where supported)

Example:
```python
indices = nk.complexity(x, sampling_rate=1000)
apen = nk.entropy_approximate(x)
dfa = nk.fractal_dfa(x)
```
