# Competing Risks Analysis

## Overview

Competing risks occur when a study subject can experience one of several mutually exclusive events (event types). When one of these events occurs, it prevents (“competes” with) the occurrence of other events.

### Competing Risks Examples

**Medical Research:**
- Death from cancer vs. death from cardiovascular disease vs. other causes of death
- Recurrence vs. death without recurrence in cancer studies
- Different types of infections in transplant patients

**Other Applications:**
- Employee turnover: Retirement vs. resignation vs. termination
- Equipment failure: Different failure modes
- Customer churn: Different reasons for churning

### Core Concept: Cumulative Incidence Function (CIF)

The **Cumulative Incidence Function (CIF)** represents the probability of experiencing a specific type of event by time *t*, accounting for the presence of competing risks.

**CIF_k(t) = P(T ≤ t, Event Type = k)**

This differs from the Kaplan-Meier estimator, which overestimates the probability of an event occurring when competing risks are present.

## When to Use Competing Risks Analysis

**Use competing risks analysis when:**
- There are multiple mutually exclusive event types
- The occurrence of one event prevents others from occurring
- You need to estimate the probability of a specific event type
- You want to understand how covariates affect different event types

**Do not use when:**
- Focusing on only one event type (use standard survival analysis)
- Events are not mutually exclusive (use recurrent events methods)
- Competing events are extremely rare (can be treated as censoring)

## Cumulative Incidence Under Competing Risks

### cumulative_incidence_competing_risks Function

Estimates the cumulative incidence function for each event type.

```python
from sksurv.nonparametric import cumulative_incidence_competing_risks
from sksurv.datasets import load_leukemia

# Load data with competing risks
X, y = load_leukemia()
# y contains event types: 0=censored, 1=relapse, 2=death

# Calculate cumulative incidence for each event type
# Returns: time points, CIF for event 1, CIF for event 2, ...
time_points, cif_1, cif_2 = cumulative_incidence_competing_risks(y)

# Plot cumulative incidence functions
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.step(time_points, cif_1, where='post', label='Relapse', linewidth=2)
plt.step(time_points, cif_2, where='post', label='Death in remission', linewidth=2)
plt.xlabel('Time (weeks)')
plt.ylabel('Cumulative Incidence')
plt.title('Competing Risks: Relapse vs Death')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

### Interpreting Results

- **CIF at time t**: The probability of experiencing that specific event by time t.
- **Sum of all CIFs**: The total probability of experiencing any event (all-cause).
- **1 - Sum of CIFs**: The probability of being event-free and not censored.

## Data Format for Competing Risks

### Creating Structured Arrays with Event Types

```python
import numpy as np
from sksurv.util import Surv

# Event types: 0 = censored, 1 = event type 1, 2 = event type 2
event_types = np.array([0, 1, 2, 1, 0, 2, 1])
times = np.array([10.2, 5.3, 8.1, 3.7, 12.5, 6.8, 4.2])

# Create survival analysis array
# For competing risks: event=True if any event occurred
# Store event types separately or encode them in the event field
y = Surv.from_arrays(
    event=(event_types > 0),  # True if any event occurred
    time=times
)

# Keep event_types to distinguish between different event types
```

### Converting Data with Event Types

```python
import pandas as pd
from sksurv.util import Surv

# Assume data contains: time, event_type columns
# event_type: 0=censored, 1=type 1, 2=type 2, etc.

df = pd.read_csv('competing_risks_data.csv')

# Create survival outcome
y = Surv.from_arrays(
    event=(df['event_type'] > 0),
    time=df['time']
)

# Store event types
event_types = df['event_type'].values
```

## Comparing Cumulative Incidence Between Groups

### Stratified Analysis

```python
from sksurv.nonparametric import cumulative_incidence_competing_risks
import matplotlib.pyplot as plt

# Split by treatment group
mask_treatment = X['treatment'] == 'A'
mask_control = X['treatment'] == 'B'

y_treatment = y[mask_treatment]
y_control = y[mask_control]

# Calculate CIF for each group
time_trt, cif1_trt, cif2_trt = cumulative_incidence_competing_risks(y_treatment)
time_ctl, cif1_ctl, cif2_ctl = cumulative_incidence_competing_risks(y_control)

# Plot comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Event Type 1
ax1.step(time_trt, cif1_trt, where='post', label='Treatment', linewidth=2)
ax1.step(time_ctl, cif1_ctl, where='post', label='Control', linewidth=2)
ax1.set_xlabel('Time')
ax1.set_ylabel('Cumulative Incidence')
ax1.set_title('Event Type 1')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Event Type 2
ax2.step(time_trt, cif2_trt, where='post', label='Treatment', linewidth=2)
ax2.step(time_ctl, cif2_ctl, where='post', label='Control', linewidth=2)
ax2.set_xlabel('Time')
ax2.set_ylabel('Cumulative Incidence')
ax2.set_title('Event Type 2')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

## Statistical Testing for Competing Risks

### Gray's Test

Use Gray's test to compare cumulative incidence functions between groups (available in other libraries like lifelines).

```python
# Note: Gray's test is not directly provided in scikit-survival
# Consider using lifelines or other libraries

# from lifelines.statistics import multivariate_logrank_test
# result = multivariate_logrank_test(times, groups, events, event_of_interest=1)
```

## Competing Risks Modeling

### Method 1: Cause-Specific Hazard Models

Fit a Cox model for each event type separately, treating other event types as censored.

```python
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.util import Surv

# Set separate outcomes for each event type
# Event type 1: Treat type 2 as censored
y_event1 = Surv.from_arrays(
    event=(event_types == 1),
    time=times
)

# Event type 2: Treat type 1 as censored
y_event2 = Surv.from_arrays(
    event=(event_types == 2),
    time=times
)

# Fit cause-specific models
cox_event1 = CoxPHSurvivalAnalysis()
cox_event1.fit(X, y_event1)

cox_event2 = CoxPHSurvivalAnalysis()
cox_event2.fit(X, y_event2)

# Interpret coefficients for each event type
print("Event Type 1 (e.g., Relapse):")
print(cox_event1.coef_)

print("\nEvent Type 2 (e.g., Death):")
print(cox_event2.coef_)
```

**Interpretation:**
- Build independent models for each competing event.
- Coefficients show the effect of covariates on the cause-specific hazard ratio for that event type.
- A covariate might increase the risk of one event type while decreasing the risk of another.

### Method 2: Fine-Gray Sub-distribution Hazard Model

Directly models the cumulative incidence (not directly provided in scikit-survival; other libraries can be used).

```python
# Note: Fine-Gray models are not directly provided in scikit-survival
# Consider using lifelines or calling R's cmprsk package via rpy2
# from lifelines import CRCSplineFitter
# crc = CRCSplineFitter()
# crc.fit(df, event_col='event', duration_col='time')
```

## Practical Example: Complete Competing Risks Analysis

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sksurv.nonparametric import cumulative_incidence_competing_risks
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.util import Surv

# Simulate competing risks data
np.random.seed(42)
n = 200

# Create features
age = np.random.normal(60, 10, n)
treatment = np.random.choice(['A', 'B'], n)

# Simulate event times and types
# Event types: 0=censored, 1=relapse, 2=death
times = np.random.exponential(100, n)
event_types = np.zeros(n, dtype=int)

# Older age increases both events, Treatment A reduces relapse
for i in range(n):
    if times[i] < 150:  # Event occurs
        # Probability for each event type
        p_relapse = 0.6 if treatment[i] == 'B' else 0.4
        event_types[i] = 1 if np.random.rand() < p_relapse else 2
    else:
        times[i] = 150  # Censored at the end of the study

# Create DataFrame
df = pd.DataFrame({
    'time': times,
    'event_type': event_types,
    'age': age,
    'treatment': treatment
})

# Encode treatment variable
df['treatment_A'] = (df['treatment'] == 'A').astype(int)

# 1. Overall Cumulative Incidence
print("=" * 60)
print("OVERALL CUMULATIVE INCIDENCE")
print("=" * 60)

y_all = Surv.from_arrays(event=(df['event_type'] > 0), time=df['time'])
time_points, cif_relapse, cif_death = cumulative_incidence_competing_risks(y_all)

plt.figure(figsize=(10, 6))
plt.step(time_points, cif_relapse, where='post', label='Relapse', linewidth=2)
plt.step(time_points, cif_death, where='post', label='Death', linewidth=2)
plt.xlabel('Time (days)')
plt.ylabel('Cumulative Incidence')
plt.title('Competing Risks: Relapse vs Death')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

print(f"5-year relapse incidence: {cif_relapse[-1]:.2%}")
print(f"5-year death incidence: {cif_death[-1]:.2%}")

# 2. Stratified by Treatment
print("\n" + "=" * 60)
print("CUMULATIVE INCIDENCE BY TREATMENT")
print("=" * 60)

for trt in ['A', 'B']:
    mask = df['treatment'] == trt
    y_trt = Surv.from_arrays(
        event=(df.loc[mask, 'event_type'] > 0),
        time=df.loc[mask, 'time']
    )
    time_trt, cif1_trt, cif2_trt = cumulative_incidence_competing_risks(y_trt)
    print(f"\nTreatment {trt}:")
    print(f"  5-year relapse: {cif1_trt[-1]:.2%}")
    print(f"  5-year death: {cif2_trt[-1]:.2%}")

# 3. Cause-Specific Hazard Models
print("\n" + "=" * 60)
print("CAUSE-SPECIFIC HAZARD MODELS")
print("=" * 60)

X = df[['age', 'treatment_A']]

# Relapse model (Event type 1)
y_relapse = Surv.from_arrays(
    event=(df['event_type'] == 1),
    time=df['time']
)
cox_relapse = CoxPHSurvivalAnalysis()
cox_relapse.fit(X, y_relapse)

print("\nRelapse Model:")
print(f"  Age:        HR = {np.exp(cox_relapse.coef_[0]):.3f}")
print(f"  Treatment A: HR = {np.exp(cox_relapse.coef_[1]):.3f}")

# Death model (Event type 2)
y_death = Surv.from_arrays(
    event=(df['event_type'] == 2),
    time=df['time']
)
cox_death = CoxPHSurvivalAnalysis()
cox_death.fit(X, y_death)

print("\nDeath Model:")
print(f"  Age:        HR = {np.exp(cox_death.coef_[0]):.3f}")
print(f"  Treatment A: HR = {np.exp(cox_death.coef_[1]):.3f}")

print("\n" + "=" * 60)
```

## Important Notes

### Censoring in Competing Risks

- **Administrative censoring**: Subjects are still at risk when the study ends.
- **Loss to follow-up**: Subjects leave the study before an event occurs.
- **Competing events**: Other events occurred—**NOT** considered censoring for CIF, but treated as censoring for cause-specific models.

### Choosing Between Cause-Specific and Sub-distribution Models

**Cause-Specific Hazard Models:**
- Easier to interpret.
- Directly reflects the effect on the hazard rate.
- Better for understanding etiology.
- Can be fitted using scikit-survival.

**Fine-Gray Sub-distribution Models:**
- Directly models the cumulative incidence.
- Better for prediction and risk stratification.
- More suitable for clinical decision-making.
- Requires using other libraries.

### Common Mistakes

**Mistake 1**: Using Kaplan-Meier to estimate the probability of a specific event.
- **Incorrect**: Performing Kaplan-Meier analysis on event type 1 while treating type 2 as censored.
- **Correct**: Using the Cumulative Incidence Function that accounts for competing risks.

**Mistake 2**: Ignoring competing risks when they are significantly present.
- If the competing event rate is > 10-20%, competing risks methods should be used.

**Mistake 3**: Confusing cause-specific hazards and sub-distribution hazards.
- They answer different questions.
- Choose the appropriate model based on your research question.

## Summary

**Key Functions:**
- `cumulative_incidence_competing_risks`: Estimates the CIF for each event type.
- Fit separate Cox models for cause-specific hazards.
- Use stratified analysis to compare differences between groups.

**Best Practices:**
1. Always plot the Cumulative Incidence Function.
2. Report both specific event incidence and overall incidence.
3. Use cause-specific models in scikit-survival.
4. Consider Fine-Gray models for prediction (using other libraries).
5. Clearly distinguish between competing events and censoring.