# Phase 1: Engineering Chassis Analysis

Detailed guidance for analyzing the software engineering foundations.

## Workflow

Phase 1 skills run in parallel via the 4-tier agent hierarchy:
```
Skill Agent (coordinator) → Reader Agents (file clusters) → Synthesis → Output
```

Each skill agent:
1. Clusters files by relationship (hierarchy, cohort, type+usage, etc.)
2. Spawns reader agents to extract patterns from clusters
3. Synthesizes extracts into skill analysis report

Output: `forensics-output/frameworks/{name}/phase1/*.md`

## 1.1 Data Substrate Analysis

### What to Look For

**Type Definitions**
- Search for: `types.py`, `schema.py`, `models.py`, `schemas.py`
- Identify: Pydantic models, dataclasses, TypedDict, NamedTuple

**Classification Matrix**

| Approach | Indicators | Trade-offs |
|----------|-----------|------------|
| Pydantic | `BaseModel`, `Field()`, validators | Runtime safety vs. performance |
| Dataclass | `@dataclass`, `field()` | Simplicity vs. no validation |
| TypedDict | `TypedDict`, `Required[]` | Lightweight vs. no runtime checks |
| Loose Dict | Plain `dict`, `Dict[str, Any]` | Flexible vs. error-prone |

**Mutation Analysis**

Look for these patterns:

```python
# MUTABLE (risky)
state.messages.append(msg)
state['key'] = value

# IMMUTABLE (safer)
new_state = state.copy()
new_state = replace(state, messages=[*state.messages, msg])
new_state = state.model_copy(update={'key': value})
```

**Serialization**

| Method | Pattern | Notes |
|--------|---------|-------|
| Pydantic | `.model_dump()`, `.model_dump_json()` | Automatic, type-safe |
| Dataclass | `asdict()`, custom `to_dict()` | Manual conversion |
| Pickle | `pickle.dumps()` | Fast but fragile |
| JSON | `json.dumps()` | Requires encoder |

## 1.2 Execution Engine Analysis

### Async Classification

**Native Async**
```python
async def run(self):
    result = await self.llm.agenerate(...)
    return await self.process(result)
```

**Sync with Wrappers**
```python
def run(self):
    return asyncio.run(self._async_run())

# or thread pool
def run(self):
    with ThreadPoolExecutor() as pool:
        future = pool.submit(self._blocking_call)
```

### Execution Topology

**DAG (Directed Acyclic Graph)**
- Look for: `Graph`, `Node`, `Edge` classes
- Pattern: Nodes with dependencies, topological execution

**FSM (Finite State Machine)**
- Look for: `State`, `Transition`, state enums
- Pattern: Explicit state transitions

**Linear Chain**
- Look for: Sequential `run()` calls, pipeline patterns
- Pattern: Step 1 → Step 2 → Step 3

### Event Architecture

| Pattern | Indicators | Flexibility |
|---------|-----------|-------------|
| Callbacks | `on_start`, `on_end`, `on_error` | Limited hooks |
| Listeners | `EventEmitter`, `subscribe()` | Dynamic registration |
| Generators | `yield`, async generators | Streaming, pausable |

## 1.3 Component Model Analysis

### Abstraction Depth

**Thick Abstractions**
```python
class BaseLLM(ABC):
    # Many methods, lots of logic
    def generate(self): ...
    def stream(self): ...
    def batch(self): ...
    def _preprocess(self): ...
    def _postprocess(self): ...
    # ... 20+ methods
```

**Thin Abstractions (Protocols)**
```python
class LLM(Protocol):
    def generate(self, messages: list) -> str: ...
```

### Dependency Injection Patterns

| Pattern | Example | Trade-offs |
|---------|---------|------------|
| Constructor | `Agent(llm=OpenAI(), tools=[...])` | Explicit, testable |
| Factory | `Agent.from_config(cfg)` | Flexible, discoverable |
| Registry | `@register_tool("search")` | Magic, harder to trace |
| Container | `container.resolve(Agent)` | Full DI, complex |

## 1.4 Resilience Analysis

### Error Propagation Map

Trace exceptions through:
1. Tool execution
2. LLM calls
3. Parsing logic
4. State updates

**Questions to Answer**:
- Does a tool crash terminate the agent?
- Are LLM errors retried?
- Is parsing failure recoverable?

### Sandboxing Mechanisms

| Mechanism | Safety | Performance |
|-----------|--------|-------------|
| Subprocess | Medium | Overhead |
| Docker | High | High overhead |
| RestrictedPython | Medium | Some limitations |
| AST analysis | Low | Fast |
| None | None | Fastest |
