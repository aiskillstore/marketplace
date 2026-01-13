# ML Training Debugger - Detailed Workflow

## Process Overview

Systematic debugging of ML training issues with root cause analysis and verified fixes.

## Phase Breakdown

### Phase 1: Diagnose Issue (8 min)
**Agent**: ML-Developer
- Analyze training curves
- Check for loss divergence, NaN, overfitting
- Assess convergence rate
- Generate diagnostic report

### Phase 2: Analyze Root Cause (10 min)
**Agent**: Performance-Analyzer
- **Gradient Analysis**: Check for vanishing/exploding gradients
- **Data Analysis**: Class imbalance, outliers, normalization
- **Architecture Review**: Model complexity, regularization

### Phase 3: Apply Fix (15 min)
**Agent**: Coder
- **Learning Rate**: Adjust based on divergence/convergence
- **Overfitting**: Add dropout, L2 regularization
- **Gradients**: Gradient clipping, activation changes
- **Data**: Class weights, re-normalization

### Phase 4: Validate Fix (12 min)
**Agent**: Performance-Analyzer
- Retrain model with fixes
- Compare before/after metrics
- Visualize training curves
- Verify improvement >10%

### Phase 5: Optimize Performance (5 min)
**Agent**: ML-Developer
- Generate optimization recommendations
- Document improvements
- Save fixed model
- Create final report

## Common Issues & Fixes

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| Loss Divergence | LR too high | Reduce LR by 10x |
| NaN Loss | Numerical instability | Gradient clipping + lower LR |
| Overfitting | Model too complex | Dropout + L2 regularization |
| Slow Convergence | LR too low | Increase LR + scheduler |
| Vanishing Gradients | Deep network, poor activations | ReLU/LeakyReLU + batch norm |
| Exploding Gradients | No clipping | Gradient clipping (clipnorm=1.0) |

## Diagnostic Checks

```python
check_loss_divergence()  # Loss increasing
check_overfitting()      # Val >> Train
check_convergence_rate() # Loss plateau
check_gradient_health()  # NaN, vanishing, exploding
```

## Best Practices

1. **Always** save training history for analysis
2. **Monitor** gradients during training
3. **Start** with small learning rate
4. **Use** callbacks (early stopping, LR scheduling)
5. **Validate** fixes with full retraining

For implementation details, see SKILL.md
