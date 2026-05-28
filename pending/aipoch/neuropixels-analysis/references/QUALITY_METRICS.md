# Quality Metrics Reference Guide

This guide provides a detailed overview of how to use SpikeInterface metrics and Allen/IBL standards for unit quality assessment.

## Overview

Quality metrics primarily evaluate sorted units from the following three aspects:

| Category | Core Question | Key Metrics |
|----------|----------|-------------|
| **Contamination** (Type I Error) | Are spikes coming from multiple neurons? | ISI violations ratio, SNR |
| **Completeness** (Type II Error) | Are spikes missing? | Amplitude cutoff, presence ratio |
| **Stability** | Is the unit stable over time? | Drift metrics, amplitude coefficient of variation (CV) |

## Computing Quality Metrics

```python
import spikeinterface.full as si

# Create analyzer using pre-computed waveforms
analyzer = si.create_sorting_analyzer(sorting, recording, sparse=True)
analyzer.compute('random_spikes', max_spikes_per_unit=500)
analyzer.compute('waveforms', ms_before=1.5, ms_after=2.0)
analyzer.compute('templates')
analyzer.compute('noise_levels')
analyzer.compute('spike_amplitudes')
analyzer.compute('principal_components', n_components=5)

# Compute all quality metrics
analyzer.compute('quality_metrics')

# Or compute specific metrics
analyzer.compute('quality_metrics', metric_names=[
    'firing_rate', 'snr', 'isi_violations_ratio',
    'presence_ratio', 'amplitude_cutoff'
])

# Get results
qm = analyzer.get_extension('quality_metrics').get_data()
print(qm.columns.tolist())  # View available metrics
```

## Metric Definitions and Thresholds

### Contamination Metrics

#### ISI Violations Ratio
Proportion of spikes violating the refractory period. All neurons have a refractory period of approximately 1.5ms.

```python
# Compute using a custom refractory period
analyzer.compute('quality_metrics',
                 metric_names=['isi_violations_ratio'],
                 isi_threshold_ms=1.5,
                 min_isi_ms=0.0)
```

| Value | Interpretation |
|-------|---------------|
| < 0.01 | Excellent (well-isolated single unit) |
| 0.01 - 0.1 | Good (slight contamination) |
| 0.1 - 0.5 | Fair (possible multi-unit activity) |
| > 0.5 | Poor (likely multi-unit) |

**References:** Hill et al. (2011) J Neurosci 31:8699-8705

#### Signal-to-Noise Ratio (SNR)
Ratio of the peak waveform amplitude to the background noise.

```python
analyzer.compute('quality_metrics', metric_names=['snr'])
```

| Value | Interpretation |
|-------|---------------|
| > 10 | Excellent |
| 5 - 10 | Good |
| 2 - 5 | Acceptable |
| < 2 | Poor (likely noise) |

#### Isolation Distance
Mahalanobis distance to the nearest cluster in PCA space.

```python
analyzer.compute('quality_metrics',
                 metric_names=['isolation_distance'],
                 n_neighbors=4)
```

| Value | Interpretation |
|-------|---------------|
| > 50 | Well-isolated |
| 20 - 50 | Moderately isolated |
| < 20 | Poorly isolated |

#### L-ratio
A contamination measure based on Mahalanobis distance.

| Value | Interpretation |
|-------|---------------|
| < 0.05 | Well-isolated |
| 0.05 - 0.1 | Acceptable |
| > 0.1 | Contaminated |

#### D-prime
Measures the discriminability between a unit and its nearest neighbor cluster.

| Value | Interpretation |
|-------|---------------|
| > 8 | Excellent separation |
| 5 - 8 | Good separation |
| < 5 | Poor separation |

### Completeness Metrics

#### Amplitude Cutoff
Estimated proportion of spikes below the detection threshold.

```python
analyzer.compute('quality_metrics',
                 metric_names=['amplitude_cutoff'],
                 peak_sign='neg')  # 'neg' (negative), 'pos' (positive), or 'both'
```

| Value | Interpretation |
|-------|---------------|
| < 0.01 | Excellent (nearly complete) |
| 0.01 - 0.1 | Good |
| 0.1 - 0.2 | Fair (some missing spikes) |
| > 0.2 | Poor (significant spike loss) |

**For precise temporal analysis:** < 0.01 is recommended.

#### Presence Ratio
Fraction of the total recording time during which spikes are detected.

```python
analyzer.compute('quality_metrics',
                 metric_names=['presence_ratio'],
                 bin_duration_s=60)  # 1 minute per bin
```

| Value | Interpretation |
|-------|---------------|
| > 0.99 | Excellent |
| 0.9 - 0.99 | Good |
| 0.8 - 0.9 | Acceptable |
| < 0.8 | Unit may have drifted (moved out of electrode range) |

### Stability Metrics

#### Drift Metrics
Measures the change in unit position over time.

```python
analyzer.compute('quality_metrics',
                 metric_names=['drift_ptp', 'drift_std', 'drift_mad'])
```

| Metric | Description | Ideal Value |
|--------|-------------|------------|
| `drift_ptp` | Peak-to-peak drift (μm) | < 40 |
| `drift_std` | Drift standard deviation | < 10 |
| `drift_mad` | Median absolute deviation | < 10 |

#### Amplitude CV
Coefficient of variation of spike amplitudes.

| Value | Interpretation |
|-------|---------------|
| < 0.25 | Very stable |
| 0.25 - 0.5 | Acceptable |
| > 0.5 | Unstable (drift or contamination present) |

### Cluster Quality Metrics

#### Silhouette Score
Comparison of cluster cohesion and separation (-1 to 1).

| Value | Interpretation |
|-------|---------------|
| > 0.5 | Well-defined clusters |
| 0.25 - 0.5 | Fair |
| < 0.25 | Overlapping clusters |

#### Nearest-Neighbor Metrics

```python
analyzer.compute('quality_metrics',
                 metric_names=['nn_hit_rate', 'nn_miss_rate'],
                 n_neighbors=4)
```

| Metric | Description | Ideal Value |
|--------|-------------|------------|
| `nn_hit_rate` | Proportion of spikes whose neighbors belong to the same unit | > 0.9 |
| `nn_miss_rate` | Proportion of spikes whose neighbors belong to other units | < 0.1 |

## Standard Filtering Criteria

### Allen Institute Default Criteria

```python
# Allen Visual Coding / Behavior default criteria
allen_query = """
    presence_ratio > 0.95 and
    isi_violations_ratio < 0.5 and
    amplitude_cutoff < 0.1
"""
good_units = qm.query(allen_query).index.tolist()
```

### IBL Criteria

```python
# IBL reproducible ephys criteria
ibl_query = """
    presence_ratio > 0.9 and
    isi_violations_ratio < 0.1 and
    amplitude_cutoff < 0.1 and
    firing_rate > 0.1
"""
good_units = qm.query(ibl_query).index.tolist()
```

### Strict Single-Unit Criteria

```python
# For precise temporal/spike timing analysis
strict_query = """
    snr > 5 and
    presence_ratio > 0.99 and
    isi_violations_ratio < 0.01 and
    amplitude_cutoff < 0.01 and
    isolation_distance > 20 and
    drift_ptp < 40
"""
single_units = qm.query(strict_query).index.tolist()
```

### Multi-Unit Activity (MUA)

```python
# Including multi-unit activity
mua_query = """
    snr > 2 and
    presence_ratio > 0.5 and
    isi_violations_ratio < 1.0
"""
all_units = qm.query(mua_query).index.tolist()
```

## Visualization

### Quality Metrics Summary

```python
# Plot all metrics
si.plot_quality_metrics(analyzer)
```

### Distribution of Individual Metrics

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 3, figsize=(15, 10))

metrics = ['snr', 'isi_violations_ratio', 'presence_ratio',
           'amplitude_cutoff', 'firing_rate', 'drift_ptp']

for ax, metric in zip(axes.flat, metrics):
    ax.hist(qm[metric].dropna(), bins=50, edgecolor='black')
    ax.set_xlabel(metric)
    ax.set_ylabel('Count')
    # Add threshold lines
    if metric == 'snr':
        ax.axvline(5, color='r', linestyle='--', label='threshold')
    elif metric == 'isi_violations_ratio':
        ax.axvline(0.01, color='r', linestyle='--')
    elif metric == 'presence_ratio':
        ax.axvline(0.9, color='r', linestyle='--')

plt.tight_layout()
```

### Unit Quality Summary

```python
# Comprehensive unit summary plot
si.plot_unit_summary(analyzer, unit_id=0)
```

### Quality vs. Firing Rate Plot

```python
fig, ax = plt.subplots()
scatter = ax.scatter(qm['firing_rate'], qm['snr'],
                     c=qm['isi_violations_ratio'],
                     cmap='RdYlGn_r', alpha=0.6)
ax.set_xlabel('Firing Rate (Hz)')
ax.set_ylabel('SNR')
plt.colorbar(scatter, label='ISI Violations')
ax.set_xscale('log')
```

## Computing All Metrics at Once

```python
# Complete quality metrics calculation
all_metric_names = [
    # Firing properties
    'firing_rate', 'presence_ratio',
    # Waveform
    'snr', 'amplitude_cutoff', 'amplitude_cv_median', 'amplitude_cv_range',
    # ISI
    'isi_violations_ratio', 'isi_violations_count',
    # Drift
    'drift_ptp', 'drift_std', 'drift_mad',
    # Isolation (requires PCA)
    'isolation_distance', 'l_ratio', 'd_prime',
    # Nearest neighbor (requires PCA)
    'nn_hit_rate', 'nn_miss_rate',
    # Cluster quality
    'silhouette_score',
    # Synchrony
    'sync_spike_2', 'sync_spike_4', 'sync_spike_8',
]

# Compute PCA first (required for some metrics)
analyzer.compute('principal_components', n_components=5)

# Compute metrics
analyzer.compute('quality_metrics', metric_names=all_metric_names)
qm = analyzer.get_extension('quality_metrics').get_data()

# Save to CSV
qm.to_csv('quality_metrics.csv')
```

## Custom Metrics

```python
from spikeinterface.qualitymetrics import compute_firing_rates, compute_snrs

# Compute individual metrics
firing_rates = compute_firing_rates(sorting)
snrs = compute_snrs(analyzer)

# Add custom score to DataFrame
qm['custom_score'] = qm['snr'] * qm['presence_ratio'] / (qm['isi_violations_ratio'] + 0.001)
```

## References

- [SpikeInterface quality metrics documentation](https://spikeinterface.readthedocs.io/en/latest/modules/qualitymetrics.html)
- [Allen Institute ecephys_quality_metrics](https://allensdk.readthedocs.io/en/latest/_static/examples/nb/ecephys_quality_metrics.html)
- Hill et al. (2011) "Quality metrics to accompany spike sorting of extracellular signals"
- Siegle et al. (2021) "Survey of spiking in the mouse visual system reveals functional hierarchy"