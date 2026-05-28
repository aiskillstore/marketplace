# Motion/Drift Correction Guide (Motion/Drift Correction Reference)

Mechanical drift is a major challenge for Neuropixels recordings during acute probe insertions. This guide covers methods for detecting, estimating, and correcting motion artifacts.

## Why Motion Correction is Important

- Neuropixels probes can drift by 10-100+ μm during a recording.
- Uncorrected drift leads to:
  - Units appearing or disappearing mid-recording
  - Changes in waveform amplitude
  - Spike-to-unit assignment errors
  - Reduced unit yield

## Detection: Pre-sorting Check

**Always inspect drift before running spike sorting!**

```python
import spikeinterface.full as si
from spikeinterface.sortingcomponents.peak_detection import detect_peaks
from spikeinterface.sortingcomponents.peak_localization import localize_peaks

# First, perform preprocessing (do not whiten - it affects peak localization)
rec = si.highpass_filter(recording, freq_min=400.)
rec = si.common_reference(rec, operator='median', reference='global')

# Detect peaks
noise_levels = si.get_noise_levels(rec, return_in_uV=False)
peaks = detect_peaks(
    rec,
    method='locally_exclusive',
    noise_levels=noise_levels,
    detect_threshold=5,
    radius_um=50.,
    n_jobs=8,
    chunk_duration='1s',
    progress_bar=True
)

# Localize peaks
peak_locations = localize_peaks(
    rec, peaks,
    method='center_of_mass',
    n_jobs=8,
    chunk_duration='1s'
)

# Visualize drift
si.plot_drift_raster_map(
    peaks=peaks,
    peak_locations=peak_locations,
    recording=rec,
    clim=(-200, 0)  # Adjust color limits
)
```

### Drift Map Interpretation

| Pattern | Interpretation | Action |
|---------|---------------|--------|
| Horizontal bands, stable | No significant drift | Skip correction |
| Diagonal bands (slow) | Gradual, steady drift | Use motion correction |
| Rapid jumps | Brain pulsation or movement | Use non-rigid correction |
| Chaotic pattern | Severe instability | Consider discarding this data segment |

## Motion Correction Methods

### Fast Correction (Recommended for beginners)

```python
# Simple one-liner using preset parameters
rec_corrected = si.correct_motion(
    recording=rec,
    preset='nonrigid_fast_and_accurate'
)
```

### Available Presets

| Preset | Speed | Accuracy | Use Case |
|--------|-------|----------|----------|
| `rigid_fast` | Fast | Low | Quick check, minor drift |
| `kilosort_like` | Medium | Good | Kilosort-compatible results |
| `nonrigid_accurate` | Slow | High | Publication quality |
| `nonrigid_fast_and_accurate` | Medium | High | **Recommended default option** |
| `dredge` | Slow | Highest | Best results, complex drift |
| `dredge_fast` | Medium | High | DREDge with lower computational resources |

### Full Control Pipeline

```python
from spikeinterface.sortingcomponents.motion import (
    estimate_motion,
    interpolate_motion
)

# Step 1: Estimate motion
motion, temporal_bins, spatial_bins = estimate_motion(
    rec,
    peaks,
    peak_locations,
    method='decentralized',
    direction='y',
    rigid=False,          # Neuropixels uses non-rigid
    win_step_um=50,       # Spatial window step
    win_sigma_um=150,     # Spatial smoothness
    bin_s=2.0,            # Temporal bin size
    progress_bar=True
)

# Step 2: Visualize motion estimation
si.plot_motion(
    motion,
    temporal_bins,
    spatial_bins,
    recording=rec
)

# Step 3: Apply correction via interpolation
rec_corrected = interpolate_motion(
    recording=rec,
    motion=motion,
    temporal_bins=temporal_bins,
    spatial_bins=spatial_bins,
    border_mode='force_extrapolate'
)
```

### Saving Motion Estimates

```python
# Save for later use
import numpy as np
np.savez('motion_estimate.npz',
         motion=motion,
         temporal_bins=temporal_bins,
         spatial_bins=spatial_bins)

# Load later
data = np.load('motion_estimate.npz')
motion = data['motion']
temporal_bins = data['temporal_bins']
spatial_bins = data['spatial_bins']
```

## DREDge: Cutting-edge Method

DREDge (Decentralized Registration of Electrophysiology Data) is currently the best-performing motion correction method.

### Using DREDge Presets

```python
# AP band motion estimation
rec_corrected = si.correct_motion(rec, preset='dredge')

# Or compute explicitly
motion, motion_info = si.compute_motion(
    rec,
    preset='dredge',
    output_motion_info=True,
    folder='motion_output/',
    **job_kwargs
)
```

### LFP-based Motion Estimation

For extremely fast drift or cases where AP band estimation fails:

```python
# Load LFP data stream
lfp = si.read_spikeglx('/path/to/data', stream_name='imec0.lf')

# Estimate motion from LFP (faster, handles rapid drift)
motion_lfp, motion_info = si.compute_motion(
    lfp,
    preset='dredge_lfp',
    output_motion_info=True
)

# Apply to AP recording
rec_corrected = interpolate_motion(
    recording=rec,  # AP recording
    motion=motion_lfp,
    temporal_bins=motion_info['temporal_bins'],
    spatial_bins=motion_info['spatial_bins']
)
```

## Integration with Spike Sorting

### Option 1: Pre-correction (Recommended)

```python
# Correct before sorting
rec_corrected = si.correct_motion(rec, preset='nonrigid_fast_and_accurate')

# Save corrected recording
rec_corrected = rec_corrected.save(folder='preprocessed_motion_corrected/',
                                    format='binary', n_jobs=8)

# Run spike sorting on corrected data
sorting = si.run_sorter('kilosort4', rec_corrected, output_folder='ks4/')
```

### Option 2: Let Kilosort Handle It

Kilosort 2.5+ has built-in drift correction:

```python
sorting = si.run_sorter(
    'kilosort4',
    rec,  # Without motion correction
    output_folder='ks4/',
    nblocks=5,  # Number of non-rigid blocks for drift correction
    do_correction=True  # Enable Kilosort's drift correction
)
```

### Option 3: Post-hoc Correction

```python
# Sort first
sorting = si.run_sorter('kilosort4', rec, output_folder='ks4/')

# Then estimate motion from sorted spikes
# (Usually more accurate as it uses real spike times)
from spikeinterface.sortingcomponents.motion import estimate_motion_from_sorting

motion = estimate_motion_from_sorting(sorting, rec)
```

## Parameter Details

### Peak Detection

```python
peaks = detect_peaks(
    rec,
    method='locally_exclusive',  # Best for high-density probes
    noise_levels=noise_levels,
    detect_threshold=5,          # Lower = more spikes (noisier estimates)
    radius_um=50.,               # Exclusion radius
    exclude_sweep_ms=0.1,        # Temporal exclusion window
)
```

### Motion Estimation

```python
motion = estimate_motion(
    rec, peaks, peak_locations,
    method='decentralized',      # 'decentralized' or 'iterative_template'
    direction='y',               # Along probe axis
    rigid=False,                 # Set to False for non-rigid
    bin_s=2.0,                   # Temporal resolution (seconds)
    win_step_um=50,              # Spatial window step
    win_sigma_um=150,            # Spatial smoothing sigma
    margin_um=0,                 # Probe edge margin
    win_scale_um=150,            # Weight window scale
)
```

## Troubleshooting

### Over-correction (Wavy patterns)

```python
# Increase temporal smoothness
motion = estimate_motion(..., bin_s=5.0)  # Use larger bins

# Or use rigid correction for minor drift
motion = estimate_motion(..., rigid=True)
```

### Under-correction (Residual drift)

```python
# Decrease spatial window for finer non-rigid estimation
motion = estimate_motion(..., win_step_um=25, win_sigma_um=75)

# Use more spikes
peaks = detect_peaks(..., detect_threshold=4)  # Lower threshold
```

### Edge Artifacts

```python
rec_corrected = interpolate_motion(
    rec, motion, temporal_bins, spatial_bins,
    border_mode='force_extrapolate',  # or 'remove_channels'
    spatial_interpolation_method='kriging'
)
```

## Validation

After correction, re-visualize to confirm the effect:

```python
# Re-detect peaks on corrected recording
peaks_corrected = detect_peaks(rec_corrected, ...)
peak_locations_corrected = localize_peaks(rec_corrected, peaks_corrected, ...)

# Plot before/after comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Before Correction
si.plot_drift_raster_map(peaks, peak_locations, rec, ax=axes[0])
axes[0].set_title('Before Correction')

# After Correction
si.plot_drift_raster_map(peaks_corrected, peak_locations_corrected,
                         rec_corrected, ax=axes[1])
axes[1].set_title('After Correction')
```

## References

- [SpikeInterface Motion Correction Documentation](https://spikeinterface.readthedocs.io/en/stable/modules/motion_correction.html)
- [How to Handle Drift Tutorial](https://spikeinterface.readthedocs.io/en/stable/how_to/handle_drift.html)
- [DREDge GitHub Repository](https://github.com/evarol/DREDge)
- Windolf et al. (2023) "DREDge: robust motion correction for high-density extracellular recordings"