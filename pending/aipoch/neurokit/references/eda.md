# Electrodermal Activity (EDA) Analysis

## Overview

Electrodermal Activity (EDA), also known as Galvanic Skin Response (GSR) or Skin Conductance (SC), reflects the level of sympathetic nervous system arousal and sweat gland activity by measuring the electrical conductivity of the skin. EDA is widely used in psychophysiology, affective computing, and polygraphy.

## Main Processing Pipeline

### eda_process()

Automatically processes raw EDA signals, returning Tonic/Phasic decomposition results and Skin Conductance Response (SCR) features.

```python
signals, info = nk.eda_process(eda_signal, sampling_rate=100, method='neurokit')
```

**Pipeline Steps:**
1. Signal cleaning (low-pass filtering)
2. Tonic-phasic decomposition
3. Skin Conductance Response (SCR) detection
4. SCR feature extraction (onsets, peaks, amplitude, rise/recovery time)

**Return Values:**
- `signals`: A DataFrame containing the following columns:
  - `EDA_Clean`: Filtered signal
  - `EDA_Tonic`: Slowly changing baseline
  - `EDA_Phasic`: Fast-changing response
  - `SCR_Onsets`, `SCR_Peaks`, `SCR_Height`: Response markers
  - `SCR_Amplitude`, `SCR_RiseTime`, `SCR_RecoveryTime`: Response features
- `info`: A dictionary containing processing parameters

**Methods:**
- `'neurokit'`: cvxEDA decomposition + neurokit peak detection
- `'biosppy'`: Median smoothing + biosppy method

## Preprocessing Functions

### eda_clean()

Removes noise through low-pass filtering.

```python
cleaned_eda = nk.eda_clean(eda_signal, sampling_rate=100, method='neurokit')
```

**Methods:**
- `'neurokit'`: Low-pass Butterworth filter (3 Hz cutoff frequency)
- `'biosppy'`: Low-pass Butterworth filter (5 Hz cutoff frequency)

**Automatic Skip:**
- If sampling rate < 7 Hz, cleaning is skipped (assumed to be already low-pass filtered)

**Principles:**
- EDA frequency components are typically between 0-3 Hz
- Removes high-frequency noise and motion artifacts
- Preserves slow SCRs (typical rise time of 1-3 seconds)

### eda_phasic()

Decomposes EDA into Tonic (slow baseline) and Phasic (fast response) components.

```python
tonic, phasic = nk.eda_phasic(eda_cleaned, sampling_rate=100, method='cvxeda')
```

**Methods:**

**1. cvxEDA (Default, Recommended):**
```python
tonic, phasic = nk.eda_phasic(eda_cleaned, sampling_rate=100, method='cvxeda')
```
- Convex optimization approach (Greco et al., 2016)
- Sparse phasic driver model
- Physiologically most accurate
- Computationally intensive but provides superior decomposition

**2. Median Smoothing:**
```python
tonic, phasic = nk.eda_phasic(eda_cleaned, sampling_rate=100, method='smoothmedian')
```
- Median filter with configurable window
- Fast and simple
- Lower accuracy than cvxEDA

**3. High-pass Filtering (Biopac's Acqknowledge):**
```python
tonic, phasic = nk.eda_phasic(eda_cleaned, sampling_rate=100, method='highpass')
```
- Extracts phasic component via high-pass filtering (0.05 Hz)
- Fast computation
- Tonic component derived by subtraction

**4. SparsEDA:**
```python
tonic, phasic = nk.eda_phasic(eda_cleaned, sampling_rate=100, method='sparseda')
```
- Sparse deconvolution method
- Alternative optimization approach

**Return Values:**
- `tonic`: Slowly changing Skin Conductance Level (SCL)
- `phasic`: Fast-changing Skin Conductance Responses (SCRs)

**Physiological Interpretation:**
- **Tonic (SCL)**: Baseline arousal, general activation state, hydration
- **Phasic (SCR)**: Event-related responses, orientation, emotional reactions

### eda_peaks()

Detects Skin Conductance Responses (SCRs) in the phasic component.

```python
peaks, info = nk.eda_peaks(eda_phasic, sampling_rate=100, method='neurokit',
                           amplitude_min=0.1)
```

**Methods:**
- `'neurokit'`: Optimized for reliability with configurable thresholds
- `'gamboa2008'`: Gamboa algorithm
- `'kim2004'`: Kim method
- `'vanhalem2020'`: Van Halem method
- `'nabian2018'`: Nabian algorithm

**Key Parameters:**
- `amplitude_min`: Minimum SCR amplitude (default: 0.1 µS)
  - Too low: Noise creates false positives
  - Too high: Misses small but valid responses
- `rise_time_max`: Maximum rise time (default: 2 seconds)
- `rise_time_min`: Minimum rise time (default: 0.01 seconds)

**Return Values:**
- A dictionary containing:
  - `SCR_Onsets`: Indices of SCR starts
  - `SCR_Peaks`: Indices of peak amplitudes
  - `SCR_Height`: Peak height above baseline
  - `SCR_Amplitude`: Amplitude from onset to peak
  - `SCR_RiseTime`: Duration from onset to peak
  - `SCR_RecoveryTime`: Duration from peak to recovery (50% decay)

**SCR Timing Conventions:**
- **Latency**: 1-3 seconds after stimulus (typical)
- **Rise time**: 0.5-3 seconds
- **Recovery time**: 2-10 seconds (to 50% recovery)
- **Minimum amplitude**: 0.01-0.05 µS (detection threshold)

### eda_fixpeaks()

Corrects detected SCR peaks (currently a placeholder for EDA).

```python
corrected_peaks = nk.eda_fixpeaks(peaks)
```

**Note:** Due to slower EDA dynamics, this step is less critical for EDA than for ECG signals.

## Analysis Functions

### eda_analyze()

Automatically selects the appropriate analysis type based on data duration.

```python
analysis = nk.eda_analyze(signals, sampling_rate=100)
```

**Mode Selection:**
- Duration < 10 seconds → `eda_eventrelated()`
- Duration ≥ 10 seconds → `eda_intervalrelated()`

**Return Values:**
- A DataFrame containing EDA metrics suitable for the analysis mode

### eda_eventrelated()

Analyzes stimulus-locked EDA epochs for event-related responses.

```python
results = nk.eda_eventrelated(epochs)
```

**Calculated Metrics (per epoch):**
- `EDA_SCR`: Presence of SCR (binary: 0 or 1)
- `SCR_Amplitude`: Maximum SCR amplitude within the epoch
- `SCR_Magnitude`: Average phasic activity
- `SCR_Peak_Amplitude`: Amplitude from onset to peak
- `SCR_RiseTime`: Time from onset to peak
- `SCR_RecoveryTime`: Time to 50% recovery
- `SCR_Latency`: Delay from stimulus to SCR onset
- `EDA_Tonic`: Mean tonic level during the epoch

**Typical Parameters:**
- Epoch duration: 0-10 seconds post-stimulus
- Baseline: -1 to 0 seconds pre-stimulus
- Expected SCR latency: 1-3 seconds

**Applications:**
- Emotional stimuli processing (images, sounds)
- Cognitive load assessment (mental arithmetic)
- Anticipation and prediction error
- Orienting response

### eda_intervalrelated()

Analyzes long-duration EDA recordings for overall arousal and activation patterns.

```python
results = nk.eda_intervalrelated(signals, sampling_rate=100)
```

**Calculated Metrics:**
- `SCR_Peaks_N`: Number of detected SCRs
- `SCR_Peaks_Amplitude_Mean`: Average SCR amplitude
- `EDA_Tonic_Mean`, `EDA_Tonic_SD`: Tonic level statistics
- `EDA_Sympathetic`: Sympathetic nervous system index
- `EDA_SympatheticN`: Normalized sympathetic index
- `EDA_Autocorrelation`: Temporal structure (4s lag)
- `EDA_Phasic_*`: Mean, SD, Min, Max of the phasic component

**Recording Duration:**
- **Minimum**: 10 seconds
- **Recommended**: 60+ seconds for stable SCR rates
- **Sympathetic Index**: Requires at least 64 seconds

**Applications:**
- Resting-state arousal assessment
- Stress level monitoring
- Baseline sympathetic activity
- Long-term affective states

## Specialized Analysis Functions

### eda_sympathetic()

Derives sympathetic nervous system activity from frequency bands (0.045-0.25 Hz).

```python
sympathetic = nk.eda_sympathetic(signals, sampling_rate=100, method='posada',
                                  show=False)
```

**Methods:**
- `'posada'`: Posada-Quintero method (2016)
  - Spectral power within the 0.045-0.25 Hz band
  - Validated against other autonomic measures
- `'ghiasi'`: Ghiasi method (2018)
  - Alternative frequency-based approach

**Requirements:**
- **Minimum duration**: 64 seconds
- Sufficient frequency resolution for the target band

**Return Values:**
- `EDA_Sympathetic`: Sympathetic index (absolute)
- `EDA_SympatheticN`: Normalized sympathetic index (0-1)

**Interpretation:**
- Higher values: Increased sympathetic arousal
- Reflects tonic sympathetic activity rather than phasic responses
- Complementary to SCR analysis

**Applications:**
- Stress assessment
- Monitoring arousal changes over time
- Cognitive load measurement
- Complementary to HRV for assessing autonomic balance

### eda_autocor()

Calculates autocorrelation to assess the temporal structure of the EDA signal.

```python
autocorr = nk.eda_autocor(eda_phasic, sampling_rate=100, lag=4)
```

**Parameters:**
- `lag`: Time lag in seconds (default: 4 seconds)

**Interpretation:**
- High autocorrelation: Persistent and slowly changing signal
- Low autocorrelation: Fast and uncorrelated fluctuations
- Reflects the temporal regularity of SCRs

**Applications:**
- Signal quality assessment
- Characterizing response patterns
- Distinguishing sustained vs. transient arousal

### eda_changepoints()

Detects abrupt changes in the mean and variance of the EDA signal.

```python
changepoints = nk.eda_changepoints(eda_phasic, penalty=10000, show=False)
```

**Methods:**
- Penalty-based segmentation
- Identifies transitions between states

**Parameters:**
- `penalty`: Controls sensitivity (default: 10,000)
  - Higher penalty: Fewer and more robust changepoints
  - Lower penalty: More sensitive to minor changes

**Return Values:**
- Indices of detected changepoints
- Optional visualization of segments

**Applications:**
- Identifying state transitions in continuous monitoring
- Segmenting data by arousal levels
- Detecting phase changes in experiments
- Automatic epoch definition

## Visualization

### eda_plot()

Creates static or interactive visualizations of processed EDA.

```python
nk.eda_plot(signals, info, static=True)
```

**Displays:**
- Raw and cleaned EDA signals
- Tonic and Phasic components
- Detected SCR onsets, peaks, and recovery points
- Sympathetic index timeline (if calculated)

**Interactive Mode (`static=False`):**
- Plotly-based interactive exploration
- Zoom, pan, and hover for details
- Export to image formats

## Simulation and Testing

### eda_simulate()

Generates synthetic EDA signals with configurable parameters.

```python
synthetic_eda = nk.eda_simulate(duration=10, sampling_rate=100, scr_number=3,
                                noise=0.01, drift=0.01)
```

**Parameters:**
- `duration`: Signal length (seconds)
- `sampling_rate`: Sampling frequency (Hz)
- `scr_number`: Number of SCRs to include
- `noise`: Gaussian noise level
- `drift`: Amplitude of slow baseline drift
- `random_state`: Random seed for reproducibility

**Return Values:**
- Synthetic EDA signal with realistic SCR morphology

**Applications:**
- Algorithm testing and validation
- Educational demonstrations
- Method comparison

## Practical Considerations

### Sampling Rate Recommendations
- **Minimum**: 10 Hz (sufficient to capture slow SCRs)
- **Standard**: 20-100 Hz (most commercial systems)
- **High Resolution**: 1000 Hz (research grade, oversampled)

### Recording Duration
- **SCR Detection**: ≥10 seconds (depending on stimulus)
- **Event-Related**: Typically 10-20 seconds per trial
- **Interval-Related**: ≥60 seconds for stable estimates
- **Sympathetic Index**: ≥64 seconds (frequency resolution requirement)

### Electrode Placement
- **Standard Sites**:
  - Palmar: Distal/intermediate phalanges (fingers)
  - Plantar: Sole of the foot
- **High Density**: Thenar/Hypothenar eminence
- **Avoid**: Hairy skin, areas with low sweat gland density
- **Bilateral Comparison**: Left vs. Right hand (usually similar)

### Signal Quality Issues

**Flat Signal (No Change):**
- Check electrode contact and conductive paste
- Confirm placement in sweat-gland-rich areas
- Allow 5-10 minutes for adaptation

**Excessive Noise:**
- Motion artifacts: Minimize subject movement
- Electromagnetic interference: Check grounding and shielding
- Temperature effects: Control room temperature

**Baseline Drift:**
- Normal: Slow changes over minutes
- Excessive: Electrode polarization, poor contact
- Solution: Use `eda_phasic()` to isolate tonic drift

**Non-responders:**
- Approximately 5-10% of the population has minimal EDA
- Genetic/physiological difference
- Does not necessarily indicate equipment failure

### Best Practices

**Preprocessing Workflow:**
```python
# 1. Clean signal
cleaned = nk.eda_clean(eda_raw, sampling_rate=100, method='neurokit')

# 2. Decompose Tonic/Phasic
tonic, phasic = nk.eda_phasic(cleaned, sampling_rate=100, method='cvxeda')

# 3. Detect SCRs
signals, info = nk.eda_peaks(phasic, sampling_rate=100, amplitude_min=0.05)

# 4. Analyze
analysis = nk.eda_analyze(signals, sampling_rate=100)
```

**Event-Related Workflow:**
```python
# 1. Process signal
signals, info = nk.eda_process(eda_raw, sampling_rate=100)

# 2. Find events
events = nk.events_find(trigger_channel, threshold=0.5)

# 3. Create epochs (-1 to 10s around stimulus)
epochs = nk.epochs_create(signals, events, sampling_rate=100,
                          epochs_start=-1, epochs_end=10)

# 4. Event-related analysis
results = nk.eda_eventrelated(epochs)

# 5. Statistical analysis
# Compare SCR amplitudes across different conditions
```

## Clinical and Research Applications

**Emotional and Affective Science:**
- Arousal dimension of emotion (rather than valence)
- Emotional picture viewing
- Music-induced emotion
- Fear conditioning

**Cognitive Processes:**
- Mental workload and effort
- Attention and alertness
- Decision making and uncertainty
- Error processing

**Clinical Populations:**
- Anxiety disorders: Elevated baseline, exaggerated responses
- PTSD: Deficits in fear conditioning and extinction
- Autism: Atypical arousal patterns
- Psychopathy: Reduced fear responses

**Applied Scenarios:**
- Polygraphy (Lie detection)
- User Experience (UX) research
- Driver monitoring
- Stress assessment in real-world environments

**Neuroimaging Integration:**
- fMRI: EDA correlates with amygdala and insula activity
- Synchronous recording during brain imaging
- Autonomic-brain coupling

## Interpretation Guidelines

**SCR Amplitude:**
- **0.01-0.05 µS**: Tiny but detectable
- **0.05-0.2 µS**: Moderate response
- **>0.2 µS**: Strong response
- **Context-dependent**: Should be normalized within-subject

**SCR Frequency:**
- **Resting**: 1-3 SCRs per minute (typical)
- **Stress**: >5 SCRs per minute
- **Non-specific SCRs**: Spontaneously occurring (no clear stimulus)

**Tonic SCL:**
- **Range**: 2-20 µS (highly variable between individuals)
- **Within-subject changes** are more interpretable than absolute levels
- **Increase**: Arousal, stress, cognitive load
- **Decrease**: Relaxation, habituation

## References

- Boucsein, W. (2012). Electrodermal activity (2nd ed.). Springer Science & Business Media.
- Greco, A., Valenza, G., & Scilingo, E. P. (2016). cvxEDA: A convex optimization approach to electrodermal activity processing. IEEE Transactions on Biomedical Engineering, 63(4), 797-804.
- Posada-Quintero, H. F., Florian, J. P., Orjuela-Cañón, A. D., Aljama-Corrales, T., Charleston-Villalobos, S., & Chon, K. H. (2016). Power spectral density analysis of electrodermal activity for sympathetic function assessment. Annals of biomedical engineering, 44(10), 3124-3135.
- Dawson, M. E., Schell, A. M., & Filion, D. L. (2017). The electrodermal system. In Handbook of psychophysiology (pp. 217-243). Cambridge University Press.