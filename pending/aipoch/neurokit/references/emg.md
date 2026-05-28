# Electromyography (EMG) Analysis

## Overview

Electromyography (EMG) measures the electrical activity produced by skeletal muscles during contraction. EMG analysis in NeuroKit2 primarily focuses on amplitude estimation, muscle activation detection, and temporal dynamics for research in psychophysiology and motor control.

## Main Processing Pipeline

### emg_process()

Automated EMG signal processing pipeline.

```python
signals, info = nk.emg_process(emg_signal, sampling_rate=1000)
```

**Pipeline Steps:**
1. Signal cleaning (high-pass filtering, detrending)
2. Amplitude envelope extraction
3. Muscle activation detection
4. Identification of activation Onsets and Offsets

**Return Values:**
- `signals`: A DataFrame containing:
  - `EMG_Clean`: Filtered EMG signal
  - `EMG_Amplitude`: Linear envelope (smoothed rectified signal)
  - `EMG_Activity`: Binary activation indicator (0/1)
  - `EMG_Onsets`: Activation onset markers
  - `EMG_Offsets`: Activation offset markers
- `info`: A dictionary containing activation parameters

**Typical Workflow:**
- Process raw EMG → Extract amplitude → Detect activation → Analyze features

## Preprocessing Functions

### emg_clean()

Applies filters to remove noise in preparation for amplitude extraction.

```python
cleaned_emg = nk.emg_clean(emg_signal, sampling_rate=1000)
```

**Filtering Method (BioSPPy method):**
- Fourth-order Butterworth high-pass filter (100 Hz)
- Removal of low-frequency motion artifacts and baseline wander
- Removal of DC offset
- Signal detrending

**Basic Principles:**
- EMG frequency content: 20-500 Hz (dominant frequencies: 50-150 Hz)
- 100 Hz high-pass filtering isolates muscle activity
- Removal of ECG interference (especially for trunk muscles)
- Removal of motion artifacts (<20 Hz)

**EMG Signal Characteristics:**
- Random, zero-mean oscillations during contraction
- Higher amplitude = stronger contraction
- Raw EMG: contains both positive and negative deflections

## Feature Extraction

### emg_amplitude()

Calculates the linear envelope representing muscle contraction intensity.

```python
amplitude = nk.emg_amplitude(cleaned_emg, sampling_rate=1000)
```

**Method:**
1. Full-wave rectification (taking the absolute value)
2. Low-pass filtering (smoothing the envelope)
3. Downsampling (optional)

**Linear Envelope:**
- A smooth curve following the EMG amplitude modulation
- Represents muscle force/activation level
- Suitable for further analysis (activation detection, integration)

**Typical Smoothing:**
- Low-pass filter: 10-20 Hz cutoff frequency
- Moving average: 50-200 ms window
- Balance point: Response speed vs. smoothness

## Activation Detection

### emg_activation()

Detects muscle activation periods (onsets and offsets).

```python
activity, info = nk.emg_activation(emg_amplitude, sampling_rate=1000, method='threshold',
                                   threshold='auto', duration_min=0.05)
```

**Methods:**

**1. Threshold-based (Default):**
```python
activity = nk.emg_activation(amplitude, method='threshold', threshold='auto')
```
- Compares amplitude to a threshold
- `threshold='auto'`: Automatically calculated based on signal statistics (e.g., mean + 1 SD)
- `threshold=0.1`: Manually set absolute threshold
- Simple, fast, and widely used

**2. Gaussian Mixture Model (GMM):**
```python
activity = nk.emg_activation(amplitude, method='mixture', n_clusters=2)
```
- Unsupervised clustering: Activation vs. Rest
- Adaptive to signal characteristics
- More robust to fluctuating baselines

**3. Changepoint Detection:**
```python
activity = nk.emg_activation(amplitude, method='changepoint')
```
- Detects abrupt changes in signal properties
- Identifies activation/deactivation points
- Suitable for complex temporal patterns

**4. Bimodal Method (Silva et al., 2013):**
```python
activity = nk.emg_activation(amplitude, method='bimodal')
```
- Tests for a bimodal distribution (activation vs. rest)
- Determines the optimal separation threshold
- Statistically grounded

**Key Parameters:**
- `duration_min`: Minimum activation duration (seconds)
  - Filters out brief false activations
  - Typical values: 50-100 ms
- `threshold`: Activation threshold (depends on the specific method)

**Return Values:**
- `activity`: Binary array (0 = rest, 1 = activation)
- `info`: Dictionary containing onset/offset indices

**Activation Metrics:**
- **Onset**: Transition from rest to activation
- **Offset**: Transition from activation to rest
- **Duration**: Time between onset and offset
- **Burst**: A single continuous activation period

## Analysis Functions

### emg_analyze()

Automatically selects between event-related or interval-related analysis.

```python
analysis = nk.emg_analyze(signals, sampling_rate=1000)
```

**Mode Selection:**
- Duration < 10 seconds → Event-related
- Duration ≥ 10 seconds → Interval-related

### emg_eventrelated()

Analyzes EMG responses to specific events/stimuli.

```python
results = nk.emg_eventrelated(epochs)
```

**Calculated Metrics (per epoch):**
- `EMG_Activation`: Presence of activation (binary)
- `EMG_Amplitude_Mean`: Average amplitude during the epoch
- `EMG_Amplitude_Max`: Peak amplitude
- `EMG_Bursts`: Number of activation bursts
- `EMG_Onset_Latency`: Time from event to first activation (if applicable)

**Application Scenarios:**
- Startle response (Orbicularis oculi EMG)
- Facial EMG during emotional stimuli (Corrugator supercilii, Zygomaticus major)
- Motor response latency
- Muscle reactivity paradigms

### emg_intervalrelated()

Analyzes longer EMG recordings.

```python
results = nk.emg_intervalrelated(signals, sampling_rate=1000)
```

**Calculated Metrics:**
- `EMG_Bursts_N`: Total number of activation bursts
- `EMG_Amplitude_Mean`: Average amplitude across the interval
- `EMG_Activation_Duration`: Total time spent in activation
- `EMG_Rest_Duration`: Total time spent at rest

**Application Scenarios:**
- Resting muscle tension assessment
- Chronic pain or stress-related muscle activity
- Fatigue monitoring during sustained tasks
- Postural muscle assessment

## Simulation and Visualization

### emg_simulate()

Generates synthetic EMG signals for testing.

```python
synthetic_emg = nk.emg_simulate(duration=10, sampling_rate=1000, burst_number=3,
                                noise=0.1, random_state=42)
```

**Parameters:**
- `burst_number`: Number of activation bursts to include
- `noise`: Background noise level
- `random_state`: Random seed for reproducibility

**Generated Features:**
- Simulated random EMG oscillations during bursts
- Realistic frequency content
- Variable burst timing and amplitude

**Application Scenarios:**
- Algorithm validation
- Tuning detection parameters
- Educational demonstrations

### emg_plot()

Visualizes processed EMG signals.

```python
nk.emg_plot(signals, info, static=True)
```

**Displayed Content:**
- Raw and cleaned EMG signals
- Amplitude envelope
- Detected activation periods
- Onset/Offset markers

**Interactive Mode:** Set `static=False` to use Plotly for visualization

## Practical Considerations

### Sampling Rate Recommendations
- **Minimum**: 500 Hz (Nyquist frequency for 250 Hz upper limit)
- **Standard**: 1000 Hz (most research applications)
- **High Resolution**: 2000-4000 Hz (detailed motor unit studies)
- **Surface EMG (sEMG)**: Typically 1000-2000 Hz
- **Intramuscular EMG (iEMG)**: 10,000+ Hz for single motor units

### Recording Duration
- **Event-related**: Depends on paradigm (e.g., 2-5 seconds per trial)
- **Sustained contraction**: Seconds to minutes
- **Fatigue studies**: Minutes to hours
- **Chronic monitoring**: Days (wearable EMG)

### Electrode Placement

**Surface EMG (Most Common):**
- Bipolar configuration (two electrodes placed on the muscle belly)
- Reference/ground electrode placed on an electrically neutral site (bony area)
- Skin preparation: Cleaning, abrasion, reducing impedance
- Inter-electrode distance: 10-20 mm (SENIAM standard)

**Specific Muscle Guidelines:**
- Follow SENIAM (Surface Electromyography for the Non-Invasive Assessment of Muscles) recommendations
- Palpate the muscle during contraction to locate the muscle belly
- Align electrodes with the direction of muscle fibers

**Common Muscles in Psychophysiology:**
- **Corrugator supercilii**: Frowning, negative emotions (above eyebrows)
- **Zygomaticus major**: Smiling, positive emotions (cheeks)
- **Orbicularis oculi**: Startle response, fear (around eyes)
- **Masseter**: Jaw clenching, stress (jaw muscle)
- **Trapezius**: Shoulder tension, stress (upper back)
- **Frontalis**: Forehead tension, surprise

### Signal Quality Issues

**ECG Contamination:**
- Common in trunk and proximal muscles
- High-pass filtering (>100 Hz) is often sufficient
- If it persists: Use template subtraction, Independent Component Analysis (ICA)

**Motion Artifacts:**
- Low-frequency interference
- Electrode cable movement
- Secure electrodes and minimize cable sway

**Electrode Issues:**
- Poor contact: High impedance, low amplitude
- Sweating: Gradual amplitude increase, instability
- Hair: Clean or shave the area

**Cross-talk:**
- Activity from adjacent muscles leaking into the recording
- Careful electrode placement
- Reduce inter-electrode distance

### Best Practices

**Standard Workflow:**
```python
# 1. Clean signal (high-pass filter, detrend)
cleaned = nk.emg_clean(emg_raw, sampling_rate=1000)

# 2. Extract amplitude envelope
amplitude = nk.emg_amplitude(cleaned, sampling_rate=1000)

# 3. Detect activation periods
activity, info = nk.emg_activation(amplitude, sampling_rate=1000,
                                   method='threshold', threshold='auto')

# 4. Integrated processing (alternative)
signals, info = nk.emg_process(emg_raw, sampling_rate=1000)

# 5. Analysis
analysis = nk.emg_analyze(signals, sampling_rate=1000)
```

**Normalization:**
```python
# Maximum Voluntary Contraction (MVC) normalization
mvc_amplitude = np.max(mvc_emg_amplitude)  # From a separate MVC trial
normalized_emg = (amplitude / mvc_amplitude) * 100  # Expressed as % MVC

# Commonly used in ergonomics and exercise physiology
# Allows comparison across individuals and sessions
```

## Clinical and Research Applications

**Psychophysiology:**
- **Facial EMG**: Emotional valence (smiling vs. frowning)
- **Startle Response**: Fear, surprise, defensive reactivity
- **Stress**: Chronic muscle tension (Trapezius, Masseter)

**Motor Control and Rehabilitation:**
- Gait analysis
- Movement disorders (tremors, dystonia)
- Stroke recovery (muscle reactivation)
- Prosthetic control (myoelectric control)

**Ergonomics and Occupational Health:**
- Work-related musculoskeletal disorders
- Postural assessment
- Repetitive strain risk

**Sports Science:**
- Muscle activation patterns during exercise
- Fatigue assessment (median frequency shift)
- Training optimization

**Biofeedback:**
- Relaxation training (reducing muscle tension)
- Neuromuscular re-education
- Chronic pain management

**Sleep Medicine:**
- Mentalis EMG for detecting REM atonia
- Periodic limb movements
- Bruxism (teeth grinding)

## Advanced EMG Analysis (Beyond Basic NeuroKit2)

**Frequency Domain Analysis:**
- Median frequency shift during fatigue
- Power spectrum analysis
- Requires longer segments (≥1 second per analysis window)

**Motor Unit Identification:**
- Intramuscular EMG
- Spike detection and sorting
- Firing rate analysis
- Requires high sampling rates (10+ kHz)

**Muscle Coordination:**
- Co-contraction index
- Synergy analysis
- Multi-muscle integration

## Interpretation Guidelines

**Amplitude (Linear Envelope):**
- Higher amplitude ≈ stronger contraction (not perfectly linear)
- Relationship with force: Sigmoidal, influenced by many factors
- Within-subject comparisons are most reliable

**Activation Thresholds:**
- Auto-threshold: Convenient, but requires manual visual verification
- Manual threshold: May be needed for non-standard muscles
- Resting baseline: Should be close to zero (if not, check electrodes)

**Burst Characteristics:**
- **Phasic**: Short bursts (startle, rapid movements)
- **Tonic**: Sustained activation (posture maintenance, continuous grip)
- **Rhythmic**: Repetitive bursts (tremor, walking)

## References

- Fridlund, A. J., & Cacioppo, J. T. (1986). Guidelines for human electromyographic research. Psychophysiology, 23(5), 567-589.
- Hermens, H. J., Freriks, B., Disselhorst-Klug, C., & Rau, G. (2000). Development of recommendations for SEMG sensors and sensor placement procedures. Journal of electromyography and Kinesiology, 10(5), 361-374.
- Silva, H., Scherer, R., Sousa, J., & Londral, A. (2013). Towards improving the usability of electromyographic interfaces. Journal of Oral Rehabilitation, 40(6), 456-465.
- Tassinary, L. G., Cacioppo, J. T., & Vanman, E. J. (2017). The skeletomotor system: Surface electromyography. In Handbook of psychophysiology (pp. 267-299). Cambridge University Press.