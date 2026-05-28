---
name: scikit-survival
description: A comprehensive toolkit for survival analysis and time-to-event modeling in Python using scikit-survival; use it when you need to model censored time-to-event outcomes, fit Cox/RSF/GB models or Survival SVMs, evaluate with C-index/Brier score, or handle competing risks.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

Use this skill when you need to:

1. Model **time-to-event outcomes with censoring** (right/left/interval censored observations).
2. Fit and interpret **Cox Proportional Hazards** models (including **penalized** Cox for high-dimensional data).
3. Train **non-linear survival models** such as **Random Survival Forests** or **Gradient Boosting** survival models.
4. Use **Survival SVMs** for margin-based survival prediction (linear or kernel).
5. Evaluate survival predictions with **censoring-aware metrics** (Uno/Harrell C-index, time-dependent AUC, Brier/Integrated Brier Score) and/or perform **competing risks** analysis.

## Key Features

- **Survival target construction** via `sksurv.util.Surv` (arrays or DataFrame).
- **Model families**
  - Cox models: `CoxPHSurvivalAnalysis`, `CoxnetSurvivalAnalysis`
  - Ensembles: `RandomSurvivalForest`, `GradientBoostingSurvivalAnalysis`, `ExtraSurvivalTrees`
  - SVM-based: `FastSurvivalSVM`, `FastKernelSurvivalSVM`
- **Non-parametric estimators**: Kaplan–Meier and Nelson–Aalen.
- **Competing risks**: cumulative incidence estimation.
- **scikit-learn compatibility**: pipelines, cross-validation, and `GridSearchCV` with survival scorers.
- **Evaluation utilities**: IPCW-based metrics (e.g., Uno’s C-index) and calibration-aware scores (IBS).

> Additional topic guides may exist under:
> - `references/cox-models.md`
> - `references/ensemble-models.md`
> - `references/svm-models.md`
> - `references/data-handling.md`
> - `references/evaluation-metrics.md`
> - `references/competing-risks.md`

## Dependencies

- `scikit-survival` (recommended: `>=0.22`)
- `scikit-learn` (recommended: `>=1.2`)
- `numpy` (recommended: `>=1.23`)
- `pandas` (recommended: `>=1.5`)

## Example Usage

A complete, runnable example using a scikit-survival built-in dataset, a scikit-learn pipeline, and Uno’s C-index (IPCW):

```python
import numpy as np

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from sksurv.datasets import load_breast_cancer
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.metrics import concordance_index_ipcw, as_concordance_index_ipcw_scorer

# 1) Load data (X: features, y: structured array with fields like ('event', 'time'))
X, y = load_breast_cancer()

# 2) Split (keep y_train for IPCW-based metrics)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 3) Build a pipeline (scaling is important for many survival models)
pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("model", CoxPHSurvivalAnalysis()),
])

# 4) Optional: hyperparameter tuning (CoxPH has few knobs; shown for workflow completeness)
# If your version exposes regularization parameters, tune them here.
param_grid = {
    # Example placeholder; remove if unsupported in your installed version:
    # "model__alpha": [0.0, 1e-4, 1e-3]
}

if param_grid:
    search = GridSearchCV(
        pipe,
        param_grid=param_grid,
        scoring=as_concordance_index_ipcw_scorer(),
        cv=5,
        n_jobs=-1,
    )
    search.fit(X_train, y_train)
    best = search.best_estimator_
else:
    best = pipe.fit(X_train, y_train)

# 5) Predict risk scores (higher typically means higher risk / shorter survival)
risk_scores = best.predict(X_test)

# 6) Evaluate with Uno's C-index (IPCW)
c_uno = concordance_index_ipcw(y_train, y_test, risk_scores)[0]
print(f"Uno's C-index (IPCW): {c_uno:.3f}")
```

## Implementation Details

### 1) Survival Target Representation (`Surv`)
scikit-survival expects outcomes as a **structured array** with at least:
- an **event indicator** (boolean)
- a **time** value (float/int)

Common construction patterns:

```python
from sksurv.util import Surv

y = Surv.from_arrays(event=event_array, time=time_array)
# or
y = Surv.from_dataframe("event", "time", df)
```

### 2) Model Selection Heuristics
- **High-dimensional (p > n)**: prefer `CoxnetSurvivalAnalysis` (Elastic Net) for stability and feature selection.
- **Interpretability required**: prefer `CoxPHSurvivalAnalysis` (coefficients as log hazard ratios).
- **Strong non-linearities / interactions**: prefer `RandomSurvivalForest` or `GradientBoostingSurvivalAnalysis`.
- **Kernelized decision boundaries**: consider `FastKernelSurvivalSVM` (ensure scaling).

### 3) Preprocessing Requirements
- **Scaling**: strongly recommended for SVMs and often beneficial for penalized Cox models.
- **Categoricals**: encode (e.g., one-hot) before fitting most estimators.
- **Data validation**: ensure non-negative times; verify enough events relative to feature count.

### 4) Evaluation Under Censoring
- **Harrell’s C-index** (`concordance_index_censored`): common, but can be less robust with heavy censoring.
- **Uno’s C-index** (`concordance_index_ipcw`): uses **inverse probability of censoring weights** and requires `y_train` to estimate censoring distribution.

```python
from sksurv.metrics import concordance_index_censored, concordance_index_ipcw

c_harrell = concordance_index_censored(y_test["event"], y_test["time"], risk_scores)[0]
c_uno = concordance_index_ipcw(y_train, y_test, risk_scores)[0]
```

### 5) Time-dependent Metrics (AUC, Brier/IBS)
- **Time-dependent AUC** evaluates discrimination at specific time horizons.
- **Brier score / Integrated Brier Score (IBS)** evaluates calibration + discrimination over time and requires survival probabilities/functions.

```python
from sksurv.metrics import cumulative_dynamic_auc

times = np.array([365, 730, 1095])  # example horizons
auc, mean_auc = cumulative_dynamic_auc(y_train, y_test, risk_scores, times)
```

### 6) Competing Risks (Cumulative Incidence)
Use competing risks methods when multiple mutually exclusive event types exist and one event prevents the others.

```python
from sksurv.nonparametric import cumulative_incidence_competing_risks

# y must encode event types appropriately for competing risks workflows
time_points, cif1, cif2 = cumulative_incidence_competing_risks(y)
```