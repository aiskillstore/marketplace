# Parallel Agent Execution

Patterns for launching and managing multiple agents simultaneously.

## Core Principle

**CRITICAL**: Launch all agents in ONE message with multiple Task tool calls.

```
CORRECT (true parallel):
Message 1: Task(...) Task(...) Task(...) Task(...)
           └── All launch simultaneously

WRONG (sequential):
Message 1: Task(...)
           └── Wait for response
Message 2: Task(...)
           └── Wait for response
           └── Defeats purpose entirely
```

## Basic Pattern

```typescript
// Launch 3 agents in parallel
Task({
  subagent_type: "general-purpose",
  description: "Research query 1 [agent-1]",
  prompt: "...",
  model: "haiku",
  run_in_background: true
})
Task({
  subagent_type: "general-purpose",
  description: "Research query 2 [agent-2]",
  prompt: "...",
  model: "haiku",
  run_in_background: true
})
Task({
  subagent_type: "general-purpose",
  description: "Research query 3 [agent-3]",
  prompt: "...",
  model: "haiku",
  run_in_background: true
})
```

## Instance ID Tagging

Tag each agent for observability:

```
[agent-type-N]

Examples:
[researcher-web-1]
[researcher-docs-2]
[validator-1]
[fetcher-url-3]
```

Tags enable:
- Tracking in run logs
- Debugging failures
- Observability dashboard correlation

## Result Collection

### Blocking Collection

Wait for all agents:

```typescript
// After parallel launch
result1 = TaskOutput({ task_id: agent1_id, block: true })
result2 = TaskOutput({ task_id: agent2_id, block: true })
result3 = TaskOutput({ task_id: agent3_id, block: true })
```

### Timeout-Based Collection

Proceed after timeout:

```typescript
// Collect with timeout
result1 = TaskOutput({ task_id: agent1_id, timeout: 120000 })
result2 = TaskOutput({ task_id: agent2_id, timeout: 120000 })
result3 = TaskOutput({ task_id: agent3_id, timeout: 120000 })

// Handle partial results
available = [r for r in [result1, result2, result3] if r.status == "completed"]
```

## Mode Patterns

### Quick Mode (2-3 agents)

```
Use case: Fast fact-checking, simple lookups
Timeout: 2 minutes
Model: haiku for all

Launch:
├─ Agent 1: Primary query
└─ Agent 2: Alternative source
```

### Standard Mode (4-6 agents)

```
Use case: Typical research, moderate depth
Timeout: 3-5 minutes
Model: haiku for workers, sonnet for synthesis

Launch:
├─ Agent 1-2: Web search (different angles)
├─ Agent 3: Documentation search
├─ Agent 4: Code examples
└─ Synthesis: Combine results (sonnet)
```

### Extensive Mode (8+ agents)

```
Use case: Deep research, comprehensive coverage
Timeout: 10 minutes
Model: haiku for workers, sonnet/opus for synthesis

Launch:
├─ Agent 1-4: Web search (varied queries)
├─ Agent 5-6: Documentation (breadth + depth)
├─ Agent 7-8: Code examples (patterns + tests)
└─ Synthesis: Cross-validate and summarize (sonnet)
```

## Model Selection for Parallel

| Role | Model | Why |
|------|-------|-----|
| Worker agents | haiku | Speed, parallel scales cost |
| Synthesis agent | sonnet | Quality matters for final output |
| Complex synthesis | opus | Deep cross-validation needed |

## Error Handling

### Partial Failure

```
If some agents fail:
1. Collect successful results
2. Note failed agents in metadata
3. Adjust confidence based on coverage
4. Return partial results (useful > nothing)
```

### Full Failure

```
If all agents fail:
1. Report failure with reasons
2. Suggest retry or alternative approach
3. Check network/API availability
```

### Timeout Handling

```
HARD TIMEOUT: [configured duration]

At timeout:
1. Stop waiting for pending agents
2. Collect available results
3. Note incomplete agents
4. Proceed with synthesis
5. TIMELY RESULTS > COMPLETENESS
```

## Observability Integration

Parallel execution produces events:

```json
{"event": "agent_start", "agent_id": "researcher-web-1", "timestamp": "..."}
{"event": "agent_start", "agent_id": "researcher-web-2", "timestamp": "..."}
{"event": "agent_end", "agent_id": "researcher-web-1", "status": "success"}
{"event": "agent_end", "agent_id": "researcher-web-2", "status": "timeout"}
{"event": "research_synthesis", "input_agents": 2, "successful": 1}
```

View in observability dashboard:
```bash
.claude/ai-dev-kit/dev-tools/observability/manage.sh start
# Open http://localhost:5173
```

## Anti-Patterns

### Sequential Launch

```
DON'T:
Task(...) → wait → Task(...) → wait → Task(...)

DO:
Task(...) Task(...) Task(...)  ← Single message
```

### Same Query to All Agents

```
DON'T:
All agents: "What is X?"

DO:
Agent 1: "What is X?" (definition)
Agent 2: "How to implement X?" (practical)
Agent 3: "X best practices" (guidance)
```

### Heavy Model for All Workers

```
DON'T:
8 opus agents for research workers

DO:
8 haiku workers + 1 sonnet synthesizer
```

### No Instance Tagging

```
DON'T:
Task({ description: "Research" })

DO:
Task({ description: "Research query [researcher-1]" })
```

## Quick Reference

| Pattern | Agents | Timeout | Workers | Synthesis |
|---------|--------|---------|---------|-----------|
| Quick | 2-3 | 2 min | haiku | haiku |
| Standard | 4-6 | 3-5 min | haiku | sonnet |
| Extensive | 8+ | 10 min | haiku | sonnet/opus |
