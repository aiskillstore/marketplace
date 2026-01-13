# ML Antipattern Reference

상세 예시 및 검증 코드 모음입니다. 핵심 내용은 `SKILL.md` 참조.

---

## Category 4: Statistical Errors 📊

### 4.1 P-Hacking
**Problem**: Multiple testing without Bonferroni or FDR correction.

```python
❌ WRONG: Test 100 hypotheses at α=0.05
for feature in features:  # 100 features
    p_value = test(feature, target)
    if p_value < 0.05:  # 5 false positives expected!
        print(f"{feature} is significant")

✅ CORRECT: Bonferroni correction
alpha = 0.05 / len(features)  # Corrected threshold
```

### 4.2 Selection Bias
```python
❌ WRONG: Train on volunteer survey responses
train_data = voluntary_survey_responses  # Self-selection bias!

✅ CORRECT: Use random sampling or adjust for bias
train_data = resample(population, n_samples=1000, stratify=demographics)
```

### 4.3 Survivorship Bias
```python
❌ WRONG: Train stock predictor on companies still operating
train_data = currently_trading_stocks  # Ignores bankrupt companies!

✅ CORRECT: Include delisted/failed companies
train_data = pd.concat([currently_trading_stocks, delisted_stocks, bankrupt_companies])
```

### 4.4 Simpson's Paradox
```python
❌ WRONG: Aggregate without grouping
overall_effect = df['outcome'].mean()  # Positive

✅ CORRECT: Check subgroup effects
for group in df['group'].unique():
    group_effect = df[df['group'] == group]['outcome'].mean()
```

### 4.5 Regression to the Mean
```python
❌ WRONG: Select worst performers, re-test, claim improvement
worst = df[df['score'] < 20]
retest = measure_again(worst)
print(f"Improved by {retest.mean() - worst.mean()}")  # Natural regression!

✅ CORRECT: Use control group
treatment = df.sample(frac=0.5)
control = df.drop(treatment.index)
```

---

## Category 5: Deployment Issues 🚀

### 5.1 Covariate Shift
```python
✅ CORRECT: Monitor input distribution shift
from scipy.stats import ks_2samp
for feature in features:
    statistic, p_value = ks_2samp(train[feature], production[feature])
    if p_value < 0.01:
        alert(f"Covariate shift detected in {feature}")
```

### 5.2 Concept Drift
```python
✅ CORRECT: Monitor performance and retrain
performance_history = []
for batch in production_batches:
    current_performance = evaluate(model, batch)
    performance_history.append(current_performance)
    if detect_drift(performance_history):
        retrain_model(recent_data)
```

### 5.3 Feedback Loop Poisoning
```python
✅ CORRECT: Exploration vs exploitation
recommendations = [
    model.predict(user) if random() > 0.1  # 90% exploitation
    else random_recommendation()  # 10% exploration
    for user in users
]
```

### 5.4 Label Shift
```python
✅ CORRECT: Recalibrate threshold for new distribution
from sklearn.calibration import CalibratedClassifierCV
calibrated_model = CalibratedClassifierCV(model, method='isotonic')
calibrated_model.fit(recent_data, recent_labels)
```

### 5.5 Online Learning Memory Leakage
```python
✅ CORRECT: Explicitly separate test set
test_sample_ids = load_test_ids()
for sample in production_stream:
    prediction = model.predict(sample)
    if sample.id not in test_sample_ids and sample.has_label():
        online_buffer.add(sample)
```

---

## Category 6: Architecture Mistakes 🏗️

### 6.1 Softmax Temperature Miscalibration
```python
✅ CORRECT: Calibrate temperature on validation set
best_temp = find_best_temperature(model, val_data)  # e.g., temp=2.5
probs = softmax(logits / best_temp)  # Calibrated [0.7, 0.2, 0.1]
```

### 6.2 Bottleneck Layers Too Restrictive
```python
✅ CORRECT: Use intrinsic dimensionality estimation
from sklearn.decomposition import PCA
pca = PCA(n_components=0.95)  # Preserve 95% variance
pca.fit(X_train)
bottleneck_dim = pca.n_components_
```

### 6.3 Wrong Loss Function for Task
```python
✅ CORRECT: Use ranking loss
from pytorch_metric_learning.losses import TripletMarginLoss
loss = TripletMarginLoss()  # Optimizes ranking directly
```

### 6.4 Ignoring Class Weights in Multi-Class
```python
✅ CORRECT: Use inverse frequency weights
from sklearn.utils.class_weight import compute_class_weight
class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
criterion = nn.CrossEntropyLoss(weight=torch.tensor(class_weights))
```

---

## Quick Reference Scenarios

### Scenario 1: Splitting Time Series Data
```python
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5)
for train_idx, test_idx in tscv.split(X):
    X_train, X_test = X[train_idx], X[test_idx]
    assert X_train.index.max() < X_test.index.min()
```

### Scenario 2: Evaluating Generalization
```python
# 1. Split data FIRST
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 2. Train on training data
model.fit(X_train, y_train)

# 3. Test on UNSEEN test data
test_accuracy = model.score(X_test, y_test)

# 4. Verify generalization
if train_accuracy > test_accuracy + 0.2:
    warnings.warn("Possible overfitting detected")
```

### Scenario 3: Handling Imbalanced Classes
```python
from sklearn.utils.class_weight import compute_class_weight
class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
criterion = nn.CrossEntropyLoss(weight=torch.tensor(class_weights))
print(classification_report(y_true, y_pred))
```

### Scenario 4: Preventing Benchmark Contamination
```python
benchmark_hashes = load_benchmark_hashes()
training_data = [sample for sample in web_corpus if hash(sample) not in benchmark_hashes]

def check_ngram_overlap(train, test, n=13):
    overlap = set(extract_ngrams(train, n)) & set(extract_ngrams(test, n))
    contamination = len(overlap) / len(set(extract_ngrams(test, n)))
    assert contamination < 0.01, f"Contamination: {contamination:.2%}"
```

---

## Validation Scripts

```bash
# Data Leakage Detector
python scripts/validate_split.py --train train.csv --test test.csv

# Evaluation Validator
python scripts/validate_evaluation.py --test-data test.csv --train-data train.csv

# Deployment Readiness Checker
python scripts/validate_deployment.py --model model.pkl --production-data prod.csv
```
