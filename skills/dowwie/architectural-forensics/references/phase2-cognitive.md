# Phase 2: Cognitive Architecture Analysis

Detailed guidance for extracting agent "business logic" patterns.

## Workflow

Phase 2 skills run in parallel after Phase 1 completes:
```
Skill Agent (coordinator) → Reader Agents (file clusters) → Synthesis → Output
```

Each skill agent:
1. Uses codebase map and Phase 1 patterns to identify relevant files
2. Clusters files by relationship (hierarchy, cohort, type+usage, etc.)
3. Spawns reader agents to extract cognitive patterns from clusters
4. Synthesizes extracts, referencing Phase 1 findings where relevant

Output: `forensics-output/frameworks/{name}/phase2/*.md`

## 2.1 Control Loop Analysis

### Reasoning Pattern Detection

**ReAct Pattern**
```
Thought: I need to search for the user's question
Action: search
Action Input: "climate change effects"
Observation: [search results]
Thought: Based on the results...
Final Answer: ...
```

Key indicators:
- Explicit "Thought" prefix in prompts
- Action/Observation cycles
- Self-narrated reasoning

**Plan-and-Solve Pattern**
```
Step 1: Understand the problem
Step 2: Break into subtasks
Step 3: Execute each subtask
Step 4: Synthesize results
```

Key indicators:
- Upfront planning phase
- Numbered steps
- Plan revision logic

**Reflection Pattern**
```
Initial attempt → Self-critique → Revision → Final
```

Key indicators:
- Explicit evaluation prompts
- "Was this good?" / "How can I improve?"
- Iterative refinement

### Step Function Anatomy

Every agent has a core decision function. Find it by searching for:

```python
# Common names
def step(self, ...):
def _run_step(self, ...):
def invoke(self, ...):
def execute_step(self, ...):
```

Document:
1. **How context is assembled** (message building)
2. **How LLM is called** (API parameters, model selection)
3. **How output is parsed** (structured output, regex, JSON)
4. **How actions are dispatched** (tool execution, finish detection)

### Termination Analysis

Create a termination condition table:

| Condition | Location | Mechanism | Risk |
|-----------|----------|-----------|------|
| Step limit | `L45` | `if steps >= 10` | May cut off valid work |
| Token limit | `L52` | Token counter | Mid-thought truncation |
| Finish action | `L78` | Parse "FINISH" | LLM non-compliance |
| Error limit | `L89` | `if errors >= 3` | Premature exit |

## 2.2 Memory & Context Orchestration

### Context Assembly Order

Typical structure:
```
[System Prompt]
[Memory/Retrieved Context]
[Tool Definitions]
[Conversation History]
[Current User Message]
[Agent Scratchpad / Thinking Space]
```

Document:
- Where each piece is defined
- How order is determined
- Maximum lengths per section

### Eviction Strategies

| Strategy | Implementation | When to Use |
|----------|---------------|-------------|
| FIFO | Drop oldest messages | Simple, fast |
| Summarize | LLM summarizes old messages | Preserves context |
| Sliding Window | Keep last N turns | Predictable |
| Importance | Score and keep important | Expensive but smart |
| Vector Swap | Move to vector store | Scalable long-term |

### Memory Tiers

```
┌─────────────────────────────────────┐
│         Short-Term (RAM)            │
│  - Current conversation             │
│  - Working scratchpad               │
├─────────────────────────────────────┤
│         Medium-Term (Session)       │
│  - Summarized history               │
│  - Recent tool results              │
├─────────────────────────────────────┤
│         Long-Term (Persistent)      │
│  - Vector database                  │
│  - SQL/Document store               │
│  - User preferences                 │
└─────────────────────────────────────┘
```

## 2.3 Tool Interface Analysis

### Schema Generation Methods

**Introspection (Automatic)**
```python
@tool
def search(query: str, max_results: int = 10) -> list[str]:
    """Search the web for information."""
    ...

# Framework inspects signature + docstring → JSON Schema
```

**Pydantic (Semi-automatic)**
```python
class SearchInput(BaseModel):
    query: str = Field(description="Search query")
    max_results: int = Field(default=10, ge=1, le=100)

# Model generates schema
```

**Manual Definition**
```python
SEARCH_SCHEMA = {
    "name": "search",
    "description": "Search the web",
    "parameters": {...}
}
```

### Error Feedback Loops

| Pattern | Implementation | Quality |
|---------|---------------|---------|
| Silent | Errors swallowed | Poor |
| Basic | Exception message only | Okay |
| Structured | Type + message + context | Good |
| Self-healing | Error → LLM → Retry | Best |

Document:
- What error info reaches the LLM
- Maximum retry attempts
- Backoff strategy

## 2.4 Multi-Agent Analysis

### Coordination Models

**Supervisor**
```
        Supervisor
       /    |    \
   Worker1  Worker2  Worker3
```
- Central control
- Explicit task assignment
- Single point of failure

**Peer-to-Peer**
```
  Agent A ←→ Agent B
     ↕          ↕
  Agent C ←→ Agent D
```
- Decentralized
- Direct communication
- Complex coordination

**Pipeline**
```
Agent A → Agent B → Agent C → Output
```
- Sequential
- Clear data flow
- Limited parallelism

### State Sharing

**Blackboard (Shared State)**
```python
class Blackboard:
    state: dict  # All agents read/write
```
- Simple
- Race conditions possible
- Full visibility

**Message Passing (Isolated)**
```python
agent_a.send(agent_b, message)
```
- Isolated
- Explicit communication
- More complex

### Handoff Mechanisms

Document:
1. **How is the next agent selected?** (Router logic)
2. **What context is transferred?** (Full/partial state)
3. **Can control return?** (One-way vs. bidirectional)
4. **How are loops prevented?** (Depth limits, visited tracking)
