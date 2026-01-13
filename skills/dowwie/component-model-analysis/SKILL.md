---
name: component-model-analysis
description: Evaluate extensibility patterns, abstraction layers, and configuration approaches in frameworks. Use when (1) assessing base class/protocol design, (2) understanding dependency injection patterns, (3) evaluating plugin/extension systems, (4) comparing code-first vs config-first approaches, or (5) determining framework flexibility for customization.
---

# Component Model Analysis

Evaluates extensibility patterns and configuration approaches.

## Process

1. **Identify base classes** — Find BaseLLM, BaseTool, BaseAgent, etc.
2. **Classify abstraction depth** — Thick (lots of logic) vs thin (interfaces)
3. **Analyze DI patterns** — Constructor, factory, registry, container
4. **Document configuration** — Code-first, config-first, or hybrid

## Abstraction Layer Assessment

### Thick Abstractions

```python
class BaseLLM(ABC):
    """Many methods, lots of inherited behavior"""
    
    def __init__(self, model: str, temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self._cache = {}
    
    def generate(self, prompt: str) -> str:
        cached = self._check_cache(prompt)
        if cached:
            return cached
        result = self._generate_impl(prompt)
        self._update_cache(prompt, result)
        return self._postprocess(result)
    
    @abstractmethod
    def _generate_impl(self, prompt: str) -> str: ...
    
    def _check_cache(self, prompt): ...
    def _update_cache(self, prompt, result): ...
    def _postprocess(self, result): ...
    def stream(self, prompt): ...
    def batch(self, prompts): ...
    # ... 15+ more methods
```

**Characteristics**:
- Deep inheritance trees (3+ levels)
- Many non-abstract methods
- Shared state/caching logic
- Hard to understand full behavior

### Thin Abstractions (Protocols)

```python
from typing import Protocol

class LLM(Protocol):
    """Minimal interface contract"""
    
    def generate(self, messages: list[Message]) -> str: ...

class StreamingLLM(Protocol):
    def stream(self, messages: list[Message]) -> Iterator[str]: ...
```

**Characteristics**:
- Pure interfaces
- No inherited behavior
- Duck typing compatible
- Easy to mock/test

### Mixed Approach

```python
class LLMBase(ABC):
    """Some shared logic, but minimal"""
    
    @abstractmethod
    def generate(self, messages: list) -> str: ...
    
    def generate_with_retry(self, messages: list, retries: int = 3) -> str:
        """Optional convenience method"""
        for i in range(retries):
            try:
                return self.generate(messages)
            except RateLimitError:
                time.sleep(2 ** i)
        raise
```

## Dependency Injection Patterns

### Constructor Injection

```python
class Agent:
    def __init__(
        self,
        llm: LLM,
        tools: list[Tool],
        memory: Memory | None = None
    ):
        self.llm = llm
        self.tools = tools
        self.memory = memory or InMemoryStore()
```

**Pros**: Explicit, testable, IDE support
**Cons**: Verbose construction, manual wiring

### Factory Pattern

```python
class Agent:
    @classmethod
    def from_config(cls, config: AgentConfig) -> "Agent":
        llm = LLMFactory.create(config.llm)
        tools = [ToolFactory.create(t) for t in config.tools]
        return cls(llm=llm, tools=tools)
    
    @classmethod
    def from_yaml(cls, path: str) -> "Agent":
        config = yaml.safe_load(open(path))
        return cls.from_config(AgentConfig(**config))
```

**Pros**: Flexible construction, config-driven
**Cons**: Hidden dependencies, magic

### Global Registry

```python
TOOL_REGISTRY: dict[str, type[Tool]] = {}

def register_tool(name: str):
    def decorator(cls):
        TOOL_REGISTRY[name] = cls
        return cls
    return decorator

@register_tool("search")
class SearchTool(Tool): ...

# Usage
tool = TOOL_REGISTRY["search"]()
```

**Pros**: Plugin-friendly, discoverable
**Cons**: Global state, harder to test, implicit

### Container-Based DI

```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    llm = providers.Singleton(
        OpenAI,
        api_key=config.openai.api_key
    )
    
    agent = providers.Factory(
        Agent,
        llm=llm
    )
```

**Pros**: Full lifecycle control, scopes
**Cons**: Complex, learning curve

## Configuration Strategy

### Code-First

```python
agent = Agent(
    llm=OpenAI(model="gpt-4", temperature=0.7),
    tools=[SearchTool(), CalculatorTool()],
    max_steps=10
)
```

**Characteristics**: Type-safe, IDE completion, refactorable

### Config-First

```yaml
# agent.yaml
llm:
  provider: openai
  model: gpt-4
  temperature: 0.7
tools:
  - search
  - calculator
max_steps: 10
```

```python
agent = Agent.from_yaml("agent.yaml")
```

**Characteristics**: Non-developer friendly, runtime changes, less type safety

### Hybrid

```python
# Base config from file
base = AgentConfig.from_yaml("agent.yaml")

# Code overrides
agent = Agent(
    **base.dict(),
    llm=CustomLLM()  # Override specific component
)
```

## Output Template

```markdown
## Component Model Analysis: [Framework Name]

### Abstraction Assessment

| Component | Base Class | Depth | Type |
|-----------|-----------|-------|------|
| LLM | BaseLLM | 3 levels | Thick |
| Tool | BaseTool | 2 levels | Mixed |
| Memory | Protocol | 0 levels | Thin |

### Dependency Injection
- **Primary Pattern**: [Constructor/Factory/Registry/Container]
- **Testability**: [Easy/Medium/Hard]
- **Configuration**: [Code/Config/Hybrid]

### Extension Points

| Extension | Mechanism | Difficulty |
|-----------|-----------|------------|
| Custom LLM | Inherit BaseLLM | Medium |
| Custom Tool | @register_tool | Easy |
| Custom Memory | Implement Protocol | Easy |

### Configuration
- **Strategy**: [Code-first/Config-first/Hybrid]
- **Formats**: [Python/YAML/JSON/TOML]
- **Validation**: [Pydantic/Manual/None]

### Recommendations
- [List any concerns or suggestions]
```

## Integration

- **Prerequisite**: `codebase-mapping` to identify base classes
- **Feeds into**: `comparative-matrix` for extensibility decisions
- **Related**: `antipattern-catalog` for inheritance issues
