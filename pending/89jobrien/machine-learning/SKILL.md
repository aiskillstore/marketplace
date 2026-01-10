---
name: machine-learning
description: Machine learning development patterns, model training, evaluation, and
  deployment. Use when building ML pipelines, training models, feature engineering,
  model evaluation, or deploying ML systems to production.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# Machine Learning

Comprehensive machine learning skill covering the full ML lifecycle from experimentation to production deployment.

## When to Use This Skill

- Building machine learning pipelines
- Feature engineering and data preprocessing
- Model training, evaluation, and selection
- Hyperparameter tuning and optimization
- Model deployment and serving
- ML experiment tracking and versioning
- Production ML monitoring and maintenance

## ML Development Lifecycle

### 1. Problem Definition

**Classification Types:**

- Binary classification (spam/not spam)
- Multi-class classification (image categories)
- Multi-label classification (document tags)
- Regression (price prediction)
- Clustering (customer segmentation)
- Ranking (search results)
- Anomaly detection (fraud detection)

**Success Metrics by Problem Type:**

| Problem Type | Primary Metrics | Secondary Metrics |
|--------------|-----------------|-------------------|
| Binary Classification | AUC-ROC, F1 | Precision, Recall, PR-AUC |
| Multi-class | Macro F1, Accuracy | Per-class metrics |
| Regression | RMSE, MAE | R², MAPE |
| Ranking | NDCG, MAP | MRR |
| Clustering | Silhouette, Calinski-Harabasz | Davies-Bouldin |

### 2. Data Preparation

**Data Quality Checks:**

- Missing value analysis and imputation strategies
- Outlier detection and handling
- Data type validation
- Distribution analysis
- Target leakage detection

**Feature Engineering Patterns:**

- Numerical: scaling, binning, log transforms, polynomial features
- Categorical: one-hot, target encoding, frequency encoding, embeddings
- Temporal: lag features, rolling statistics, cyclical encoding
- Text: TF-IDF, word embeddings, transformer embeddings
- Geospatial: distance features, clustering, grid encoding

**Train/Test Split Strategies:**

- Random split (standard)
- Stratified split (imbalanced classes)
- Time-based split (temporal data)
- Group split (prevent data leakage)
- K-fold cross-validation

### 3. Model Selection

**Algorithm Selection Guide:**

| Data Size | Problem | Recommended Models |
|-----------|---------|-------------------|
| Small (<10K) | Classification | Logistic Regression, SVM, Random Forest |
| Small (<10K) | Regression | Linear Regression, Ridge, SVR |
| Medium (10K-1M) | Classification | XGBoost, LightGBM, Neural Networks |
| Medium (10K-1M) | Regression | XGBoost, LightGBM, Neural Networks |
| Large (>1M) | Any | Deep Learning, Distributed training |
| Tabular | Any | Gradient Boosting (XGBoost, LightGBM, CatBoost) |
| Images | Classification | CNN, ResNet, EfficientNet, Vision Transformers |
| Text | NLP | Transformers (BERT, RoBERTa, GPT) |
| Sequential | Time Series | LSTM, Transformer, Prophet |

### 4. Model Training

**Hyperparameter Tuning:**

- Grid Search: exhaustive, good for small spaces
- Random Search: efficient, good for large spaces
- Bayesian Optimization: smart exploration (Optuna, Hyperopt)
- Early stopping: prevent overfitting

**Common Hyperparameters:**

| Model | Key Parameters |
|-------|---------------|
| XGBoost | learning_rate, max_depth, n_estimators, subsample |
| LightGBM | num_leaves, learning_rate, n_estimators, feature_fraction |
| Random Forest | n_estimators, max_depth, min_samples_split |
| Neural Networks | learning_rate, batch_size, layers, dropout |

### 5. Model Evaluation

**Evaluation Best Practices:**

- Always use held-out test set for final evaluation
- Use cross-validation during development
- Check for overfitting (train vs validation gap)
- Evaluate on multiple metrics
- Analyze errors qualitatively

**Handling Imbalanced Data:**

- Resampling: SMOTE, undersampling
- Class weights: weighted loss functions
- Threshold tuning: optimize decision threshold
- Evaluation: use PR-AUC over ROC-AUC

### 6. Production Deployment

**Model Serving Patterns:**

- REST API (Flask, FastAPI, TF Serving)
- Batch inference (scheduled jobs)
- Streaming (real-time predictions)
- Edge deployment (mobile, IoT)

**Production Considerations:**

- Latency requirements (p50, p95, p99)
- Throughput (requests per second)
- Model size and memory footprint
- Fallback strategies
- A/B testing framework

### 7. Monitoring & Maintenance

**What to Monitor:**

- Prediction latency
- Input feature distributions (data drift)
- Prediction distributions (concept drift)
- Model performance metrics
- Error rates and types

**Retraining Triggers:**

- Performance degradation below threshold
- Significant data drift detected
- Scheduled retraining (daily, weekly)
- New training data available

## MLOps Best Practices

### Experiment Tracking

Track for every experiment:

- Code version (git commit)
- Data version (hash or version ID)
- Hyperparameters
- Metrics (train, validation, test)
- Model artifacts
- Environment (packages, versions)

### Model Versioning

```
models/
├── model_v1.0.0/
│   ├── model.pkl
│   ├── metadata.json
│   ├── requirements.txt
│   └── metrics.json
├── model_v1.1.0/
└── model_v2.0.0/
```

### CI/CD for ML

1. **Continuous Integration:**
   - Data validation tests
   - Model training tests
   - Performance regression tests

2. **Continuous Deployment:**
   - Staging environment validation
   - Shadow mode testing
   - Gradual rollout (canary)
   - Automatic rollback

## Reference Files

For detailed patterns and code examples, load reference files as needed:

- **`references/preprocessing.md`** - Data preprocessing patterns and feature engineering techniques
- **`references/model_patterns.md`** - Model architecture patterns and implementation examples
- **`references/evaluation.md`** - Comprehensive evaluation strategies and metrics

## Integration with Other Skills

- **performance** - For optimizing inference latency
- **testing** - For ML-specific testing patterns
- **database-optimization** - For feature store queries
- **debugging** - For model debugging and error analysis
