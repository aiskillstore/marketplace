# Agent Pipeline Chaining - Quick Start

Chain agent outputs as inputs in sequential or parallel pipelines.

## Quick Start

```bash
# 1. Design pipeline
npx claude-flow@alpha pipeline design --stages "research,code,test" --output design.json

# 2. Connect agents
npx claude-flow@alpha pipeline init --design design.json
npx claude-flow@alpha agent spawn --type researcher --pipeline-stage 1
npx claude-flow@alpha agent spawn --type coder --pipeline-stage 2

# 3. Execute pipeline
npx claude-flow@alpha pipeline execute --design design.json --input data.json

# 4. Monitor and validate
npx claude-flow@alpha pipeline monitor --interval 5
npx claude-flow@alpha pipeline results --output results.json
```

## Agents
- **task-orchestrator:** Pipeline coordination
- **memory-coordinator:** Data flow management

## Success Metrics
- Stage latency: <30s
- Throughput: ≥10 items/min
- Error rate: <2%
