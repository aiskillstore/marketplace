# EEG Analysis and Microstates

## Overview

Analysis of EEG signal band power, channel quality assessment, source localization, and microstate identification. NeuroKit2 integrates with MNE-Python to provide a comprehensive EEG processing workflow.

## Core EEG Functions

### eeg_power()

Calculates power in standard frequency bands for specified channels.

```python
power = nk.eeg_power(eeg_data, sampling_rate=250, channels=['Fz', 'Cz', 'Pz'],
                     frequency_bands={'Delta': (0.5, 4),
                                     'Theta': (4, 8),
                                     'Alpha': (8, 13),
                                     'Beta': (13, 30),
                                     'Gamma': (30, 45)})
```

**Standard Frequency Bands:**
- **Delta (0.5-4 Hz)**: Deep sleep, unconscious processes
- **Theta (4-8 Hz)**: Drowsiness, meditation, memory encoding
- **Alpha (8-13 Hz)**: Relaxed wakefulness, eyes closed
- **Beta (13-30 Hz)**: Active thinking, focus, anxiety
- **Gamma (30-45 Hz)**: Cognitive processing, integration

**Return Value:**
- A DataFrame containing power values for each channel × band combination
- Column names: `Channel_Band` (e.g., 'Fz_Alpha', 'Cz_Beta')

**Use Cases:**
- Resting-state analysis
- Cognitive state classification
- Sleep staging
- Meditation or neurofeedback monitoring

### eeg_badchannels()

Identifies problematic channels using statistical outlier detection.

```python
bad_channels = nk.eeg_badchannels(eeg_data, sampling_rate=250, bad_threshold=2)
```

**Detection Methods:**
- Inter-channel standard deviation outliers
- Correlation with other channels
- Flatlines or dead channels
- Excessively noisy channels

**Parameters:**
- `bad_threshold`: Z-score threshold for outlier detection (default: 2)

**Return Value:**
- A list of names identified as problematic channels

**Use Cases:**
- Quality control before analysis
- Automated bad channel rejection
- Interpolation or exclusion decisions

### eeg_rereference()

Re-represents voltage measurements relative to different reference points.

```python
rereferenced = nk.eeg_rereference(eeg_data, reference='average', robust=False)
```

**Reference Types:**
- `'average'`: Average reference (mean of all electrodes)
- `'REST'`: Reference Electrode Standardization Technique
- `'bipolar'`: Differential recording between electrode pairs
- Specific channel name: Using a single electrode as reference

**Common References:**
- **Average reference**: Most common for high-density EEG
- **Linked mastoids**: Traditional clinical EEG
- **Vertex (Cz)**: Sometimes used in ERP studies
- **REST**: Approximate infinity reference

**Return Value:**
- Re-referenced EEG data

### eeg_gfp()

Calculates Global Field Power (GFP) — the standard deviation across all electrodes at each time point.

```python
gfp = nk.eeg_gfp(eeg_data)
```

**Interpretation:**
- High GFP: Strong and synchronized brain activity across regions
- Low GFP: Weak or desynchronized activity
- GFP Peaks: Points of topographic stability used for microstate detection

**Use Cases:**
- Identifying periods of stable topographic patterns
- Selecting time points for microstate analysis
- Event-Related Potential (ERP) visualization

### eeg_diss()

Measures topographic differences between electric field configurations.

```python
dissimilarity = nk.eeg_diss(eeg_data1, eeg_data2, method='gfp')
```

**Methods:**
- GFP-based: Normalized difference
- Spatial correlation
- Cosine distance

**Use Cases:**
- Comparing topographies across conditions
- Microstate transition analysis
- Template matching

## Source Localization

### eeg_source()

Performs source reconstruction to estimate brain-level activity from scalp recordings.

```python
sources = nk.eeg_source(eeg_data, method='sLORETA')
```

**Methods:**
- `'sLORETA'`: Standardized Low Resolution Electromagnetic Tomography
  - Zero localization error for point sources
  - Good spatial resolution
- `'MNE'`: Minimum Norm Estimate
  - Fast, mature
  - Biased towards superficial sources
- `'dSPM'`: Dynamic Statistical Parametric Mapping
  - Normalized MNE
- `'eLORETA'`: Exact LORETA
  - Improved localization accuracy

**Requirements:**
- Forward model (Lead field matrix)
- Co-registered electrode positions
- Head model (BEM or sphere)

**Return Value:**
- Estimates of source space activity

### eeg_source_extract()

Extracts activity from specific anatomical brain regions.

```python
regional_activity = nk.eeg_source_extract(sources, regions=['PFC', 'MTL', 'Parietal'])
```

**Region Options:**
- Standard atlases: Desikan-Killiany, Destrieux, AAL
- Custom ROIs
- Brodmann areas

**Return Value:**
- Time series for each region
- Mean or principal component across voxels

**Use Cases:**
- Region of Interest (ROI) analysis
- Functional connectivity
- Source-level statistics

## Microstate Analysis

Microstates are brief (80-120 ms) periods where the brain topography remains stable, representing coordinated neural networks. Usually, there are 4-7 classes of microstates (typically labeled A, B, C, D) with distinct functions.

### microstates_segment()

Identifies and extracts microstates using clustering algorithms.

```python
microstates = nk.microstates_segment(eeg_data, n_microstates=4, sampling_rate=250,
                                      method='kmod', normalize=True)
```

**Methods:**
- `'kmod'` (default): Modified k-means optimized for EEG topographies
  - Polarity-invariant clustering
  - Most common in microstate literature
- `'kmeans'`: Standard k-means clustering
- `'kmedoids'`: K-medoids (more robust to outliers)
- `'pca'`: Principal Component Analysis
- `'ica'`: Independent Component Analysis
- `'aahc'`: Atomize and Agglomerate Hierarchical Clustering

**Parameters:**
- `n_microstates`: Number of microstate classes (usually 4-7)
- `normalize`: Normalize topographies (recommended: True)
- `n_inits`: Number of random initializations (increase for stability)

**Return Value:**
- A dictionary containing:
  - `'maps'`: Microstate template topographies
  - `'labels'`: Microstate labels for each time point
  - `'gfp'`: Global Field Power
  - `'gev'`: Global Explained Variance

### microstates_findnumber()

Estimates the optimal number of microstates.

```python
optimal_k = nk.microstates_findnumber(eeg_data, show=True)
```

**Criteria:**
- **Global Explained Variance (GEV)**: Percentage of variance explained
  - Elbow method: Looking for the "knee" in the GEV curve
  - Usually reaching 70-80% GEV
- **Krzanowski-Lai (KL) criterion**: Statistical index balancing goodness-of-fit and parsimony
  - Maximum KL value indicates optimal k

**Typical Range:** 4-7 microstates
- 4 microstates: Classic A, B, C, D states
- 5-7 microstates: Finer-grained decomposition

### microstates_classify()

Reorders microstates based on anterior-posterior and left-right channel values.

```python
classified = nk.microstates_classify(microstates)
```

**Purpose:**
- Standardize microstate labels across subjects
- Match conventional A, B, C, D topographies:
  - **A**: Left-right orientation, parieto-occipital
  - **B**: Right-left orientation, fronto-temporal
  - **C**: Anterior-posterior orientation, fronto-central
  - **D**: Fronto-central, anterior-posterior orientation (inverse of C)

**Return Value:**
- Reordered microstate maps and labels

### microstates_clean()

Preprocesses EEG data for microstate extraction.

```python
cleaned_eeg = nk.microstates_clean(eeg_data, sampling_rate=250)
```

**Preprocessing Steps:**
- Band-pass filtering (usually 2-20 Hz)
- Artifact rejection
- Bad channel interpolation
- Re-referencing to average reference

**Rationale:**
- Microstates reflect large-scale network activity
- High and low frequency artifacts distort topographies

### microstates_peaks()

Identifies GFP peaks used for microstate analysis.

```python
peak_indices = nk.microstates_peaks(eeg_data, sampling_rate=250)
```

**Purpose:**
- Microstates are typically analyzed at GFP peaks
- Peaks represent moments of maximal and stable topographic activity
- Reduces computational load and noise sensitivity

**Return Value:**
- Indices of GFP local maxima

### microstates_static()

Calculates temporal properties of individual microstates.

```python
static_metrics = nk.microstates_static(microstates)
```

**Metrics:**
- **Duration (ms)**: Average time spent in each microstate
  - Typical values: 80-120 ms
  - Reflects stability and persistence
- **Occurrence (times/sec)**: Frequency of microstate appearance
  - Frequency of entering each state
- **Coverage (%)**: Percentage of total time spent in each microstate
  - Relative dominance
- **Global Explained Variance (GEV)**: Variance explained by each class
  - Template fit quality

**Return Value:**
- A DataFrame containing metrics for each microstate class

**Interpretation:**
- Duration changes: Network stability alterations
- Occurrence changes: State dynamics switching
- Coverage changes: Dominance of specific networks

### microstates_dynamic()

Analyzes transition patterns between microstates.

```python
dynamic_metrics = nk.microstates_dynamic(microstates)
```

**Metrics:**
- **Transition matrix**: Probability of transitioning from state i to state j
  - Reveals preferred sequences
- **Transition rate**: Overall transition frequency
  - Higher rate: faster switching
- **Entropy**: Randomness of transitions
  - High entropy: unpredictable switching
  - Low entropy: stereotypical sequences
- **Markov test**: Whether transitions have history dependence?

**Return Value:**
- A dictionary containing transition statistics

**Use Cases:**
- Identifying abnormal microstate sequences in clinical populations
- Network dynamics and flexibility
- State-dependent information processing

### microstates_plot()

Visualizes microstate topographies and time course.

```python
nk.microstates_plot(microstates, eeg_data)
```

**Displays:**
- Topographies for each microstate class
- GFP trace with microstate labels
- Transition map showing state sequences
- Statistical summary

## MNE Integration Utilities

### mne_data()

Accesses sample datasets from MNE-Python.

```python
raw = nk.mne_data(dataset='sample', directory=None)
```

**Available Datasets:**
- `'sample'`: Multimodal (MEG/EEG) example
- `'ssvep'`: Steady-State Visual Evoked Potentials
- `'eegbci'`: Motor imagery BCI dataset

### mne_to_df() / mne_to_dict()

Converts MNE objects to NeuroKit compatible formats.

```python
df = nk.mne_to_df(raw)
data_dict = nk.mne_to_dict(epochs)
```

**Use Cases:**
- Processing MNE-handled data in NeuroKit2
- Converting between analysis formats

### mne_channel_add() / mne_channel_extract()

Manages individual channels in MNE objects.

```python
# Extract specific channels
subset = nk.mne_channel_extract(raw, ['Fz', 'Cz', 'Pz'])

# Add derived channel
raw_with_eog = nk.mne_channel_add(raw, new_channel_data, ch_name='EOG')
```

### mne_crop()

Crops recordings by time or sample count.

```python
cropped = nk.mne_crop(raw, tmin=10, tmax=100)
```

### mne_templateMRI()

Provides template anatomy for source localization.

```python
subjects_dir = nk.mne_templateMRI()
```

**Use Cases:**
- Source analysis without individual MRI
- Group-level source localization
- fsaverage template brain

### eeg_simulate()

Generates synthetic EEG signals for testing.

```python
synthetic_eeg = nk.eeg_simulate(duration=60, sampling_rate=250, n_channels=32)
```

## Practical Considerations

### Sampling Rate Recommendations
- **Minimum**: 100 Hz (for basic power analysis)
- **Standard**: 250-500 Hz (for most applications)
- **High-resolution**: 1000+ Hz (for detailed temporal dynamics)

### Recording Duration
- **Power analysis**: ≥2 minutes for stable estimates
- **Microstates**: ≥2-5 minutes, longer is better
- **Resting-state**: Usually 3-10 minutes
- **Event-related**: Depends on trial count (≥30 trials per condition)

### Artifact Management
- **Eye blinks**: Remove using ICA or regression
- **Muscle artifacts**: High-pass filter (≥1 Hz) or manual rejection
- **Bad channels**: Detect and interpolate before analysis
- **Line noise**: 50/60 Hz notch filter

### Best Practices

**Power Analysis:**
```python
# 1. Clean data
cleaned = nk.signal_filter(eeg_data, sampling_rate=250, lowcut=0.5, highcut=45)

# 2. Identify and interpolate bad channels
bad = nk.eeg_badchannels(cleaned, sampling_rate=250)
# Use MNE to interpolate bad channels

# 3. Re-reference
rereferenced = nk.eeg_rereference(cleaned, reference='average')

# 4. Calculate power
power = nk.eeg_power(rereferenced, sampling_rate=250, channels=channel_list)
```

**Microstate Workflow:**
```python
# 1. Preprocessing
cleaned = nk.microstates_clean(eeg_data, sampling_rate=250)

# 2. Determine optimal number of states
optimal_k = nk.microstates_findnumber(cleaned, show=True)

# 3. Segment microstates
microstates = nk.microstates_segment(cleaned, n_microstates=optimal_k,
                                     sampling_rate=250, method='kmod')

# 4. Classify to standard labels
microstates = nk.microstates_classify(microstates)

# 5. Calculate temporal metrics
static = nk.microstates_static(microstates)
dynamic = nk.microstates_dynamic(microstates)

# 6. Visualization
nk.microstates_plot(microstates, cleaned)
```

## Clinical and Research Applications

**Cognitive Neuroscience:**
- Attention, working memory, executive function
- Language processing
- Perception

**Clinical Populations:**
- Epilepsy: Seizure detection, localization
- Alzheimer's: EEG slowing, microstate changes
- Schizophrenia: Microstate alterations, especially state C
- ADHD: Increased theta/beta ratio
- Depression: Frontal alpha asymmetry

**Consciousness Research:**
- Anesthesia monitoring
- Disorders of consciousness
- Sleep staging

**Neurofeedback:**
- Real-time band training
- Enhancing Alpha for relaxation
- Enhancing Beta for focus

## References

- Michel, C. M., & Koenig, T. (2018). EEG microstates as a tool for studying the temporal dynamics of whole-brain neuronal networks: A review. Neuroimage, 180, 577-593.
- Pascual-Marqui, R. D., Michel, C. M., & Lehmann, D. (1995). Segmentation of brain electrical activity into microstates: model estimation and validation. IEEE Transactions on Biomedical Engineering, 42(7), 658-665.
- Gramfort, A., Luessi, M., Larson, E., Engemann, D. A., Strohmeier, D., Brodbeck, C., ... & Hämäläinen, M. (2013). MEG and EEG data analysis with MNE-Python. Frontiers in neuroscience, 7, 267.