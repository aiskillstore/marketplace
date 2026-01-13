# ML Expert - Quick Start

## Purpose
Complete ML model development workflow from data preparation to production deployment.

## When to Use
- Training neural networks
- Model development
- Production ML deployment

## Quick Start

```bash
npx claude-flow@alpha skill-run ml-expert \
  --data "dataset.csv" \
  --target "label_column" \
  --architecture "dnn"
```

## 5-Phase Process

1. **Data Prep** (10 min) - Clean, split, normalize
2. **Model Selection** (10 min) - Choose architecture
3. **Train** (20 min) - Execute training with monitoring
4. **Validate** (10 min) - Evaluate on test set
5. **Deploy** (15 min) - Package for production

## Supported Architectures

- Deep Neural Networks (DNN)
- Convolutional Networks (CNN)
- Recurrent Networks (RNN)
- Transformers

## Output

- Trained model (.h5, SavedModel, TFLite)
- Evaluation report
- Deployment package
- Training curves

For detailed documentation, see SKILL.md
