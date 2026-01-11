---
name: antipattern-catalog
description: Document technical debt, anti-patterns, and patterns to avoid from analyzed frameworks. Use when (1) creating a "Do Not Repeat" list from framework analysis, (2) categorizing observed code smells and issues, (3) assessing severity of architectural problems, (4) generating remediation suggestions, or (5) synthesizing lessons learned across multiple frameworks.
---

# Anti-Pattern Catalog

Documents technical debt and patterns to avoid.

## Process

1. **Collect observations** — Gather issues from Phase 1 & 2 analyses
2. **Categorize** — Structural, behavioral, observability, performance
3. **Assess severity** — Critical, major, minor, cosmetic
4. **Generate remediation** — Suggest fixes for each pattern
5. **Create checklist** — "Do Not Repeat" guidelines

## Anti-Pattern Categories

### Structural Anti-Patterns

Issues with code organization, inheritance, and modularity.

| Pattern | Symptom | Example |
|---------|---------|---------|
| **Deep Inheritance** | 5+ levels of class hierarchy | `Agent → BaseAgent → RunnableAgent → ExecutableAgent → ...` |
| **God Class** | One class with 50+ methods | `AgentExecutor` doing routing, execution, memory, tools |
| **Circular Dependencies** | Module A imports B, B imports A | `agent.py ↔ tools.py` |
| **Leaky Abstraction** | Implementation details exposed | Base class assumes specific LLM response format |
| **Premature Abstraction** | Over-engineered for flexibility | 5 interfaces for a single implementation |

### Behavioral Anti-Patterns

Issues with runtime behavior and logic.

| Pattern | Symptom | Example |
|---------|---------|---------|
| **Hidden State Mutation** | State changes not obvious | `tool.run()` modifies agent's memory |
| **Implicit Contracts** | Undocumented assumptions | Tools assume specific message format |
| **Silent Failures** | Errors swallowed | `except: pass` in tool execution |
| **Infinite Loop Risk** | No termination guarantee | No step limit on agent loop |
| **Race Conditions** | Concurrent state access | Shared dict without locks |

### Observability Anti-Patterns

Issues with debugging and monitoring.

| Pattern | Symptom | Example |
|---------|---------|---------|
| **Hidden LLM Response** | Raw response not accessible | Token counts unavailable |
| **Opaque Errors** | Generic error messages | `"Something went wrong"` |
| **No Tracing** | Can't follow execution | No request IDs, no spans |
| **Swallowed Context** | Information lost | Tool error not fed back to LLM |
| **Missing Metrics** | No performance data | No latency, token, or cost tracking |

### Performance Anti-Patterns

Issues affecting speed and resource usage.

| Pattern | Symptom | Example |
|---------|---------|---------|
| **Sync in Async** | Blocking calls in async code | `requests.get()` in async function |
| **N+1 Queries** | Repeated similar operations | Loading each tool config separately |
| **Unbounded Memory** | History grows forever | No eviction policy |
| **Eager Loading** | Loading unused resources | All tools initialized at startup |
| **No Caching** | Repeated expensive operations | Re-parsing same schema each call |

## Severity Assessment

### Critical (P0)
- Security vulnerabilities
- Data loss risk
- Infinite loops without guards
- Production outage risk

### Major (P1)
- Performance issues >2x slowdown
- Poor error handling
- Difficult to extend
- Concurrency bugs

### Minor (P2)
- Code style issues
- Minor inefficiencies
- Documentation gaps
- Inconsistent patterns

### Cosmetic (P3)
- Naming conventions
- Formatting
- Minor redundancy

## Catalog Entry Template

```markdown
### [Pattern Name]

**Category**: [Structural/Behavioral/Observability/Performance]
**Severity**: [Critical/Major/Minor/Cosmetic]
**Framework(s)**: [Where observed]

#### Description
[Brief explanation of the anti-pattern]

#### Example
[Code snippet showing the problem]

#### Impact
- [Impact 1]
- [Impact 2]

#### Remediation
[How to fix or avoid this pattern]

#### Code Example (Fixed)
[Corrected code snippet]
```

## Common Anti-Patterns Deep Dive

### Deep Inheritance Hell

**Problem**:
```python
class Agent(BaseAgent):
    pass

class BaseAgent(RunnableAgent):
    pass

class RunnableAgent(ExecutableAgent):
    pass

class ExecutableAgent(ConfigurableAgent):
    pass

class ConfigurableAgent(LoggableAgent):
    pass

class LoggableAgent(ABC):
    pass

# 6 layers! Which method comes from where?
```

**Remediation**: Prefer composition over inheritance
```python
class Agent:
    def __init__(
        self,
        executor: Executor,
        config: Config,
        logger: Logger
    ):
        self.executor = executor
        self.config = config
        self.logger = logger
```

### Silent Tool Failures

**Problem**:
```python
def run_tool(self, tool, args):
    try:
        return tool.execute(args)
    except Exception:
        return None  # Error lost forever!
```

**Remediation**: Capture and propagate errors
```python
def run_tool(self, tool, args) -> ToolResult:
    try:
        output = tool.execute(args)
        return ToolResult(success=True, output=output)
    except Exception as e:
        return ToolResult(
            success=False,
            error=f"{type(e).__name__}: {e}",
            traceback=traceback.format_exc()
        )
```

### Hidden LLM Response

**Problem**:
```python
class LLMWrapper:
    def generate(self, prompt: str) -> str:
        response = self.client.chat(prompt)
        return response.content  # Token counts, model info lost!
```

**Remediation**: Expose full response
```python
class LLMWrapper:
    def generate(self, prompt: str) -> LLMResponse:
        response = self.client.chat(prompt)
        return LLMResponse(
            content=response.content,
            model=response.model,
            usage=TokenUsage(
                prompt=response.usage.prompt_tokens,
                completion=response.usage.completion_tokens
            ),
            raw=response  # Always keep raw
        )
```

## Output Template

```markdown
# Anti-Pattern Catalog: [Analysis Name]

## Summary

| Severity | Count |
|----------|-------|
| Critical | 2 |
| Major | 5 |
| Minor | 8 |
| Cosmetic | 3 |

## Critical Issues

### 1. [Pattern Name]
[Full catalog entry]

### 2. [Pattern Name]
[Full catalog entry]

## Major Issues

### 1. [Pattern Name]
[Full catalog entry]

...

## Do Not Repeat Checklist

- [ ] Never use more than 3 levels of inheritance
- [ ] Always expose raw LLM response with token counts
- [ ] Never swallow exceptions without logging
- [ ] Always include step limits on agent loops
- [ ] Never mutate shared state without locks
- [ ] Always provide structured error feedback to LLM
...
```

## Integration

- **Inputs from**: All Phase 1 & 2 analysis skills
- **Feeds into**: `architecture-synthesis` for design decisions
- **Related**: `comparative-matrix` for pattern comparison
