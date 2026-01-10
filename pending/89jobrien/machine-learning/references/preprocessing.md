---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: machine-learning
---

# Data Preprocessing Patterns

## Missing Value Strategies

### Numerical Features

```python
# Simple imputation
df['col'].fillna(df['col'].median(), inplace=True)

# Model-based imputation
from sklearn.impute import KNNImputer
imputer = KNNImputer(n_neighbors=5)
df_imputed = imputer.fit_transform(df)
```

### Categorical Features

```python
# Mode imputation
df['col'].fillna(df['col'].mode()[0], inplace=True)

# New category for missing
df['col'].fillna('MISSING', inplace=True)
```

## Feature Scaling

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

# Standard scaling (mean=0, std=1) - use for most models
scaler = StandardScaler()

# MinMax scaling [0,1] - use for neural networks
scaler = MinMaxScaler()

# Robust scaling - use when outliers present
scaler = RobustScaler()

X_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

## Categorical Encoding

```python
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import category_encoders as ce

# One-hot encoding (low cardinality)
encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')

# Target encoding (high cardinality)
encoder = ce.TargetEncoder(cols=['category_col'])

# Frequency encoding
df['col_freq'] = df['col'].map(df['col'].value_counts(normalize=True))
```

## Feature Engineering Examples

### Temporal Features

```python
df['hour'] = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.dayofweek
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
df['month'] = df['timestamp'].dt.month

# Cyclical encoding
df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
```

### Numerical Transformations

```python
# Log transform (right-skewed data)
df['col_log'] = np.log1p(df['col'])

# Box-Cox transform
from scipy.stats import boxcox
df['col_bc'], lambda_param = boxcox(df['col'] + 1)

# Polynomial features
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)
```

### Interaction Features

```python
# Manual interactions
df['feature_interaction'] = df['feat1'] * df['feat2']
df['feature_ratio'] = df['feat1'] / (df['feat2'] + 1e-8)

# Automated interactions
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(degree=2, interaction_only=True)
```

## Outlier Handling

```python
# IQR method
Q1 = df['col'].quantile(0.25)
Q3 = df['col'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
df_clean = df[(df['col'] >= lower_bound) & (df['col'] <= upper_bound)]

# Clipping
df['col_clipped'] = df['col'].clip(lower=lower_bound, upper=upper_bound)

# Z-score method
from scipy import stats
z_scores = np.abs(stats.zscore(df['col']))
df_clean = df[z_scores < 3]
```

## Data Leakage Prevention

**Common Leakage Sources:**

1. Future information in features
2. Target information in features
3. Train-test contamination during preprocessing

**Prevention:**

```python
# Always fit on train, transform on test
scaler.fit(X_train)
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Use pipelines
from sklearn.pipeline import Pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LogisticRegression())
])
pipeline.fit(X_train, y_train)
```
