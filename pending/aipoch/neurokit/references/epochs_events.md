# Epochs and Event-Related Analysis

## Overview

Event-related analysis studies physiological responses that are time-locked to specific stimuli or events. NeuroKit2 provides tools for event detection, epoch creation, averaging, and event-related feature extraction across all signal types.

## Event Detection

### events_find()

Automatically detect events/triggers in a signal based on threshold crossings or changes.

```python
events = nk.events_find(event_channel, threshold=0.5, threshold_keep='above',
                        duration_min=1, inter_min=0)
```

**Parameters:**
- `threshold`: Detection threshold
- `threshold_keep`: `'above'` or `'below'` the threshold
- `duration_min`: Minimum duration of an event to be kept (in samples)
- `inter_min`: Minimum interval between events (in samples)

**Return Value:**
- A dictionary containing:
  - `'onset'`: Event start indices
  - `'offset'`: Event end indices (if applicable)
  - `'duration'`: Event durations
  - `'label'`: Event labels (if multiple event types exist)

**Common Use Cases:**

**TTL Triggers in Experiments:**
```python
# Trigger channel: 0V baseline, 5V pulse during events
events = nk.events_find(trigger_channel, threshold=2.5, threshold_keep='above')
```

**Button Presses:**
```python
# Detect when the button signal goes high
button_events = nk.events_find(button_signal, threshold=0.5, threshold_keep='above',
                               duration_min=10)  # Debouncing
```

**State Changes:**
```python
# Detect periods above/below a threshold
high_arousal = nk.events_find(eda_signal, threshold='auto', duration_min=100)
```

### events_plot()

Visualize event time points relative to the signal.

```python
nk.events_plot(events, signal)
```

**Displays:**
- Signal trace
- Event markers (vertical lines or shaded areas)
- Event labels

**Use Cases:**
- Verify accuracy of event detection
- Check temporal distribution of events
- Quality control before epoching

## Epoch Creation

### epochs_create()

Create data epochs (segments) around events for event-related analysis.

```python
epochs = nk.epochs_create(data, events, sampling_rate=1000,
                          epochs_start=-0.5, epochs_end=2.0,
                          event_labels=None, event_conditions=None,
                          baseline_correction=False)
```

**Parameters:**
- `data`: DataFrame containing signals or a single signal
- `events`: Event indices or a dictionary from `events_find()`
- `sampling_rate`: Signal sampling rate (Hz)
- `epochs_start`: Start time relative to the event (seconds, negative values indicate pre-event)
- `epochs_end`: End time relative to the event (seconds, positive values indicate post-event)
- `event_labels`: List of labels for each event (optional)
- `event_conditions`: List of experimental condition names for each event (optional)
- `baseline_correction`: If True, subtracts the baseline mean from each epoch

**Return Value:**
- A dictionary of DataFrames, one for each epoch
- Each DataFrame contains time data relative to the event (event onset at Index=0)
- Includes `'Label'` and `'Condition'` columns if labels and conditions are provided

**Typical Epoch Time Windows:**
- **Visual ERP**: -0.2 to 1.0 seconds (200 ms baseline, 1 s post-stimulus)
- **Cardiac Orienting Response**: -1.0 to 10 seconds (captures anticipation and response)
- **EMG Startle Response**: -0.1 to 0.5 seconds (brief response)
- **EDA SCR**: -1.0 to 10 seconds (1-3 s latency, slow recovery)

### Event Labels and Conditions

Organize events by type and experimental condition:

```python
# Example: Emotional picture experiment
event_times = [1000, 2500, 4200, 5800]  # Event onset times in samples
event_labels = ['trial1', 'trial2', 'trial3', 'trial4']
event_conditions = ['positive', 'negative', 'positive', 'neutral']

epochs = nk.epochs_create(signals, events=event_times, sampling_rate=1000,
                          epochs_start=-1, epochs_end=5,
                          event_labels=event_labels,
                          event_conditions=event_conditions)
```

**Accessing Epochs:**
```python
# Access epochs by number
epoch_1 = epochs['1']

# Filter by condition
positive_epochs = {k: v for k, v in epochs.items() if v['Condition'][0] == 'positive'}
```

### Baseline Correction

Subtract the pre-stimulus baseline from the epoch to isolate event-related changes:

**Automatic Correction (during epoch creation):**
```python
epochs = nk.epochs_create(data, events, sampling_rate=1000,
                          epochs_start=-0.5, epochs_end=2.0,
                          baseline_correction=True)  # Subtracts mean of the entire baseline segment
```

**Manual Correction (after epoch creation):**
```python
# Subtract the mean of the baseline period
baseline_start = -0.5  # seconds
baseline_end = 0.0     # seconds

for key, epoch in epochs.items():
    baseline_mask = (epoch.index >= baseline_start) & (epoch.index < baseline_end)
    baseline_mean = epoch[baseline_mask].mean()
    epochs[key] = epoch - baseline_mean
```

**When to perform baseline correction:**
- **ERPs**: Always required (to isolate event-related changes)
- **Cardiac/EDA**: Usually required (to remove inter-individual baseline differences)
- **Absolute Measurements**: Sometimes not required (e.g., when analyzing absolute amplitudes)

## Epoch Analysis and Visualization

### epochs_plot()

Visualize individual or averaged epochs.

```python
nk.epochs_plot(epochs, column='ECG_Rate', condition=None, show=True)
```

**Parameters:**
- `column`: Signal column to plot
- `condition`: Plot only specific conditions (optional)

**Displays:**
- Individual epoch traces (semi-transparent)
- Average across epochs (thick line)
- Optional: Shaded error area (SEM or SD)

**Use Cases:**
- Visualize event-related responses
- Compare different conditions
- Identify outlier epochs

### epochs_average()

Calculate the grand average and statistics across epochs.

```python
average_epochs = nk.epochs_average(epochs, output='dict')
```

**Parameters:**
- `output`: `'dict'` (default) or `'df'` (DataFrame)

**Return Value:**
- A dictionary or DataFrame containing:
  - `'Mean'`: Mean value at each time point across all epochs
  - `'SD'`: Standard deviation
  - `'SE'`: Standard error
  - `'CI_lower'`, `'CI_upper'`: 95% confidence intervals

**Use Cases:**
- Calculate Event-Related Potentials (ERPs)
- Grand average cardiac/EDA/EMG responses
- Group-level analysis

**Condition-Specific Averaging:**
```python
# Calculate averages separately by condition
positive_epochs = {k: v for k, v in epochs.items() if v['Condition'][0] == 'positive'}
negative_epochs = {k: v for k, v in epochs.items() if v['Condition'][0] == 'negative'}

avg_positive = nk.epochs_average(positive_epochs)
avg_negative = nk.epochs_average(negative_epochs)
```

### epochs_to_df()

Convert the dictionary of epochs into a unified DataFrame.

```python
epochs_df = nk.epochs_to_df(epochs)
```

**Return Value:**
- A single DataFrame containing all stacked epochs
- Includes `'Epoch'`, `'Time'`, `'Label'`, and `'Condition'` columns
- Facilitates statistical analysis and plotting with pandas/seaborn

**Use Cases:**
- Prepare data for mixed-effects models
- Plotting with seaborn/plotly
- Export to R or statistical software

### epochs_to_array()

Convert epochs into a 3D NumPy array.

```python
epochs_array = nk.epochs_to_array(epochs, column='ECG_Rate')
```

**Return Value:**
- 3D array: (n_epochs, n_timepoints, n_columns)

**Use Cases:**
- Machine learning input (epoch features)
- Custom array-based analysis
- Statistical tests on array data

## Signal-Specific Event-Related Analysis

NeuroKit2 provides specialized event-related analysis functions for each signal type:

### ECG Event-Related
```python
ecg_epochs = nk.epochs_create(ecg_signals, events, sampling_rate=1000,
                              epochs_start=-1, epochs_end=10)
ecg_results = nk.ecg_eventrelated(ecg_epochs)
```

**Metrics Calculated:**
- `ECG_Rate_Baseline`: Pre-event heart rate
- `ECG_Rate_Min/Max`: Min/max heart rate during the epoch
- `ECG_Phase_*`: Cardiac phase at event onset
- Frequency dynamics within different time windows

### EDA Event-Related
```python
eda_epochs = nk.epochs_create(eda_signals, events, sampling_rate=100,
                              epochs_start=-1, epochs_end=10)
eda_results = nk.eda_eventrelated(eda_epochs)
```

**Metrics Calculated:**
- `EDA_SCR`: Presence of SCR (binary)
- `SCR_Amplitude`: Maximum SCR amplitude
- `SCR_Latency`: Time to SCR onset (latency)
- `SCR_RiseTime`, `SCR_RecoveryTime`: Rise time, recovery time
- `EDA_Tonic`: Average tonic level

### RSP Event-Related
```python
rsp_epochs = nk.epochs_create(rsp_signals, events, sampling_rate=100,
                              epochs_start=-0.5, epochs_end=5)
rsp_results = nk.rsp_eventrelated(rsp_epochs)
```

**Metrics Calculated:**
- `RSP_Rate_Mean`: Mean respiration rate
- `RSP_Amplitude_Mean`: Mean respiration amplitude
- `RSP_Phase`: Respiration phase at event
- Frequency/amplitude dynamics

### EMG Event-Related
```python
emg_epochs = nk.epochs_create(emg_signals, events, sampling_rate=1000,
                              epochs_start=-0.1, epochs_end=1.0)
emg_results = nk.emg_eventrelated(emg_epochs)
```

**Metrics Calculated:**
- `EMG_Activation`: Presence of activation
- `EMG_Amplitude_Mean/Max`: Amplitude statistics
- `EMG_Onset_Latency`: Time to activation onset
- `EMG_Bursts`: Number of activation bursts

### EOG Event-Related
```python
eog_epochs = nk.epochs_create(eog_signals, events, sampling_rate=500,
                              epochs_start=-0.5, epochs_end=2.0)
eog_results = nk.eog_eventrelated(eog_epochs)
```

**Metrics Calculated:**
- `EOG_Blinks_N`: Number of blinks during the epoch
- `EOG_Rate_Mean`: Blink rate
- Temporal distribution of blinks

### PPG Event-Related
```python
ppg_epochs = nk.epochs_create(ppg_signals, events, sampling_rate=100,
                              epochs_start=-1, epochs_end=10)
ppg_results = nk.ppg_eventrelated(ppg_epochs)
```

**Metrics Calculated:**
- Similar to ECG: frequency dynamics, phase information

## Practical Workflows

### Complete Event-Related Analysis Pipeline

```python
import neurokit2 as nk

# 1. Process physiological signals
ecg_signals, ecg_info = nk.ecg_process(ecg, sampling_rate=1000)
eda_signals, eda_info = nk.eda_process(eda, sampling_rate=100)

# 2. Resample signals if necessary to align sampling rates
eda_signals_resampled = nk.signal_resample(eda_signals, sampling_rate=100,
                                           desired_sampling_rate=1000)

# 3. Combine signals into a single DataFrame
signals = pd.concat([ecg_signals, eda_signals_resampled], axis=1)

# 4. Detect events
events = nk.events_find(trigger_channel, threshold=0.5)

# 5. Add event labels and conditions
event_labels = ['trial1', 'trial2', 'trial3', ...]
event_conditions = ['condition_A', 'condition_B', 'condition_A', ...]

# 6. Create epochs
epochs = nk.epochs_create(signals, events, sampling_rate=1000,
                          epochs_start=-1.0, epochs_end=5.0,
                          event_labels=event_labels,
                          event_conditions=event_conditions,
                          baseline_correction=True)

# 7. Signal-specific event-related analysis
ecg_results = nk.ecg_eventrelated(epochs)
eda_results = nk.eda_eventrelated(epochs)

# 8. Merge results
results = pd.merge(ecg_results, eda_results, left_index=True, right_index=True)

# 9. Statistical analysis by condition
results['Condition'] = event_conditions
condition_comparison = results.groupby('Condition').mean()
```

### Handling Multiple Event Types

```python
# Use different markers for different event types
event_type1 = nk.events_find(trigger_ch1, threshold=0.5)
event_type2 = nk.events_find(trigger_ch2, threshold=0.5)

# Combine events and add labels
all_events = np.concatenate([event_type1['onset'], event_type2['onset']])
event_labels = ['type1'] * len(event_type1['onset']) + ['type2'] * len(event_type2['onset'])

# Sort by time
sort_idx = np.argsort(all_events)
all_events = all_events[sort_idx]
event_labels = [event_labels[i] for i in sort_idx]

# Create epochs
epochs = nk.epochs_create(signals, all_events, sampling_rate=1000,
                          epochs_start=-0.5, epochs_end=3.0,
                          event_labels=event_labels)

# Separate by type
type1_epochs = {k: v for k, v in epochs.items() if v['Label'][0] == 'type1'}
type2_epochs = {k: v for k, v in epochs.items() if v['Label'][0] == 'type2'}
```

### Quality Control and Artifact Rejection

```python
# Reject epochs with excessive noise or artifacts
clean_epochs = {}
for key, epoch in epochs.items():
    # Example: Reject if EDA amplitude is too high (motion artifact)
    if epoch['EDA_Phasic'].abs().max() < 5.0:  # Threshold
        # Example: Reject if heart rate change is too large (invalid data)
        if epoch['ECG_Rate'].max() - epoch['ECG_Rate'].min() < 50:
            clean_epochs[key] = epoch

print(f"Kept {len(clean_epochs)}/{len(epochs)} epochs")

# Analyze cleaned epochs
results = nk.ecg_eventrelated(clean_epochs)
```

## Statistical Considerations

### Sample Size
- **ERP/Averaging**: At least 20-30 trials per condition.
- **Single-trial Analysis**: Mixed-effects models can handle varying numbers of trials.
- **Group Comparisons**: Refer to pilot data for power analysis.

### Time Window Selection
- **A Priori Hypotheses**: Pre-register time windows based on literature.
- **Exploratory Analysis**: Use the entire epoch and correct for multiple comparisons.
- **Avoid**: Selecting time windows based on observed data (circular reasoning).

### Baseline Period
- Should exclude the influence of anticipatory effects.
- Duration should be sufficient to obtain a stable estimate (typically 500-1000 ms).
- For fast-dynamic signals (e.g., startle response), a shorter window (e.g., 100 ms) is sufficient.

### Condition Comparisons
- Within-subject designs use Repeated Measures ANOVA.
- Unbalanced data use mixed-effects models.
- Non-parametric comparisons use permutation tests.
- Correct for multiple comparisons (time points/signals).

## Common Applications

**Cognitive Psychology:**
- P300 ERP analysis
- Error-Related Negativity (ERN)
- Attentional blink
- Working memory load effects

**Affective Neuroscience:**
- Emotional picture viewing (EDA, HR, facial EMG)
- Fear conditioning (heart rate deceleration, SCR)
- Valence/Arousal dimensions

**Clinical Research:**
- Startle response (orbicularis oculi EMG)
- Orienting response (heart rate deceleration)
- Anticipation and prediction error

**Psychophysiology:**
- Cardiac defense response
- Orienting and defense reflexes
- Respiratory changes during emotional processing

**Human-Computer Interaction (HCI):**
- User engagement during events
- Surprise/violation of expectation
- Cognitive load during task events

## References

- Luck, S. J. (2014). An introduction to the event-related potential technique (2nd ed.). MIT press.
- Bradley, M. M., & Lang, P. J. (2000). Measuring emotion: Behavior, feeling, and physiology. In R. D. Lane & L. Nadel (Eds.), Cognitive neuroscience of emotion (pp. 242-276). Oxford University Press.
- Boucsein, W. (2012). Electrodermal activity (2nd ed.). Springer.
- Gratton, G., Coles, M. G., & Donchin, E. (1983). A new method for off-line removal of ocular artifact. Electroencephalography and clinical neurophysiology, 55(4), 468-484.