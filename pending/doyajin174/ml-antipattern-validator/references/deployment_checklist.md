# ML Deployment Checklist

## Overview

This checklist ensures ML models are production-ready and won't fail due to distribution shift, feedback loops, or monitoring blind spots.

**Key Principle**: Production is different from development. Monitor everything that can change.

## Pre-Deployment Checklist

### ✅ Model Validation

- [ ] **Final test performance documented** with confidence intervals
- [ ] **Baseline comparison** shows meaningful improvement
- [ ] **Per-class metrics** analyzed (not just aggregate)
- [ ] **Error analysis** completed on failure cases
- [ ] **Edge cases tested** (OOV, missing features, extreme values)
- [ ] **Model size acceptable** for production constraints
- [ ] **Inference latency measured** and within requirements

### ✅ Data Validation

- [ ] **Input schema defined** with types and ranges
- [ ] **Missing value handling** strategy documented
- [ ] **Feature scaling** parameters saved
- [ ] **Vocabulary/encoding** mappings persisted
- [ ] **Distribution statistics** recorded (mean, std, quantiles)
- [ ] **Outlier thresholds** defined

### ✅ Code Quality

- [ ] **Model serialization tested** (save/load works)
- [ ] **Reproducibility verified** (same inputs → same outputs)
- [ ] **Dependencies pinned** (requirements.txt with exact versions)
- [ ] **Unit tests written** for preprocessing and inference
- [ ] **Integration tests** for end-to-end pipeline
- [ ] **Error handling** for all failure modes

### ✅ Monitoring Setup

- [ ] **Input drift detection** configured
- [ ] **Prediction drift monitoring** enabled
- [ ] **Performance metrics** logged
- [ ] **Latency tracking** implemented
- [ ] **Error rate alerts** configured
- [ ] **Resource usage** monitored (CPU, memory, GPU)

### ✅ Rollback Strategy

- [ ] **Previous model version** saved and accessible
- [ ] **A/B testing framework** ready
- [ ] **Rollback procedure** documented
- [ ] **Canary deployment** plan defined
- [ ] **Feature flags** for gradual rollout

## Deployment Antipatterns to Avoid

### Antipattern 1: No Monitoring

```python
# ❌ WRONG: Deploy and forget
model = load_model('model.pkl')
app.add_route('/predict', predict_handler)
# No monitoring!

# ✅ CORRECT: Monitor everything
import prometheus_client as prom

input_drift_gauge = prom.Gauge('model_input_drift', 'Input distribution drift')
prediction_latency = prom.Histogram('model_latency_seconds', 'Prediction latency')

@app.route('/predict')
@prediction_latency.time()
def predict(request):
    input_data = request.json

    # Check input drift
    drift_score = check_drift(input_data, reference_distribution)
    input_drift_gauge.set(drift_score)

    if drift_score > 0.1:
        alert('High input drift detected')

    prediction = model.predict(input_data)
    log_prediction(input_data, prediction)

    return {'prediction': prediction}
```

### Antipattern 2: Ignoring Distribution Shift

```python
# ❌ WRONG: Assume distribution stays constant
model = load_model_from_2020()  # 5 years old!
predictions = model.predict(current_data)  # Likely wrong!

# ✅ CORRECT: Monitor and retrain
from scipy.stats import ks_2samp

def monitor_covariate_shift(current_batch, reference_data):
    """Detect P(X) change"""
    for feature in features:
        statistic, p_value = ks_2samp(
            reference_data[feature],
            current_batch[feature]
        )

        if p_value < 0.01:  # Significant shift
            alert(f'Covariate shift detected in {feature}')
            trigger_retraining()
```

### Antipattern 3: Feedback Loop Poisoning

```python
# ❌ WRONG: Train on biased data from own predictions
recommendations = model.recommend(users)
clicks = collect_user_clicks(recommendations)  # Biased!
model.retrain(clicks)  # Reinforces bias!

# ✅ CORRECT: Exploration to get unbiased data
def recommend_with_exploration(user, exploration_rate=0.1):
    if random.random() < exploration_rate:
        # Random recommendation (exploration)
        return random_recommendation()
    else:
        # Model recommendation (exploitation)
        return model.recommend(user)

# Train on exploration data only
exploration_data = filter(lambda x: x.is_exploration, all_data)
model.retrain(exploration_data)
```

### Antipattern 4: No Concept Drift Detection

```python
# ❌ WRONG: Never check if P(Y|X) changed
performance = 0.85  # Measured 6 months ago
# Assume still accurate!

# ✅ CORRECT: Monitor performance over time
performance_history = []

for batch in production_batches:
    current_perf = evaluate(model, batch)
    performance_history.append(current_perf)

    # Detect drift using moving average
    recent_avg = np.mean(performance_history[-10:])
    baseline_avg = np.mean(performance_history[:10])

    if recent_avg < baseline_avg - 0.05:  # 5% drop
        alert('Concept drift detected - performance degraded')
        trigger_retraining()
```

### Antipattern 5: No Graceful Degradation

```python
# ❌ WRONG: Fail completely on invalid input
prediction = model.predict(input_data)  # Crash if invalid!

# ✅ CORRECT: Graceful degradation
def predict_with_fallback(input_data):
    try:
        # Validate input
        if not validate_input(input_data):
            return fallback_prediction(input_data)

        # Check confidence
        prediction, confidence = model.predict_with_confidence(input_data)

        if confidence < 0.5:
            return fallback_prediction(input_data)

        return prediction

    except Exception as e:
        log_error(e)
        return fallback_prediction(input_data)
```

## Monitoring Implementation

### Input Distribution Monitoring

```python
from scipy.stats import ks_2samp, wasserstein_distance
import numpy as np

class InputMonitor:
    def __init__(self, reference_data):
        """Initialize with training data statistics"""
        self.reference_data = reference_data
        self.reference_stats = {
            'mean': reference_data.mean(),
            'std': reference_data.std(),
            'min': reference_data.min(),
            'max': reference_data.max(),
            'quantiles': reference_data.quantile([0.25, 0.5, 0.75])
        }

    def check_drift(self, current_batch):
        """Detect covariate shift"""
        drift_scores = {}

        for feature in self.reference_data.columns:
            # Kolmogorov-Smirnov test
            statistic, p_value = ks_2samp(
                self.reference_data[feature],
                current_batch[feature]
            )

            # Wasserstein distance
            w_dist = wasserstein_distance(
                self.reference_data[feature],
                current_batch[feature]
            )

            drift_scores[feature] = {
                'ks_statistic': statistic,
                'p_value': p_value,
                'wasserstein': w_dist,
                'drifted': p_value < 0.01 or w_dist > 0.1
            }

        return drift_scores

    def check_outliers(self, input_data):
        """Detect out-of-range inputs"""
        outliers = {}

        for feature in input_data.columns:
            ref_min = self.reference_stats['min'][feature]
            ref_max = self.reference_stats['max'][feature]

            below_min = (input_data[feature] < ref_min).sum()
            above_max = (input_data[feature] > ref_max).sum()

            if below_min > 0 or above_max > 0:
                outliers[feature] = {
                    'below_min': below_min,
                    'above_max': above_max
                }

        return outliers
```

### Performance Monitoring

```python
from collections import deque
import numpy as np

class PerformanceMonitor:
    def __init__(self, baseline_performance, window_size=100):
        self.baseline = baseline_performance
        self.window_size = window_size
        self.recent_scores = deque(maxlen=window_size)

    def log_prediction(self, true_label, predicted_label):
        """Log individual prediction for monitoring"""
        correct = (true_label == predicted_label)
        self.recent_scores.append(correct)

    def check_degradation(self, threshold=0.05):
        """Check if performance dropped significantly"""
        if len(self.recent_scores) < self.window_size:
            return False  # Not enough data yet

        current_performance = np.mean(self.recent_scores)
        degradation = self.baseline - current_performance

        if degradation > threshold:
            print(f"⚠️ Performance degradation detected!")
            print(f"   Baseline: {self.baseline:.3f}")
            print(f"   Current: {current_performance:.3f}")
            print(f"   Drop: {degradation:.3f}")
            return True

        return False
```

### Prediction Distribution Monitoring

```python
class PredictionMonitor:
    def __init__(self, training_predictions):
        """Initialize with predictions from training set"""
        self.ref_distribution = np.histogram(
            training_predictions,
            bins=50,
            density=True
        )

    def check_prediction_drift(self, current_predictions):
        """Detect if prediction distribution changed"""
        current_dist = np.histogram(
            current_predictions,
            bins=self.ref_distribution[1],  # Same bins
            density=True
        )

        # Jensen-Shannon divergence
        from scipy.spatial.distance import jensenshannon
        js_div = jensenshannon(
            self.ref_distribution[0],
            current_dist[0]
        )

        if js_div > 0.1:  # Threshold
            print(f"⚠️ Prediction drift detected (JS divergence: {js_div:.3f})")
            return True

        return False
```

## Retraining Strategy

### When to Retrain

```python
class RetrainingTrigger:
    def __init__(self):
        self.performance_monitor = PerformanceMonitor(baseline=0.85)
        self.input_monitor = InputMonitor(reference_data)
        self.last_retrain = datetime.now()

    def should_retrain(self, current_batch, labels):
        """Determine if model needs retraining"""

        # Check 1: Performance degradation
        for true, pred in zip(labels, current_batch['predictions']):
            self.performance_monitor.log_prediction(true, pred)

        if self.performance_monitor.check_degradation():
            return True, 'Performance degraded'

        # Check 2: Input drift
        drift_scores = self.input_monitor.check_drift(current_batch)
        drifted_features = [
            feat for feat, scores in drift_scores.items()
            if scores['drifted']
        ]

        if len(drifted_features) > 3:  # More than 3 features drifted
            return True, f'Input drift in {drifted_features}'

        # Check 3: Time since last retrain
        days_since_retrain = (datetime.now() - self.last_retrain).days
        if days_since_retrain > 90:  # 3 months
            return True, 'Scheduled retraining (90 days)'

        return False, 'No retraining needed'
```

### Safe Retraining Process

```python
def safe_retrain_workflow():
    """Safe retraining with validation gates"""

    # 1. Collect new data (with exploration)
    new_data = collect_recent_data(include_exploration=True)

    # 2. Combine with historical data
    combined_data = pd.concat([historical_data, new_data])

    # 3. Proper train/val/test split
    train, temp = train_test_split(combined_data, test_size=0.3)
    val, test = train_test_split(temp, test_size=0.5)

    # 4. Train new model
    new_model = train_model(train)

    # 5. Validate on validation set
    val_score = evaluate(new_model, val)

    if val_score < current_model_validation_score:
        print("⚠️ New model worse than current - aborting")
        return current_model

    # 6. Final test on held-out test set
    test_score = evaluate(new_model, test)

    if test_score < current_model_test_score - 0.05:
        print("⚠️ New model significantly worse - aborting")
        return current_model

    # 7. A/B test in production
    ab_test_result = run_ab_test(
        model_a=current_model,
        model_b=new_model,
        duration_hours=24
    )

    if ab_test_result['b_better']:
        print("✅ New model validated - deploying")
        return new_model
    else:
        print("⚠️ A/B test failed - keeping current model")
        return current_model
```

## Deployment Checklist Summary

### Before Production

- [ ] All pre-deployment checks passed
- [ ] Monitoring systems tested
- [ ] Alerting configured
- [ ] Rollback plan documented
- [ ] Team trained on incident response

### During Deployment

- [ ] Canary deployment (10% traffic first)
- [ ] Monitor key metrics for 24 hours
- [ ] A/B test running
- [ ] No alerts triggered
- [ ] Gradual rollout to 100%

### After Deployment

- [ ] Daily monitoring checks
- [ ] Weekly performance review
- [ ] Monthly drift analysis
- [ ] Quarterly retraining evaluation
- [ ] Continuous improvement planning

## Emergency Rollback Procedure

```python
def emergency_rollback():
    """Quick rollback to previous version"""

    print("🚨 Executing emergency rollback")

    # 1. Load previous model version
    previous_model = load_model('model_v{previous_version}.pkl')

    # 2. Swap models atomically
    with model_lock:
        global current_model
        current_model = previous_model

    # 3. Clear problematic cached predictions
    clear_prediction_cache()

    # 4. Notify team
    send_alert('Emergency rollback executed')

    # 5. Log incident
    log_incident({
        'timestamp': datetime.now(),
        'action': 'rollback',
        'reason': 'production_issue',
        'previous_version': previous_version,
        'current_version': current_version - 1
    })

    print("✅ Rollback complete")
```

---

**Remember**: Production ML is about continuous monitoring and adaptation. The deployment is just the beginning!
