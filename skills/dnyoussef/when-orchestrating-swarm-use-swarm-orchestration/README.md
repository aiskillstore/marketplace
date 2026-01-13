# Swarm Orchestration - Quick Start

## Overview

Complex multi-agent swarm orchestration with task decomposition, distributed execution, and result synthesis.

## Quick Start

```bash
# 1. Plan orchestration
npx claude-flow@alpha task decompose --task "Build application" --output decomposition.json

# 2. Initialize swarm
npx claude-flow@alpha swarm init --topology hierarchical --max-agents 15

# 3. Spawn coordinators and agents
npx claude-flow@alpha agent spawn --type coordinator --role "task-orchestrator"
npx claude-flow@alpha agent spawn --type researcher --count 2
npx claude-flow@alpha agent spawn --type coder --count 5

# 4. Orchestrate execution
npx claude-flow@alpha task orchestrate --plan decomposition.json --strategy adaptive

# 5. Monitor and synthesize
npx claude-flow@alpha swarm monitor --interval 10
npx claude-flow@alpha task synthesize --output final-results.json
```

## Key Features

- **Intelligent Task Decomposition:** Break complex tasks into manageable subtasks
- **Dependency Management:** Handle task dependencies automatically
- **Distributed Execution:** Coordinate multiple agents efficiently
- **Progress Tracking:** Real-time visibility into execution
- **Result Synthesis:** Aggregate outputs intelligently

## Agents

- **task-orchestrator:** Central orchestration and coordination
- **hierarchical-coordinator:** Hierarchical task delegation
- **adaptive-coordinator:** Dynamic workload balancing

## Success Metrics

- Task success rate: ≥95%
- Agent utilization: 70-90%
- Coordination overhead: <15%

## Documentation

- **SKILL.md:** Complete SOP with all phases
- **PROCESS.md:** Detailed workflow guide
- **process-diagram.gv:** Visual workflow diagram
