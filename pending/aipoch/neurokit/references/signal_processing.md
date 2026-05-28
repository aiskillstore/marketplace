# General Signal Processing

## Overview

NeuroKit2 provides comprehensive signal processing tools suitable for any time-series data. These functions support filtering, transformation, peak detection, decomposition, and analysis operations, applicable to all signal types.

## Preprocessing Functions

### signal_filter()

Apply frequency-domain filtering to remove noise or isolate specific frequency bands.

```python
filtered = nk.signal_filter(signal, sampling_rate=1000, lowcut=None, highcut=None,
                            method='butterworth', order=5)
```

**Filter Types (via lowcut/highcut combinations):**

**Lowpass** (highcut only):
```python
lowpass = nk.signal_filter(signal, sampling_rate=1000, highcut=50)
```
- Removes frequencies higher than highcut
- Smoothes the signal, removing high-frequency noise

**Highpass** (lowcut only):
```python
highpass = nk.signal_filter(signal, sampling_rate=1000, lowcut=0.5)
```
- Removes frequencies lower than lowcut
- Removes baseline wander and DC offset

**Bandpass** (both lowcut and highcut):
```python
bandpass = nk.signal_filter(signal, sampling_rate=1000, lowcut=0.5, highcut=50)
```
- Retains frequencies between lowcut and highcut
- Isolates specific frequency bands

**Bandstop/Notch** (powerline removal):
```python
notch = nk.signal_filter(signal, sampling_rate=1000, method='powerline', powerline=50)
```
- Removes 50 or 60 Hz powerline noise
- Narrowband notch filter

**Methods:**
- `'butterworth'` (default): Smooth frequency response, flat passband
- `'bessel'`: Linear phase, minimal ringing effect
- `'chebyshev1'`: Steeper roll-off, ripples in passband
- `'chebyshev2'`: Steeper roll-off, ripples in stopband
- `'elliptic'`: Steepest roll-off, ripples in both bands
- `'powerline'`: Notch filter targeted at 50/60 Hz

**Order parameter:**
- High order: Steeper transition, more ringing effects
- Low order: Gentler transition, fewer ringing effects
- Typical values: 2-5 for physiological signals

### signal_sanitize()

Remove invalid values (NaN, inf) and optionally perform interpolation.

```python
clean_signal = nk.signal_sanitize(signal, interpolate=True)
```

**Use Cases:**
- Handling missing data points
- Removing artifacts marked as NaN
- Preparing signals for algorithms that require continuous data

### signal_resample()

Change the signal sampling rate (upsampling or downsampling).

```python
resampled = nk.signal_resample(signal, sampling_rate=1000, desired_sampling_rate=500,
                               method='interpolation')
```

**Methods:**
- `'interpolation'`: Cubic spline interpolation
- `'FFT'`: Frequency-domain resampling
- `'poly'`: Polyphase filtering (best for downsampling)

**Use Cases:**
- Matching sampling rates of multimodal recordings
- Reducing data size (downsampling)
- Increasing temporal resolution (upsampling)

### signal_fillmissing()

Interpolate missing or invalid data points.

```python
filled = nk.signal_fillmissing(signal, method='linear')
```

**Methods:**
- `'linear'`: Linear interpolation
- `'nearest'`: Nearest neighbor interpolation
- `'pad'`: Forward/backward fill
- `'cubic'`: Cubic spline
- `'polynomial'`: Polynomial fitting

## Transformation Functions

### signal_detrend()

Remove slow trends from the signal.

```python
detrended = nk.signal_detrend(signal, method='polynomial', order=1)
```

**Methods:**
- `'polynomial'`: Fit and subtract a polynomial (order 1 = linear)
- `'loess'`: Locally weighted regression
- `'tarvainen2002'`: Smoothness priors detrending method

**Use Cases:**
- Removing baseline wander
- Stabilizing the mean before analysis
- Preparing for algorithms that assume stationarity

### signal_decompose()

Decompose a signal into its constituent components.

```python
components = nk.signal_decompose(signal, sampling_rate=1000, method='emd')
```

**Methods:**

**Empirical Mode Decomposition (EMD):**
```python
components = nk.signal_decompose(signal, sampling_rate=1000, method='emd')
```
- Data-adaptive decomposition into Intrinsic Mode Functions (IMFs)
- Each IMF represents different frequency content (from high to low)
- No predefined basis functions required

**Singular Spectrum Analysis (SSA):**
```python
components = nk.signal_decompose(signal, method='ssa')
```
- Decomposes into trend, oscillations, and noise
- Based on eigenvalue decomposition of the trajectory matrix

**Wavelet decomposition:**
- Time-frequency representation
- Localized in both time and frequency

**Returns:**
- Dictionary containing component signals
- Trends, oscillatory components, residuals

**Use Cases:**
- Isolating physiological rhythms
- Separating signal from noise
- Multi-scale analysis

### signal_recompose()

Reconstruct a signal from decomposed components.

```python
reconstructed = nk.signal_recompose(components, indices=[1, 2, 3])
```

**Use Cases:**
- Selective reconstruction after decomposition
- Removing specific IMFs or components
- Adaptive filtering

### signal_binarize()

Convert a continuous signal to binary (0/1) based on a threshold.

```python
binary = nk.signal_binarize(signal, method='threshold', threshold=0.5)
```

**Methods:**
- `'threshold'`: Simple threshold
- `'median'`: Based on the median
- `'mean'`: Based on the mean
- `'quantile'`: Based on quantiles

**Use Cases:**
- Detecting events from continuous signals
- Trigger pulse extraction
- State classification

### signal_distort()

Add controlled noise or artifacts for testing.

```python
distorted = nk.signal_distort(signal, sampling_rate=1000, noise_amplitude=0.1,
                              noise_frequency=50, artifacts_amplitude=0.5)
```

**Parameters:**
- `noise_amplitude`: Gaussian noise level
- `noise_frequency`: Sinusoidal interference (e.g., powerline)
- `artifacts_amplitude`: Random spike artifacts
- `artifacts_number`: Number of artifacts to add

**Use Cases:**
- Algorithm robustness testing
- Evaluation of preprocessing methods
- Simulation of real-world data

### signal_interpolate()

Interpolate the signal at new time points or fill gaps.

```python
interpolated = nk.signal_interpolate(x_values, y_values, x_new=None, method='quadratic')
```

**Methods:**
- `'linear'`, `'quadratic'`, `'cubic'`: Polynomial interpolation
- `'nearest'`: Nearest neighbor interpolation
- `'monotone_cubic'`: Preserves monotonicity

**Use Cases:**
- Converting irregular samples to a regular grid
- Upsampling for visualization
- Aligning signals with different time bases

### signal_merge()

Merge multiple signals with different sampling rates.

```python
merged = nk.signal_merge(signal1, signal2, time1=None, time2=None, sampling_rate=None)
```

**Use Cases:**
- Multimodal signal integration
- Combining data from different devices
- Synchronization based on timestamps

### signal_flatline()

Identify periods where the signal is constant (artifacts or sensor failure).

```python
flatline_mask = nk.signal_flatline(signal, duration=5.0, sampling_rate=1000)
```

**Returns:**
- Binary mask, True indicates flatline periods
- Duration threshold prevents false positives from normal stability

### signal_noise()

Add various types of noise to a signal.

```python
noisy = nk.signal_noise(signal, sampling_rate=1000, noise_type='gaussian',
                        amplitude=0.1)
```

**Noise Types:**
- `'gaussian'`: White noise
- `'pink'`: 1/f noise (common in physiological signals)
- `'brown'`: Brownian noise (random walk)
- `'powerline'`: Sinusoidal interference (50/60 Hz)

### signal_surrogate()

Generate surrogate signals that preserve certain properties.

```python
surrogate = nk.signal_surrogate(signal, method='IAAFT')
```

**Methods:**
- `'IAAFT'`: Iterative Amplitude Adjusted Fourier Transform
  - Preserves amplitude distribution and power spectrum
- `'random_shuffle'`: Random permutation (null hypothesis testing)

**Use Cases:**
- Nonlinearity testing
- Null hypothesis generation for statistical tests

## Peak Detection and Correction

### signal_findpeaks()

Detect local maxima (peaks) in a signal.

```python
peaks_dict = nk.signal_findpeaks(signal, height_min=None, height_max=None,
                                 relative_height_min=None, relative_height_max=None)
```

**Key Parameters:**
- `height_min/max`: Absolute amplitude thresholds
- `relative_height_min/max`: Thresholds relative to signal range (0-1)
- `threshold`: Minimum prominence
- `distance`: Minimum number of samples between peaks

**Returns:**
- Dictionary containing:
  - `'Peaks'`: Peak indices
  - `'Height'`: Peak amplitudes
  - `'Distance'`: Inter-peak distances

**Use Cases:**
- General peak detection for any signal
- R-waves, respiratory peaks, pulse peaks
- Event detection

### signal_fixpeaks()

Correct detected artifacts and abnormal peaks.

```python
corrected = nk.signal_fixpeaks(peaks, sampling_rate=1000, iterative=True,
                               method='Kubios', interval_min=None, interval_max=None)
```

**Methods:**
- `'Kubios'`: Kubios HRV software method (default)
- `'Malik1996'`: Task Force Standards (1996)
- `'Kamath1993'`: Kamath method

**Corrections:**
- Removing physiologically implausible intervals
- Interpolating missing peaks
- Removing redundant detections (duplicates)

**Use Cases:**
- Artifact correction in R-R intervals
- Improving HRV analysis quality
- Respiratory or pulse peak correction

## Analysis Functions

### signal_rate()

Calculate instantaneous rate based on event occurrences (peaks).

```python
rate = nk.signal_rate(peaks, sampling_rate=1000, desired_length=None)
```

**Method:**
- Calculates inter-event intervals
- Converts to events per minute
- Interpolates to match the desired length

**Use Cases:**
- Heart rate from R-waves
- Respiration rate from respiratory peaks
- Frequency of any periodic event

### signal_period()

Find the dominant period/frequency in a signal.

```python
period = nk.signal_period(signal, sampling_rate=1000, method='autocorrelation',
                          show=False)
```

**Methods:**
- `'autocorrelation'`: Peak in the autocorrelation function
- `'powerspectraldensity'`: Peak in the spectrum

**Returns:**
- Period in samples or seconds
- Frequency in Hz (1/period)

**Use Cases:**
- Detecting dominant rhythms
- Estimating fundamental frequency
- Respiration rate, heart rate estimation

### signal_phase()

Calculate the instantaneous phase of a signal.

```python
phase = nk.signal_phase(signal, method='hilbert')
```

**Methods:**
- `'hilbert'`: Hilbert transform (analytic signal)
- `'wavelet'`: Wavelet-based phase

**Returns:**
- Phase in radians (-π to π) or 0 to 1 (normalized)

**Use Cases:**
- Phase-locked analysis
- Synchrony measurements
- Phase-amplitude coupling

### signal_psd()

Calculate Power Spectral Density (PSD).

```python
psd, freqs = nk.signal_psd(signal, sampling_rate=1000, method='welch',
                           max_frequency=None, show=False)
```

**Methods:**
- `'welch'`: Welch's periodogram (windowed FFT, default)
- `'multitapers'`: Multi-taper method (superior spectral estimation)
- `'lomb'`: Lomb-Scargle method (for unevenly sampled data)
- `'burg'`: Autoregressive method (parametric)

**Returns:**
- `psd`: Power at each frequency (units²/Hz)
- `freqs`: Frequency bins (Hz)

**Use Cases:**
- Frequency component analysis
- HRV frequency domain analysis
- Spectral feature extraction

### signal_power()

Calculate power in specific frequency bands.

```python
power_dict = nk.signal_power(signal, sampling_rate=1000, frequency_bands={
    'VLF': (0.003, 0.04),
    'LF': (0.04, 0.15),
    'HF': (0.15, 0.4)
}, method='welch')
```

**Returns:**
- Dictionary with absolute and relative power for each band
- Peak frequencies

**Use Cases:**
- HRV frequency analysis
- EEG band power
- Rhythm quantification

### signal_autocor()

Calculate the autocorrelation function.

```python
autocorr = nk.signal_autocor(signal, lag=1000, show=False)
```

**Interpretation:**
- High autocorrelation at a lag: Signal repeats every `lag` samples
- Periodic signals: Peaks at multiples of the period
- Random signals: Decays quickly to zero

**Use Cases:**
- Detecting periodicity
- Assessing temporal structure
- Signal memory analysis

### signal_zerocrossings()

Calculate the zero-crossing rate (sign changes).

```python
n_crossings = nk.signal_zerocrossings(signal)
```

**Interpretation:**
- More crossings: More high-frequency components
- Related to dominant frequency (rough estimate)

**Use Cases:**
- Simple frequency estimation
- Signal regularity assessment

### signal_changepoints()

Detect abrupt changes in signal characteristics (mean, variance).

```python
changepoints = nk.signal_changepoints(signal, penalty=10, method='pelt', show=False)
```

**Methods:**
- `'pelt'`: Pruned Exact Linear Time (fast, exact)
- `'binseg'`: Binary segmentation (faster, approximate)

**Parameters:**
- `penalty`: Controls sensitivity (higher = fewer changepoints)

**Returns:**
- Indices of detected changepoints
- Segments between changepoints

**Use Cases:**
- Segmenting signals into different states
- Detecting transitions (e.g., sleep stages, arousal states)
- Automatic epoch definition

### signal_synchrony()

Evaluate synchrony between two signals.

```python
sync = nk.signal_synchrony(signal1, signal2, method='correlation')
```

**Methods:**
- `'correlation'`: Pearson correlation
- `'coherence'`: Frequency-domain coherence
- `'mutual_information'`: Information theory measure
- `'phase'`: Phase locking value

**Use Cases:**
- Heart-brain coupling
- Inter-brain synchrony
- Multi-channel coordination

### signal_smooth()

Apply smoothing to reduce noise.

```python
smoothed = nk.signal_smooth(signal, method='convolution', kernel='boxzen', size=10)
```

**Methods:**
- `'convolution'`: Apply a kernel (boxcar, gaussian, etc.)
- `'median'`: Median filtering (robust to outliers)
- `'savgol'`: Savitzky-Golay filter (preserves peaks)
- `'loess'`: Locally weighted regression

**Kernel Types (for convolution):**
- `'boxcar'`: Simple moving average
- `'gaussian'`: Gaussian weighted average
- `'hann'`, `'hamming'`, `'blackman'`: Window functions

**Use Cases:**
- Noise reduction
- Trend extraction
- Enhancing visualization

### signal_timefrequency()

Time-frequency representation (spectrogram).

```python
tf, time, freq = nk.signal_timefrequency(signal, sampling_rate=1000, method='stft',
                                        max_frequency=50, show=False)
```

**Methods:**
- `'stft'`: Short-Time Fourier Transform
- `'cwt'`: Continuous Wavelet Transform

**Returns:**
- `tf`: Time-frequency matrix (power at each time-frequency point)
- `time`: Time bins
- `freq`: Frequency bins

**Use Cases:**
- Non-stationary signal analysis
- Time-varying frequency components
- EEG/MEG time-frequency analysis

## Simulation

### signal_simulate()

Generate various synthetic signals for testing.

```python
signal = nk.signal_simulate(duration=10, sampling_rate=1000, frequency=[5, 10],
                            amplitude=[1.0, 0.5], noise=0.1)
```

**Signal Types:**
- Sinusoidal oscillations (specify frequency)
- Multi-frequency components
- Gaussian noise
- Combined signals

**Use Cases:**
- Algorithm testing
- Method validation
- Educational demonstrations

## Visualization

### signal_plot()

Visualize signals and optional markers.

```python
nk.signal_plot(signal, sampling_rate=1000, peaks=None, show=True)
```

**Features:**
- Time axis in seconds
- Peak markers
- Multi-subplot plotting for signal arrays

## Practical Tips

**Choosing filter parameters:**
- **Lowcut**: Set below the lowest frequency of interest
- **Highcut**: Set above the highest frequency of interest
- **Order**: Start with 2-5; increase if transitions are too slow
- **Method**: Butterworth is a safe default choice

**Handling edge effects:**
- Filtering introduces artifacts at the signal edges
- Pad the signal before filtering, then crop
- Alternatively, discard the first and last few seconds

**Handling gaps:**
- Small gaps: Use `signal_fillmissing()` for interpolation
- Large gaps: Segment the signal and analyze separately
- Mark gaps as NaN and use interpolation with caution

**Combination operation example:**
```python
# Typical preprocessing pipeline
signal = nk.signal_sanitize(raw_signal)  # Remove invalid values
signal = nk.signal_filter(signal, sampling_rate=1000, lowcut=0.5, highcut=40)  # Bandpass filter
signal = nk.signal_detrend(signal, method='polynomial', order=1)  # Remove linear trend
```

**Performance considerations:**
- Filtering: FFT-based methods are faster for long signals
- Resampling: Downsample early in the pipeline to increase speed
- Large datasets: Process in chunks if memory is limited

## References

- Virtanen, P., et al. (2020). SciPy 1.0: fundamental algorithms for scientific computing in Python. Nature methods, 17(3), 261-272.
- Tarvainen, M. P., Ranta-aho, P. O., & Karjalainen, P. A. (2002). An advanced detrending method with application to HRV analysis. IEEE Transactions on Biomedical Engineering, 49(2), 172-175.
- Huang, N. E., et al. (1998). The empirical mode decomposition and the Hilbert spectrum for nonlinear and non-stationary time series analysis. Proceedings of the Royal Society of London A, 454(1971), 903-995.