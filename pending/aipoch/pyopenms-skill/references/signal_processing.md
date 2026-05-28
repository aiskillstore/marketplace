# Signal Processing & Algorithms

PyOpenMS maps OpenMS C++ kernels for high-performance signal processing.

## Filters

### Smoothing
**GaussFilter**: Smooths raw data to reduce noise.
```python
gf = ms.GaussFilter()
param = gf.getParameters()
param.setValue("gaussian_width", 0.2) # Configure width
gf.setParameters(param)
gf.filterExperiment(exp)
```

### Baseline Correction
Used to remove background noise/baseline drift.

## Feature Detection

### Peak Picking
Identifies peaks in raw spectra.
```python
pp = ms.PeakPickerHiRes()
pp.pickExperiment(exp)
```

### Isotope Patterns
Identifies and links isotope patterns for quantification.
