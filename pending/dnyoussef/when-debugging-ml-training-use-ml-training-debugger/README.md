# ML Training Debugger - Quick Start

## Purpose
Debug and fix ML training issues: loss divergence, overfitting, slow convergence, gradient problems.

## When to Use
- Training loss becomes NaN
- Overfitting (train >> val)
- Training not converging
- Poor validation performance

## Quick Start

```bash
npx claude-flow@alpha skill-run ml-training-debugger \
  --model "model.h5" \
  --history "training_history.json"
```

## 5-Phase Process

1. **Diagnose** (8 min) - Identify training issues
2. **Analyze** (10 min) - Root cause investigation
3. **Fix** (15 min) - Apply corrections
4. **Validate** (12 min) - Retrain and verify
5. **Optimize** (5 min) - Additional recommendations

## Common Issues Fixed

- **Loss Divergence**: Reduce learning rate
- **NaN Loss**: Gradient clipping, check data
- **Overfitting**: Add dropout, L2 regularization
- **Slow Convergence**: Increase LR, better init
- **Gradient Issues**: Clipping, activation changes

## Output

- Diagnostic report
- Fixed model
- Training comparison (before/after)
- Optimization recommendations

For detailed documentation, see SKILL.md
