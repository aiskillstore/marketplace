# ECG and Heart Signal Processing

## Overview

Processing Electrocardiogram (ECG) and Photoplethysmogram (PPG) signals for cardiovascular analysis. This module provides a comprehensive suite of tools for R-peak detection, delineation, quality assessment, and heart rate analysis.

## Main Processing Pipeline

### ecg_process()

Complete automated ECG processing pipeline, coordinating multiple processing steps.

```python
signals, info = nk.ecg_process(ecg_signal, sampling_rate=1000, method='neurokit')
```

**Pipeline Steps:**
1. Signal cleaning (denoising)
2. R-peak detection
3. Heart rate calculation
4. Quality assessment
5. QRS delineation (P, Q, S, T waves)
6. Cardiac phase determination

**Return Values:**
- `signals`: A DataFrame containing cleaned ECG, peaks, heart rate, quality, and cardiac phases
- `info`: A dictionary containing R-peak positions and processing parameters

**Common Methods:**
- `'neurokit'` (default): Comprehensive NeuroKit2 pipeline
- `'biosppy'`: BioSPPy-based processing
- `'pantompkins1985'`: Pan-Tompkins algorithm
- `'hamilton2002'`, `'elgendi2010'`, `'engzeemod2012'`: Other alternative methods

## Preprocessing Functions

### ecg_clean()

Removes noise from the raw ECG signal using specific filtering methods.

```python
cleaned_ecg = nk.ecg_clean(ecg_signal, sampling_rate=1000, method='neurokit')
```

**Methods:**
- `'neurokit'`: High-pass Butterworth filter (0.5 Hz) + powerline notch filtering
- `'biosppy'`: FIR filtering between 0.67-45 Hz
- `'pantompkins1985'`: 5-15 Hz bandpass filtering + derivative-based method
- `'hamilton2002'`: 8-16 Hz bandpass filtering
- `'elgendi2010'`: 8-20 Hz bandpass filtering
- `'engzeemod2012'`: 0.5-40 Hz FIR bandpass filtering

**Key Parameters:**
- `powerline`: Remove 50 or 60 Hz powerline noise (default: 50)

### ecg_peaks()

Detects R-peaks in ECG signals, with optional artifact correction.

```python
peaks_dict, info = nk.ecg_peaks(cleaned_ecg, sampling_rate=1000, method='neurokit', correct_artifacts=False)
```

**Available Methods (13+ algorithms):**
- `'neurokit'`: Hybrid method optimized for reliability
- `'pantompkins1985'`: Classic Pan-Tompkins algorithm
- `'hamilton2002'`: Hamilton adaptive thresholding
- `'christov2004'`: Christov adaptive method
- `'gamboa2008'`: Gamboa method
- `'elgendi2010'`: Elgendi double moving average
- `'engzeemod2012'`: Modified Engelse-Zeelenberg method
- `'kalidas2017'`: XQRS-based method
- `'martinez2004'`, `'rodrigues2021'`, `'koka2022'`, `'promac'`: Advanced methods

**Artifact Correction:**
Set `correct_artifacts=True` to apply Lipponen & Tarvainen (2019) correction:
- Detects ectopic beats, long/short intervals, missed beats
- Uses threshold-based detection with configurable parameters

**Return Values:**
- A dictionary containing the `'ECG_R_Peaks'` key (storing peak indices)

### ecg_delineate()

Identifies P, Q, S, T waves and their onsets and offsets.

```python
waves, waves_peak = nk.ecg_delineate(cleaned_ecg, rpeaks, sampling_rate=1000, method='dwt')
```

**Methods:**
- `'dwt'` (default): Discrete Wavelet Transform-based detection
- `'peak'`: Simple peak detection around R-peaks
- `'cwt'`: Continuous Wavelet Transform (Martinez et al., 2004)

**Detected Components:**
- P-wave: `ECG_P_Peaks`, `ECG_P_Onsets`, `ECG_P_Offsets`
- Q-wave: `ECG_Q_Peaks`
- S-wave: `ECG_S_Peaks`
- T-wave: `ECG_T_Peaks`, `ECG_T_Onsets`, `ECG_T_Offsets`
- QRS complex: onset and offset points

**Return Values:**
- `waves`: A dictionary containing all waveform indices
- `waves_peak`: A dictionary containing peak amplitudes

### ecg_quality()

Assesses the integrity and quality of the ECG signal.

```python
quality = nk.ecg_quality(ecg_signal, rpeaks=None, sampling_rate=1000, method='averageQRS')
```

**Methods:**
- `'averageQRS'` (default): Template matching correlation (Zhao & Zhang, 2018)
  - Returns a quality score between 0-1 for each heartbeat
  - Threshold: >0.6 indicates good quality
- `'zhao2018'`: Multi-index approach using skewness, power spectral distribution

**Use Cases:**
- Identifying low-quality signal segments
- Filtering noisy heartbeats before analysis
- Validating R-peak detection accuracy

## Analysis Functions

### ecg_analyze()

High-level analysis function that automatically selects event-related or interval-related mode.

```python
analysis = nk.ecg_analyze(signals, sampling_rate=1000, method='auto')
```

**Mode Selection:**
- Duration < 10 seconds → event-related analysis
- Duration ≥ 10 seconds → interval-related analysis

**Return Values:**
A DataFrame containing cardiac metrics applicable to the analysis mode.

### ecg_eventrelated()

Analyzes stimulus-locked ECG epochs for event-related responses.

```python
results = nk.ecg_eventrelated(epochs)
```

**Calculated Metrics:**
- `ECG_Rate_Baseline`: Average heart rate before stimulus
- `ECG_Rate_Min/Max`: Min/max heart rate within the epoch
- `ECG_Phase_Atrial/Ventricular`: Cardiac phase at stimulus onset
- Dynamic heart rate changes across the epoch window

**Use Cases:**
Experimental paradigms with discrete trials (e.g., stimulus presentation, task events).

### ecg_intervalrelated()

Analyzes continuous ECG recordings (resting state or long periods).

```python
results = nk.ecg_intervalrelated(signals, sampling_rate=1000)
```

**Calculated Metrics:**
- `ECG_Rate_Mean`: Mean heart rate within the interval
- Comprehensive HRV metrics (delegated to the `hrv()` function):
  - Time domain: SDNN, RMSSD, pNN50, etc.
  - Frequency domain: LF, HF, LF/HF ratio
  - Non-linear: Poincaré plots, entropy, fractal measures

**Minimum Duration Limits:**
- Basic heart rate: Any duration
- HRV frequency domain: Recommended ≥60 seconds, 1-5 minutes optimal

## Utility Functions

### ecg_rate()

Calculates instantaneous heart rate from R-peak intervals.

```python
heart_rate = nk.ecg_rate(peaks, sampling_rate=1000, desired_length=None)
```

**Methods:**
- Calculates Inter-Beat Intervals (IBIs) between adjacent R-peaks
- Converts to Beats Per Minute (BPM): 60 / IBI
- If `desired_length` is specified, matches signal length via interpolation

**Return Values:**
- Array of instantaneous heart rate values

### ecg_phase()

Determines atrial and ventricular systole/diastole phases.

```python
cardiac_phase = nk.ecg_phase(ecg_cleaned, rpeaks, delineate_info)
```

**Calculated Phases:**
- `ECG_Phase_Atrial`: Atrial systole (1) vs. diastole (0)
- `ECG_Phase_Ventricular`: Ventricular systole (1) vs. diastole (0)
- `ECG_Phase_Completion_Atrial/Ventricular`: Percentage of phase completion (0-1)

**Use Cases:**
- Cardiac-locked stimulus presentation
- Psychophysiological experiments timing events to the cardiac cycle

### ecg_segment()

Extracts individual heartbeats for morphological analysis.

```python
heartbeats = nk.ecg_segment(ecg_cleaned, rpeaks, sampling_rate=1000)
```

**Return Values:**
- A dictionary of epochs, each containing one heartbeat
- Centered on R-peaks with configurable pre/post windows
- Suitable for beat-to-beat morphological comparison

### ecg_invert()

Automatically detects and corrects inverted ECG signals.

```python
corrected_ecg, is_inverted = nk.ecg_invert(ecg_signal, sampling_rate=1000)
```

**Methods:**
- Analyzes QRS complex polarity
- Flips the signal if predominantly negative
- Returns corrected signal and inversion status

### ecg_rsp()

Extracts ECG-Derived Respiration (EDR) as a respiratory proxy.

```python
edr_signal = nk.ecg_rsp(ecg_cleaned, sampling_rate=1000, method='vangent2019')
```

**Methods:**
- `'vangent2019'`: 0.1-0.4 Hz bandpass filtering
- `'charlton2016'`: 0.15-0.4 Hz bandpass filtering
- `'soni2019'`: 0.08-0.5 Hz bandpass filtering

**Use Cases:**
- Estimating respiration when no direct respiratory signal is available
- Multimodal physiological analysis

## Simulation and Visualization

### ecg_simulate()

Generates synthetic ECG signals for testing and validation.

```python
synthetic_ecg = nk.ecg_simulate(duration=10, sampling_rate=1000, heart_rate=70, method='ecgsyn', noise=0.01)
```

**Methods:**
- `'ecgsyn'`: Realistic dynamical model (McSharry et al., 2003)
  - Simulates P-QRS-T complex morphology
  - Physiologically plausible waveforms
- `'simple'`: Faster wavelet-based approximation
  - Gaussian-like QRS complexes
  - Lower realism but high computational efficiency

**Key Parameters:**
- `heart_rate`: Average BPM (default: 70)
- `heart_rate_std`: Heart rate variability magnitude (default: 1)
- `noise`: Gaussian noise level (default: 0.01)
- `random_state`: Random seed for reproducibility

### ecg_plot()

Visualizes processed ECG, including detected R-peaks and signal quality.

```python
nk.ecg_plot(signals, info)
```

**Displays:**
- Raw and cleaned ECG signals
- Overlaid R-peak positions
- Heart rate curve
- Signal quality metrics

## ECG Special Considerations

### Sampling Rate Recommendations
- **Minimum requirement**: 250 Hz (for basic R-peak detection)
- **Recommended**: 500-1000 Hz (for delineation)
- **High resolution**: 2000+ Hz (for detailed morphological analysis)

### Signal Duration Requirements
- **R-peak detection**: Any duration (at least ≥2 beats)
- **Basic heart rate**: ≥10 seconds
- **HRV time domain**: ≥60 seconds
- **HRV frequency domain**: 1-5 minutes (optimal)
- **Ultra-low frequency HRV**: ≥24 hours

### Common Issues and Solutions

**Poor R-peak detection:**
- Try different methods: `method='pantompkins1985'` is usually robust
- Ensure sufficient sampling rate (≥250 Hz)
- Check if ECG is inverted: use `ecg_invert()`
- Apply artifact correction: `correct_artifacts=True`

**Noisy signals:**
- Choose appropriate cleaning methods based on noise type
- Adjust powerline frequency if outside US/Europe
- Consider signal quality assessment before analysis

**Missing waveform components:**
- Increase sampling rate (≥500 Hz recommended for delineation)
- Try different delineation methods (`'dwt'`, `'peak'`, `'cwt'`)
- Validate signal quality using `ecg_quality()`

## Integration with Other Signals

### ECG + RSP: Respiratory Sinus Arrhythmia (RSA)
```python
# Process both signals
ecg_signals, ecg_info = nk.ecg_process(ecg, sampling_rate=1000)
rsp_signals, rsp_info = nk.rsp_process(rsp, sampling_rate=1000)

# Calculate RSA
rsa = nk.hrv_rsa(ecg_info['ECG_R_Peaks'], rsp_signals['RSP_Clean'], sampling_rate=1000)
```

### Multimodal Integration
```python
# Process multiple signals at once
bio_signals, bio_info = nk.bio_process(
    ecg=ecg_signal,
    rsp=rsp_signal,
    eda=eda_signal,
    sampling_rate=1000
)
```

## References

- Pan, J., & Tompkins, W. J. (1985). A real-time QRS detection algorithm. IEEE transactions on biomedical engineering, 32(3), 230-236.
- Hamilton, P. (2002). Open source ECG analysis. Computers in cardiology, 101-104.
- Martinez, J. P., Almeida, R., Olmos, S., Rocha, A. P., & Laguna, P. (2004). A wavelet-based ECG delineator: evaluation on standard databases. IEEE Transactions on biomedical engineering, 51(4), 570-581.
- Lipponen, J. A., & Tarvainen, M. P. (2019). A robust algorithm for heart rate variability time series artefact correction using novel beat classification. Journal of medical engineering & technology, 43(3), 173-181.