# Survival Model Evaluation Metrics

## Overview

Evaluating survival models requires specialized metrics capable of handling censored data. scikit-survival provides three main categories of evaluation metrics:
1. Concordance Index (C-index)
2. Time-dependent ROC and AUC
3. Brier Score

## Concordance Index (C-index)

### What it Measures

The Concordance Index measures the rank correlation between predicted risk scores and observed time-to-event. It represents the probability that, for a randomly selected pair of subjects, the model correctly orders their survival times.

**Range**: 0 to 1
- 0.5 = Random prediction
- 1.0 = Perfect concordance
- Typical good performance: 0.7-0.8

### Two Implementations

#### Harrell's C-index (concordance_index_censored)

A traditional estimation method that is simple but has limitations.

**When to use:**
- When the censoring rate is low (< 40%)
- Quick evaluation during the development process
- Comparing models on the same dataset

**Limitations:**
- Bias increases as the censoring rate rises
- Starts to overestimate model performance when the censoring rate is around 49%

```python
from sksurv.metrics import concordance_index_censored

# Calculate Harrell's C-index
result = concordance_index_censored(y_test['event'], y_test['time'], risk_scores)
c_index = result[0]
print(f"Harrell's C-index: {c_index:.3f}")
```

#### Uno's C-index (concordance_index_ipcw)

An Inverse Probability of Censoring Weighting (IPCW) estimator that corrects for censoring bias.

**When to use:**
- When the censoring rate is moderate to high (> 40%)
- When unbiased estimation is required
- Comparing models across different datasets
- Publishing results (more robust)

**Advantages:**
- Remains stable even under high censoring
- More reliable estimation results
- Lower bias

```python
from sksurv.metrics import concordance_index_ipcw

# Calculate Uno's C-index
# Requires training data to calculate IPCW
c_index, concordant, discordant, tied_risk = concordance_index_ipcw(
    y_train, y_test, risk_scores
)
print(f"Uno's C-index: {c_index:.3f}")
```

### Choosing Between Harrell's and Uno's

**Use Uno's C-index when:**
- Censoring rate > 40%
- Most precise estimation is needed
- Comparing models from different studies
- Publishing research findings

**Use Harrell's C-index when:**
- Censoring rate is low
- Quickly comparing models during development
- Computational efficiency is critical

### Example Comparison

```python
from sksurv.metrics import concordance_index_censored, concordance_index_ipcw

# Harrell's C-index
harrell = concordance_index_censored(y_test['event'], y_test['time'], risk_scores)[0]

# Uno's C-index
uno = concordance_index_ipcw(y_train, y_test, risk_scores)[0]

print(f"Harrell's C-index: {harrell:.3f}")
print(f"Uno's C-index: {uno:.3f}")
```

## Time-dependent ROC and AUC

### What it Measures

Time-dependent AUC evaluates the model's discriminative power at a specific time point. It distinguishes subjects who experience an event before time *t* from those who do not.

**Question Answered**: "How well does the model predict who will experience an event before time t?"

### When to use

- Predicting event occurrence within specific time windows
- Clinical decision-making at specific time points (e.g., 5-year survival)
- Wanting to evaluate performance over different time horizons
- Needing both discrimination and temporal information

### Key Function: cumulative_dynamic_auc

```python
from sksurv.metrics import cumulative_dynamic_auc

# Define evaluation time points
times = [365, 730, 1095, 1460, 1825]  # 1, 2, 3, 4, 5 years

# Calculate time-dependent AUC
auc, mean_auc = cumulative_dynamic_auc(
    y_train, y_test, risk_scores, times
)

# Plot AUC over time
import matplotlib.pyplot as plt
plt.plot(times, auc, marker='o')
plt.xlabel('Time (days)')
plt.ylabel('Time-dependent AUC')
plt.title('Model Discrimination Over Time')
plt.show()

print(f"Mean AUC: {mean_auc:.3f}")
```

### Interpretation

- **AUC at time t**: The probability that the model correctly ranks a subject who experienced an event before time t above a subject who did not.
- **AUC over time**: Indicates how model performance changes across different time horizons.
- **Mean AUC**: A general summary of discrimination across all time points.

### Example: Comparing Models

```python
# Compare two models
auc1, mean_auc1 = cumulative_dynamic_auc(y_train, y_test, risk_scores1, times)
auc2, mean_auc2 = cumulative_dynamic_auc(y_train, y_test, risk_scores2, times)

plt.plot(times, auc1, marker='o', label='Model 1')
plt.plot(times, auc2, marker='s', label='Model 2')
plt.xlabel('Time (days)')
plt.ylabel('Time-dependent AUC')
plt.legend()
plt.show()
```

## Brier Score

### What it Measures

The Brier Score extends Mean Squared Error (MSE) to survival data with censoring. It measures both discrimination (ranking) and calibration (accuracy of predicted probabilities).

**Formula**: **(1/n) Σ (S(t|x_i) - I(T_i > t))²**

Where S(t|x_i) is the predicted survival probability for subject i at time t.

**Range**: 0 to 1
- 0 = Perfect prediction
- Lower is better
- Typical good performance: < 0.2

### When to use

- Calibration assessment is needed (not just ranking)
- Wanting to evaluate predicted probabilities rather than just risk scores
- Comparing models that output survival functions
- Clinical applications requiring probability estimates

### Key Functions

#### brier_score: Single Time Point

```python
from sksurv.metrics import brier_score

# Calculate Brier score at a specific time point
time_point = 1825  # 5 years
surv_probs = model.predict_survival_function(X_test)
# Extract survival probability for each subject at time_point
surv_at_t = [fn(time_point) for fn in surv_probs]

bs = brier_score(y_train, y_test, surv_at_t, time_point)[1]
print(f"Brier score at {time_point} days: {bs:.3f}")
```

#### integrated_brier_score: Comprehensive Assessment Over Time

```python
from sksurv.metrics import integrated_brier_score

# Calculate Integrated Brier Score (IBS)
times = [365, 730, 1095, 1460, 1825]
surv_probs = model.predict_survival_function(X_test)

ibs = integrated_brier_score(y_train, y_test, surv_probs, times)
print(f"Integrated Brier Score: {ibs:.3f}")
```

### Interpretation

- **Brier Score at time t**: The expected squared difference between predicted and actual survival at time t.
- **Integrated Brier Score (IBS)**: The weighted average of Brier scores across time.
- **Lower value = Better prediction**.

### Comparison with Null Model

Always compare with a baseline model (e.g., Kaplan-Meier):

```python
from sksurv.nonparametric import kaplan_meier_estimator

# Calculate Kaplan-Meier baseline
time_km, surv_km = kaplan_meier_estimator(y_train['event'], y_train['time'])

# Use KM prediction for each test subject
surv_km_test = [surv_km[time_km <= time_point][-1] if any(time_km <= time_point) else 1.0
                for _ in range(len(X_test))]

bs_km = brier_score(y_train, y_test, surv_km_test, time_point)[1]
bs_model = brier_score(y_train, y_test, surv_at_t, time_point)[1]

print(f"Kaplan-Meier Brier Score: {bs_km:.3f}")
print(f"Model Brier Score: {bs_model:.3f}")
print(f"Improvement: {(bs_km - bs_model) / bs_km * 100:.1f}%")
```

## Using Metrics in Cross-Validation

### Concordance Index Scorer

```python
from sklearn.model_selection import cross_val_score
from sksurv.metrics import as_concordance_index_ipcw_scorer

# Create scorer
scorer = as_concordance_index_ipcw_scorer()

# Perform cross-validation
scores = cross_val_score(model, X, y, cv=5, scoring=scorer)
print(f"Mean C-index: {scores.mean():.3f} (±{scores.std():.3f})")
```

### Integrated Brier Score Scorer

```python
from sksurv.metrics import as_integrated_brier_score_scorer

# Define evaluation time points
times = np.percentile(y['time'][y['event']], [25, 50, 75])

# Create scorer
scorer = as_integrated_brier_score_scorer(times)

# Perform cross-validation
scores = cross_val_score(model, X, y, cv=5, scoring=scorer)
print(f"Mean IBS: {scores.mean():.3f} (±{scores.std():.3f})")
```

## Model Selection with GridSearchCV

```python
from sklearn.model_selection import GridSearchCV
from sksurv.ensemble import RandomSurvivalForest
from sksurv.metrics import as_concordance_index_ipcw_scorer

# Define parameter grid
param_grid = {
    'n_estimators': [100, 200, 300],
    'min_samples_split': [10, 20, 30],
    'max_depth': [None, 10, 20]
}

# Create scorer
scorer = as_concordance_index_ipcw_scorer()

# Execute grid search
cv = GridSearchCV(
    RandomSurvivalForest(random_state=42),
    param_grid,
    scoring=scorer,
    cv=5,
    n_jobs=-1
)
cv.fit(X, y)

print(f"Best parameters: {cv.best_params_}")
print(f"Best C-index: {cv.best_score_:.3f}")
```

## Comprehensive Model Evaluation

### Recommended Evaluation Pipeline

```python
from sksurv.metrics import (
    concordance_index_censored,
    concordance_index_ipcw,
    cumulative_dynamic_auc,
    integrated_brier_score
)

def evaluate_survival_model(model, X_train, X_test, y_train, y_test):
    """Comprehensive survival model evaluation"""

    # Get predictions
    risk_scores = model.predict(X_test)
    surv_funcs = model.predict_survival_function(X_test)

    # 1. Concordance Index (two versions)
    c_harrell = concordance_index_censored(y_test['event'], y_test['time'], risk_scores)[0]
    c_uno = concordance_index_ipcw(y_train, y_test, risk_scores)[0]

    # 2. Time-dependent AUC
    times = np.percentile(y_test['time'][y_test['event']], [25, 50, 75])
    auc, mean_auc = cumulative_dynamic_auc(y_train, y_test, risk_scores, times)

    # 3. Integrated Brier Score
    ibs = integrated_brier_score(y_train, y_test, surv_funcs, times)

    # Print results
    print("=" * 50)
    print("Model Evaluation Results")
    print("=" * 50)
    print(f"Harrell's C-index:  {c_harrell:.3f}")
    print(f"Uno's C-index:      {c_uno:.3f}")
    print(f"Mean AUC:           {mean_auc:.3f}")
    print(f"Integrated Brier:   {ibs:.3f}")
    print("=" * 50)

    return {
        'c_harrell': c_harrell,
        'c_uno': c_uno,
        'mean_auc': mean_auc,
        'ibs': ibs,
        'time_auc': dict(zip(times, auc))
    }

# Use evaluation function
results = evaluate_survival_model(model, X_train, X_test, y_train, y_test)
```

## Choosing the Right Metric

### Decision Guide

**Use C-index (Uno's) when:**
- Primary goal is ranking/discrimination
- Probability calibration is not required
- Standard survival analysis scenarios
- Most general-purpose choice

**Use Time-dependent AUC when:**
- Discrimination needs to be evaluated at specific time points
- Clinical decisions target specific time horizons
- Wanting to understand how performance changes over time

**Use Brier Score when:**
- Calibrated probability estimates are required
- Discrimination and calibration are equally important
- Clinical decisions require probability values
- Wanting to perform a comprehensive evaluation

**Best Practices**: Report multiple metrics for a comprehensive evaluation. At minimum, report:
- Uno's C-index (Discrimination)
- Integrated Brier Score (Discrimination + Calibration)
- Time-dependent AUC at clinically meaningful time points