---
name: memory-orchestration
description: Analyze context management, memory systems, and state continuity in agent frameworks. Use when (1) understanding how prompts are assembled, (2) evaluating eviction policies for context overflow, (3) mapping memory tiers (short-term/long-term), (4) analyzing token budget management, or (5) comparing context strategies across frameworks.
---

# Memory Orchestration

Analyzes context management and memory systems.

## Process

1. **Trace context assembly** — How prompts are built from components
2. **Identify eviction policies** — How context overflow is handled
3. **Map memory tiers** — Short-term (RAM) to long-term (DB)
4. **Analyze token management** — Counting, budgeting, truncation

## Context Assembly Analysis

### Standard Assembly Order

```
┌─────────────────────────────────────────┐
│ 1. System Prompt                        │
│    - Role definition                    │
│    - Behavioral guidelines              │
│    - Output format instructions         │
├─────────────────────────────────────────┤
│ 2. Retrieved Context / Memory           │
│    - Relevant past interactions         │
│    - Retrieved documents (RAG)          │
│    - User preferences                   │
├─────────────────────────────────────────┤
│ 3. Tool Definitions                     │
│    - Available tools and schemas        │
│    - Usage examples                     │
├─────────────────────────────────────────┤
│ 4. Conversation History                 │
│    - Previous turns (user/assistant)    │
│    - Prior tool calls and results       │
├─────────────────────────────────────────┤
│ 5. Current Input                        │
│    - User's current message             │
│    - Any attachments/context            │
├─────────────────────────────────────────┤
│ 6. Agent Scratchpad (Optional)          │
│    - Current thinking/planning          │
│    - Intermediate results               │
└─────────────────────────────────────────┘
```

### Assembly Patterns

**Template-Based**
```python
PROMPT_TEMPLATE = """
{system_prompt}

## Available Tools
{tool_descriptions}

## Conversation
{history}

## Current Request
{user_input}
"""

prompt = PROMPT_TEMPLATE.format(
    system_prompt=self.system_prompt,
    tool_descriptions=self._format_tools(),
    history=self._format_history(),
    user_input=message
)
```

**Message List (Chat API)**
```python
messages = [
    {"role": "system", "content": system_prompt},
    *self._get_history_messages(),
    {"role": "user", "content": user_input}
]
```

**Programmatic Assembly**
```python
def build_prompt(self, input):
    builder = PromptBuilder()
    builder.add_system(self.system_prompt)
    builder.add_context(self.memory.retrieve(input))
    builder.add_tools(self.tools)
    builder.add_history(self.history, max_tokens=2000)
    builder.add_user(input)
    return builder.build()
```

## Eviction Policies

### FIFO (First In, First Out)

```python
def trim_history(self, max_messages: int):
    while len(self.history) > max_messages:
        self.history.pop(0)  # Remove oldest
```

**Pros**: Simple, predictable
**Cons**: May lose important early context

### Sliding Window

```python
def get_context_window(self, max_tokens: int):
    window = []
    token_count = 0
    for msg in reversed(self.history):
        msg_tokens = count_tokens(msg)
        if token_count + msg_tokens > max_tokens:
            break
        window.insert(0, msg)
        token_count += msg_tokens
    return window
```

**Pros**: Token-aware, keeps recent
**Cons**: Still loses old context

### Summarization

```python
def summarize_and_trim(self, max_tokens: int):
    if self.total_tokens < max_tokens:
        return
    
    # Summarize oldest messages
    old_messages = self.history[:len(self.history)//2]
    summary = self.llm.summarize(old_messages)
    
    # Replace with summary
    self.history = [
        {"role": "system", "content": f"Previous conversation summary: {summary}"},
        *self.history[len(self.history)//2:]
    ]
```

**Pros**: Preserves context semantically
**Cons**: Expensive (LLM call), lossy

### Vector Store Swapping

```python
def manage_context(self, current_input: str, max_tokens: int):
    # Move old messages to vector store
    if self.total_tokens > max_tokens:
        to_archive = self.history[:-10]
        self.vector_store.add(to_archive)
        self.history = self.history[-10:]
    
    # Retrieve relevant context
    relevant = self.vector_store.search(current_input, k=5)
    return self._build_prompt(relevant, self.history)
```

**Pros**: Scalable, relevance-based
**Cons**: Complex, retrieval quality matters

### Importance Scoring

```python
def score_and_trim(self, max_tokens: int):
    scored = []
    for msg in self.history:
        score = self._compute_importance(msg)
        scored.append((score, msg))
    
    # Keep highest scoring until budget
    scored.sort(reverse=True)
    kept = []
    tokens = 0
    for score, msg in scored:
        if tokens + count_tokens(msg) > max_tokens:
            break
        kept.append(msg)
        tokens += count_tokens(msg)
    
    # Restore chronological order
    self.history = sorted(kept, key=lambda m: m['timestamp'])
```

**Pros**: Keeps important context
**Cons**: Expensive to compute

## Memory Tier Mapping

```
┌─────────────────────────────────────────────────────┐
│                  MEMORY TIERS                        │
├─────────────────────────────────────────────────────┤
│ Tier 1: Working Memory (In-Prompt)                  │
│ ├── Current conversation turns                      │
│ ├── Active tool results                             │
│ └── Immediate scratchpad                            │
│ Latency: 0ms | Capacity: Context window             │
├─────────────────────────────────────────────────────┤
│ Tier 2: Session Memory (RAM)                        │
│ ├── Full conversation history                       │
│ ├── Session state                                   │
│ └── Cached retrievals                               │
│ Latency: <1ms | Capacity: GB                        │
├─────────────────────────────────────────────────────┤
│ Tier 3: Persistent Memory (Database)                │
│ ├── Vector store (semantic search)                  │
│ ├── SQL/Document store (structured)                 │
│ └── User profiles and preferences                   │
│ Latency: 10-100ms | Capacity: TB+                   │
└─────────────────────────────────────────────────────┘
```

### Tier Promotion/Demotion

```python
class MemoryManager:
    def on_turn_end(self, turn):
        # Tier 1 → Tier 2: Move from prompt to session
        self.session_memory.add(turn)
        
        # Tier 2 → Tier 3: Persist important turns
        if self.should_persist(turn):
            self.persistent_memory.add(turn)
    
    def on_session_end(self):
        # Tier 2 → Tier 3: Archive session
        summary = self.summarize_session()
        self.persistent_memory.add(summary)
```

## Token Management

### Counting Strategies

| Method | Accuracy | Speed |
|--------|----------|-------|
| `tiktoken` | Exact | Fast |
| `len(text) / 4` | Rough estimate | Instant |
| API response | Post-hoc | After call |
| Tokenizer model | Exact | Medium |

### Budget Allocation

```python
class TokenBudget:
    def __init__(self, total: int = 8000):
        self.total = total
        self.allocations = {
            'system': 1000,
            'tools': 1500,
            'history': 4000,
            'input': 1000,
            'output_reserve': 500
        }
    
    def remaining_for_history(self, used: dict) -> int:
        fixed = used.get('system', 0) + used.get('tools', 0)
        return self.total - fixed - self.allocations['output_reserve']
```

## Output Template

```markdown
## Memory Orchestration Analysis: [Framework Name]

### Context Assembly
- **Order**: [System → Memory → Tools → History → Input]
- **Method**: [Template/Message List/Programmatic]
- **Location**: `path/to/prompt_builder.py`

### Eviction Policy
- **Strategy**: [FIFO/Window/Summarization/Vector/Importance]
- **Trigger**: [Token count/Message count/Explicit]
- **Location**: `path/to/memory.py:L45`

### Memory Tiers

| Tier | Storage | Capacity | Retrieval |
|------|---------|----------|-----------|
| Working | In-prompt | ~4K tokens | Immediate |
| Session | Dict/List | Unlimited | Direct |
| Persistent | [Chroma/Pinecone/SQL] | Unlimited | Semantic |

### Token Management
- **Counting**: [tiktoken/estimate/API]
- **Budget Allocation**: [Description]
- **Overflow Handling**: [Truncate/Summarize/Error]
```

## Integration

- **Prerequisite**: `codebase-mapping` to identify memory files
- **Feeds into**: `comparative-matrix` for context strategies
- **Related**: `control-loop-extraction` for scratchpad usage
