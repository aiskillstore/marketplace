# ML Expert - Detailed Workflow

## Process Overview

Complete machine learning model development from data preparation through production deployment.

## Phase Breakdown

### Phase 1: Data Preparation (10 min)
**Agent**: ML-Developer
- Load and analyze dataset
- Handle missing values and outliers
- Encode categorical variables
- Split into train/val/test (70/15/15)
- Normalize features

### Phase 2: Model Selection (10 min)
**Agent**: Researcher
- Analyze task type (classification/regression)
- Recommend architecture based on data
- Define model layers and parameters
- Configure training (optimizer, loss, callbacks)

### Phase 3: Train Model (20 min)
**Agent**: ML-Developer
- Execute training loop
- Monitor loss and accuracy
- Apply early stopping
- Save best model checkpoints
- Plot training curves

### Phase 4: Validate Performance (10 min)
**Agent**: Tester
- Evaluate on test set
- Calculate metrics (accuracy, precision, recall, F1)
- Generate confusion matrix
- Create evaluation report
- Check for overfitting

### Phase 5: Deploy to Production (15 min)
**Agent**: ML-Developer
- Export model (Keras, SavedModel, TFLite)
- Save preprocessing pipeline
- Create inference script
- Package deployment files
- Write documentation

## Architectures Supported

**Deep Neural Network (DNN)**:
```
Input → Dense(256) → Dropout(0.3) →
Dense(128) → Dropout(0.3) →
Dense(64) → Output
```

**CNN**:
```
Conv2D(32) → MaxPool → Conv2D(64) → MaxPool →
Flatten → Dense(128) → Output
```

**RNN/LSTM**:
```
LSTM(128) → Dropout(0.3) → LSTM(64) → Output
```

## Distributed Training

Use Flow-Nexus MCP for multi-node training:
```bash
mcp__flow-nexus__neural_cluster_init
mcp__flow-nexus__neural_train_distributed
```

## Best Practices

1. **Data**: Clean thoroughly, handle imbalance
2. **Training**: Use callbacks (early stopping, LR reduction)
3. **Validation**: Monitor overfitting
4. **Deployment**: Test inference performance

For implementation details, see SKILL.md
