---
name: building-multiagent-systems
description: This skill should be used when designing or implementing systems with multiple AI agents that coordinate to accomplish tasks. Triggers on "multi-agent", "orchestrator", "sub-agent", "coordination", "delegation", "parallel agents", "sequential pipeline", "fan-out", "map-reduce", "spawn agents", "agent hierarchy".
---

# Building Multi-Agent, Tool-Using Agentic Systems

## Overview

Comprehensive architecture patterns for multi-agent systems where AI agents coordinate to accomplish complex tasks using tools. Language-agnostic and applicable across TypeScript, Python, Go, Rust, and other environments.

## Discovery Questions (Required)

Before architecting any system, ask these six mandatory questions:

1. **Starting Point** - Greenfield, adding to existing system, or fixing current implementation?
2. **Primary Use Case** - Parallel work, sequential pipeline, recursive delegation, peer collaboration, work queues, or other?
3. **Scale Expectations** - Small (2-5 agents), medium (10-50), or large (100+)?
4. **State Requirements** - Stateless runs, session-based, or persistent across crashes?
5. **Tool Coordination** - Independent agents, shared read-only resources, write coordination, or rate-limited APIs?
6. **Existing Constraints** - Language, framework, performance needs, compliance requirements?

## Foundational Architecture

### Four-Layer Stack

Every agent follows the four-layer architecture for testability, safety, and modularity:

| Layer | Name | Responsibility |
|-------|------|----------------|
| 1 | Reasoning (LLM) | Plans, critiques, decides which tools to call |
| 2 | Orchestration | Validates, routes, enforces policy, spawns sub-agents |
| 3 | Tool Bus | Schema validation, tool execution coordination |
| 4 | Deterministic Adapters | File I/O, APIs, shell commands, database access |

**Critical Rule**: Everything below Layer 1 must be deterministic. No LLM calls in tools.

See `references/four-layer-architecture.md` for detailed implementation with code examples.

### Foundational Patterns

| Pattern | Purpose |
|---------|---------|
| **Event-Sourcing** | All state changes as events for audit trails and replay |
| **Hierarchical IDs** | Encode delegation hierarchy (e.g., `session.1.2`) for cost aggregation |
| **Agent State Machines** | Explicit states (idle → thinking → tool_execution → stopped) with invalid transition errors |
| **Communication** | EventEmitter for state changes, promises for result collection |

## Seven Coordination Patterns

Choose based on discovery question answers:

| Pattern | Use Case | Trade-offs |
|---------|----------|------------|
| **Fan-Out/Fan-In** | Parallel independent work | Fast but costly; watch for orphans |
| **Sequential Pipeline** | Multi-stage transformations | Bottleneck at slowest stage |
| **Recursive Delegation** | Hierarchical task breakdown | Must add depth limits |
| **Work-Stealing Queue** | 1000+ tasks with load balancing | No built-in priority |
| **Map-Reduce** | Cost optimization | Cheap map ($0.01), smart reduce ($0.15) |
| **Peer Collaboration** | LLM council for bias reduction | Expensive (3N+1 calls), slow |
| **MAKER** | Zero-error tasks (100K+ steps) | 5× cost but ~0% error rate |

See `references/coordination-patterns.md` for detailed implementations.

### Pattern Selection Guide

| Requirement | Recommended Pattern |
|-------------|---------------------|
| Parallel independent tasks | Fan-Out/Fan-In |
| Each stage depends on previous | Sequential Pipeline |
| Complex task decomposition | Recursive Delegation |
| Large batch processing | Work-Stealing Queue |
| Cost-sensitive analysis | Map-Reduce |
| Need diverse perspectives | Peer Collaboration |
| Zero error tolerance | MAKER |

### MAKER Pattern (Zero Errors)

For tasks requiring 100K+ steps with zero error tolerance (medical, financial, legal domains):

1. **Extreme Decomposition** - Recursive breakdown until each subtask <100 steps
2. **Microagents** - Single tool, focused expertise, cheap models
3. **Multi-Agent Voting** - N parallel attempts per subtask, majority consensus
4. **Error Correction** - Deterministic validation + retry with failure context

**Cost comparison**: Same cost as traditional approach, zero errors vs. 10+ errors.

See `references/maker-pattern.md` for full implementation with medical diagnosis example.

## Tool Coordination

| Mechanism | Purpose |
|-----------|---------|
| **Permission Inheritance** | Children inherit subset of parent permissions (cannot escalate) |
| **Resource Locking** | Acquire/release patterns for shared resources |
| **Rate Limiting** | Token bucket algorithm across all agents |
| **Result Caching** | Cache read-only, idempotent, expensive operations |

**Sub-Agent as Tool Pattern**: Wrap specialized agents as tools the parent can call, providing composable abstractions and natural lifecycle management.

See `references/tool-coordination.md` for implementations.

## Critical Lifecycle: Cascading Stop

"Always stop children before stopping self." This prevents orphaned agents.

```
1. Get all child agents
2. Stop all children in parallel
3. Stop self
4. Cancel ongoing work
5. Flush events
```

If pause/resume unavailable, implement manual checkpointing: save agent state (messages, context, tool results), then restore later.

## Production Hardening

| Concern | Solution |
|---------|----------|
| **Orphan Detection** | Heartbeat monitoring every 30 seconds |
| **Cost Tracking** | Hierarchical aggregation across agent tree |
| **Session Persistence** | Project-level task store for cross-session work |
| **Checkpointing** | Save after 10+ tools, $1.00 cost, or 5 minutes elapsed |
| **Self-Modification Safety** | Blast radius assessment, branch isolation, test-first |

See `references/production-hardening.md` for detailed implementations.

## Real-World Example: Code Review System

A pull request orchestrator using Fan-Out/Fan-In:

1. Spawns four specialist reviewers in parallel (security, performance, style, tests)
2. Security and tests use smart models (Sonnet); style and performance use fast models (Haiku)
3. Each reviewer has 2-minute timeout
4. Results aggregate regardless of partial failures
5. Costs track per reviewer
6. All agents stop cleanly via cascading stop after completion

## Execution Checklist

When guiding implementation of multi-agent systems:

1. **Ask discovery questions** - Understand requirements before architecting
2. **Assess error tolerance** - Zero errors → MAKER; some acceptable → simpler patterns
3. **Establish four-layer architecture** - Reasoning, orchestration, tool bus, adapters
4. **Design schema-first tools** - Typed contracts before implementation
5. **Define deterministic boundary** - No LLM in Layers 3-4
6. **Choose orchestration model** - YOLO, Safety-First, or Hybrid
7. **Select coordination pattern** - Fan-out, pipeline, delegation, queue, map-reduce, peer, or MAKER
8. **Design tool coordination** - Permission inheritance, locking, rate limiting
9. **Implement cascading cleanup** - Always stop children before parent
10. **Add monitoring and cost tracking** - Hierarchical aggregation across agent tree
11. **Consider self-modification safety** - If agents can modify code, add safety protocol

## Common Pitfalls

| Pitfall | Impact |
|---------|--------|
| Missing four-layer architecture | Untestable, unsafe, hard to debug |
| LLM calls in tools (Layer 3-4) | Non-deterministic, can't unit test |
| No schema-first tool design | Sub-agents can't discover tools |
| Missing cascading stop | Orphaned agents consuming resources |
| No permission inheritance | Sub-agents can escalate privileges |
| No timeouts | Indefinite hangs waiting for sub-agents |
| Unbounded concurrency | Resource exhaustion from too many agents |
| Ignoring cost tracking | Budget surprises |
| No partial-failure handling | One failure cascades to all agents |
| Unpersisted state | Unrecoverable workflows on crash |
| Uncoordinated tool access | Race conditions on shared resources |
| Wrong model selection | Cost inefficiency (Sonnet for simple tasks) |
| Self-modification without safety | Sub-agents break themselves |
| No heartbeat monitoring | Can't detect orphans after parent crash |

## Reference Files

Detailed implementations with code examples:

| File | Contents |
|------|----------|
| `references/four-layer-architecture.md` | Four-layer stack, deterministic boundary, schema-first tools |
| `references/coordination-patterns.md` | Seven coordination patterns with code |
| `references/maker-pattern.md` | MAKER implementation, voting, medical diagnosis example |
| `references/tool-coordination.md` | Permission inheritance, locking, rate limiting, caching |
| `references/production-hardening.md` | Cascading stop, orphan detection, cost tracking, checkpointing |
