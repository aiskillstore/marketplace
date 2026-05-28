# Heart Rate Variability (HRV) Analysis

## Overview

Heart Rate Variability (HRV) reflects the variation in time intervals between consecutive heartbeats, providing insights into autonomic nervous system regulation, cardiovascular health, and psychological states. NeuroKit2 provides comprehensive HRV analysis across time, frequency, and non-linear domains.

## Main Functions

### hrv()

Calculates all available HRV indices from all domains at once.

```python
hrv_indices = nk.hrv(peaks, sampling_rate=1000, show=False)
```

**Input:**
- `peaks`: A dictionary containing the `'ECG_R_Peaks'` key or an array of R-peak indices.
- `sampling_rate`: The sampling rate of the signal (in Hz).

**Returns:**
- A DataFrame containing HRV indices from all domains:
  - Time-domain indices
  - Frequency-domain power spectrum
  - Non-linear complexity measures

**This is a convenient wrapper function** that combines:
- `hrv_time()`
- `hrv_frequency()`
- `hrv_nonlinear()`

## Time-Domain Analysis

### hrv_time()

Calculates time-domain HRV indices based on inter-beat intervals (IBIs).

```python
hrv_time = nk.hrv_time(peaks, sampling_rate=1000)
```

### Key Metrics

**Basic Interval Statistics:**
- `HRV_MeanNN`: Mean of the NN intervals (ms).
- `HRV_SDNN`: Standard deviation of the NN intervals (ms).
  - Reflects total HRV, capturing all cyclic components.
  - Requires ≥5 minutes for short-term analysis and ≥24 hours for long-term analysis.
- `HRV_RMSSD`: Root mean square of successive differences (ms).
  - High-frequency variability, reflecting parasympathetic activity.
  - More stable in shorter recordings.

**Difference Measures:**
- `HRV_SDSD`: Standard deviation of successive differences (ms).
  - Similar to RMSSD, correlated with parasympathetic activity.
- `HRV_pNN50`: Percentage of successive NN interval differences > 50ms.
  - Parasympathetic index, may be insensitive in certain populations.
- `HRV_pNN20`: Percentage of successive NN interval differences > 20ms.
  - A more sensitive alternative to pNN50.

**Range Measures:**
- `HRV_MinNN`, `HRV_MaxNN`: Minimum and maximum values of NN intervals (ms).
- `HRV_CVNN`: Coefficient of variation (SDNN/MeanNN).
  - A standardized measure suitable for inter-subject comparison.
- `HRV_CVSD`: Coefficient of variation of successive differences (RMSSD/MeanNN).

**Median-based Statistics:**
- `HRV_MedianNN`: Median of the NN intervals (ms).
  - Robust to outliers.
- `HRV_MadNN`: Median absolute deviation of the NN intervals.
  - A robust measure of dispersion.
- `HRV_MCVNN`: Median-based coefficient of variation.

**Advanced Time-Domain Indices:**
- `HRV_IQRNN`: Interquartile range of the NN intervals.
- `HRV_pNN10`, `HRV_pNN25`, `HRV_pNN40`: Additional percentile thresholds.
- `HRV_TINN`: Triangular interpolation of the NN interval histogram.
- `HRV_HTI`: HRV Triangular Index (Total number of NN intervals / histogram height).

### Recording Duration Requirements
- **Ultra-short-term (< 5 min)**: RMSSD and pNN50 are the most reliable.
- **Short-term (5 min)**: The standard for clinical use; all time-domain indices are valid.
- **Long-term (24 hours)**: Necessary for interpreting SDNN to capture circadian rhythms.

## Frequency-Domain Analysis

### hrv_frequency()

Analyzes HRV power in different frequency bands using spectral analysis.

```python
hrv_freq = nk.hrv_frequency(peaks, sampling_rate=1000, ulf=(0, 0.0033), vlf=(0.0033, 0.04),
                            lf=(0.04, 0.15), hf=(0.15, 0.4), vhf=(0.4, 0.5),
                            psd_method='welch', normalize=True)
```

### Frequency Bands

**Ultra-Low Frequency (ULF): 0-0.0033 Hz**
- Requires ≥24-hour recordings.
- Circadian rhythms, thermoregulation.
- Slow metabolic processes.

**Very-Low Frequency (VLF): 0.0033-0.04 Hz**
- Requires ≥5-minute recordings.
- Thermoregulation, hormonal fluctuations.
- Renin-angiotensin system, peripheral vasomotor activity.

**Low Frequency (LF): 0.04-0.15 Hz**
- Mixed influence of sympathetic and parasympathetic nervous systems.
- Baroreceptor reflex activity.
- Blood pressure regulation (10-second rhythm).

**High Frequency (HF): 0.15-0.4 Hz**
- Parasympathetic (vagal) activity.
- Respiratory Sinus Arrhythmia (RSA).
- Synchronized with respiration (respiratory rate range).

**Very-High Frequency (VHF): 0.4-0.5 Hz**
- Rarely used, may reflect measurement noise.
- Requires cautious interpretation.

### Key Metrics

**Absolute Power (ms²):**
- `HRV_ULF`, `HRV_VLF`, `HRV_LF`, `HRV_HF`, `HRV_VHF`: Power in each band.
- `HRV_TP`: Total Power (variance of NN intervals).
- `HRV_LFHF`: LF/HF ratio (sympathovagal balance).

**Normalized Power:**
- `HRV_LFn`: LF power / (LF + HF) - Normalized LF.
- `HRV_HFn`: HF power / (LF + HF) - Normalized HF.
- `HRV_LnHF`: Natural logarithm of HF (log-normal distribution).

**Peak Frequency:**
- `HRV_LFpeak`, `HRV_HFpeak`: Frequencies corresponding to the maximum power in each band.
- Used to identify dominant oscillations.

### Power Spectral Density (PSD) Methods

**Welch Method (Default):**
```python
hrv_freq = nk.hrv_frequency(peaks, sampling_rate=1000, psd_method='welch')
```
- Segmented FFT with overlap.
- Smoother spectrum with lower variance.
- Suitable for standard HRV analysis.

**Lomb-Scargle Periodogram:**
```python
hrv_freq = nk.hrv_frequency(peaks, sampling_rate=1000, psd_method='lomb')
```
- Handles unevenly sampled data.
- No interpolation required.
- Suitable for data with noise or artifacts.

**Multitaper Method:**
```python
hrv_freq = nk.hrv_frequency(peaks, sampling_rate=1000, psd_method='multitapers')
```
- Superior spectral estimation.
- Reduced variance and minimal bias.
- Computationally intensive.

**Burg Autoregressive Model:**
```python
hrv_freq = nk.hrv_frequency(peaks, sampling_rate=1000, psd_method='burg', order=16)
```
- Parametric method.
- Smooth spectrum with well-defined peaks.
- Requires selection of the model order.

### Interpretation Guidelines

**LF/HF Ratio:**
- Traditionally interpreted as sympathovagal balance.
- **Note**: Recent evidence has questioned this interpretation.
- LF reflects combined sympathetic and parasympathetic influences.
- Context-dependent: Controlled breathing affects HF.

**HF Power:**
- Reliable parasympathetic indicator.
- Increases with: Rest, relaxation, deep breathing.
- Decreases with: Stress, anxiety, sympathetic activation.

**Recording Requirements:**
- **Minimum**: 60 seconds for LF/HF estimation.
- **Recommended**: 2-5 minutes for short-term HRV.
- **Optimal**: 5 minutes according to Task Force standards.
- **Long-term**: 24 hours for ULF analysis.

## Non-linear Domain Analysis

### hrv_nonlinear()

Calculates complexity, entropy, and fractal measures reflecting autonomic dynamics.

```python
hrv_nonlinear = nk.hrv_nonlinear(peaks, sampling_rate=1000)
```

### Poincaré Plot Metrics

**Poincaré Plot**: A scatter plot of NN(i+1) vs NN(i) geometric structure.

- `HRV_SD1`: Standard deviation perpendicular to the line of identity (ms).
  - Short-term HRV, rapid beat-to-beat variability.
  - Reflects parasympathetic activity.
  - Mathematically related to RMSSD: SD1 ≈ RMSSD/√2.

- `HRV_SD2`: Standard deviation along the line of identity (ms).
  - Long-term HRV, slow variability.
  - Reflects both sympathetic and parasympathetic activity.
  - Related to SDNN.

- `HRV_SD1SD2`: SD1/SD2 ratio.
  - Balance between short-term and long-term variability.
  - <1: Predominantly long-term variability.

- `HRV_SD2SD1`: SD2/SD1 ratio.
  - Inverse of SD1SD2.

- `HRV_S`: Area of the ellipse (π × SD1 × SD2).
  - Total HRV magnitude.

- `HRV_CSI`: Cardiac Sympathetic Index (SD2/SD1).
  - Proposed sympathetic indicator.

- `HRV_CVI`: Cardiac Vagal Index (log10(SD1 × SD2)).
  - Proposed parasympathetic indicator.

- `HRV_CSI_Modified`: Modified CSI (SD2²/(SD1 × SD2)).

### Heart Rate Asymmetry

Analyzes whether heart rate accelerations and decelerations contribute differently to HRV.

- `HRV_GI`: Guzik's Index - Asymmetry in short-term variability.
- `HRV_SI`: Slope Index - Asymmetry in long-term variability.
- `HRV_AI`: Area Index - Overall asymmetry.
- `HRV_PI`: Porta's Index - Percentage of decelerations.
- `HRV_C1d`, `HRV_C2d`: Contributions of decelerations.
- `HRV_C1a`, `HRV_C2a`: Contributions of accelerations.
- `HRV_SD1d`, `HRV_SD1a`: Poincaré SD1 corresponding to decelerations/accelerations.
- `HRV_SD2d`, `HRV_SD2a`: Poincaré SD2 corresponding to decelerations/accelerations.

**Interpretation:**
- Healthy individuals: Presence of asymmetry (more/larger decelerations).
- Clinical populations: Reduced asymmetry.
- Reflects different autonomic control over acceleration vs. deceleration.

### Entropy Measures

**Approximate Entropy (ApEn):**
- `HRV_ApEn`: Measure of regularity; lower = more regular/predictable.
- Sensitive to data length, order m, and tolerance r.

**Sample Entropy (SampEn):**
- `HRV_SampEn`: Improved ApEn with lower dependence on data length.
- More consistent for short-term recordings.
- Lower values = more regular patterns.

**Multiscale Entropy (MSE):**
- `HRV_MSE`: Complexity across multiple time scales.
- Distinguishes true complexity from randomness.

**Fuzzy Entropy (FuzzyEn):**
- `HRV_FuzzyEn`: Uses fuzzy membership functions for pattern matching.
- More stable with short data.

**Shannon Entropy (ShanEn):**
- `HRV_ShanEn`: Information-theoretic measure of randomness.

### Fractal Measures

**Detrended Fluctuation Analysis (DFA):**
- `HRV_DFA_alpha1`: Short-term fractal scaling exponent (4-11 beats).
  - α1 > 1: Correlation, reduced in heart disease.
  - α1 ≈ 1: Pink noise, healthy.
  - α1 < 0.5: Anti-correlation.

- `HRV_DFA_alpha2`: Long-term fractal scaling exponent (>11 beats).
  - Reflects long-range correlations.

- `HRV_DFA_alpha1alpha2`: α1/α2 ratio.

**Correlation Dimension:**
- `HRV_CorDim`: Dimension of the attractor in phase space.
- Indicates system complexity.

**Higuchi Fractal Dimension:**
- `HRV_HFD`: Complexity and self-similarity.
- Higher value = more complex, more irregular.

**Petrosian Fractal Dimension:**
- `HRV_PFD`: Another measure of complexity.
- Computationally efficient.

**Katz Fractal Dimension:**
- `HRV_KFD`: Waveform complexity.

### Heart Rate Fragmentation

Quantifies abnormal short-term fluctuations reflecting autonomic dysregulation.

- `HRV_PIP`: Percentage of inflection points.
  - Normal: ~50%, Fragmented: >70%.
- `HRV_IALS`: Inverse of the average length of acceleration/deceleration segments.
- `HRV_PSS`: Percentage of short segments (<3 beats).
- `HRV_PAS`: Percentage of NN intervals in alternating segments.

**Clinical Relevance:**
- Increased fragmentation is associated with cardiovascular risk.
- Independent predictor superior to traditional HRV indices.

### Other Non-linear Indices

- `HRV_Hurst`: Hurst exponent (long-range dependency).
- `HRV_LZC`: Lempel-Ziv Complexity (algorithmic complexity).
- `HRV_MFDFA`: Multifractal DFA indices.

## Specialized HRV Functions

### hrv_rsa()

Respiratory Sinus Arrhythmia - Heart rate modulation caused by respiration.

```python
rsa = nk.hrv_rsa(peaks, rsp_signal, sampling_rate=1000, method='porges1980')
```

**Methods:**
- `'porges1980'`: Porges-Bohrer method (band-pass filtered heart rate around respiratory frequency).
- `'harrison2021'`: Peak-to-trough RSA (max-min heart rate difference per respiratory cycle).

**Requirements:**
- Simultaneous ECG and respiration signals.
- Synchronized timestamps.
- At least a few respiratory cycles.

**Returns:**
- `RSA`: RSA magnitude (depends on the method, units in bpm or similar).

### hrv_rqa()

Recurrence Quantification Analysis - Analyzes non-linear dynamics from phase-space reconstruction.

```python
rqa = nk.hrv_rqa(peaks, sampling_rate=1000)
```

**Metrics:**
- `RQA_RR`: Recurrence Rate - System predictability.
- `RQA_DET`: Determinism - Percentage of recurrence points forming lines.
- `RQA_LMean`, `RQA_LMax`: Average and maximum diagonal line length.
- `RQA_ENTR`: Shannon entropy of line lengths - Complexity.
- `RQA_LAM`: Laminarity - System trapped in a specific state.
- `RQA_TT`: Trapping Time - Duration in laminar states.

**Use Cases:**
- Detecting transitions in physiological states.
- Assessing system determinism vs. randomness.

## Interval Processing

### intervals_process()

Preprocesses RR intervals before HRV analysis.

```python
processed_intervals = nk.intervals_process(rr_intervals, interpolate=False,
                                           interpolate_sampling_rate=1000)
```

**Operations:**
- Removes physiologically implausible intervals.
- Optional: Interpolation to regular sampling.
- Optional: Detrending to remove slow trends.

**Use Cases:**
- When using pre-extracted RR intervals.
- Cleaning interval data from external devices.
- Preparing data for frequency-domain analysis.

### intervals_to_peaks()

Converts interval data (RR, NN) into peak indices for HRV analysis.

```python
peaks_dict = nk.intervals_to_peaks(rr_intervals, sampling_rate=1000)
```

**Use Cases:**
- Importing data from external HRV devices.
- Processing interval data from commercial systems.
- Converting between interval and peak representations.

## Practical Considerations

### Minimum Recording Duration

| Analysis Type | Minimum Duration | Optimal Duration |
|---------------|------------------|------------------|
| RMSSD, pNN50  | 30 seconds       | 5 minutes        |
| SDNN          | 5 minutes        | 5 min (short), 24 hr (long) |
| LF, HF Power  | 2 minutes        | 5 minutes        |
| VLF Power     | 5 minutes        | 10+ minutes      |
| ULF Power     | 24 hours         | 24 hours         |
| Non-linear (ApEn, SampEn) | 100-300 beats | 500+ beats |
| DFA           | 300 beats        | 1000+ beats      |

### Artifact Management

**Preprocessing:**
```python
# R-peak detection with artifact correction
peaks, info = nk.ecg_peaks(cleaned_ecg, sampling_rate=1000, correct_artifacts=True)

# Or manual interval processing
processed = nk.intervals_process(rr_intervals, interpolate=False)
```

**Quality Checks:**
- Visual inspection of tachograms (NN intervals over time).
- Identify physiologically implausible intervals (<300 ms or >2000 ms).
- Check for sudden jumps or missed beats.
- Assess signal quality before analysis.

### Standardization and Comparison

**Task Force Standards (1996):**
- Use 5-minute recordings for short-term analysis.
- Recommended supine position, controlled breathing.
- Use 24-hour recordings for long-term evaluation.

**Normalization:**
- Consider the effects of age, gender, and fitness level.
- Note the time of day and circadian rhythm influences.
- Body posture (supine vs. standing).
- Respiratory rate and depth.

**Inter-individual Differences:**
- HRV varies greatly between subjects.
- Intra-subject changes are more interpretable.
- Comparison with baseline is recommended.

## Clinical and Research Applications

**Cardiovascular Health:**
- Reduced HRV: Risk factor for cardiac events.
- SDNN, DFA alpha1: Prognostic indicators.
- Post-MI monitoring.

**Psychological States:**
- Anxiety/Stress: Reduced HRV (especially RMSSD, HF).
- Depression: Altered autonomic balance.
- PTSD: Fragmentation indices.

**Sports Performance:**
- Monitoring training load via daily RMSSD.
- Overtraining: Reduced HRV.
- Recovery assessment.

**Neuroscience:**
- Emotion regulation studies.
- Cognitive load assessment.
- Brain-heart axis research.

**Aging:**
- HRV decreases with age.
- Decline in complexity measures.
- Baseline references required.

## References

- Task Force of the European Society of Cardiology. (1996). Heart rate variability: standards of measurement, physiological interpretation and clinical use. Circulation, 93(5), 1043-1065.
- Shaffer, F., & Ginsberg, J. P. (2017). An overview of heart rate variability metrics and norms. Frontiers in public health, 5, 258.
- Peng, C. K., Havlin, S., Stanley, H. E., & Goldberger, A. L. (1995). Quantification of scaling exponents and crossover phenomena in nonstationary heartbeat time series. Chaos, 5(1), 82-87.
- Guzik, P., Piskorski, J., Krauze, T., Wykretowicz, A., & Wysocki, H. (2006). Heart rate asymmetry by Poincaré plots of RR intervals. Biomedizinische Technik/Biomedical Engineering, 51(4), 272-275.
- Costa, M., Goldberger, A. L., & Peng, C. K. (2005). Multiscale entropy analysis of biological signals. Physical review E, 71(2), 021906.