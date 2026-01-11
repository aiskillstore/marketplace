---
name: execution-engine-analysis
description: Analyze control flow, concurrency models, and event architectures in agent frameworks. Use when (1) understanding async vs sync execution patterns, (2) classifying execution topology (DAG/FSM/Linear), (3) mapping event emission and observability hooks, (4) evaluating scalability characteristics, or (5) comparing execution models across frameworks.
---

# Execution Engine Analysis

Analyzes the control flow substrate and concurrency model.

## Process

1. **Identify async model** — Native async, sync-with-wrappers, or hybrid
2. **Classify topology** — DAG, FSM, or linear chain
3. **Catalog events** — Callbacks, listeners, generators
4. **Map observability** — Pre/post hooks, interception points

## Concurrency Model Classification

### Native Async

```python
# Signature: async/await throughout
async def run(self):
    result = await self.llm.agenerate(messages)
    return await self.process(result)

# Entry point uses asyncio
asyncio.run(agent.run())
```

**Indicators**: `async def`, `await`, `asyncio.gather`, `aiohttp`

### Sync with Wrappers

```python
# Signature: sync API wrapping async internals
def run(self):
    return asyncio.run(self._async_run())

# Or using thread pools
def run(self):
    with ThreadPoolExecutor() as pool:
        future = pool.submit(self._blocking_call)
        return future.result()
```

**Indicators**: `asyncio.run()` inside sync methods, `ThreadPoolExecutor`, `run_in_executor`

### Hybrid

```python
# Both sync and async APIs exposed
def invoke(self, input):
    return self._sync_invoke(input)

async def ainvoke(self, input):
    return await self._async_invoke(input)
```

**Indicators**: Paired methods (`invoke`/`ainvoke`), `sync_to_async` decorators

## Execution Topology

### DAG (Directed Acyclic Graph)

```python
# Signature: Nodes with dependencies
class Node:
    def __init__(self, deps: list[Node]): ...

graph.add_edge(node_a, node_b)
result = graph.execute()  # Topological order
```

**Indicators**: `Graph`, `Node`, `Edge` classes, `networkx`, topological sort

### FSM (Finite State Machine)

```python
# Signature: Explicit states and transitions
class State(Enum):
    THINKING = "thinking"
    ACTING = "acting"
    DONE = "done"

def transition(self, current: State, event: str) -> State:
    if current == State.THINKING and event == "action_chosen":
        return State.ACTING
```

**Indicators**: State enums, transition tables, `current_state`, state machine libraries

### Linear Chain

```python
# Signature: Sequential step execution
def run(self):
    result = self.step1()
    result = self.step2(result)
    result = self.step3(result)
    return result

# Or pipeline pattern
chain = step1 | step2 | step3
result = chain.invoke(input)
```

**Indicators**: Sequential calls, pipe operators (`|`), `Chain`, `Pipeline` classes

## Event Architecture

### Callbacks

```python
class Callbacks:
    def on_llm_start(self, prompt): ...
    def on_llm_end(self, response): ...
    def on_tool_start(self, tool, input): ...
    def on_tool_end(self, output): ...
    def on_error(self, error): ...
```

**Flexibility**: Low — fixed hook points
**Traceability**: Medium — easy to follow

### Event Listeners/Emitters

```python
emitter = EventEmitter()
emitter.on('llm:start', handler)
emitter.on('tool:*', wildcard_handler)
emitter.emit('llm:start', {'prompt': prompt})
```

**Flexibility**: High — dynamic registration
**Traceability**: Low — harder to trace

### Async Generators (Streaming)

```python
async def run(self):
    async for chunk in self.llm.astream(prompt):
        yield {"type": "token", "content": chunk}
    yield {"type": "done"}
```

**Flexibility**: Medium — streaming-native
**Traceability**: High — follows data flow

## Observability Hooks Inventory

| Hook Point | Purpose | Interception Level |
|------------|---------|-------------------|
| Pre-LLM | Modify prompt | Input |
| Post-LLM | Access raw response | Output |
| Pre-Tool | Validate tool input | Input |
| Post-Tool | Transform tool output | Output |
| Pre-Step | Observe state | Read-only |
| Post-Step | Modify next step | Control flow |
| On-Error | Handle/transform | Error |

### Questions to Answer

- Can you intercept tool input before execution?
- Is the raw LLM response accessible (with token counts)?
- Can you modify control flow from hooks?
- Are hooks sync or async?

## Output Template

```markdown
## Execution Engine Analysis: [Framework Name]

### Concurrency Model
- **Type**: [Native Async / Sync-with-Wrappers / Hybrid]
- **Entry Point**: `path/to/main.py:run()`
- **Thread Safety**: [Yes/No/Partial]

### Execution Topology
- **Model**: [DAG / FSM / Linear Chain]
- **Implementation**: [Description with code refs]
- **Parallelization**: [Supported/Not Supported]

### Event Architecture
- **Pattern**: [Callbacks / Listeners / Generators]
- **Registration**: [Static / Dynamic]
- **Streaming**: [Supported / Not Supported]

### Observability Inventory

| Hook | Location | Async | Modifiable |
|------|----------|-------|------------|
| on_llm_start | callbacks.py:L23 | Yes | Input only |
| on_tool_end | callbacks.py:L45 | Yes | Output |
| ... | ... | ... | ... |

### Scalability Assessment
- **Blocking Operations**: [List any]
- **Resource Limits**: [Token counters, rate limits]
- **Recommended Concurrency**: [Threads/Processes/AsyncIO]
```

## Integration

- **Prerequisite**: `codebase-mapping` to identify execution files
- **Feeds into**: `comparative-matrix` for async decisions
- **Related**: `control-loop-extraction` for agent-specific flow
