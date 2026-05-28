# Photoplethysmogram (PPG) Analysis

## Overview

Photoplethysmography (PPG) measures blood volume changes in microvascular tissue using optical sensors. PPG is widely used in wearable devices, pulse oximeters, and clinical monitors for heart rate monitoring, pulse characterization, and cardiovascular assessment.

## Main Processing Pipeline

### ppg_process()

Automated PPG signal processing pipeline.

```python
signals, info = nk.ppg_process(ppg_signal, sampling_rate=100, method='elgendi')
```

**Pipeline Steps:**
1. Signal cleaning (filtering)
2. Systolic peak detection
3. Heart rate calculation
4. Signal quality assessment

**Return Values:**
- `signals`: A DataFrame containing:
  - `PPG_Clean`: Filtered PPG signal
  - `PPG_Peaks`: Systolic peak markers
  - `PPG_Rate`: Instantaneous heart rate (BPM)
  - `PPG_Quality`: Signal quality index
- `info`: A dictionary containing peak indices and parameters

**Methods:**
- `'elgendi'`: Algorithm by Elgendi et al. (2013) (Default, robust)
- `'nabian2018'`: Method by Nabian et al. (2018)

## Preprocessing Functions

### ppg_clean()

Prepares raw PPG signals for peak detection.

```python
cleaned_ppg = nk.ppg_clean(ppg_signal, sampling_rate=100, method='elgendi')
```

**Methods:**

**1. Elgendi (Default):**
- Butterworth bandpass filter (0.5-8 Hz)
- Removes baseline drift and high-frequency noise
- Optimized for peak detection reliability

**2. Nabian2018:**
- Alternative filtering method
- Different frequency characteristics

**PPG Signal Features:**
- **Systolic peak**: Rapid rise, sharp peak (cardiac ejection)
- **Dicrotic notch**: Secondary peak (aortic valve closure)
- **Baseline**: Slow drift caused by respiration, movement, and perfusion

### ppg_peaks()

Detects systolic peaks in PPG signals.

```python
peaks, info = nk.ppg_peaks(cleaned_ppg, sampling_rate=100, method='elgendi',
                           correct_artifacts=False)
```

**Methods:**
- `'elgendi'`: Two moving averages with dynamic thresholds
- `'bishop'`: Bishop algorithm
- `'nabian2018'`: Nabian's method
- `'scipy'`: Simple scipy peak detection

**Artifact Correction:**
- Set `correct_artifacts=True` for physiological plausibility checks
- Rejects false peaks based on inter-beat interval outliers

**Return Values:**
- A dictionary containing the `'PPG_Peaks'` key (storing peak indices)

**Typical Inter-beat Intervals:**
- Resting adults: 600-1200 ms (50-100 BPM)
- Athletes: Potentially longer (bradycardia)
- Stress/Exercise: Shorter (<600 ms, >100 BPM)

### ppg_findpeaks()

Low-level peak detection with algorithm comparison.

```python
peaks_dict = nk.ppg_findpeaks(cleaned_ppg, sampling_rate=100, method='elgendi')
```

**Use Cases:**
- Custom parameter tuning
- Algorithm testing
- Research method development

## Analysis Functions

### ppg_analyze()

Automatically selects event-related or interval-related analysis.

```python
analysis = nk.ppg_analyze(signals, sampling_rate=100)
```

**Mode Selection:**
- Duration < 10 seconds → Event-related
- Duration ≥ 10 seconds → Interval-related

### ppg_eventrelated()

Analyzes PPG response to discrete events/stimuli.

```python
results = nk.ppg_eventrelated(epochs)
```

**Calculated Metrics (per epoch):**
- `PPG_Rate_Baseline`: Heart rate before the event
- `PPG_Rate_Min/Max`: Minimum/maximum heart rate during the epoch
- Dynamic heart rate changes across the epoch time window

**Use Cases:**
- Cardiovascular response to emotional stimuli
- Cognitive load assessment
- Stress response paradigms

### ppg_intervalrelated()

Analyzes prolonged PPG recordings.

```python
results = nk.ppg_intervalrelated(signals, sampling_rate=100)
```

**Calculated Metrics:**
- `PPG_Rate_Mean`: Average heart rate
- Heart Rate Variability (HRV) metrics
  - Calls the `hrv()` function
  - Includes time-domain, frequency-domain, and non-linear domains

**Recording Duration:**
- Minimum: 60 seconds required for baseline heart rate
- HRV analysis: 2-5 minutes recommended

**Use Cases:**
- Resting-state cardiovascular assessment
- Wearable device data analysis
- Long-term heart rate monitoring

## Quality Assessment

### ppg_quality()

Evaluates signal quality and reliability.

```python
quality = nk.ppg_quality(ppg_signal, sampling_rate=100, method='averageQRS')
```

**Methods:**

**1. averageQRS (Default):**
- Template matching method
- Correlates each pulse with an average template
- Returns a quality score (0-1) for each beat
- Threshold: >0.6 = Acceptable quality

**2. dissimilarity:**
- Topographic dissimilarity measurement
- Detects morphological changes

**Use Cases:**
- Identifying corrupted segments
- Filtering low-quality data before analysis
- Validating peak detection accuracy

**Common Quality Issues:**
- Motion artifacts: Sudden signal changes
- Poor sensor contact: Low amplitude, noise
- Vasoconstriction: Reduced signal amplitude (cold, stress)

## Utility Functions

### ppg_segment()

Extracts individual pulses for morphological analysis.

```python
pulses = nk.ppg_segment(cleaned_ppg, peaks, sampling_rate=100)
```

**Return Values:**
- A dictionary of pulse epochs, each centered on a systolic peak
- Supports comparison between pulses
- Morphological analysis under different conditions

**Use Cases:**
- Pulse Wave Analysis (PWA)
- Arterial stiffness proxies
- Vascular aging assessment

### ppg_methods()

Documents preprocessing methods used in the analysis.

```python
methods_info = nk.ppg_methods(method='elgendi')
```

**Return Values:**
- A string documenting the processing pipeline
- Suitable for the methods section of a paper

## Simulation and Visualization

### ppg_simulate()

Generates synthetic PPG signals for testing.

```python
synthetic_ppg = nk.ppg_simulate(duration=60, sampling_rate=100, heart_rate=70,
                                noise=0.1, random_state=42)
```

**Parameters:**
- `heart_rate`: Average BPM (Default: 70)
- `heart_rate_std`: HRV magnitude
- `noise`: Gaussian noise level
- `random_state`: Seed for reproducibility

**Use Cases:**
- Algorithm validation
- Parameter optimization
- Educational demonstrations

### ppg_plot()

Visualizes processed PPG signals.

```python
nk.ppg_plot(signals, info, static=True)
```

**Displays:**
- Raw and cleaned PPG signals
- Detected systolic peaks
- Instantaneous heart rate trajectory
- Signal quality indicators

## Practical Considerations

### Sampling Rate Recommendations
- **Minimum**: 20 Hz (Basic heart rate)
- **Standard**: 50-100 Hz (Most wearables)
- **High Resolution**: 200-500 Hz (Research, Pulse Wave Analysis)
- **Excessive**: >1000 Hz (Unnecessary for PPG)

### Recording Duration
- **Heart Rate**: ≥10 seconds (several beats)
- **HRV Analysis**: At least 2-5 minutes
- **Long-term Monitoring**: Hours to days (wearables)

### Sensor Placement

**Common Sites:**
- **Fingertip**: Highest signal quality, most common
- **Earlobe**: Fewer motion artifacts, clinical use
- **Wrist**: Wearable devices (smartwatches)
- **Forehead**: Reflectance mode, medical monitoring

**Transmissive vs. Reflective:**
- **Transmissive**: Light passes through tissue (fingertip, earlobe)
  - Higher signal quality
  - Fewer motion artifacts
- **Reflective**: Light reflects off tissue (wrist, forehead)
  - More susceptible to noise
  - Convenient for wearable applications

### Common Issues and Solutions

**Low Signal Amplitude:**
- Poor perfusion: Warm hands to increase blood flow
- Sensor contact: Adjust position, clean skin
- Vasoconstriction: Ambient temperature, stress

**Motion Artifacts:**
- Major issue in wearables
- Adaptive filtering, accelerometer-based correction
- Template matching, outlier rejection

**Baseline Drift:**
- Respiratory modulation (normal phenomenon)
- Movement or pressure changes
- High-pass filtering or detrending

**Missed Peaks:**
- Low signal quality: Check sensor contact
- Algorithm parameters: Adjust thresholds
- Try alternative detection methods

### Best Practices

**Standard Workflow:**
```python
# 1. Clean signal
cleaned = nk.ppg_clean(ppg_raw, sampling_rate=100, method='elgendi')

# 2. Detect peaks and correct artifacts
peaks, info = nk.ppg_peaks(cleaned, sampling_rate=100, correct_artifacts=True)

# 3. Assess quality
quality = nk.ppg_quality(cleaned, sampling_rate=100)

# 4. Comprehensive processing (Alternative)
signals, info = nk.ppg_process(ppg_raw, sampling_rate=100)

# 5. Analysis
analysis = nk.ppg_analyze(signals, sampling_rate=100)
```

**PPG-based HRV:**
```python
# Process PPG signal
signals, info = nk.ppg_process(ppg_raw, sampling_rate=100)

# Extract peaks and calculate HRV
hrv_indices = nk.hrv(info['PPG_Peaks'], sampling_rate=100)

# PPG-derived HRV is valid but may differ slightly from ECG-derived HRV
# Differences arise from pulse arrival time, vascular properties, etc.
```

## Clinical and Research Applications

**Wearable Health Monitoring:**
- Consumer smartwatches and fitness trackers
- Continuous heart rate monitoring
- Sleep tracking and activity assessment

**Clinical Monitoring:**
- Pulse oximetry (SpO₂ + Heart Rate)
- Perioperative monitoring
- Intensive care heart rate assessment

**Cardiovascular Assessment:**
- Pulse Wave Analysis (PWA)
- Arterial stiffness proxies (Pulse Arrival Time)
- Vascular aging index

**Autonomic Function:**
- HRV from PPG (PPG-HRV)
- Stress and recovery monitoring
- Mental workload assessment

**Remote Patient Monitoring:**
- Telehealth applications
- Home health tracking
- Chronic disease management

**Affective Computing:**
- Emotion recognition based on physiological signals
- User experience research
- Human-computer interaction

## PPG vs. ECG

**Advantages of PPG:**
- Non-invasive, no electrodes required
- Convenient for long-term monitoring
- Low cost, miniaturizable
- Ideal for wearable devices

**Disadvantages of PPG:**
- More susceptible to motion artifacts
- Lower signal quality during poor perfusion
- Pulse arrival time is delayed relative to the heartbeat
- Cannot evaluate cardiac electrophysiological activity

**HRV Comparison:**
- PPG-HRV is generally valid in time/frequency domains
- Slight differences may exist due to Pulse Transit Time Variability
- ECG is preferred for clinical HRV (if available)
- PPG is acceptable for research and consumer applications

## Interpretation Guidelines

**Heart Rate from PPG:**
- Interpreted the same as heart rate from ECG
- Slight delay (Pulse Arrival Time) is negligible for heart rate calculation
- Motion artifacts are more common: Validate with signal quality

**Pulse Amplitude:**
- Reflects peripheral perfusion
- Increase: Vasodilation, warmth
- Decrease: Vasoconstriction, cold, stress, poor contact

**Pulse Morphology:**
- Systolic peak: Cardiac ejection
- Dicrotic notch: Aortic valve closure, arterial compliance
- Aging/Stiffness: Dicrotic notch appears earlier and is more pronounced

## References

- Elgendi, M. (2012). On the analysis of fingertip photoplethysmogram signals. Current cardiology reviews, 8(1), 14-25.
- Elgendi, M., Norton, I., Brearley, M., Abbott, D., & Schuurmans, D. (2013). Systolic peak detection in acceleration photoplethysmograms measured from emergency responders in tropical conditions. PloS one, 8(10), e76585.
- Allen, J. (2007). Photoplethysmography and its application in clinical physiological measurement. Physiological measurement, 28(3), R1.
- Tamura, T., Maeda, Y., Sekine, M., & Yoshida, M. (2014). Wearable photoplethysmographic sensors—past and present. Electronics, 3(2), 282-302.