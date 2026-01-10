---
name: tool-interface-analysis
description: Analyze tool registration, schema generation, and error feedback mechanisms in agent frameworks. Use when (1) understanding how tools are defined and registered, (2) evaluating schema generation approaches (introspection vs manual), (3) tracing error feedback loops to the LLM, (4) assessing retry and self-correction mechanisms, or (5) comparing tool interfaces across frameworks.
---

# Tool Interface Analysis

Analyzes how agent frameworks model, register, and execute tools. This skill examines the **tool abstraction layer**, **schema generation**, **built-in inventory**, and **error feedback mechanisms**.

## Distinction from harness-model-protocol

| tool-interface-analysis | harness-model-protocol |
|------------------------|------------------------|
| How a "tool" is represented (types, base classes) | How tool calls are encoded on the wire |
| Schema generation (Pydantic -> JSON Schema) | Schema transmission to LLM API |
| Built-in tool inventory | Provider-specific tool formats |
| Registration and discovery patterns | Message format translation |
| Error feedback to LLM for retry | Response parsing and streaming |
| Tool execution orchestration | Partial tool call handling |

## Process

1. **Map tool modeling** - Identify how tools are represented (types, protocols, base classes)
2. **Analyze schema generation** - How tool definitions become JSON Schema
3. **Catalog built-in inventory** - What tools ship with the framework
4. **Trace registration flow** - How tools are discovered and made available
5. **Document execution patterns** - Invocation, validation, error handling
6. **Evaluate retry mechanisms** - Self-correction and feedback loops

## Tool Modeling Patterns

### Abstract Base Class Pattern

```python
from abc import ABC, abstractmethod
from typing import Any

class BaseTool(ABC):
    """Framework's tool abstraction."""
    name: str
    description: str

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool with validated arguments."""
        ...

    @property
    @abstractmethod
    def parameters_schema(self) -> dict:
        """Return JSON Schema for parameters."""
        ...
```

**Characteristics**: Explicit contract, inheritance-based, type-safe
**Used by**: LangChain, CrewAI, AutoGen

### Protocol/Interface Pattern

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Tool(Protocol):
    """Structural typing for tools."""
    name: str
    description: str

    def __call__(self, **kwargs) -> Any: ...
    def get_schema(self) -> dict: ...
```

**Characteristics**: Duck typing, flexible, composition-friendly
**Used by**: Pydantic-AI, OpenAI Agents SDK

### Decorated Function Pattern

```python
from functools import wraps

def tool(name: str = None, description: str = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper._tool_name = name or func.__name__
        wrapper._tool_description = description or func.__doc__
        wrapper._is_tool = True
        return wrapper
    return decorator

@tool(description="Search the web for information")
def search(query: str, max_results: int = 10) -> list[str]:
    ...
```

**Characteristics**: Lightweight, DRY, preserves function identity
**Used by**: Google ADK, Swarm, Function calling patterns

### Pydantic Model Pattern

```python
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    """Input schema for search tool."""
    query: str = Field(description="The search query")
    max_results: int = Field(default=10, ge=1, le=100)

class SearchTool(BaseTool):
    name = "search"
    description = "Search the web"
    args_schema = SearchInput

    def execute(self, **kwargs) -> list[str]:
        validated = SearchInput(**kwargs)
        return perform_search(validated.query, validated.max_results)
```

**Characteristics**: Rich validation, auto-schema, clear separation
**Used by**: LangChain, CrewAI

## Schema Generation Methods

### Introspection-Based (Automatic)

```python
import inspect
from typing import get_type_hints

def generate_schema_from_function(func) -> dict:
    hints = get_type_hints(func)
    sig = inspect.signature(func)
    doc = inspect.getdoc(func) or ""

    schema = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": doc.split("\n")[0],
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }

    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue

        prop = {"type": python_type_to_json(hints.get(name, str))}

        # Extract description from docstring if available
        if f":param {name}:" in doc:
            prop["description"] = extract_param_doc(doc, name)

        if param.default is inspect.Parameter.empty:
            schema["function"]["parameters"]["required"].append(name)
        else:
            prop["default"] = param.default

        schema["function"]["parameters"]["properties"][name] = prop

    return schema
```

**Pros**: DRY, always in sync with code, minimal boilerplate
**Cons**: Limited expressiveness, relies on annotations, docstring parsing fragile

### Pydantic-Based (Semi-Automatic)

```python
from pydantic import BaseModel, Field
from pydantic.json_schema import GenerateJsonSchema

class SearchInput(BaseModel):
    """Search the web for information."""
    query: str = Field(description="The search query")
    max_results: int = Field(default=10, ge=1, le=100, description="Max results to return")

def generate_schema_from_pydantic(model: type[BaseModel]) -> dict:
    return {
        "type": "function",
        "function": {
            "name": model.__name__.replace("Input", "").lower(),
            "description": model.__doc__ or "",
            "parameters": model.model_json_schema()
        }
    }
```

**Pros**: Rich validation, excellent descriptions, composable
**Cons**: Class per tool, more boilerplate, Pydantic dependency

### Decorator-Based (Explicit)

```python
@tool(
    name="search",
    description="Search the web for information",
    parameters={
        "query": {"type": "string", "description": "Search query"},
        "max_results": {"type": "integer", "default": 10}
    }
)
def search(query: str, max_results: int = 10) -> list[str]:
    ...
```

**Pros**: Explicit, flexible, no dependencies
**Cons**: Can drift from implementation, manual maintenance

### Manual Definition

```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    }
]
```

**Pros**: Full control, no magic, portable
**Cons**: Maintenance burden, drift risk, duplication

### Schema Generation Comparison

| Method | Sync with Code | Expressiveness | Boilerplate | Validation |
|--------|---------------|----------------|-------------|------------|
| Introspection | Automatic | Low | None | None |
| Pydantic | Automatic | High | Medium | Built-in |
| Decorator | Manual | Medium | Low | Optional |
| Manual | Manual | Full | High | None |

## Registration Patterns

### Declarative List

```python
agent = Agent(
    tools=[search_tool, calculator_tool, weather_tool]
)
```

**Characteristics**: Explicit, static, easy to understand, testable

### Registry Pattern

```python
TOOL_REGISTRY = {}

def register_tool(name: str = None):
    def decorator(func):
        tool_name = name or func.__name__
        TOOL_REGISTRY[tool_name] = func
        return func
    return decorator

@register_tool("search")
def search(query: str) -> list[str]: ...

# Agent uses registry
agent = Agent(tools=list(TOOL_REGISTRY.values()))
```

**Characteristics**: Dynamic, plugin-friendly, implicit coupling

### Discovery-Based (Auto-Import)

```python
import importlib
import pkgutil

def discover_tools(package):
    tools = []
    for module_info in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package.__name__}.{module_info.name}")
        for name, obj in inspect.getmembers(module):
            if hasattr(obj, '__tool__') or isinstance(obj, BaseTool):
                tools.append(obj)
    return tools

# Usage
from myapp import tools as tools_package
agent = Agent(tools=discover_tools(tools_package))
```

**Characteristics**: Automatic, magic, harder to trace, good for plugins

### Factory Pattern

```python
class ToolFactory:
    _registry: dict[str, type[BaseTool]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(tool_class):
            cls._registry[name] = tool_class
            return tool_class
        return decorator

    @classmethod
    def create(cls, config: ToolConfig) -> BaseTool:
        tool_class = cls._registry.get(config.type)
        if not tool_class:
            raise ValueError(f"Unknown tool type: {config.type}")
        return tool_class(**config.params)

# Registration
@ToolFactory.register("search")
class SearchTool(BaseTool): ...

# Creation
tool = ToolFactory.create(ToolConfig(type="search", params={"api_key": "..."}))
```

**Characteristics**: Configurable, testable, DI-friendly, more complex

### Toolset/Toolkit Pattern

```python
class WebToolkit:
    """Collection of related tools."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_tools(self) -> list[BaseTool]:
        return [
            SearchTool(api_key=self.api_key),
            BrowseTool(api_key=self.api_key),
            ExtractTool(api_key=self.api_key)
        ]

# Usage
agent = Agent(tools=WebToolkit(api_key="...").get_tools())
```

**Characteristics**: Cohesive grouping, shared configuration, composable

## Error Feedback Analysis

### Feedback Quality Levels

| Level | What LLM Sees | Self-Correction Possible |
|-------|--------------|-------------------------|
| Silent | Nothing | No |
| Basic | Exception type | Unlikely |
| Message | Exception message | Sometimes |
| Detailed | Type + message + context | Often |
| Structured | Error object with hints | Yes |
| Actionable | Suggestion + example | Very likely |

### Implementation Patterns

**Silent (Anti-Pattern)**
```python
def run_tool(self, tool, args):
    try:
        return tool.execute(**args)
    except Exception:
        return None  # Error lost - LLM has no feedback
```

**Basic**
```python
def run_tool(self, tool, args):
    try:
        return tool.execute(**args)
    except Exception as e:
        return f"Error: {type(e).__name__}"
```

**Detailed with Context**
```python
@dataclass
class ToolResult:
    success: bool
    output: Any = None
    error: str | None = None
    error_type: str | None = None
    suggestion: str | None = None

def run_tool(self, tool, args) -> ToolResult:
    try:
        # Validate first
        validated = tool.validate_args(args)
        result = tool.execute(**validated)
        return ToolResult(success=True, output=result)
    except ValidationError as e:
        return ToolResult(
            success=False,
            error=str(e),
            error_type="validation_error",
            suggestion=f"Check parameter types: {e.errors()}"
        )
    except ToolExecutionError as e:
        return ToolResult(
            success=False,
            error=str(e),
            error_type="execution_error",
            suggestion=e.suggestion if hasattr(e, 'suggestion') else None
        )
```

**Structured for LLM Consumption**
```python
def format_error_for_llm(self, result: ToolResult) -> str:
    if result.success:
        return str(result.output)

    parts = [f"Tool execution failed: {result.error}"]

    if result.error_type == "validation_error":
        parts.append("The provided arguments did not match the expected schema.")

    if result.suggestion:
        parts.append(f"Suggestion: {result.suggestion}")

    return "\n".join(parts)
```

### Retry Mechanisms

**Simple Retry with Backoff**
```python
async def run_with_retry(self, tool, args, max_retries=3):
    for attempt in range(max_retries):
        result = await self.run_tool(tool, args)
        if result.success:
            return result
        if not self._is_retryable(result.error_type):
            return result
        await asyncio.sleep(2 ** attempt)  # Exponential backoff
    return result
```

**LLM-Guided Self-Correction**
```python
async def run_with_self_correction(self, tool, args, max_retries=3):
    for attempt in range(max_retries):
        result = await self.run_tool(tool, args)
        if result.success:
            return result

        # Ask LLM to fix the error
        correction_prompt = f"""
Tool `{tool.name}` failed with error: {result.error}
Original arguments: {json.dumps(args)}
Tool schema: {json.dumps(tool.parameters_schema)}

Provide corrected arguments as JSON.
"""
        corrected = await self.llm.generate(correction_prompt)
        args = json.loads(corrected)

    return result
```

**Fallback Chain**
```python
async def run_with_fallback(self, tool_chain: list[BaseTool], args):
    for tool in tool_chain:
        result = await self.run_tool(tool, args)
        if result.success:
            return result
    return result  # Return last failure
```

## Built-in Tool Categories

### Common Categories

| Category | Examples | Typical Implementation |
|----------|----------|----------------------|
| Search | Web search, semantic search | API wrapper |
| Code | Execute code, REPL | Sandbox + subprocess |
| File | Read, write, list files | Filesystem API |
| Web | HTTP requests, scraping | HTTP client |
| Database | SQL query, vector search | Client + sanitization |
| Calculation | Math, unit conversion | Python eval or library |
| Memory | Store, retrieve facts | Vector store or KV |
| Communication | Email, Slack, API calls | API wrappers |

### Tool Inventory Template

| Tool Name | Category | Input Schema | Output Type | Sandbox | Notes |
|-----------|----------|--------------|-------------|---------|-------|
| `search_web` | Search | query: str | list[Result] | No | API key required |
| `execute_python` | Code | code: str | stdout: str | Yes | Isolated container |
| `read_file` | File | path: str | content: str | Partial | Path validation |
| `http_request` | Web | url, method, body | response | No | Rate limited |

---

## Output Document

When invoking this skill, produce a markdown document saved to:
```
forensics-output/frameworks/{framework}/phase2/tool-interface-analysis.md
```

### Document Structure

The analysis document MUST follow this structure:

```markdown
# Tool Interface Analysis: {Framework Name}

## Summary
- **Tool Modeling**: [Base class / Protocol / Decorated functions / Pydantic models]
- **Schema Generation**: [Introspection / Pydantic / Decorator / Manual]
- **Registration Pattern**: [Declarative / Registry / Discovery / Factory]
- **Error Handling**: [Silent / Basic / Detailed / Structured]
- **Built-in Tools**: [Count] tools in [N] categories

## Tool Modeling

### Core Abstraction

**Type**: [Abstract Base Class / Protocol / Decorated Function / Pydantic Model / Hybrid]

**Location**: `path/to/tool.py:L##`

```python
# Show the core tool type definition
```

**Key Attributes**:
| Attribute | Type | Purpose |
|-----------|------|---------|
| name | str | Tool identifier for LLM |
| description | str | Tool purpose for LLM selection |
| parameters | ... | Input schema |
| ... | ... | ... |

**Inheritance/Composition**:
```
BaseTool
├── BuiltinTool
├── APITool
└── CustomTool
```

### Tool Creation Patterns

**Pattern 1: [Name]**
```python
# Example code
```

**Pattern 2: [Name]** (if applicable)
```python
# Example code
```

## Schema Generation

### Method Used

**Primary Method**: [Introspection / Pydantic / Decorator / Manual / Hybrid]

**Location**: `path/to/schema.py:L##`

### Schema Generation Code

```python
# Show how schemas are generated
```

### Generated Schema Example

```json
{
  "type": "function",
  "function": {
    "name": "example_tool",
    "description": "...",
    "parameters": {...}
  }
}
```

### Type Mapping

| Python Type | JSON Schema Type | Notes |
|-------------|-----------------|-------|
| str | string | |
| int | integer | |
| float | number | |
| bool | boolean | |
| list[T] | array | items type derived |
| dict | object | |
| Optional[T] | T | Not in required |
| Union[A, B] | anyOf/oneOf | |

## Built-in Tool Inventory

### Tool Categories

| Category | Tools | Purpose |
|----------|-------|---------|
| Search | [list] | Information retrieval |
| Code | [list] | Code execution |
| File | [list] | File operations |
| ... | ... | ... |

### Complete Tool List

| Tool Name | Location | Schema Method | Category | Notes |
|-----------|----------|---------------|----------|-------|
| `tool_name` | `path:L##` | Pydantic | Search | ... |
| ... | ... | ... | ... | ... |

### Tool Detail: [Example Tool]

**Purpose**: [What the tool does]

**Input Schema**:
```python
# Show input type/schema
```

**Output Type**: [Return type]

**Error Handling**: [How errors are reported]

## Registration & Discovery

### Registration Pattern

**Type**: [Declarative List / Registry / Discovery / Factory / Toolkit]

**Location**: `path/to/registration.py:L##`

### Registration Flow

```
1. Tool defined →
2. [Registration step] →
3. [Discovery step] →
4. Available to agent
```

### Code Example

```python
# Show registration code
```

### Dynamic vs Static

- **Static tools**: [List or describe]
- **Dynamic tools**: [How tools are added at runtime, if supported]

## Execution Flow

### Invocation Pattern

**Location**: `path/to/executor.py:L##`

```python
# Show tool execution code
```

### Validation

**Pre-execution validation**: [Yes/No, method]
**Schema validation**: [Pydantic / JSON Schema / Custom / None]

### Error Handling

| Error Type | Handling | Feedback to LLM |
|------------|----------|-----------------|
| Validation error | ... | ... |
| Execution error | ... | ... |
| Timeout | ... | ... |
| Permission denied | ... | ... |

### Error Feedback Pattern

```python
# Show how errors are formatted for LLM
```

### Retry Mechanisms

- **Automatic retry**: [Yes/No, attempts, backoff]
- **Self-correction**: [Yes/No, LLM-guided]
- **Fallback**: [Yes/No, chain description]

## Parallel Execution

**Supported**: [Yes/No]

**Location**: `path/to/parallel.py:L##`

**Pattern**: [Concurrent futures / asyncio.gather / Task groups]

```python
# Show parallel execution code if present
```

## Code References

- `path/to/base_tool.py:L##` - Core tool abstraction
- `path/to/schema.py:L##` - Schema generation
- `path/to/registry.py:L##` - Tool registration
- `path/to/executor.py:L##` - Tool execution
- `path/to/builtin/*.py` - Built-in tools
- ... (include all key file:line references)

## Implications for New Framework

### Positive Patterns
- **Pattern 1**: [Description and why to adopt]
- **Pattern 2**: [Description and why to adopt]
- ...

### Considerations
- **Trade-off 1**: [Description]
- **Trade-off 2**: [Description]
- ...

## Anti-Patterns Observed

- **Anti-pattern 1**: [Description and location]
- **Anti-pattern 2**: [Description and location]
- ...
```

---

## Integration Points

- **Prerequisite**: `codebase-mapping` to identify tool-related files
- **Related**: `harness-model-protocol` for wire encoding of tool calls
- **Related**: `resilience-analysis` for error handling patterns
- **Feeds into**: `comparative-matrix` for interface decisions
- **Feeds into**: `architecture-synthesis` for tool layer design

## Key Questions to Answer

1. How is a "tool" represented in this framework? (type, class, protocol)
2. How are tool schemas generated from definitions?
3. What built-in tools ship with the framework?
4. How are tools registered and discovered?
5. How is tool execution orchestrated?
6. How are errors fed back to the LLM for retry?
7. Does the framework support parallel tool execution?
8. How does validation work (pre-execution, schema-based)?
9. What retry/self-correction mechanisms exist?
10. Can tools be dynamically added/removed at runtime?

## Files to Examine

When analyzing a framework, prioritize these file patterns:

| Pattern | Purpose |
|---------|---------|
| `**/tool*.py`, `**/tools/**` | Tool definitions and base classes |
| `**/schema*.py` | Schema generation |
| `**/registry*.py`, `**/register*.py` | Tool registration |
| `**/executor*.py`, `**/runner*.py` | Tool execution |
| `**/builtin*.py`, `**/default*.py` | Built-in tool inventory |
| `**/error*.py`, `**/exception*.py` | Error types and handling |
| `**/validation*.py` | Argument validation |
| `**/function*.py`, `**/callable*.py` | Function-based tools |
