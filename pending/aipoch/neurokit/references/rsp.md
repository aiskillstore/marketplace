# Respiration Signal Processing

## Overview

Respiration signal processing in NeuroKit2 allows for the analysis of breathing patterns, respiration rate, amplitude, and variability. Respiration is closely linked to cardiac activity (Respiratory Sinus Arrhythmia), emotional states, and cognitive processes.

## Main Processing Pipeline

### rsp_process()

Automatically processes respiration signals, including peak/trough detection and feature extraction.

```python
signals, info = nk.rsp_process(rsp_signal, sampling_rate=100, method='khodadad2018')
```

**Pipeline Steps:**
1. Signal cleaning (noise removal, filtering)
2. Peak (exhalation) and trough (inhalation) detection
3. Respiration rate calculation
4. Amplitude calculation
5. Phase determination (inhalation/exhalation)
6. Respiratory Volume per Time (RVT)

**Return Values:**
- `signals`: A DataFrame containing the following columns:
  - `RSP_Clean`: Filtered respiration signal
  - `RSP_Peaks`, `RSP_Troughs`: Extrema markers
  - `RSP_Rate`: Instantaneous respiration rate (breaths per minute)
  - `RSP_Amplitude`: Breath-to-breath amplitude
  - `RSP_Phase`: Inhalation (0) and Exhalation (1)
  - `RSP_Phase_Completion`: Phase completion percentage (0-1)
  - `RSP_RVT`: Respiratory Volume per Time
- `info`: A dictionary containing peak/trough indices

**Methods:**
- `'khodadad2018'`: Algorithm by Khodadad et al. (default, robust)
- `'biosppy'`: Processing based on BioSPPy (alternative)

## Preprocessing Functions

### rsp_clean()

Removes noise and smoothes the respiration signal.

```python
cleaned_rsp = nk.rsp_clean(rsp_signal, sampling_rate=100, method='khodadad2018')
```

**Methods:**

**1. Khodadad2018 (Default):**
- Butterworth low-pass filter
- Removes high-frequency noise
- Preserves respiration waveform

**2. BioSPPy:**
- Another filtering method
- Performance similar to Khodadad

**3. Hampel Filter:**
```python
cleaned_rsp = nk.rsp_clean(rsp_signal, sampling_rate=100, method='hampel')
```
- Median-based outlier removal
- Robust to artifacts and spikes
- Preserves sharp transitions

**Typical Respiration Frequencies:**
- Resting adults: 12-20 breaths/minute (0.2-0.33 Hz)
- Children: Faster frequencies
- During exercise: Up to 40-60 breaths/minute

### rsp_peaks()

Identifies inhalation troughs and exhalation peaks in the respiration signal.

```python
peaks, info = nk.rsp_peaks(cleaned_rsp, sampling_rate=100, method='khodadad2018')
```

**Detection Methods:**
- `'khodadad2018'`: Optimized for clean signals
- `'biosppy'`: Alternative method
- `'scipy'`: Simple detection based on scipy

**Return Values:**
- A dictionary containing:
  - `RSP_Peaks`: Exhalation peak indices (local maxima)
  - `RSP_Troughs`: Inhalation trough indices (local minima)

**Respiration Cycle Definition:**
- **Inhalation**: Trough → Peak (air flows in, chest/abdomen expands)
- **Exhalation**: Peak → Trough (air flows out, chest/abdomen contracts)

### rsp_findpeaks()

Low-level peak detection, providing multiple algorithm options.

```python
peaks_dict = nk.rsp_findpeaks(cleaned_rsp, sampling_rate=100, method='scipy')
```

**Methods:**
- `'scipy'`: Uses Scipy's find_peaks
- Custom threshold-based algorithms

**Use Cases:**
- Fine-tuning peak detection
- Custom parameter adjustment
- Algorithm comparison

### rsp_fixpeaks()

Corrects detected peak/trough anomalies (e.g., missed or false detections).

```python
corrected_peaks = nk.rsp_fixpeaks(peaks, sampling_rate=100)
```

**Corrections:**
- Removal of physiologically impossible intervals
- Interpolation of missing peaks
- Removal of artifact-related false peaks

## Feature Extraction Functions

### rsp_rate()

Calculates instantaneous respiration rate (breaths per minute).

```python
rate = nk.rsp_rate(peaks, sampling_rate=100, desired_length=None)
```

**Methods:**
- Calculates breath-to-breath intervals based on peak/trough times
- Converts to breaths per minute (BPM)
- Interpolates to match signal length

**Typical Values:**
- Resting adults: 12-20 BPM
- Slow breathing: <10 BPM (meditation, relaxation)
- Fast breathing: >25 BPM (exercise, anxiety)

### rsp_amplitude()

Calculates breath-to-breath amplitude (peak-to-trough difference).

```python
amplitude = nk.rsp_amplitude(cleaned_rsp, peaks)
```

**Interpretation:**
- Large amplitude: Deep breathing (increased tidal volume)
- Small amplitude: Shallow breathing
- Variable amplitude: Irregular breathing patterns

**Clinical Significance:**
- Decreased amplitude: Restrictive lung disease, chest wall stiffness
- Increased amplitude: Compensatory hyperventilation

### rsp_phase()

Determines inhalation/exhalation phase and completion percentage.

```python
phase, completion = nk.rsp_phase(cleaned_rsp, peaks, sampling_rate=100)
```

**Return Values:**
- `RSP_Phase`: Binary (0 = inhalation, 1 = exhalation)
- `RSP_Phase_Completion`: Continuous value between 0-1, indicating phase progress

**Use Cases:**
- Respiratory-gated stimulus presentation
- Phase-locked averaging
- Respiration-cardiac coupling analysis

### rsp_symmetry()

Analyzes respiration symmetry patterns (peak-trough balance, rise-decay timing).

```python
symmetry = nk.rsp_symmetry(cleaned_rsp, peaks)
```

**Metrics:**
- Peak-trough symmetry: Are peaks and troughs equidistant?
- Rise-decay symmetry: Is inhalation time equal to exhalation time?

**Interpretation:**
- Symmetric: Normal, relaxed breathing
- Asymmetric: Labored breathing, airway obstruction

## Advanced Analysis Functions

### rsp_rrv()

Respiratory Rate Variability (RRV) — similar to heart rate variability.

```python
rrv_indices = nk.rsp_rrv(peaks, sampling_rate=100)
```

**Time-domain Metrics:**
- `RRV_SDBB`: Standard deviation of breath-to-breath intervals
- `RRV_RMSSD`: Root mean square of successive differences
- `RRV_MeanBB`: Mean breath-to-breath interval

**Frequency-domain Metrics:**
- Power in various frequency bands (if applicable)

**Interpretation:**
- High RRV: Flexible, adaptive respiratory control
- Low RRV: Rigid, restricted breathing
- RRV changes: Anxiety, respiratory disorders, autonomic dysfunction

**Recording Duration:**
- Minimum: 2-3 minutes
- Ideal: 5-10 minutes for stable estimates

### rsp_rvt()

Respiratory Volume per Time (RVT) — fMRI nuisance regressor.

```python
rvt = nk.rsp_rvt(cleaned_rsp, peaks, sampling_rate=100)
```

**Calculation:**
- Derivative of the respiration signal
- Captures rate of volume change
- Correlated with BOLD signal fluctuations

**Use Cases:**
- fMRI artifact correction
- Neuroimaging preprocessing
- Respiratory nuisance regression

**References:**
- Birn, R. M., et al. (2008). Separating respiratory-variation-related fluctuations from neuronal-activity-related fluctuations in fMRI. NeuroImage, 31(4), 1536-1548.

### rsp_rav()

Respiratory Amplitude Variability (RAV) metrics.

```python
rav = nk.rsp_rav(amplitude, sampling_rate=100)
```

**Metrics:**
- Standard deviation of amplitude
- Coefficient of variation
- Amplitude range

**Interpretation:**
- High RAV: Irregular breathing depth (sighing, arousal changes)
- Low RAV: Stable, controlled breathing

## Analysis Functions

### rsp_analyze()

Automatically selects event-related or interval-related analysis.

```python
analysis = nk.rsp_analyze(signals, sampling_rate=100)
```

**Mode Selection:**
- Duration < 10 seconds → event-related
- Duration ≥ 10 seconds → interval-related

### rsp_eventrelated()

Analyzes respiration responses to specific events/stimuli.

```python
results = nk.rsp_eventrelated(epochs)
```

**Metrics (per epoch):**
- `RSP_Rate_Mean`: Mean respiration rate during the epoch
- `RSP_Rate_Min/Max`: Min/max respiration rate
- `RSP_Amplitude_Mean`: Mean breathing depth
- `RSP_Phase`: Respiration phase at event onset
- Dynamic changes in respiration rate and amplitude during the epoch

**Use Cases:**
- Respiration changes during emotional stimuli
- Anticipatory breathing before task events
- Breath-holding or hyperventilation paradigms

### rsp_intervalrelated()

Analyzes long respiration recordings.

```python
results = nk.rsp_intervalrelated(signals, sampling_rate=100)
```

**Metrics:**
- `RSP_Rate_Mean`: Mean respiration rate
- `RSP_Rate_SD`: Respiration rate variability
- `RSP_Amplitude_Mean`: Mean breathing depth
- RRV metrics (if sufficient data)
- RAV metrics

**Recording Duration:**
- Minimum: 60 seconds
- Ideal: 5-10 minutes

**Use Cases:**
- Resting-state breathing patterns
- Baseline respiration assessment
- Stress or relaxation monitoring

## Simulation and Visualization

### rsp_simulate()

Generates synthetic respiration signals for testing.

```python
synthetic_rsp = nk.rsp_simulate(duration=60, sampling_rate=100, respiratory_rate=15,
                                method='sinusoidal', noise=0.1, random_state=42)
```

**Methods:**
- `'sinusoidal'`: Simple sinusoidal oscillation (fast)
- `'breathmetrics'`: Advanced realistic respiration model (slower but more accurate)

**Parameters:**
- `respiratory_rate`: Breaths per minute (default: 15)
- `noise`: Gaussian noise level
- `random_state`: Random seed for reproducibility

**Use Cases:**
- Algorithm validation
- Parameter tuning
- Educational demonstrations

### rsp_plot()

Visualizes processed respiration signals.

```python
nk.rsp_plot(signals, info, static=True)
```

**Display Content:**
- Raw and cleaned respiration signals
- Detected peaks and troughs
- Instantaneous respiration rate
- Phase markers

**Interactive Mode:** Set `static=False` to use Plotly for visualization.

## Practical Application Suggestions

### Sampling Rate Recommendations
- **Minimum**: 10 Hz (sufficient for frequency estimation)
- **Standard**: 50-100 Hz (research grade)
- **High resolution**: 1000 Hz (usually unnecessary, oversampling)

### Recording Duration
- **Frequency estimation**: ≥10 seconds (a few breaths)
- **RRV analysis**: ≥2-3 minutes
- **Resting state**: 5-10 minutes
- **Circadian patterns**: Hours to days

### Signal Acquisition Methods

**Strain Gauges / Piezoelectric Belts:**
- Measures chest or abdominal expansion
- Most common
- Comfortable, non-invasive

**Thermistors / Thermocouples:**
- Measures nasal/oral airflow temperature
- Direct airflow measurement
- Can be invasive

**Capnography:**
- End-tidal CO2 measurement
- Physiological gold standard
- Expensive, common in clinical settings

**Impedance Pneumography:**
- Derived from ECG electrodes
- Convenient for multimodal recording
- Less accurate than dedicated sensors

### Common Issues and Solutions

**Irregular Breathing:**
- Normal in awake, resting humans
- Sighs, yawns, talking, swallowing cause variability
- Exclude artifacts or model them as events

**Shallow Breathing:**
- Low signal amplitude
- Check sensor placement and tightness
- Increase gain if possible

**Motion Artifacts:**
- Appear as spikes or discontinuities
- Minimize subject movement
- Use robust peak detection (Hampel filter)

**Talking/Coughing:**
- Disrupts natural breathing patterns
- Annotate and exclude in analysis
- Or model as separate event types

### Best Practices

**Standard Workflow:**
```python
# 1. Clean signal
cleaned = nk.rsp_clean(rsp_raw, sampling_rate=100, method='khodadad2018')

# 2. Detect peaks/troughs
peaks, info = nk.rsp_peaks(cleaned, sampling_rate=100)

# 3. Extract features
rate = nk.rsp_rate(peaks, sampling_rate=100, desired_length=len(cleaned))
amplitude = nk.rsp_amplitude(cleaned, peaks)
phase = nk.rsp_phase(cleaned, peaks, sampling_rate=100)

# 4. Integrated processing (alternative)
signals, info = nk.rsp_process(rsp_raw, sampling_rate=100)

# 5. Analysis
analysis = nk.rsp_analyze(signals, sampling_rate=100)
```

**Respiration-Cardiac Integration:**
```python
# Process both signals
ecg_signals, ecg_info = nk.ecg_process(ecg, sampling_rate=1000)
rsp_signals, rsp_info = nk.rsp_process(rsp, sampling_rate=100)

# Respiratory Sinus Arrhythmia (RSA)
rsa = nk.hrv_rsa(ecg_info['ECG_R_Peaks'], rsp_signals['RSP_Clean'], sampling_rate=1000)

# Or use bio_process for multi-signal integration
bio_signals, bio_info = nk.bio_process(ecg=ecg, rsp=rsp, sampling_rate=1000)
```

## Clinical and Research Applications

**Psychophysiology:**
- Emotion and arousal (fast and shallow breathing during stress)
- Relaxation interventions (deep, slow breathing)
- Respiratory biofeedback

**Anxiety and Panic Disorders:**
- Hyperventilation during panic attacks
- Altered breathing patterns
- Evaluation of breathing retraining treatment efficacy

**Sleep Medicine:**
- Sleep apnea detection
- Abnormal breathing patterns
- Sleep stage correlation

**Cardiorespiratory Coupling:**
- Respiratory Sinus Arrhythmia (respiratory modulation of HRV)
- Cardiorespiratory interaction
- Autonomic nervous system assessment

**Neuroimaging:**
- fMRI artifact correction (RVT regressors)
- BOLD signal nuisance removal
- Respiration-related brain activity

**Meditation and Mindfulness:**
- Breath awareness training
- Slow breathing exercises (resonance frequency ~6 breaths/min)
- Physiological markers of relaxation

**Sports Performance:**
- Breathing efficiency
- Training adaptation
- Recovery monitoring

## Interpretation Guide

**Respiration Rate:**
- **Normal**: 12-20 BPM (resting adult)
- **Slow**: <10 BPM (relaxation, meditation, sleep)
- **Fast**: >25 BPM (exercise, anxiety, pain, fever)

**Respiration Amplitude:**
- Resting tidal volume usually 400-600 mL
- Deep breathing: 2-3 L
- Shallow breathing: <300 mL

**Breathing Patterns:**
- **Normal**: Smooth, regular sine wave
- **Cheyne-Stokes**: Crescendo-decrescendo with apnea (clinical pathology)
- **Ataxic**: Completely irregular (brainstem injury)

## References

- Khodadad, D., Nordebo, S., Müller, B., Waldmann, A., Yerworth, R., Becher, T., ... & Bayford, R. (2018). A review of tissue substitutes for ultrasound imaging. Ultrasound in medicine & biology, 44(9), 1807-1823.
- Grossman, P., & Taylor, E. W. (2007). Toward understanding respiratory sinus arrhythmia: Relations to cardiac vagal tone, evolution and biobehavioral functions. Biological psychology, 74(2), 263-285.
- Birn, R. M., Diamond, J. B., Smith, M. A., & Bandettini, P. A. (2006). Separating respiratory-variation-related fluctuations from neuronal-activity-related fluctuations in fMRI. NeuroImage, 31(4), 1536-1548.