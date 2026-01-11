# Data Leakage Patterns - Comprehensive Reference

## Overview

Data leakage is the #1 cause of invalid ML results. This document provides in-depth explanations, detection methods, and prevention strategies for all types of leakage.

**Key Principle**: Information from outside the training set must never influence model training.

## Pattern 1: Target Leakage

### Definition
Features contain information that would not be available at prediction time, or that are direct consequences of the target variable.

### Real-World Examples

**Example 1: Fraud Detection**
```python
# ❌ WRONG
features = [
    'transaction_amount',
    'refund_issued',  # ⚠️ Only known AFTER fraud detected!
    'account_suspended'  # ⚠️ Consequence of fraud detection!
]

# ✅ CORRECT
features = [
    'transaction_amount',
    'device_id',
    'time_of_day',
    'merchant_category',
    'previous_transaction_count'
]
```

**Example 2: Medical Diagnosis**
```python
# ❌ WRONG
features = [
    'symptoms',
    'medication_prescribed',  # ⚠️ Prescribed AFTER diagnosis!
    'recovery_time'  # ⚠️ Only known in future!
]

# ✅ CORRECT
features = [
    'symptoms',
    'vital_signs',
    'medical_history',
    'age',
    'lab_test_results'
]
```

### Detection Methods

```python
def detect_target_leakage(df, features, target):
    """Detect suspiciously high correlations"""
    correlations = {}

    for feature in features:
        # Pearson correlation for numerical features
        if df[feature].dtype in ['float64', 'int64']:
            corr = df[feature].corr(df[target])
            correlations[feature] = abs(corr)

        # Mutual information for categorical features
        else:
            from sklearn.feature_selection import mutual_info_classif
            mi = mutual_info_classif(
                df[[feature]].fillna(0),
                df[target],
                random_state=42
            )[0]
            correlations[feature] = mi

    # Flag suspiciously high correlations
    suspicious = {
        feat: corr for feat, corr in correlations.items()
        if corr > 0.95  # Very high correlation threshold
    }

    if suspicious:
        print("⚠️ Potential target leakage detected:")
        for feat, corr in suspicious.items():
            print(f"  {feat}: {corr:.3f}")

    return suspicious
```

### Prevention Checklist

- [ ] Review data collection timestamp - is feature available at prediction time?
- [ ] Check feature definitions - are any derived from the target?
- [ ] Verify feature semantics - do any depend on future information?
- [ ] Analyze correlation matrix - any suspiciously perfect correlations?
- [ ] Consult domain experts - ask "would we know this before predicting?"

## Pattern 2: Temporal Leakage

### Definition
Using future information to predict past events, violating causality.

### Real-World Examples

**Example 1: Stock Price Prediction**
```python
# ❌ WRONG: Using tomorrow's volume to predict today's price
df['feature_volume_tomorrow'] = df['volume'].shift(-1)  # Future info!
df['target_price_today'] = df['price']

# ✅ CORRECT: Only use past/present information
df['feature_volume_yesterday'] = df['volume'].shift(1)
df['feature_volume_last_week'] = df['volume'].rolling(7).mean()
df['target_price_tomorrow'] = df['price'].shift(-1)
```

**Example 2: Time Series with Wrong Split**
```python
# ❌ WRONG: Random shuffle breaks temporal order
X_train, X_test = train_test_split(df, test_size=0.2)
# Result: Training on 2024 data, testing on 2023 data!

# ✅ CORRECT: Respect temporal ordering
cutoff_date = pd.Timestamp('2024-01-01')
train = df[df['date'] < cutoff_date]
test = df[df['date'] >= cutoff_date]
```

### Detection Methods

```python
def detect_temporal_leakage(train_df, test_df, date_column):
    """Verify temporal ordering"""
    train_dates = train_df[date_column]
    test_dates = test_df[date_column]

    train_min, train_max = train_dates.min(), train_dates.max()
    test_min, test_max = test_dates.min(), test_dates.max()

    print(f"Training period: {train_min} to {train_max}")
    print(f"Testing period: {test_min} to {test_max}")

    # Check for temporal leakage
    if train_max > test_min:
        overlap_days = (train_max - test_min).days
        raise ValueError(
            f"⚠️ Temporal leakage detected! "
            f"Training data extends {overlap_days} days into test period"
        )

    # Check for suspicious gaps
    gap = (test_min - train_max).days
    if gap > 365:
        warnings.warn(
            f"Large gap ({gap} days) between train and test - "
            f"possible distribution shift"
        )

    print("✅ Temporal ordering verified")
```

### Prevention Checklist

- [ ] Always split by time, never shuffle temporal data
- [ ] Use `TimeSeriesSplit` for cross-validation
- [ ] Check feature creation - no `.shift(-n)` with negative n
- [ ] Verify train dates < test dates
- [ ] Avoid lookback windows that span into future

## Pattern 3: Preprocessing Leakage

### Definition
Fitting preprocessing transformations (scaling, imputation, encoding) on entire dataset before splitting.

### Real-World Examples

**Example 1: Standardization Leakage**
```python
# ❌ WRONG: Scaler sees test set statistics
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # Fit on ALL data!
X_train, X_test = train_test_split(X_scaled)
# Test set statistics influenced the scaling!

# ✅ CORRECT: Fit only on training data
X_train, X_test = train_test_split(X)
scaler = StandardScaler()
scaler.fit(X_train)  # Only training data
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

**Example 2: Imputation Leakage**
```python
# ❌ WRONG: Imputer learns from test set
imputer = SimpleImputer(strategy='mean')
X_imputed = imputer.fit_transform(X)  # Mean includes test data!
X_train, X_test = train_test_split(X_imputed)

# ✅ CORRECT: Fit imputer on training data only
X_train, X_test = train_test_split(X)
imputer = SimpleImputer(strategy='mean')
imputer.fit(X_train)  # Mean from training only
X_train_imputed = imputer.transform(X_train)
X_test_imputed = imputer.transform(X_test)
```

**Example 3: Feature Selection Leakage**
```python
# ❌ WRONG: Select features using all data
from sklearn.feature_selection import SelectKBest
selector = SelectKBest(k=10)
X_selected = selector.fit_transform(X, y)  # Sees test targets!
X_train, X_test, y_train, y_test = train_test_split(X_selected, y)

# ✅ CORRECT: Select features using training data only
X_train, X_test, y_train, y_test = train_test_split(X, y)
selector = SelectKBest(k=10)
selector.fit(X_train, y_train)  # Only training data
X_train_selected = selector.transform(X_train)
X_test_selected = selector.transform(X_test)
```

### Detection Methods

```python
def detect_preprocessing_leakage(preprocessor, X_train):
    """Check if preprocessor saw more samples than training set"""

    # For sklearn transformers
    if hasattr(preprocessor, 'n_samples_seen_'):
        n_seen = preprocessor.n_samples_seen_
        n_train = len(X_train)

        if n_seen > n_train:
            raise ValueError(
                f"⚠️ Preprocessing leakage detected! "
                f"Preprocessor saw {n_seen} samples, "
                f"but training set has only {n_train}"
            )

    # For custom transformers
    if hasattr(preprocessor, 'statistics_'):
        # Check if statistics are reasonable
        stats = preprocessor.statistics_
        X_train_stats = X_train.describe()

        # Compare means (should be close if no leakage)
        for i, (fitted_stat, expected_stat) in enumerate(
            zip(stats, X_train_stats.loc['mean'])
        ):
            diff = abs(fitted_stat - expected_stat)
            if diff > 0.1 * abs(expected_stat):
                warnings.warn(
                    f"Feature {i}: Fitted statistic differs from training "
                    f"by {diff:.2f} - possible leakage"
                )
```

### Prevention Checklist

- [ ] Always split BEFORE any preprocessing
- [ ] Use sklearn `Pipeline` to ensure correct order
- [ ] Fit all transformers on training data only
- [ ] Apply `.transform()` (not `.fit_transform()`) to test set
- [ ] Check `n_samples_seen_` attribute after fitting

## Pattern 4: Group Leakage

### Definition
Related or correlated samples (same user, same patient, same video) split across train and test sets.

### Real-World Examples

**Example 1: User Behavior Prediction**
```python
# ❌ WRONG: Same user in both train and test
train, test = train_test_split(df, test_size=0.2)
# User ID 42 appears in both sets!

# ✅ CORRECT: Split by user ID
from sklearn.model_selection import GroupShuffleSplit
splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(splitter.split(X, y, groups=df['user_id']))
train = df.iloc[train_idx]
test = df.iloc[test_idx]
```

**Example 2: Video Frame Classification**
```python
# ❌ WRONG: Frames from same video in train and test
# Training on frame 1, testing on frame 2 of same video = leakage!

# ✅ CORRECT: Split by video ID
unique_videos = df['video_id'].unique()
train_videos, test_videos = train_test_split(unique_videos, test_size=0.2)
train = df[df['video_id'].isin(train_videos)]
test = df[df['video_id'].isin(test_videos)]
```

### Detection Methods

```python
def detect_group_leakage(train_df, test_df, group_column):
    """Detect overlapping groups between train and test"""
    train_groups = set(train_df[group_column].unique())
    test_groups = set(test_df[group_column].unique())

    overlap = train_groups & test_groups

    if overlap:
        print(f"⚠️ Group leakage detected!")
        print(f"  Total groups in train: {len(train_groups)}")
        print(f"  Total groups in test: {len(test_groups)}")
        print(f"  Overlapping groups: {len(overlap)}")
        print(f"  Overlap percentage: {len(overlap)/len(test_groups)*100:.1f}%")

        # Show examples
        print(f"\n  Example overlapping groups: {list(overlap)[:5]}")

        raise ValueError(
            f"Found {len(overlap)} groups in both train and test sets!"
        )

    print("✅ No group leakage detected")
```

### Prevention Checklist

- [ ] Identify grouping variables (user_id, patient_id, session_id, video_id)
- [ ] Use `GroupShuffleSplit` or `GroupKFold` for splitting
- [ ] Verify zero overlap in group identifiers
- [ ] Consider hierarchical groups (user → session → event)
- [ ] Document grouping strategy in code comments

## Pattern 5: Cross-Validation Fold Leakage

### Definition
Preprocessing applied across all CV folds simultaneously, allowing information flow between folds.

### Real-World Examples

```python
# ❌ WRONG: Fit on all data, then CV
imputer = SimpleImputer()
X_imputed = imputer.fit_transform(X)  # Sees all folds!
cv_scores = cross_val_score(model, X_imputed, y, cv=5)

# ✅ CORRECT: Use Pipeline for proper CV
from sklearn.pipeline import Pipeline
pipeline = Pipeline([
    ('imputer', SimpleImputer()),
    ('scaler', StandardScaler()),
    ('model', RandomForestClassifier())
])
cv_scores = cross_val_score(pipeline, X, y, cv=5)
# Each fold fits imputer/scaler independently
```

### Prevention Checklist

- [ ] Always use `Pipeline` for CV
- [ ] Never call `.fit()` on full dataset before CV
- [ ] Verify each fold's preprocessing is independent
- [ ] Use `cross_validate()` with `return_train_score=True` to check overfitting

## Pattern 6: Data Augmentation Leakage

### Definition
Augmenting data before splitting creates near-duplicate samples across train/test boundary.

### Real-World Examples

```python
# ❌ WRONG: Augment then split
X_augmented = augment_images(X)  # Creates similar images
X_train, X_test = train_test_split(X_augmented)
# Original image in test, augmented version in train!

# ✅ CORRECT: Split then augment training only
X_train, X_test = train_test_split(X)
X_train_augmented = augment_images(X_train)
# Test set remains pristine
```

### Prevention Checklist

- [ ] Always split before augmentation
- [ ] Only augment training set
- [ ] Track original sample IDs to verify no overlap
- [ ] Document augmentation strategy

## Summary: Universal Leakage Prevention Rules

1. **Split First, Process Second**: Always split data BEFORE any transformations
2. **Fit on Train Only**: All `.fit()` calls use training data exclusively
3. **Respect Time**: Never use future to predict past
4. **Respect Groups**: Keep related samples together
5. **Use Pipelines**: Automate correct preprocessing order
6. **Verify Always**: Check for leakage before trusting results

## Common Pitfalls

**Pitfall 1**: "But my test accuracy is so high!"
→ High accuracy might indicate leakage, not a good model

**Pitfall 2**: "I only used test set for scaling"
→ Even scaling on test set is leakage

**Pitfall 3**: "Cross-validation handles preprocessing"
→ Not without Pipeline, it doesn't

**Pitfall 4**: "Same user is fine if different sessions"
→ Still leakage if user behavior is predictive

**Pitfall 5**: "I need test set for normalization"
→ No, you fit normalizer on train, apply to test
