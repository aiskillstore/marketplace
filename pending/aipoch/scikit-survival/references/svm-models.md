# Survival Support Vector Machines

## Overview

Survival Support Vector Machines (SVMs) apply the traditional SVM framework to handle survival analysis with censored data. They optimize a ranking objective function to encourage the model to correctly rank survival times.

### Core Idea

SVMs for survival analysis learn a function $f(x)$ that produces a risk score, where the optimization process ensures that subjects with shorter survival times receive higher risk scores than subjects with longer survival times.

## When to Use Survival SVMs

**Suitable for:**
- Medium-sized datasets (typically 100-10,000 samples)
- Need for non-linear decision boundaries (Kernel SVMs)
- Desire for margin-based learning with regularization
- Well-defined feature spaces

**Less ideal for:**
- Extremely large datasets (>100,000 samples) — ensemble methods may be faster
- Need for interpretable coefficients — use Cox models instead
- Need for survival function estimation — use Random Survival Forests
- Extremely high-dimensional data — use regularized Cox or Gradient Boosting

## Model Types

### FastSurvivalSVM

A linear survival SVM optimized for speed using coordinate descent.

**When to use:**
- Linear relationships are expected
- Large datasets where speed is critical
- Fast training and prediction are desired

**Key Parameters:**
- `alpha`: Regularization parameter (default: 1.0)
  - Higher value = stronger regularization
- `rank_ratio`: Trade-off between ranking and regression (default: 1.0)
- `max_iter`: Maximum number of iterations (default: 20)
- `tol`: Tolerance for stopping criterion (default: 1e-5)

```python
from sksurv.svm import FastSurvivalSVM

# Fit linear survival SVM
estimator = FastSurvivalSVM(alpha=1.0, max_iter=100, tol=1e-5, random_state=42)
estimator.fit(X, y)

# Predict risk scores
risk_scores = estimator.predict(X_test)
```

### FastKernelSurvivalSVM

A kernel survival SVM for handling non-linear relationships.

**When to use:**
- Non-linear relationships exist between features and survival
- Medium-sized datasets
- Can afford longer training times for better performance

**Kernel Options:**
- `'linear'`: Linear kernel, equivalent to FastSurvivalSVM
- `'poly'`: Polynomial kernel
- `'rbf'`: Radial Basis Function (Gaussian) kernel — most commonly used
- `'sigmoid'`: Sigmoid kernel
- Custom kernel functions

**Key Parameters:**
- `alpha`: Regularization parameter (default: 1.0)
- `kernel`: Kernel function (default: 'rbf')
- `gamma`: Kernel coefficient for rbf, poly, and sigmoid
- `degree`: Degree of the polynomial kernel
- `coef0`: Independent term in poly and sigmoid
- `rank_ratio`: Trade-off parameter (default: 1.0)
- `max_iter`: Maximum number of iterations (default: 20)

```python
from sksurv.svm import FastKernelSurvivalSVM

# Fit RBF kernel survival SVM
estimator = FastKernelSurvivalSVM(
    alpha=1.0,
    kernel='rbf',
    gamma='scale',
    max_iter=50,
    random_state=42
)
estimator.fit(X, y)

# Predict risk scores
risk_scores = estimator.predict(X_test)
```

### HingeLossSurvivalSVM

A survival SVM using hinge loss, more similar to classification SVMs.

**When to use:**
- Desire to use hinge loss instead of squared hinge loss
- Need for sparse solutions
- Behavior similar to classification SVMs

**Key Parameters:**
- `alpha`: Regularization parameter
- `fit_intercept`: Whether to fit an intercept term (default: False)

```python
from sksurv.svm import HingeLossSurvivalSVM

# Fit hinge loss SVM
estimator = HingeLossSurvivalSVM(alpha=1.0, fit_intercept=False, random_state=42)
estimator.fit(X, y)

# Predict risk scores
risk_scores = estimator.predict(X_test)
```

### NaiveSurvivalSVM

The original survival SVM formulation using quadratic programming.

**When to use:**
- Small datasets
- Research/benchmarking purposes
- When other methods do not converge

**Limitations:**
- Slower than Fast variants
- Poor scalability

```python
from sksurv.svm import NaiveSurvivalSVM

# Fit naive SVM (slower)
estimator = NaiveSurvivalSVM(alpha=1.0, random_state=42)
estimator.fit(X, y)

# Predict
risk_scores = estimator.predict(X_test)
```

### MinlipSurvivalAnalysis

Survival analysis using the minimize Lipschitz constant approach.

**When to use:**
- Desire for a different optimization objective
- Research applications
- Alternative to standard survival SVMs

```python
from sksurv.svm import MinlipSurvivalAnalysis

# Fit Minlip model
estimator = MinlipSurvivalAnalysis(alpha=1.0, random_state=42)
estimator.fit(X, y)

# Predict
risk_scores = estimator.predict(X_test)
```

## Hyperparameter Tuning

### Tuning Alpha (Regularization)

```python
from sklearn.model_selection import GridSearchCV
from sksurv.metrics import as_concordance_index_ipcw_scorer

# Define parameter grid
param_grid = {
    'alpha': [0.1, 0.5, 1.0, 5.0, 10.0, 50.0]
}

# Grid search
cv = GridSearchCV(
    FastSurvivalSVM(),
    param_grid,
    scoring=as_concordance_index_ipcw_scorer(),
    cv=5,
    n_jobs=-1
)
cv.fit(X, y)

print(f"Best alpha: {cv.best_params_['alpha']}")
print(f"Best C-index: {cv.best_score_:.3f}")
```

### Tuning Kernel Parameters

```python
from sklearn.model_selection import GridSearchCV

# Define parameter grid for kernel SVM
param_grid = {
    'alpha': [0.1, 1.0, 10.0],
    'gamma': ['scale', 'auto', 0.001, 0.01, 0.1, 1.0]
}

# Grid search
cv = GridSearchCV(
    FastKernelSurvivalSVM(kernel='rbf'),
    param_grid,
    scoring=as_concordance_index_ipcw_scorer(),
    cv=5,
    n_jobs=-1
)
cv.fit(X, y)

print(f"Best parameters: {cv.best_params_}")
print(f"Best C-index: {cv.best_score_:.3f}")
```

## Clinical Kernel Transform

### ClinicalKernelTransform

A special kernel that combines clinical features with molecular data to improve prediction in medical applications.

**Usage Scenarios:**
- Simultaneously possessing clinical variables (age, stage, etc.) and high-dimensional molecular data (gene expression, genomics)
- Clinical features should have different weights
- Desire to integrate heterogeneous data types

**Key Parameters:**
- `fit_once`: Whether to fit the kernel only once or refit during cross-validation (default: False)
- Clinical features should be passed separately from molecular features

```python
from sksurv.kernels import ClinicalKernelTransform
from sksurv.svm import FastKernelSurvivalSVM
from sklearn.pipeline import make_pipeline

# Separate clinical and molecular features
clinical_features = ['age', 'stage', 'grade']
X_clinical = X[clinical_features]
X_molecular = X.drop(clinical_features, axis=1)

# Create pipeline with clinical kernel
estimator = make_pipeline(
    ClinicalKernelTransform(),
    FastKernelSurvivalSVM()
)

# Fit model
# ClinicalKernelTransform expects a tuple (clinical, molecular)
X_combined = list(zip(X_clinical.values, X_molecular.values))
estimator.fit(X_combined, y)
```

## Practical Examples

### Example 1: Linear SVM with Cross-Validation

```python
from sksurv.svm import FastSurvivalSVM
from sklearn.model_selection import cross_val_score
from sksurv.metrics import as_concordance_index_ipcw_scorer
from sklearn.preprocessing import StandardScaler

# Standardize features (crucial for SVM!)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Create model
svm = FastSurvivalSVM(alpha=1.0, max_iter=100, random_state=42)

# Cross-validation
scores = cross_val_score(
    svm, X_scaled, y,
    cv=5,
    scoring=as_concordance_index_ipcw_scorer(),
    n_jobs=-1
)

print(f"Mean C-index: {scores.mean():.3f} (±{scores.std():.3f})")
```

### Example 2: Kernel SVM with Different Kernels

```python
from sksurv.svm import FastKernelSurvivalSVM
from sklearn.model_selection import train_test_split
from sksurv.metrics import concordance_index_ipcw

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardization
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Compare different kernels
kernels = ['linear', 'poly', 'rbf', 'sigmoid']
results = {}

for kernel in kernels:
    # Fit model
    svm = FastKernelSurvivalSVM(kernel=kernel, alpha=1.0, random_state=42)
    svm.fit(X_train_scaled, y_train)

    # Predict
    risk_scores = svm.predict(X_test_scaled)

    # Evaluate
    c_index = concordance_index_ipcw(y_train, y_test, risk_scores)[0]
    results[kernel] = c_index

    print(f"{kernel:10s}: C-index = {c_index:.3f}")

# Best kernel
best_kernel = max(results, key=results.get)
print(f"\nBest kernel: {best_kernel} (C-index = {results[best_kernel]:.3f})")
```

### Example 3: Full Pipeline with Hyperparameter Tuning

```python
from sksurv.svm import FastKernelSurvivalSVM
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sksurv.metrics import as_concordance_index_ipcw_scorer

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('svm', FastKernelSurvivalSVM(kernel='rbf'))
])

# Define parameter grid
param_grid = {
    'svm__alpha': [0.1, 1.0, 10.0],
    'svm__gamma': ['scale', 0.01, 0.1, 1.0]
}

# Grid search
cv = GridSearchCV(
    pipeline,
    param_grid,
    scoring=as_concordance_index_ipcw_scorer(),
    cv=5,
    n_jobs=-1,
    verbose=1
)
cv.fit(X_train, y_train)

# Best model
best_model = cv.best_estimator_
print(f"Best parameters: {cv.best_params_}")
print(f"Best CV C-index: {cv.best_score_:.3f}")

# Evaluate on test set
risk_scores = best_model.predict(X_test)
c_index = concordance_index_ipcw(y_train, y_test, risk_scores)[0]
print(f"Test C-index: {c_index:.3f}")
```

## Important Considerations

### Feature Scaling

**Crucial**: Always standardize features before using SVM!

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

### Computational Complexity

- **FastSurvivalSVM**: $O(n \times p)$ per iteration — Fast
- **FastKernelSurvivalSVM**: $O(n^2 \times p)$ — Slower, scales quadratically
- **NaiveSurvivalSVM**: $O(n^3)$ — Very slow for large datasets

For large datasets (>10,000 samples), preferred options:
- FastSurvivalSVM (Linear)
- Gradient Boosting
- Random Survival Forest

### When SVMs May Not Be the Best Choice

- **Extremely large datasets**: Ensemble methods are faster
- **Need for survival functions**: Use Random Survival Forest or Cox models
- **Need for interpretability**: Use Cox models
- **Extremely high-dimensional data**: Use penalized Cox (Coxnet) or Gradient Boosting with feature selection

## Model Selection Guide

| Model | Speed | Non-linear | Scalability | Interpretability |
|-------|-------|---------------|-------------|------------------|
| FastSurvivalSVM | Fast | No | High | Medium |
| FastKernelSurvivalSVM | Medium | Yes | Medium | Low |
| HingeLossSurvivalSVM | Fast | No | High | Medium |
| NaiveSurvivalSVM | Slow | No | Low | Medium |

**General Recommendations:**
- Start with **FastSurvivalSVM** to establish a baseline
- Try **FastKernelSurvivalSVM** with RBF kernel if non-linearity is expected
- Use grid search to tune alpha and gamma
- Always standardize features
- Compare with Random Survival Forest and Gradient Boosting