# Cox Proportional Hazards Models

## Overview

The Cox proportional hazards model is a semi-parametric model that relates covariates to the time until an event occurs. The hazard function for individual *i* is expressed as:

**h_i(t) = h_0(t) × exp(β^T x_i)**

Where:
- h_0(t) is the baseline hazard function (unspecified)
- β is the vector of coefficients
- x_i is the vector of covariates for individual *i*

Its core assumption is that the hazard ratio between two individuals remains constant over time (proportional hazards assumption).

## CoxPHSurvivalAnalysis

Basic Cox proportional hazards model for survival analysis.

### When to Use
- Standard survival analysis with censored data
- Need for interpretable coefficients (log hazard ratios)
- The proportional hazards assumption holds
- The dataset has relatively few features

### Key Parameters
- `alpha`: Regularization parameter (default: 0, no regularization)
- `ties`: Method to handle tied event times ('breslow' or 'efron')
- `n_iter`: Maximum number of iterations for optimization

### Usage Example
```python
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.datasets import load_gbsg2

# Load data
X, y = load_gbsg2()

# Fit Cox model
estimator = CoxPHSurvivalAnalysis()
estimator.fit(X, y)

# Get coefficients (log hazard ratios)
coefficients = estimator.coef_

# Predict risk scores
risk_scores = estimator.predict(X)
```

## CoxnetSurvivalAnalysis

Cox model with Elastic Net penalty for feature selection and regularization.

### When to Use
- High-dimensional data (many features)
- Need for automatic feature selection
- Desire to handle multicollinearity
- Need for a sparse model

### Penalty Types
- **Ridge (L2)**: alpha_min_ratio=1.0, l1_ratio=0
  - Shrinks all coefficients
  - Works well when all features are relevant

- **Lasso (L1)**: l1_ratio=1.0
  - Performs feature selection (sets coefficients to zero)
  - Suitable for sparse models

- **Elastic Net**: 0 < l1_ratio < 1
  - Combination of L1 and L2
  - Balances feature selection and grouping effects

### Key Parameters
- `l1_ratio`: Balance between L1 and L2 penalties (0=Ridge, 1=Lasso)
- `alpha_min_ratio`: Ratio of the smallest to the largest penalty in the regularization path
- `n_alphas`: Number of alphas along the regularization path
- `fit_baseline_model`: Whether to fit a baseline model without penalty

### Usage Example
```python
from sksurv.linear_model import CoxnetSurvivalAnalysis

# Fit using elastic net penalty
estimator = CoxnetSurvivalAnalysis(l1_ratio=0.5, alpha_min_ratio=0.01)
estimator.fit(X, y)

# Access regularization path
alphas = estimator.alphas_
coefficients_path = estimator.coef_path_

# Predict using a specific alpha
risk_scores = estimator.predict(X, alpha=0.1)
```

### Cross-validation for Alpha Selection
```python
from sklearn.model_selection import GridSearchCV
from sksurv.metrics import concordance_index_censored

# Define parameter grid
param_grid = {'l1_ratio': [0.1, 0.5, 0.9],
              'alpha_min_ratio': [0.01, 0.001]}

# Grid search using C-index
cv = GridSearchCV(CoxnetSurvivalAnalysis(),
                  param_grid,
                  scoring='concordance_index_ipcw',
                  cv=5)
cv.fit(X, y)

# Best parameters
best_params = cv.best_params_
```

## IPCRidge

Inverse Probability of Censoring Weighted Ridge regression for Accelerated Failure Time (AFT) models.

### When to Use
- Prefer the Accelerated Failure Time (AFT) framework over proportional hazards
- Need to model how features accelerate or decelerate survival time
- High censoring rate
- Desire for regularization via Ridge penalty

### Main Differences from Cox Models
AFT models assume that features multiply the survival time by a constant factor, rather than multiplying the hazard rate. The model directly predicts the log survival time.

### Usage Example
```python
from sksurv.linear_model import IPCRidge

# Fit IPCRidge model
estimator = IPCRidge(alpha=1.0)
estimator.fit(X, y)

# Predict log survival time
log_time = estimator.predict(X)
```

## Model Comparison and Selection

### How to Choose a Model

**Use CoxPHSurvivalAnalysis when:**
- Number of features is small to medium
- Interpretable hazard ratios are required
- Standard survival analysis scenarios

**Use CoxnetSurvivalAnalysis when:**
- High-dimensional data (p >> n)
- Feature selection is needed
- Desire to identify important predictors
- Multicollinearity is present

**Use IPCRidge when:**
- The AFT framework is more appropriate
- Censoring rate is high
- Desire to model time directly rather than hazard

### Checking the Proportional Hazards Assumption

The proportional hazards assumption should be verified using:
- Schoenfeld residuals
- Log-log survival plots
- Statistical tests (available in other packages like lifelines)

If the assumption is violated, consider:
- Stratification by the covariate violating the assumption
- Time-varying coefficients
- Alternative models (AFT, parametric models)

## Interpretation

### Cox Model Coefficients
- Positive coefficient: Increased risk (shorter survival)
- Negative coefficient: Decreased risk (longer survival)
- Hazard ratio = exp(β), representing the change for each unit increase in the covariate
- Example: β=0.693 → HR=2.0 (risk doubles)

### Risk Scores
- Higher risk score = Higher risk of event = Shorter expected survival time
- Risk scores are relative; for absolute predictions, use survival functions.