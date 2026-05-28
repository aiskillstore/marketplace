# Ensemble Models for Survival Analysis

## Random Survival Forests

### Overview

Random Survival Forests (RSF) extend the Random Forest algorithm to handle censored data in survival analysis. It works by building multiple decision trees on bootstrap samples and aggregating their predictions.

### How It Works

1.  **Bootstrap Sampling**: Each tree is built on a different bootstrap sample of the training data.
2.  **Feature Randomness**: At each node, only a random subset of features is considered for splitting.
3.  **Survival Function Estimation**: At the leaf nodes, survival functions are calculated using Kaplan-Meier and Nelson-Aalen estimators.
4.  **Ensemble Aggregation**: The final prediction is the average of the survival functions from all trees.

### When to Use

-   Complex non-linear relationships exist between features and survival.
-   No assumptions about functional forms are desired.
-   Robust predictions are needed with minimal hyperparameter tuning.
-   Feature importance estimates are required.
-   Sufficient sample size (typically n > 100).

### Key Parameters

-   `n_estimators`: Number of trees (Default: 100)
    -   More trees = more stable predictions, but slower speed.
    -   Typical range: 100-1000.

-   `max_depth`: Maximum depth of the tree
    -   Controls tree complexity.
    -   None = nodes are expanded until pure or until `min_samples_split` is reached.

-   `min_samples_split`: Minimum number of samples required to split a node (Default: 6)
    -   Higher values = higher regularization.

-   `min_samples_leaf`: Minimum number of samples required in a leaf node (Default: 3)
    -   Prevents overfitting to small groups.

-   `max_features`: Number of features to consider at each split
    -   'sqrt': sqrt(n_features) - a good default.
    -   'log2': log2(n_features).
    -   None: All features.

-   `n_jobs`: Number of parallel tasks (-1 uses all processors).

### Example Usage

```python
from sksurv.ensemble import RandomSurvivalForest
from sksurv.datasets import load_breast_cancer

# Load data
X, y = load_breast_cancer()

# Fit Random Survival Forest
rsf = RandomSurvivalForest(n_estimators=1000,
                           min_samples_split=10,
                           min_samples_leaf=15,
                           max_features="sqrt",
                           n_jobs=-1,
                           random_state=42)
rsf.fit(X, y)

# Predict risk scores
risk_scores = rsf.predict(X)

# Predict survival functions
surv_funcs = rsf.predict_survival_function(X)

# Predict cumulative hazard functions
chf_funcs = rsf.predict_cumulative_hazard_function(X)
```

### Feature Importance

**Important Note**: Built-in feature importance based on split impurity is unreliable for survival data. Use permutation-based feature importance instead.

```python
from sklearn.inspection import permutation_importance
from sksurv.metrics import concordance_index_censored

# Define scoring function
def score_survival_model(model, X, y):
    prediction = model.predict(X)
    result = concordance_index_censored(y['event'], y['time'], prediction)
    return result[0]

# Calculate permutation importance
perm_importance = permutation_importance(
    rsf, X, y,
    n_repeats=10,
    random_state=42,
    scoring=score_survival_model
)

# Get feature importance
feature_importance = perm_importance.importances_mean
```

## Gradient Boosting Survival Analysis

### Overview

Gradient Boosting builds an ensemble model by sequentially adding weak learners, where each new learner corrects the errors of the previous ones. The model expression is: **f(x) = Σ β_m g(x; θ_m)**

### Model Types

#### GradientBoostingSurvivalAnalysis

Uses regression trees as base learners. Capable of capturing complex non-linear relationships.

**When to Use:**
-   Need to model complex non-linear relationships.
-   Seeking high predictive performance.
-   Have enough data to avoid overfitting.
-   Able to perform fine-grained hyperparameter tuning.

#### ComponentwiseGradientBoostingSurvivalAnalysis

Uses component-wise least squares as base learners. Produces linear models with automatic feature selection.

**When to Use:**
-   Need an interpretable linear model.
-   Need automatic feature selection (similar to Lasso).
-   Have high-dimensional data.
-   Prefer sparse models.

### Loss Functions

#### Cox's Partial Likelihood (Default)

Maintains the proportional hazards framework but replaces the linear model with an additive ensemble model.

**Suitable for:**
-   Standard survival analysis scenarios.
-   When the proportional hazards assumption is reasonable.
-   Most use cases.

#### Accelerated Failure Time (AFT)

Assumes that features accelerate or decelerate survival time by a constant factor. The loss function is: **(1/n) Σ ω_i (log y_i - f(x_i))²**

**Suitable for:**
-   Preferring the AFT framework over proportional hazards.
-   Wanting to model time directly.
-   Needing to interpret the impact on survival time.

### Regularization Strategies

Three main techniques prevent overfitting:

1.  **Learning Rate** (`learning_rate < 1`)
    -   Shrinks the contribution of each base learner.
    -   Smaller values require more iterations but offer better generalization.
    -   Typical range: 0.01 - 0.1.

2.  **Dropout** (`dropout_rate > 0`)
    -   Randomly drops previous learners during training.
    -   Forces learners to be more robust.
    -   Typical range: 0.01 - 0.2.

3.  **Subsampling** (`subsample < 1`)
    -   Uses a random subset of data for each iteration.
    -   Increases randomness and reduces overfitting.
    -   Typical range: 0.5 - 0.9.

**Recommendation**: Combine a small learning rate with early stopping for optimal performance.

### Key Parameters

-   `loss`: Loss function ('coxph' or 'ipcwls').
-   `learning_rate`: Shrinkage of each tree's contribution (Default: 0.1).
-   `n_estimators`: Number of boosting iterations (Default: 100).
-   `subsample`: Proportion of samples for each iteration (Default: 1.0).
-   `dropout_rate`: Dropout rate for learners (Default: 0.0).
-   `max_depth`: Maximum depth of trees (Default: 3).
-   `min_samples_split`: Minimum samples required to split a node (Default: 2).
-   `min_samples_leaf`: Minimum samples required in a leaf node (Default: 1).
-   `max_features`: Number of features to consider at each split.

### Example Usage

```python
from sksurv.ensemble import GradientBoostingSurvivalAnalysis
from sklearn.model_selection import train_test_split

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Fit Gradient Boosting model
gbs = GradientBoostingSurvivalAnalysis(
    loss='coxph',
    learning_rate=0.05,
    n_estimators=200,
    subsample=0.8,
    dropout_rate=0.1,
    max_depth=3,
    random_state=42
)
gbs.fit(X_train, y_train)

# Predict risk scores
risk_scores = gbs.predict(X_test)

# Predict survival functions
surv_funcs = gbs.predict_survival_function(X_test)

# Predict cumulative hazard functions
chf_funcs = gbs.predict_cumulative_hazard_function(X_test)
```

### Early Stopping

Use a validation set to prevent overfitting:

```python
from sklearn.model_selection import train_test_split

# Create train/validation split
X_tr, X_val, y_tr, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

# Fit with early stopping
gbs = GradientBoostingSurvivalAnalysis(
    n_estimators=1000,
    learning_rate=0.01,
    max_depth=3,
    validation_fraction=0.2,
    n_iter_no_change=10,
    random_state=42
)
gbs.fit(X_tr, y_tr)

# Check iterations used
print(f"Used {gbs.n_estimators_} iterations")
```

### Hyperparameter Tuning

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'learning_rate': [0.01, 0.05, 0.1],
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 5, 7],
    'subsample': [0.8, 1.0]
}

cv = GridSearchCV(
    GradientBoostingSurvivalAnalysis(),
    param_grid,
    scoring='concordance_index_ipcw',
    cv=5,
    n_jobs=-1
)
cv.fit(X, y)

best_model = cv.best_estimator_
```

## Componentwise Gradient Boosting Survival Analysis

### Overview

Uses component-wise least squares to produce sparse linear models with automatic feature selection similar to Lasso.

### When to Use

-   Need an interpretable linear model.
-   Need automatic feature selection.
-   Have high-dimensional data with many irrelevant features.
-   Prefer coefficient-based interpretation.

### Example Usage

```python
from sksurv.ensemble import ComponentwiseGradientBoostingSurvivalAnalysis

# Fit component-wise boosting model
cgbs = ComponentwiseGradientBoostingSurvivalAnalysis(
    loss='coxph',
    learning_rate=0.1,
    n_estimators=100
)
cgbs.fit(X, y)

# Get selected features and coefficients
coef = cgbs.coef_
selected_features = [i for i, c in enumerate(coef) if c != 0]
```

## Extra Survival Trees

Extra Survival Trees—similar to Random Survival Forests, but introduce additional randomness when choosing split points.

### When to Use

-   Desire stronger regularization than Random Survival Forests.
-   Limited data volume.
-   Need faster training speed.

### Key Differences

Instead of searching for the optimal split point for selected features, it chooses split points randomly, thereby increasing the diversity of the ensemble.

```python
from sksurv.ensemble import ExtraSurvivalTrees

est = ExtraSurvivalTrees(n_estimators=100, random_state=42)
est.fit(X, y)
```

## Model Comparison

| Model | Complexity | Interpretability | Performance | Speed |
|-------|-----------|------------------|-------------|-------|
| Random Survival Forest | Medium | Low | High | Medium |
| Gradient Boosting Survival Analysis | High | Low | Highest | Slow |
| Componentwise Gradient Boosting Survival Analysis | Low | High | Medium | Fast |
| Extra Survival Trees | Medium | Low | Medium-High | Fast |

**General Recommendations:**
-   **Best Overall Performance**: Tuned `GradientBoostingSurvivalAnalysis`.
-   **Best Balance**: `RandomSurvivalForest`.
-   **Best Interpretability**: `ComponentwiseGradientBoostingSurvivalAnalysis`.
-   **Fastest Training**: `ExtraSurvivalTrees`.