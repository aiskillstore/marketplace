# Complexity and Entropy Analysis

## Overview

Complexity measures are used to quantify the irregularity, unpredictability, and multiscale structure of time-series signals. NeuroKit2 provides a comprehensive set of entropy, fractal dimension, and nonlinear dynamics measures for assessing the complexity of physiological signals.

## Main Function

### complexity()

Computes multiple complexity indices simultaneously for exploratory analysis.

```python
complexity_indices = nk.complexity(signal, sampling_rate=1000, show=False)
```

**Returns:**
- A DataFrame containing numerous complexity measures across various categories:
  - Entropy indices
  - Fractal dimensions
  - Nonlinear dynamics measures
  - Information-theoretic metrics

**Use Cases:**
- Exploratory analysis to identify relevant indices
- Comprehensive signal feature extraction
- Comparative studies between signals

## Parameter Optimization

Before computing complexity indices, optimal embedding parameters should be determined:

### complexity_delay()

Determine the optimal time delay (τ) for phase-space reconstruction.

```python
optimal_tau = nk.complexity_delay(signal, delay_max=100, method='fraser1986', show=False)
```

**Methods:**
- `'fraser1986'`: First local minimum of mutual information
- `'theiler1990'`: First zero-crossing of the autocorrelation function
- `'casdagli1991'`: Cao's method

**Purpose:** Embedding delay for entropy calculation, attractor reconstruction

### complexity_dimension()

Determine the optimal embedding dimension (m).

```python
optimal_m = nk.complexity_dimension(signal, delay=None, dimension_max=20,
                                    method='afn', show=False)
```

**Methods:**
- `'afn'`: Average False Nearest Neighbors
- `'fnn'`: False Nearest Neighbors
- `'correlation'`: Correlation dimension saturation method

**Purpose:** Entropy calculation, phase-space reconstruction

### complexity_tolerance()

Determine the optimal tolerance (r) for entropy measures.

```python
optimal_r = nk.complexity_tolerance(signal, method='sd', show=False)
```

**Methods:**
- `'sd'`: Based on standard deviation (typically 0.1-0.25 × SD)
- `'maxApEn'`: Maximizing Approximate Entropy (ApEn)
- `'recurrence'`: Based on recurrence rate

**Purpose:** Approximate Entropy, Sample Entropy

### complexity_k()

Determine the optimal k parameter for Higuchi Fractal Dimension.

```python
optimal_k = nk.complexity_k(signal, k_max=20, show=False)
```

**Purpose:** Higuchi Fractal Dimension calculation

## Entropy Measures

Entropy is used to quantify randomness, unpredictability, and information content.

### entropy_shannon()

Shannon entropy — A classic information-theoretic measure.

```python
shannon_entropy = nk.entropy_shannon(signal)
```

**Interpretation:**
- Higher: More random, higher unpredictability
- Lower: More regular, higher predictability
- Unit: bits (information content)

**Use Cases:**
- General randomness assessment
- Information content calculation
- Signal irregularity analysis

### entropy_approximate()

Approximate Entropy (ApEn) — Regularity of patterns.

```python
apen = nk.entropy_approximate(signal, delay=1, dimension=2, tolerance='sd')
```

**Parameters:**
- `delay`: Time delay (τ)
- `dimension`: Embedding dimension (m)
- `tolerance`: Similarity threshold (r)

**Interpretation:**
- Lower ApEn: More regular patterns, higher self-similarity
- Higher ApEn: More complex, more irregular
- Sensitive to signal length (suggested ≥ 100-300 points)

**Physiological Applications:**
- HRV: Decreased ApEn in patients with heart disease
- EEG: Altered ApEn in neurological disorders

### entropy_sample()

Sample Entropy (SampEn) — An improved version of ApEn.

```python
sampen = nk.entropy_sample(signal, delay=1, dimension=2, tolerance='sd')
```

**Advantages over ApEn:**
- Lower dependence on signal length
- More consistent across different recordings
- No self-matching bias

**Interpretation:**
- Same meaning as ApEn but more reliable
- Superior to ApEn in most applications

**Typical Values:**
- HRV: 0.5-2.5 (context-dependent)
- EEG: 0.3-1.5

### entropy_multiscale()

Multiscale Entropy (MSE) — Complexity across time scales.

```python
mse = nk.entropy_multiscale(signal, scale=20, dimension=2, tolerance='sd',
                            method='MSEn', show=False)
```

**Methods:**
- `'MSEn'`: Multiscale Sample Entropy
- `'MSApEn'`: Multiscale Approximate Entropy
- `'CMSE'`: Composite Multiscale Entropy
- `'RCMSE'`: Refined Composite Multiscale Entropy

**Interpretation:**
- Entropy values at different coarse-grained scales
- Healthy/Complex systems: Maintain high entropy across multiple scales
- Diseased/Simple systems: Decreased entropy, especially at larger scales

**Use Cases:**
- Distinguishing true complexity from randomness
- White noise: Constant entropy as scale increases
- Pink noise/Complexity: Structured changes across scales

### entropy_fuzzy()

Fuzzy Entropy — Uses fuzzy membership functions.

```python
fuzzen = nk.entropy_fuzzy(signal, delay=1, dimension=2, tolerance='sd', r=0.2)
```

**Advantages:**
- More stable for noisy signals
- Provides fuzzy boundaries for pattern matching
- Performs better on short signals

### entropy_permutation()

Permutation Entropy — Based on ordinal patterns.

```python
perment = nk.entropy_permutation(signal, delay=1, dimension=3)
```

**Methods:**
- Encodes signal into ordinal patterns (permutations)
- Counts pattern frequencies
- Robust to noise and non-stationarity

**Interpretation:**
- Lower: More regular ordinal structure
- Higher: More random ordering

**Use Cases:**
- EEG analysis
- Anesthesia depth monitoring
- Fast computation

### entropy_spectral()

Spectral Entropy — Based on the power spectrum.

```python
spec_ent = nk.entropy_spectral(signal, sampling_rate=1000, bands=None)
```

**Methods:**
- Normalized Shannon entropy of the power spectrum
- Quantifies the regularity of frequency distribution

**Interpretation:**
- 0: Single frequency (pure tone)
- 1: White noise (flat spectrum)

**Use Cases:**
- EEG: Spectral distribution changes with state
- Anesthesia monitoring

### entropy_svd()

Singular Value Decomposition (SVD) Entropy.

```python
svd_ent = nk.entropy_svd(signal, delay=1, dimension=2)
```

**Methods:**
- Performs SVD on the trajectory matrix
- Calculates the entropy of the singular value distribution

**Use Cases:**
- Attractor complexity
- Deterministic vs. stochastic dynamics

### entropy_differential()

Differential Entropy — Generalization of Shannon entropy for continuous variables.

```python
diff_ent = nk.entropy_differential(signal)
```

**Purpose:** Continuous probability distributions

### Other Entropy Measures

**Tsallis Entropy:**
```python
tsallis = nk.entropy_tsallis(signal, q=2)
```
- Generalized entropy with parameter q
- Simplifies to Shannon entropy when q=1

**Rényi Entropy:**
```python
renyi = nk.entropy_renyi(signal, alpha=2)
```
- Generalized entropy with parameter α

**Other Specialized Entropy Indices:**
- `entropy_attention()`: Attention Entropy
- `entropy_grid()`: Grid Entropy
- `entropy_increment()`: Increment Entropy
- `entropy_slope()`: Slope Entropy
- `entropy_dispersion()`: Dispersion Entropy
- `entropy_symbolicdynamic()`: Symbolic Dynamic Entropy
- `entropy_range()`: Range Entropy
- `entropy_phase()`: Phase Entropy
- `entropy_quadratic()`, `entropy_cumulative_residual()`, `entropy_rate()`: Specialized variants

## Fractal Dimension Measures

Fractal dimensions are used to describe self-similarity and roughness characteristics.

### fractal_katz()

Katz Fractal Dimension — Waveform complexity.

```python
kfd = nk.fractal_katz(signal)
```

**Interpretation:**
- 1: Straight line
- >1: Increasing roughness and complexity
- Typical range: 1.0-2.0

**Advantages:**
- Simple and fast computation
- No parameter tuning required

### fractal_higuchi()

Higuchi Fractal Dimension — Self-similarity.

```python
hfd = nk.fractal_higuchi(signal, k_max=10)
```

**Methods:**
- Constructs k new time series from the original sequence
- Estimates dimension via the length-scale relationship

**Interpretation:**
- Higher HFD: More complex, more irregular
- Lower HFD: Smoother, more regular

**Use Cases:**
- EEG complexity
- HRV analysis
- Seizure detection

### fractal_petrosian()

Petrosian Fractal Dimension — Fast estimation.

```python
pfd = nk.fractal_petrosian(signal)
```

**Advantages:**
- Fast computation
- Direct calculation (no curve fitting)

### fractal_sevcik()

Sevcik Fractal Dimension — Normalized waveform complexity.

```python
sfd = nk.fractal_sevcik(signal)
```

### fractal_nld()

Normalized Length Density (NLD) — Measure based on curve length.

```python
nld = nk.fractal_nld(signal)
```

### fractal_psdslope()

Power Spectral Density (PSD) Slope — Frequency-domain fractal measure.

```python
slope = nk.fractal_psdslope(signal, sampling_rate=1000)
```

**Methods:**
- Linear fit to the log-log power spectrum
- Slope β is related to fractal dimension

**Interpretation:**
- β ≈ 0: White noise (random)
- β ≈ -1: Pink noise (1/f, complex)
- β ≈ -2: Brownian noise (Brownian motion)

### fractal_hurst()

Hurst Exponent — Long-term dependency.

```python
hurst = nk.fractal_hurst(signal, show=False)
```

**Interpretation:**
- H < 0.5: Anti-persistent (mean-reverting)
- H = 0.5: Random walk (white noise)
- H > 0.5: Persistent (trending, long memory)

**Use Cases:**
- Assessing long-term correlations
- Financial time series
- HRV analysis

### fractal_correlation()

Correlation Dimension — Attractor dimension.

```python
corr_dim = nk.fractal_correlation(signal, delay=1, dimension=10, radius=64)
```

**Methods:**
- Grassberger-Procaccia algorithm
- Estimates the dimension of the attractor in phase space

**Interpretation:**
- Low dimension: Deterministic, low-dimensional chaos
- High dimension: High-dimensional chaos or noise

### fractal_dfa()

Detrended Fluctuation Analysis (DFA) — Scaling exponent.

```python
dfa_alpha = nk.fractal_dfa(signal, multifractal=False, q=2, show=False)
```

**Interpretation:**
- α < 0.5: Anti-correlated
- α = 0.5: Uncorrelated (white noise)
- α = 1.0: 1/f noise (pink noise, healthy complexity)
- α = 1.5: Brownian noise
- α > 1.0: Persistent long-range correlations

**HRV Applications:**
- α1 (short-term, 4-11 beats): Reflects autonomic regulation
- α2 (long-term, >11 beats): Long-range correlations
- Decreased α1: Cardiac pathology

### fractal_mfdfa()

Multifractal DFA (MFDFA) — Multiscale fractal properties.

```python
mfdfa_results = nk.fractal_mfdfa(signal, q=None, show=False)
```

**Methods:**
- Extends DFA to multiple q-orders
- Characterizes the multifractal spectrum

**Returns:**
- Generalized Hurst exponent h(q)
- Multifractal spectrum f(α)
- Spectrum width indicates multifractality strength

**Use Cases:**
- Detecting multifractal structures
- HRV multifractality in health vs. disease
- EEG multiscale dynamics

### fractal_tmf()

Multifractal Nonlinearity — Degree of deviation from monofractality.

```python
tmf = nk.fractal_tmf(signal)
```

**Interpretation:**
- Quantifies deviation from simple scaling laws
- Higher values indicate more pronounced multifractal structure

### fractal_density()

Density Fractal Dimension.

```python
density_fd = nk.fractal_density(signal)
```

### fractal_linelength()

Line Length — Total variation measure.

```python
linelength = nk.fractal_linelength(signal)
```

**Use Cases:**
- Simple complexity proxy
- EEG seizure detection

## Nonlinear Dynamics

### complexity_lyapunov()

Largest Lyapunov Exponent (LLE) — Chaos and divergence.

```python
lyap = nk.complexity_lyapunov(signal, delay=None, dimension=None,
                              sampling_rate=1000, show=False)
```

**Interpretation:**
- λ < 0: Stable fixed point
- λ = 0: Periodic orbit
- λ > 0: Chaos (exponential divergence of nearby trajectories)

**Use Cases:**
- Detecting chaos in physiological signals
- HRV: Positive LLE suggests nonlinear dynamics
- EEG: Seizure detection (decreased λ before onset)

### complexity_lempelziv()

Lempel-Ziv Complexity (LZC) — Algorithmic complexity.

```python
lz = nk.complexity_lempelziv(signal, symbolize='median')
```

**Methods:**
- Counts the number of distinct patterns
- Coarse-grained measure of randomness

**Interpretation:**
- Lower: Repetitive, predictable patterns
- Higher: Diverse, unpredictable patterns

**Use Cases:**
- EEG: Consciousness levels, anesthesia depth
- HRV: Autonomic complexity

### complexity_rqa()

Recurrence Quantification Analysis (RQA) — Phase-space recurrence.

```python
rqa_indices = nk.complexity_rqa(signal, delay=1, dimension=3, tolerance='sd')
```

**Indices:**
- **Recurrence Rate (RR)**: Percentage of recurrent states
- **Determinism (DET)**: Percentage of recurrence points forming diagonal lines
- **Laminarity (LAM)**: Percentage of points in vertical structures (laminar states)
- **Trapping Time (TT)**: Average length of vertical lines
- **Longest diagonal/vertical line**: System predictability
- **Entropy (ENTR)**: Shannon entropy of line length distribution

**Interpretation:**
- High DET: Deterministic dynamics
- High LAM: System trapped in specific states
- Low RR: Stochastic, non-recurrent dynamics

**Use Cases:**
- Detecting transitions in system dynamics
- Physiological state change analysis
- Nonlinear time-series analysis

### complexity_hjorth()

Hjorth Parameters — Time-domain complexity.

```python
hjorth = nk.complexity_hjorth(signal)
```

**Indices:**
- **Activity**: Variance of the signal
- **Mobility**: Ratio of the standard deviation of the derivative to the standard deviation of the signal
- **Complexity**: Variation of mobility with respect to the derivative

**Use Cases:**
- EEG feature extraction
- Seizure detection
- Signal characterization

### complexity_decorrelation()

Decorrelation Time — Memory duration.

```python
decorr_time = nk.complexity_decorrelation(signal, show=False)
```

**Interpretation:**
- Time lag at which autocorrelation drops below a threshold
- Shorter: Rapid fluctuations, short-term memory
- Longer: Slow fluctuations, long-term memory

### complexity_relativeroughness()

Relative Roughness — Smoothness measure.

```python
roughness = nk.complexity_relativeroughness(signal)
```

## Information Theory

### fisher_information()

Fisher Information — Measure of order.

```python
fisher = nk.fisher_information(signal, delay=1, dimension=2)
```

**Interpretation:**
- High: Ordered, structured
- Low: Disordered, random

**Use Cases:**
- Used with Shannon entropy (Fisher-Shannon plane)
- Characterizing system complexity

### fishershannon_information()

Fisher-Shannon Information Product.

```python
fs = nk.fishershannon_information(signal)
```

**Methods:**
- Product of Fisher Information and Shannon Entropy
- Characterizes the balance between order and disorder

### mutual_information()

Mutual Information — Shared information between variables.

```python
mi = nk.mutual_information(signal1, signal2, method='knn')
```

**Methods:**
- `'knn'`: k-Nearest Neighbors (non-parametric)
- `'kernel'`: Kernel Density Estimation
- `'binning'`: Histogram-based

**Use Cases:**
- Coupling between signals
- Feature selection
- Nonlinear dependencies

## Practical Considerations

### Signal Length Requirements

| Measure | Min Length | Optimal Length |
|---------|---------------|----------------|
| Shannon Entropy | 50 | 200+ |
| ApEn, SampEn | 100-300 | 500-1000 |
| Multiscale Entropy | 500 | 1000+ per scale |
| DFA | 500 | 1000+ |
| Lyapunov Exponent | 1000 | 5000+ |
| Correlation Dimension | 1000 | 5000+ |

### Parameter Selection

**General Principles:**
- Prefer using parameter optimization functions
- Or use conventional default values:
  - Delay (τ): 1 for HRV, first local minimum of autocorrelation for EEG
  - Dimension (m): Typically 2-3
  - Tolerance (r): Commonly 0.2 × SD

**Sensitivity:**
- Results can be sensitive to parameters
- Parameters used should be reported
- Consider sensitivity analysis

### Normalization and Preprocessing

**Standardization:**
- Many indices are sensitive to signal amplitude
- Z-score normalization is generally recommended
- Detrending may be necessary

**Stationarity:**
- Some indices assume stationarity
- Check with statistical tests (e.g., ADF test)
- Process non-stationary signals in segments

### Interpretation

**Context-dependent:**
- No universal "good" or "bad" complexity
- Compare within subjects or between groups
- Consider physiological context

**Complexity vs. Randomness:**
- Max entropy ≠ Max complexity
- True complexity: structured variability
- White noise: high entropy but low complexity (MSE can distinguish)

## Applications

**Cardiovascular:**
- HRV complexity: decreased in heart disease and aging
- DFA α1: prognostic marker after myocardial infarction

**Neuroscience:**
- EEG complexity: consciousness, anesthesia depth
- Entropy: Alzheimer's, epilepsy, sleep staging
- Permutation entropy: anesthesia monitoring

**Psychology:**
- Loss of complexity in depression and anxiety
- Increased regularity under stress

**Aging:**
- "Loss of complexity" across systems during aging
- Decreased multiscale complexity

**Critical Transitions:**
- Complexity changes before state transitions
- Early warning signals (critical slowing down)

## References

- Pincus, S. M. (1991). Approximate entropy as a measure of system complexity. Proceedings of the National Academy of Sciences, 88(6), 2297-2301.
- Richman, J. S., & Moorman, J. R. (2000). Physiological time-series analysis using approximate entropy and sample entropy. American Journal of Physiology-Heart and Circulatory Physiology, 278(6), H2039-H2049.
- Peng, C. K., et al. (1995). Quantification of scaling exponents and crossover phenomena in nonstationary heartbeat time series. Chaos, 5(1), 82-87.
- Costa, M., Goldberger, A. L., & Peng, C. K. (2005). Multiscale entropy analysis of biological signals. Physical review E, 71(2), 021906.
- Grassberger, P., & Procaccia, I. (1983). Measuring the strangeness of strange attractors. Physica D: Nonlinear Phenomena, 9(1-2), 189-208.