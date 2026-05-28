# Neuropixels Preprocessing Reference Guide

Comprehensive preprocessing techniques for Neuropixels electrophysiological recordings.

## Standard Preprocessing Pipeline

```python
import spikeinterface.full as si

# Load raw data
recording = si.read_spikeglx('/path/to/data', stream_id='imec0.ap')

# 1. Phase shift correction (applicable to Neuropixels 1.0)
rec = si.phase_shift(recording)

# 2. Bandpass filtering for spike detection
rec = si.bandpass_filter(rec, freq_min=300, freq_max=6000)

# 3. Common Median Reference (removing correlated noise)
rec = si.common_reference(rec, reference='global', operator='median')

# 4. Remove bad channels (optional)
rec = si.remove_bad_channels(rec, bad_channel_ids=bad_channels)
```

## Filtering Options

### Bandpass Filter
```python
# Standard AP band
rec = si.bandpass_filter(recording, freq_min=300, freq_max=6000)

# Wide band (preserving more waveform shape)
rec = si.bandpass_filter(recording, freq_min=150, freq_max=7500)

# Filter parameter settings
rec = si.bandpass_filter(
    recording,
    freq_min=300,
    freq_max=6000,
    filter_order=5,
    ftype='butter',  # 'butter', 'bessel', or 'cheby1'
    margin_ms=5.0    # Prevent edge artifacts
)
```

### High-pass Filter Only
```python
rec = si.highpass_filter(recording, freq_min=300)
```

### Notch Filter (Removing power line noise)
```python
# Remove 60Hz and its harmonics
rec = si.notch_filter(recording, freq=60, q=30)
rec = si.notch_filter(rec, freq=120, q=30)
rec = si.notch_filter(rec, freq=180, q=30)
```

## Reference Schemes

### Common Median Reference (Recommended)
```python
# Global median reference
rec = si.common_reference(recording, reference='global', operator='median')

# Per-shank reference (for multi-shank probes)
rec = si.common_reference(recording, reference='global', operator='median',
                          groups=recording.get_channel_groups())
```

### Common Average Reference
```python
rec = si.common_reference(recording, reference='global', operator='average')
```

### Local Reference
```python
# Reference based on local channel groups
rec = si.common_reference(recording, reference='local', local_radius=(30, 100))
```

## Bad Channel Detection and Removal

### Automatic Detection
```python
# Detect bad channels
bad_channel_ids, channel_labels = si.detect_bad_channels(
    recording,
    method='coherence+psd',
    dead_channel_threshold=-0.5,
    noisy_channel_threshold=1.0,
    outside_channel_threshold=-0.3,
    n_neighbors=11
)

print(f"Bad channels: {bad_channel_ids}")
print(f"Labels: {dict(zip(bad_channel_ids, channel_labels))}")
```

### Remove Bad Channels
```python
rec_clean = si.remove_bad_channels(recording, bad_channel_ids=bad_channel_ids)
```

### Interpolate Bad Channels
```python
rec_interp = si.interpolate_bad_channels(recording, bad_channel_ids=bad_channel_ids)
```

## Motion Correction

### Estimate Motion
```python
# Estimate motion (drift)
motion, temporal_bins, spatial_bins = si.estimate_motion(
    recording,
    method='decentralized',
    rigid=False,              # Non-rigid motion estimation
    win_step_um=50,           # Spatial window step
    win_sigma_um=150,         # Spatial window sigma
    progress_bar=True
)
```

### Apply Motion Correction
```python
rec_corrected = si.correct_motion(
    recording,
    motion,
    temporal_bins,
    spatial_bins,
    interpolate_motion_border=True
)
```

### Motion Visualization
```python
si.plot_motion(motion, temporal_bins, spatial_bins)
```

## Probe-Specific Processing

### Neuropixels 1.0
```python
# Phase shift correction (each channel uses a different ADC)
rec = si.phase_shift(recording)

# Then perform standard pipeline
rec = si.bandpass_filter(rec, freq_min=300, freq_max=6000)
rec = si.common_reference(rec, reference='global', operator='median')
```

### Neuropixels 2.0
```python
# No phase shift correction required (uses a single ADC)
rec = si.bandpass_filter(recording, freq_min=300, freq_max=6000)
rec = si.common_reference(recording, reference='global', operator='median')
```

### Multi-shank (Neuropixels 2.0 4-shank)
```python
# Independent reference per shank
groups = recording.get_channel_groups()  # Returns shank assignment information
rec = si.common_reference(recording, reference='global', operator='median', groups=groups)
```

## Whitening

```python
# Whiten data (eliminate inter-channel correlation)
rec_whitened = si.whiten(recording, mode='local', local_radius_um=100)

# Global whitening
rec_whitened = si.whiten(recording, mode='global')
```

## Artifact Removal

### Remove Stimulus Artifacts
```python
# Define artifact times (in sample points)
triggers = [10000, 20000, 30000]  # Sample indices

rec = si.remove_artifacts(
    recording,
    triggers,
    ms_before=0.5,
    ms_after=3.0,
    mode='cubic'  # 'zeros', 'linear', 'cubic'
)
```

### Fill Saturation Periods
```python
rec = si.blank_staturation(recording, threshold=0.95, fill_value=0)
```

## Saving Preprocessed Data

### Binary Format (Recommended)
```python
rec_preprocessed.save(folder='preprocessed/', format='binary', n_jobs=4)
```

### Zarr Format (Compressed)
```python
rec_preprocessed.save(folder='preprocessed.zarr', format='zarr')
```

### Save as Recording Extractor
```python
# Save for later use
rec_preprocessed.save(folder='preprocessed/', format='binary')

# Load later
rec_loaded = si.load_extractor('preprocessed/')
```

## Complete Pipeline Example

```python
import spikeinterface.full as si

def preprocess_neuropixels(data_path, output_path):
    """Standard Neuropixels preprocessing pipeline."""

    # Load data
    recording = si.read_spikeglx(data_path, stream_id='imec0.ap')
    print(f"Loaded: {recording.get_num_channels()} channels, "
          f"{recording.get_total_duration():.1f}s")

    # Phase shift (NP 1.0 only)
    rec = si.phase_shift(recording)

    # Filtering
    rec = si.bandpass_filter(rec, freq_min=300, freq_max=6000)

    # Detect and remove bad channels
    bad_ids, _ = si.detect_bad_channels(rec)
    if len(bad_ids) > 0:
        print(f"Removing {len(bad_ids)} bad channels: {bad_ids}")
        rec = si.interpolate_bad_channels(rec, bad_ids)

    # Common reference
    rec = si.common_reference(rec, reference='global', operator='median')

    # Save
    rec.save(folder=output_path, format='binary', n_jobs=4)
    print(f"Saved to: {output_path}")

    return rec

# Usage example
rec_preprocessed = preprocess_neuropixels(
    '/path/to/spikeglx/data',
    '/path/to/preprocessed'
)
```

## Performance Optimization Tips

```python
# Use parallel processing
rec.save(folder='output/', n_jobs=-1)  # Use all CPU cores

# Use job keyword arguments for memory management
job_kwargs = dict(n_jobs=8, chunk_duration='1s', progress_bar=True)
rec.save(folder='output/', **job_kwargs)

# Set global job keyword arguments
si.set_global_job_kwargs(n_jobs=8, chunk_duration='1s')
```