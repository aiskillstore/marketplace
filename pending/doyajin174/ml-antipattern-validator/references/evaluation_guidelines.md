# ML Evaluation Guidelines - Best Practices

## Overview

Proper evaluation is critical for understanding true model performance. This guide covers evaluation methodology, metric selection, and common mistakes to avoid.

**Key Principle**: Test on data the model has NEVER seen during any phase of development.

## The Three-Way Split

### Standard Split Strategy

```python
# ✅ CORRECT: Three-way split for proper evaluation
from sklearn.model_selection import train_test_split

# 1. Initial split: 80% work, 20% final test
X_work, X_test, y_work, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Split work set: 80% train, 20% validation
X_train, X_val, y_train, y_val = train_test_split(X_work, y_work, test_size=0.25, random_state=42)
# Result: 60% train, 20% val, 20% test

# 3. Training phase
model.fit(X_train, y_train)

# 4. Validation phase (hyperparameter tuning)
val_score = model.score(X_val, y_val)
# Tune based on validation performance

# 5. Final evaluation (ONE TIME ONLY)
final_score = model.score(X_test, y_test)
```

### Why Three Sets?

- **Training Set**: Model learns patterns
- **Validation Set**: Hyperparameter tuning, model selection
- **Test Set**: Final unbiased performance estimate

**Critical Rule**: Test set used EXACTLY ONCE, after all development decisions finalized.

## Metric Selection Guide

### Classification Metrics

#### Binary Classification

```python
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score
)

# Choose metric based on business objective:

# 1. Balanced classes + symmetric cost
metric = accuracy_score  # Proportion of correct predictions

# 2. Imbalanced classes
metric = f1_score  # Harmonic mean of precision/recall
# or
metric = average_precision_score  # Area under PR curve

# 3. Ranking quality (e.g., search)
metric = roc_auc_score  # Area under ROC curve

# 4. Minimize false positives (e.g., spam)
metric = precision_score  # Of predicted positives, how many are correct?

# 5. Minimize false negatives (e.g., fraud, disease)
metric = recall_score  # Of actual positives, how many did we catch?
```

#### Multi-Class Classification

```python
from sklearn.metrics import classification_report

# Always use classification_report for multi-class
print(classification_report(y_true, y_pred, digits=3))

# Output shows per-class precision/recall/f1:
#               precision    recall  f1-score   support
#
#      class_0      0.850     0.920     0.884       100
#      class_1      0.920     0.880     0.900       120
#      class_2      0.750     0.700     0.724        80
```

### Regression Metrics

```python
from sklearn.metrics import (
    mean_absolute_error,  # MAE
    mean_squared_error,   # MSE
    r2_score,
    mean_absolute_percentage_error  # MAPE
)

# Choose metric based on error sensitivity:

# 1. Robust to outliers
metric = mean_absolute_error  # Average absolute difference

# 2. Penalize large errors heavily
metric = mean_squared_error  # Squared differences

# 3. Variance explained
metric = r2_score  # R² coefficient (0 to 1)

# 4. Relative error (for varying scales)
metric = mean_absolute_percentage_error  # MAPE
```

### Ranking Metrics

```python
from sklearn.metrics import (
    ndcg_score,  # Normalized Discounted Cumulative Gain
    average_precision_score  # AP@K
)

# For search/recommendation systems
ndcg = ndcg_score(y_true, y_scores)  # Position-aware ranking quality
ap_at_k = average_precision_score(y_true, y_scores)  # Precision across thresholds
```

## Evaluation Methodology

### Cross-Validation Best Practices

```python
from sklearn.model_selection import cross_validate, StratifiedKFold

# ✅ CORRECT: Stratified K-Fold for classification
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_validate(
    model,
    X,
    y,
    cv=cv,
    scoring=['accuracy', 'f1', 'roc_auc'],
    return_train_score=True,
    n_jobs=-1
)

# Check for overfitting
train_acc = scores['train_accuracy'].mean()
val_acc = scores['test_accuracy'].mean()
if train_acc - val_acc > 0.15:  # 15% gap
    print("⚠️ Possible overfitting detected")
```

### Time Series Evaluation

```python
from sklearn.model_selection import TimeSeriesSplit

# ✅ CORRECT: Time-aware cross-validation
tscv = TimeSeriesSplit(n_splits=5, gap=7)  # 7-day gap between train/test

for train_idx, test_idx in tscv.split(X):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    # Verify temporal ordering
    assert X_train.index.max() < X_test.index.min() - pd.Timedelta(days=7)

    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
```

## Common Evaluation Mistakes

### Mistake 1: Testing on Training Data

```python
# ❌ WRONG: Same data for training and testing
model.fit(X, y)
accuracy = model.score(X, y)  # Measures memorization, not generalization!

# ✅ CORRECT: Separate test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model.fit(X_train, y_train)
accuracy = model.score(X_test, y_test)  # Real generalization
```

### Mistake 2: Multiple Peeks at Test Set

```python
# ❌ WRONG: Tuning based on test performance
for param in param_grid:
    model.set_params(**param)
    model.fit(X_train, y_train)
    test_score = model.score(X_test, y_test)  # Leakage!
    if test_score > best_score:
        best_params = param

# ✅ CORRECT: Use validation set for tuning
for param in param_grid:
    model.set_params(**param)
    model.fit(X_train, y_train)
    val_score = model.score(X_val, y_val)  # Validation for tuning
    if val_score > best_score:
        best_params = param

# Final test (once only)
model.set_params(**best_params)
model.fit(X_train, y_train)
final_score = model.score(X_test, y_test)
```

### Mistake 3: Ignoring Class Imbalance

```python
# ❌ WRONG: High accuracy on imbalanced data
# Dataset: 99% negative, 1% positive
accuracy = 0.99  # Looks great!
# But model predicts all negative → 0% recall for positive class

# ✅ CORRECT: Use appropriate metrics
from sklearn.metrics import classification_report, confusion_matrix

print(classification_report(y_true, y_pred))
#               precision    recall  f1-score   support
#
#      negative      0.990     1.000     0.995      9900
#      positive      0.000     0.000     0.000       100
#
# Reveals: Model catches NO positive cases!
```

### Mistake 4: Wrong Metric for Business Goal

```python
# ❌ WRONG: Optimizing accuracy for ranking task
# Goal: Rank search results
model.optimize(metric='accuracy')  # Wrong objective!

# ✅ CORRECT: Use ranking metric
from sklearn.metrics import ndcg_score
model.optimize(metric=ndcg_score)  # Optimize ranking quality
```

## Evaluation Checklist

### Before Training

- [ ] Three-way split: train/val/test or CV + held-out test
- [ ] Test set completely isolated (never touched)
- [ ] Validation strategy chosen (CV, holdout, time-aware)
- [ ] Metrics aligned with business objective
- [ ] Baseline model defined (random, majority class, simple heuristic)
- [ ] Class distribution checked (balanced vs imbalanced)
- [ ] Temporal ordering verified (for time series)
- [ ] Group structure identified (for grouped data)

### During Training

- [ ] Only validation set used for decisions
- [ ] Hyperparameters tuned on validation, not test
- [ ] Early stopping based on validation loss
- [ ] Model selection based on validation performance
- [ ] Overfitting monitored (train vs val gap)
- [ ] Learning curves plotted
- [ ] Regularization strength tuned on validation

### Final Evaluation

- [ ] Test set used EXACTLY ONCE
- [ ] No further tuning after seeing test results
- [ ] Multiple metrics reported (not just one)
- [ ] Confidence intervals calculated
- [ ] Per-class performance analyzed
- [ ] Error analysis on failures
- [ ] Comparison to baseline
- [ ] Results documented with methodology

## Reporting Results

### Minimum Reporting Standards

```python
# Always report:
# 1. Test performance
# 2. Confidence intervals
# 3. Baseline comparison
# 4. Multiple metrics

from scipy import stats

def report_results(y_true, y_pred, y_pred_baseline):
    """Comprehensive result reporting"""

    # Main metrics
    print("=== Test Set Results ===")
    print(f"\nAccuracy: {accuracy_score(y_true, y_pred):.3f}")
    print(f"F1 Score: {f1_score(y_true, y_pred, average='weighted'):.3f}")
    print(f"ROC-AUC: {roc_auc_score(y_true, y_pred):.3f}")

    # Confidence intervals (bootstrap)
    from sklearn.utils import resample
    scores = []
    for _ in range(1000):
        y_true_boot, y_pred_boot = resample(y_true, y_pred)
        scores.append(accuracy_score(y_true_boot, y_pred_boot))

    ci_lower = np.percentile(scores, 2.5)
    ci_upper = np.percentile(scores, 97.5)
    print(f"\nAccuracy 95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]")

    # Baseline comparison
    baseline_acc = accuracy_score(y_true, y_pred_baseline)
    improvement = accuracy_score(y_true, y_pred) - baseline_acc
    print(f"\nBaseline accuracy: {baseline_acc:.3f}")
    print(f"Improvement: {improvement:.3f} ({improvement/baseline_acc*100:.1f}%)")

    # Per-class performance
    print("\n=== Per-Class Performance ===")
    print(classification_report(y_true, y_pred))

    # Confusion matrix
    print("\n=== Confusion Matrix ===")
    print(confusion_matrix(y_true, y_pred))
```

## Generalization vs Memorization

### Testing Both

```python
# Always test both generalization and memorization
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model.fit(X_train, y_train)

# Memorization (training performance)
train_acc = model.score(X_train, y_train)

# Generalization (test performance)
test_acc = model.score(X_test, y_test)

print(f"Training accuracy: {train_acc:.3f}")
print(f"Test accuracy: {test_acc:.3f}")
print(f"Generalization gap: {train_acc - test_acc:.3f}")

# Interpretation
if test_acc > train_acc:
    print("✅ Excellent! Generalization > Memorization")
    print("   Model learned semantic patterns, not memorization")
elif train_acc - test_acc < 0.05:
    print("✅ Good! Small generalization gap")
elif train_acc - test_acc < 0.15:
    print("⚠️ Moderate overfitting")
else:
    print("❌ Severe overfitting! Model memorized training data")
```

### Out-of-Vocabulary Testing

```python
# Test robustness to unseen tokens/patterns

# Test 1: In-vocabulary (similar to training)
test_in_vocab = ["hi there", "thanks a lot"]  # Words seen during training
acc_in_vocab = evaluate(model, test_in_vocab)

# Test 2: Out-of-vocabulary (completely new words)
test_oov = ["greetings friend", "many thanks"]  # New words
acc_oov = evaluate(model, test_oov)

print(f"In-vocabulary accuracy: {acc_in_vocab:.1%}")
print(f"OOV accuracy: {acc_oov:.1%}")

# OOV performance indicates true generalization ability
```

## Statistical Significance Testing

### Comparing Models

```python
from scipy.stats import wilcoxon

# Compare two models on same data
scores_model_a = cross_val_score(model_a, X, y, cv=10)
scores_model_b = cross_val_score(model_b, X, y, cv=10)

# Wilcoxon signed-rank test
statistic, p_value = wilcoxon(scores_model_a, scores_model_b)

if p_value < 0.05:
    mean_a = scores_model_a.mean()
    mean_b = scores_model_b.mean()
    better = 'A' if mean_a > mean_b else 'B'
    print(f"Model {better} is significantly better (p={p_value:.4f})")
else:
    print(f"No significant difference (p={p_value:.4f})")
```

## Evaluation Anti-Patterns Summary

### DO ✅

- Split data BEFORE any analysis
- Use validation set for ALL development decisions
- Use test set ONCE for final evaluation
- Report multiple metrics with confidence intervals
- Compare to baseline
- Analyze per-class performance
- Document methodology

### DON'T ❌

- Test on training data
- Peek at test set multiple times
- Tune on test set
- Report only accuracy on imbalanced data
- Ignore baseline comparison
- Skip confidence intervals
- Use wrong metric for task

## Quick Reference

| Task Type | Recommended Metric | CV Strategy |
|-----------|-------------------|-------------|
| Balanced classification | Accuracy, ROC-AUC | StratifiedKFold |
| Imbalanced classification | F1, PR-AUC | StratifiedKFold |
| Multi-class | Per-class F1 | StratifiedKFold |
| Regression | MAE, RMSE, R² | KFold |
| Time series | MAE, MAPE | TimeSeriesSplit |
| Ranking | NDCG, MAP | GroupKFold |
| Grouped data | Domain metric | GroupKFold |
