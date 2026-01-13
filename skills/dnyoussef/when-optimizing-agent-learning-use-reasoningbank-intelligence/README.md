# ReasoningBank Intelligence - Quick Start

## Purpose
Adaptive learning system for pattern recognition, strategy optimization, and continuous agent improvement using ReasoningBank.

## When to Use
- Agent performance optimization needed
- Pattern recognition from experience
- Strategy refinement through learning
- Building self-improving systems

## Quick Start

```bash
npx claude-flow@alpha skill-run reasoningbank-intelligence \
  --agent "my-agent" \
  --trajectories-path "./trajectories/"
```

## 5-Phase Process

1. **Initialize System** (10 min) - Set up ReasoningBank
2. **Capture Patterns** (10 min) - Track trajectories and verdicts
3. **Optimize Strategies** (10 min) - Train decision model
4. **Validate Learning** (10 min) - Benchmark improvements
5. **Deploy** (5 min) - Export model for production

## Expected Improvement

- Performance: +15-35%
- Success Rate: +20-40%
- Efficiency: +25-45%

## AgentDB Integration

For 150x faster operations:
```javascript
const db = new AgentDB({ indexing: 'hnsw', quantization: 'int8' });
await learningSystem.useVectorDB(db);
```

## Output

- Trained decision model
- Pattern library (validated)
- Performance metrics
- Integration guide

For detailed documentation, see SKILL.md
