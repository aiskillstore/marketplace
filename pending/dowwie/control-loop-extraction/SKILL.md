---
name: control-loop-extraction
description: Extract and analyze agent reasoning loops, step functions, and termination conditions. Use when needing to (1) understand how an agent framework implements reasoning (ReAct, Plan-and-Solve, Reflection, etc.), (2) locate the core decision-making logic, (3) analyze loop mechanics and termination conditions, (4) document the step-by-step execution flow of an agent, or (5) compare reasoning patterns across frameworks.
---

# Control Loop Extraction

Extracts and documents the core agent reasoning loop from framework source code.

## Process

1. **Locate the loop** - Find the main agent execution loop
2. **Classify the pattern** - Identify ReAct, Plan-and-Solve, Reflection, or Tree-of-Thoughts
3. **Extract the step function** - Document the LLM → Parse → Decide flow
4. **Map termination** - Catalog all loop exit conditions

## Reasoning Pattern Identification

### Pattern Signatures

**ReAct (Reason + Act)**
```python
# Signature: Thought → Action → Observation cycle
while not done:
    thought = llm.generate(prompt)      # Reasoning
    action = parse_action(thought)       # Action selection
    observation = execute(action)        # Environment feedback
    prompt = update_prompt(observation)  # Loop continuation
```

**Plan-and-Solve**
```python
# Signature: Upfront planning, then execution
plan = llm.generate("Create a plan for...")
for step in plan.steps:
    result = execute_step(step)
    if needs_replan(result):
        plan = replan(...)
```

**Reflection**
```python
# Signature: Act → Self-critique → Adjust
while not done:
    action = llm.generate(prompt)
    result = execute(action)
    critique = llm.generate(f"Evaluate: {result}")
    if critique.needs_adjustment:
        prompt = adjust_approach(critique)
```

**Tree-of-Thoughts**
```python
# Signature: Branch → Evaluate → Select
thoughts = [generate_thought() for _ in range(n)]
scores = [evaluate(t) for t in thoughts]
best = select_best(thoughts, scores)
```

## Step Function Analysis

The "step function" is the atomic unit of agent execution. Extract:

1. **Input Assembly** - How context is constructed for the LLM
2. **LLM Invocation** - The actual model call
3. **Output Parsing** - How raw output becomes structured actions
4. **Action Dispatch** - Tool execution vs. final response routing

### Key Code Patterns

```python
# Common step function structure
def step(self, state):
    # 1. Assemble input
    messages = self._build_messages(state)
    
    # 2. Call LLM
    response = self.llm.invoke(messages)
    
    # 3. Parse output
    parsed = self._parse_response(response)
    
    # 4. Dispatch
    if parsed.is_tool_call:
        return self._execute_tool(parsed.tool, parsed.args)
    else:
        return AgentFinish(parsed.final_answer)
```

## Termination Condition Catalog

### Common Termination Patterns

| Condition | Implementation | Risk |
|-----------|----------------|------|
| Step limit | `if step_count >= max_steps` | May cut off valid execution |
| Token limit | `if total_tokens >= max_tokens` | May truncate mid-thought |
| Explicit finish | `if action.type == "finish"` | Relies on LLM cooperation |
| Timeout | `if elapsed > timeout` | Wall-clock unpredictable |
| Loop detection | `if state in seen_states` | Requires state hashing |
| Error threshold | `if error_count >= max_errors` | May exit on recoverable errors |

### Anti-Pattern: No Termination Guard

```python
# DANGEROUS: No exit condition
while True:
    result = agent.step()
    if result.is_done:  # What if LLM never outputs done?
        break
```

**Fix:** Always include a step counter:

```python
for step in range(max_steps):
    result = agent.step()
    if result.is_done:
        break
else:
    logger.warning("Hit max steps limit")
```

## Output Template

```markdown
## Control Loop Analysis: [Framework Name]

### Reasoning Topology
- **Pattern**: [ReAct | Plan-and-Solve | Reflection | Tree-of-Thoughts | Hybrid]
- **Location**: `path/to/agent.py:L45-L120`

### Step Function
- **Input Assembly**: [Description of context building]
- **LLM Call**: [Method and parameters]
- **Parser**: [How output is structured]
- **Dispatch Logic**: [Tool vs Finish decision]

### Termination Conditions
1. [Condition 1 with code reference]
2. [Condition 2 with code reference]
3. ...

### Loop Detection
- **Method**: [Heuristic | State hash | None]
- **Implementation**: [Code reference or N/A]
```

## Integration Points

- **Prerequisite**: `codebase-mapping` to identify agent files
- **Feeds into**: `comparative-matrix` for pattern comparison
- **Feeds into**: `architecture-synthesis` for new loop design
