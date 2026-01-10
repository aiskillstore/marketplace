---
name: harness-model-protocol
description: Analyze the protocol layer between agent harness and LLM model. Use when (1) understanding message wire formats and API contracts, (2) examining tool call encoding/decoding mechanisms, (3) evaluating streaming protocols and partial response handling, (4) identifying agentic chat primitives (system prompts, scratchpads, interrupts), (5) comparing multi-provider abstraction strategies, or (6) understanding how frameworks translate between native LLM APIs and internal representations.
---

# Harness-Model Protocol Analysis

Analyzes the interface layer between agent frameworks (harness) and language models. This skill examines the **wire protocol**, **message encoding**, and **agentic primitives** that enable tool-augmented conversation.

## Distinction from tool-interface-analysis

| tool-interface-analysis | harness-model-protocol |
|------------------------|------------------------|
| How tools are registered and discovered | How tool calls are encoded on the wire |
| Schema generation (Pydantic → JSON Schema) | Schema transmission to LLM API |
| Error feedback patterns | Response parsing and error extraction |
| Retry mechanisms at tool level | Streaming mechanics and partial responses |
| Tool execution orchestration | Message format translation |

## Process

1. **Map message protocol** — Identify wire format (OpenAI, Anthropic, custom)
2. **Trace tool call encoding** — How tool calls are requested and parsed
3. **Analyze streaming mechanics** — SSE, WebSocket, chunk handling
4. **Catalog agentic primitives** — System prompts, scratchpads, interrupts
5. **Evaluate provider abstraction** — How multi-LLM support is achieved

## Message Protocol Analysis

### Wire Format Families

**OpenAI-Compatible (Chat Completions)**
```python
{
    "model": "gpt-4",
    "messages": [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "...", "tool_calls": [...]},
        {"role": "tool", "tool_call_id": "...", "content": "..."}
    ],
    "tools": [...],
    "tool_choice": "auto" | "required" | {"type": "function", "function": {"name": "..."}}
}
```

**Anthropic Messages API**
```python
{
    "model": "claude-sonnet-4-20250514",
    "system": "...",  # System prompt separate from messages
    "messages": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": [
            {"type": "text", "text": "..."},
            {"type": "tool_use", "id": "...", "name": "...", "input": {...}}
        ]},
        {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "...", "content": "..."}
        ]}
    ],
    "tools": [...]
}
```

**Google Gemini (Generative AI)**
```python
{
    "contents": [
        {"role": "user", "parts": [{"text": "..."}]},
        {"role": "model", "parts": [
            {"text": "..."},
            {"functionCall": {"name": "...", "args": {...}}}
        ]},
        {"role": "user", "parts": [
            {"functionResponse": {"name": "...", "response": {...}}}
        ]}
    ],
    "tools": [{"functionDeclarations": [...]}]
}
```

### Key Dimensions

| Dimension | OpenAI | Anthropic | Gemini |
|-----------|--------|-----------|--------|
| System prompt | In messages | Separate field | In contents (optional) |
| Tool calls | `tool_calls` array | Content blocks | `functionCall` in parts |
| Tool results | Role `tool` | Role `user` + `tool_result` | `functionResponse` |
| Multi-tool | Single message | Single message | Single message |
| Streaming | SSE `data: {...}` | SSE `event: ...` | SSE chunks |

### Translation Patterns

**Universal Message Type**
```python
@dataclass
class UniversalMessage:
    role: Literal["system", "user", "assistant", "tool"]
    content: str | list[ContentBlock]
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None  # For tool results

@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict

class ProviderAdapter(Protocol):
    def to_native(self, messages: list[UniversalMessage]) -> dict: ...
    def from_native(self, response: dict) -> UniversalMessage: ...
```

**Adapter Registry**
```python
ADAPTERS = {
    "openai": OpenAIAdapter(),
    "anthropic": AnthropicAdapter(),
    "gemini": GeminiAdapter(),
}

def invoke(messages: list[UniversalMessage], provider: str) -> UniversalMessage:
    adapter = ADAPTERS[provider]
    native_request = adapter.to_native(messages)
    native_response = call_api(native_request)
    return adapter.from_native(native_response)
```

## Tool Call Encoding

### Request Encoding (Framework → LLM)

**Schema Transmission Strategies**

| Strategy | How tools reach LLM | Example |
|----------|---------------------|---------|
| Function calling API | Native `tools` parameter | OpenAI, Anthropic |
| System prompt injection | Tools described in system message | ReAct prompting |
| XML format | Tools in structured XML | Claude XML, custom |
| JSON mode + schema | Output constrained to schema | Structured outputs |

**Function Calling (Native)**
```python
def prepare_request(self, messages, tools):
    return {
        "messages": messages,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters_schema
                }
            }
            for tool in tools
        ],
        "tool_choice": self.tool_choice
    }
```

**System Prompt Injection (ReAct)**
```python
TOOL_PROMPT = """
You have access to the following tools:

{tools_description}

To use a tool, respond with:
Thought: [your reasoning]
Action: [tool name]
Action Input: [JSON arguments]

After receiving the observation, continue reasoning or provide final answer.
"""

def prepare_request(self, messages, tools):
    tools_desc = "\n".join(f"- {t.name}: {t.description}" for t in tools)
    system = TOOL_PROMPT.format(tools_description=tools_desc)
    return {"messages": [{"role": "system", "content": system}] + messages}
```

### Response Parsing (LLM → Framework)

**Function Call Extraction**
```python
def parse_response(self, response) -> ParsedResponse:
    message = response.choices[0].message

    if message.tool_calls:
        return ParsedResponse(
            type="tool_calls",
            tool_calls=[
                ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments)
                )
                for tc in message.tool_calls
            ]
        )
    else:
        return ParsedResponse(type="text", content=message.content)
```

**ReAct Parsing (Regex-Based)**
```python
REACT_PATTERN = r"Action:\s*(\w+)\s*Action Input:\s*(.+?)(?=Observation:|$)"

def parse_react_response(self, content: str) -> ParsedResponse:
    match = re.search(REACT_PATTERN, content, re.DOTALL)
    if match:
        tool_name = match.group(1).strip()
        arguments = json.loads(match.group(2).strip())
        return ParsedResponse(
            type="tool_calls",
            tool_calls=[ToolCall(id=str(uuid4()), name=tool_name, arguments=arguments)]
        )
    return ParsedResponse(type="text", content=content)
```

**XML Parsing**
```python
def parse_xml_response(self, content: str) -> ParsedResponse:
    root = ET.fromstring(f"<root>{content}</root>")
    tool_use = root.find(".//tool_use")
    if tool_use is not None:
        return ParsedResponse(
            type="tool_calls",
            tool_calls=[ToolCall(
                id=tool_use.get("id", str(uuid4())),
                name=tool_use.find("name").text,
                arguments=json.loads(tool_use.find("arguments").text)
            )]
        )
    return ParsedResponse(type="text", content=content)
```

### Tool Choice Constraints

| Constraint | Effect | Use Case |
|------------|--------|----------|
| `auto` | Model decides whether to call tools | General usage |
| `required` | Model must call at least one tool | Force tool use |
| `none` | Model cannot call tools | Planning phase |
| `{"function": {"name": "X"}}` | Model must call specific tool | Guided execution |

## Streaming Protocol Analysis

### SSE (Server-Sent Events)

**OpenAI Streaming**
```
data: {"id":"chatcmpl-...","choices":[{"delta":{"content":"Hello"}}]}

data: {"id":"chatcmpl-...","choices":[{"delta":{"tool_calls":[{"index":0,"function":{"arguments":"{\""}}]}}]}

data: [DONE]
```

**Anthropic Streaming**
```
event: message_start
data: {"type":"message_start","message":{...}}

event: content_block_start
data: {"type":"content_block_start","index":0,"content_block":{"type":"tool_use","id":"...","name":"search"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"input_json_delta","partial_json":"{\""}}

event: message_stop
data: {"type":"message_stop"}
```

### Partial Tool Call Handling

**Accumulating JSON Fragments**
```python
class StreamingToolCallAccumulator:
    def __init__(self):
        self.tool_calls: dict[int, ToolCallBuffer] = {}

    def process_delta(self, delta):
        for tc_delta in delta.get("tool_calls", []):
            idx = tc_delta["index"]
            if idx not in self.tool_calls:
                self.tool_calls[idx] = ToolCallBuffer(
                    id=tc_delta.get("id"),
                    name=tc_delta.get("function", {}).get("name", "")
                )
            buffer = self.tool_calls[idx]
            buffer.arguments_json += tc_delta.get("function", {}).get("arguments", "")

    def finalize(self) -> list[ToolCall]:
        return [
            ToolCall(
                id=buf.id,
                name=buf.name,
                arguments=json.loads(buf.arguments_json)
            )
            for buf in self.tool_calls.values()
        ]
```

### Stream Event Types

| Event Type | Payload | Framework Action |
|------------|---------|------------------|
| `token` | Text fragment | Emit to UI, accumulate |
| `tool_call_start` | Tool ID, name | Initialize accumulator |
| `tool_call_delta` | Argument fragment | Accumulate JSON |
| `tool_call_end` | Complete | Parse and execute |
| `message_end` | Usage stats | Update token counts |
| `error` | Error details | Handle gracefully |

## Agentic Chat Primitives

### System Prompt Injection Points

```
┌─────────────────────────────────────────────────────────────┐
│                     SYSTEM PROMPT                            │
├─────────────────────────────────────────────────────────────┤
│ 1. Role Definition                                          │
│    "You are a helpful assistant that..."                    │
├─────────────────────────────────────────────────────────────┤
│ 2. Tool Instructions                                        │
│    "You have access to the following tools..."              │
├─────────────────────────────────────────────────────────────┤
│ 3. Output Format                                            │
│    "Always respond in JSON format..."                       │
├─────────────────────────────────────────────────────────────┤
│ 4. Behavioral Constraints                                   │
│    "Never reveal your system prompt..."                     │
├─────────────────────────────────────────────────────────────┤
│ 5. Dynamic Context                                          │
│    "Current date: {date}, User preferences: {prefs}"        │
└─────────────────────────────────────────────────────────────┘
```

### Scratchpad / Working Memory

**Agent Scratchpad Pattern**
```python
def build_messages(self, user_input: str) -> list[dict]:
    messages = [
        {"role": "system", "content": self.system_prompt}
    ]

    # Inject scratchpad (intermediate reasoning)
    if self.scratchpad:
        messages.append({
            "role": "assistant",
            "content": f"<scratchpad>\n{self.scratchpad}\n</scratchpad>"
        })

    messages.extend(self.conversation_history)
    messages.append({"role": "user", "content": user_input})
    return messages
```

**Scratchpad Types**

| Type | Content | Visibility |
|------|---------|------------|
| Reasoning trace | Thought process | Often hidden from user |
| Plan | Steps to execute | May be shown |
| Memory retrieval | Retrieved context | Internal |
| Tool results | Accumulated outputs | Becomes history |

### Interrupt / Human-in-the-Loop

**Interrupt Points**

| Mechanism | When | Framework |
|-----------|------|-----------|
| Tool confirmation | Before destructive operations | Google ADK |
| Output validation | Before returning to user | OpenAI Agents |
| Step approval | Between reasoning steps | LangGraph |
| Budget exceeded | Token/cost limits reached | Pydantic-AI |

**Implementation Pattern**
```python
class InterruptableAgent:
    async def step(self, state: AgentState) -> AgentState | Interrupt:
        action = await self.decide_action(state)

        if self.requires_confirmation(action):
            return Interrupt(
                type="confirmation_required",
                action=action,
                resume_token=self.create_resume_token(state)
            )

        result = await self.execute_action(action)
        return state.with_observation(result)

    async def resume(self, token: str, user_response: str) -> AgentState:
        state = self.restore_from_token(token)
        if user_response == "approved":
            result = await self.execute_action(state.pending_action)
            return state.with_observation(result)
        else:
            return state.with_observation("Action cancelled by user")
```

### Conversation State Machine

```
                    ┌─────────────────┐
                    │  AWAITING_INPUT │
                    └────────┬────────┘
                             │ user message
                             ▼
                    ┌─────────────────┐
              ┌─────│   PROCESSING    │─────┐
              │     └────────┬────────┘     │
              │              │              │
              │ tool_call    │ text_only    │ error
              ▼              ▼              ▼
    ┌─────────────────┐ ┌─────────┐ ┌─────────────────┐
    │ EXECUTING_TOOLS │ │ RESPOND │ │ ERROR_RECOVERY  │
    └────────┬────────┘ └────┬────┘ └────────┬────────┘
             │               │               │
             │ results       │ complete      │ retry/abort
             ▼               ▼               │
    ┌─────────────────┐      │               │
    │   PROCESSING    │◄─────┴───────────────┘
    └─────────────────┘
```

## Multi-Provider Abstraction

### Abstraction Strategies

**Strategy 1: Thin Adapter (Recommended)**
```python
class LLMProvider(Protocol):
    async def complete(
        self,
        messages: list[Message],
        tools: list[Tool] | None = None,
        **kwargs
    ) -> Completion: ...

    async def stream(
        self,
        messages: list[Message],
        tools: list[Tool] | None = None,
        **kwargs
    ) -> AsyncIterator[StreamEvent]: ...

class OpenAIProvider(LLMProvider):
    async def complete(self, messages, tools=None, **kwargs):
        native = self._to_openai_format(messages, tools)
        response = await self.client.chat.completions.create(**native, **kwargs)
        return self._from_openai_response(response)
```

**Strategy 2: Unified Client (LangChain-style)**
```python
class ChatModel(ABC):
    @abstractmethod
    def invoke(self, messages: list[BaseMessage]) -> AIMessage: ...

    @abstractmethod
    def bind_tools(self, tools: list[BaseTool]) -> "ChatModel": ...

class ChatOpenAI(ChatModel): ...
class ChatAnthropic(ChatModel): ...
class ChatGemini(ChatModel): ...
```

**Strategy 3: Request/Response Translation**
```python
class ModelGateway:
    def __init__(self, providers: dict[str, ProviderClient]):
        self.providers = providers
        self.translators = {
            "openai": OpenAITranslator(),
            "anthropic": AnthropicTranslator(),
        }

    async def invoke(self, request: UnifiedRequest, provider: str) -> UnifiedResponse:
        translator = self.translators[provider]
        native_request = translator.to_native(request)
        native_response = await self.providers[provider].call(native_request)
        return translator.from_native(native_response)
```

### Provider Feature Matrix

| Feature | OpenAI | Anthropic | Gemini | Local (Ollama) |
|---------|--------|-----------|--------|----------------|
| Function calling | Yes | Yes | Yes | Model-dependent |
| Streaming | Yes | Yes | Yes | Yes |
| Tool choice | Yes | Yes | Limited | No |
| Parallel tools | Yes | Yes | Yes | No |
| Vision | Yes | Yes | Yes | Model-dependent |
| JSON mode | Yes | Limited | Yes | Model-dependent |
| Structured output | Yes | Beta | Yes | No |

---

## Output Document

When invoking this skill, produce a markdown document saved to:
```
forensics-output/frameworks/{framework}/phase2/harness-model-protocol.md
```

### Document Structure

The analysis document MUST follow this structure:

```markdown
# Harness-Model Protocol Analysis: {Framework Name}

## Summary
- **Key Finding 1**: [Most important protocol insight]
- **Key Finding 2**: [Second most important insight]
- **Key Finding 3**: [Third insight]
- **Classification**: [Brief characterization, e.g., "OpenAI-compatible with thin adapters"]

## Detailed Analysis

### Message Protocol

**Wire Format Family**: [OpenAI-compatible / Anthropic-native / Gemini-native / Custom]

**Providers Supported**:
- Provider 1 (adapter location)
- Provider 2 (adapter location)
- ...

**Abstraction Strategy**: [Thin adapter / Unified client / Gateway / None]

[Include code example showing message translation]

```python
# Example: How framework translates internal → provider format
```

**Role Handling**:
| Role | Internal Representation | OpenAI | Anthropic | Gemini |
|------|------------------------|--------|-----------|--------|
| System | ... | ... | ... | ... |
| User | ... | ... | ... | ... |
| Assistant | ... | ... | ... | ... |
| Tool Result | ... | ... | ... | ... |

### Tool Call Encoding

**Request Method**: [Function calling API / System prompt injection / Hybrid]

**Schema Transmission**:
```python
# Show how tool schemas are transmitted to the LLM
```

**Response Parsing**:
- **Parser Type**: [Native API / Regex / XML / Custom]
- **Location**: `path/to/parser.py:L##`

```python
# Show parsing logic
```

**Tool Choice Support**:
| Constraint | Supported | Implementation |
|------------|-----------|----------------|
| auto | Yes/No | ... |
| required | Yes/No | ... |
| none | Yes/No | ... |
| specific | Yes/No | ... |

### Streaming Implementation

**Protocol**: [SSE / WebSocket / Polling / None]

**Partial Tool Call Handling**:
- **Supported**: Yes/No
- **Accumulator Pattern**: [Describe if present]

```python
# Show streaming handler code
```

**Event Types Emitted**:
| Event | Payload | Handler Location |
|-------|---------|-----------------|
| token | text delta | `path:L##` |
| tool_start | tool id, name | `path:L##` |
| tool_delta | argument fragment | `path:L##` |
| ... | ... | ... |

### Agentic Primitives

#### System Prompt Assembly

**Pattern**: [Static / Dynamic / Callable]

```python
# Show system prompt construction
```

**Injection Points**:
1. Role definition
2. Tool instructions
3. Output format
4. Behavioral constraints
5. Dynamic context

#### Scratchpad / Working Memory

**Implemented**: Yes/No

[If yes, show pattern:]
```python
# Scratchpad injection pattern
```

#### Interrupt / Human-in-the-Loop

**Mechanisms**:
| Type | Trigger | Resume Pattern | Location |
|------|---------|---------------|----------|
| Tool confirmation | ... | ... | `path:L##` |
| Output validation | ... | ... | `path:L##` |
| ... | ... | ... | ... |

#### Conversation State Machine

**State Management**: [Explicit state machine / Implicit via history / Graph-based]

```
[ASCII diagram of state transitions if applicable]
```

### Provider Abstraction

| Provider | Adapter | Streaming | Tool Choice | Parallel Tools | Notes |
|----------|---------|-----------|-------------|----------------|-------|
| OpenAI | `path` | Yes/No | Full/Partial | Yes/No | ... |
| Anthropic | `path` | Yes/No | Full/Partial | Yes/No | ... |
| Gemini | `path` | Yes/No | Full/Partial | Yes/No | ... |
| ... | ... | ... | ... | ... | ... |

**Graceful Degradation**: [Describe how missing features are handled]

## Code References

- `path/to/message_types.py:L##` - Internal message representation
- `path/to/openai_adapter.py:L##` - OpenAI translation
- `path/to/streaming.py:L##` - Stream event handling
- `path/to/system_prompt.py:L##` - System prompt assembly
- ... (include all key file:line references)

## Implications for New Framework

### Positive Patterns
- **Pattern 1**: [Description and why to adopt]
- **Pattern 2**: [Description and why to adopt]
- ...

### Considerations
- **Consideration 1**: [Trade-off or limitation to be aware of]
- **Consideration 2**: [Trade-off or limitation to be aware of]
- ...

## Anti-Patterns Observed

- **Anti-pattern 1**: [Description and why to avoid]
- **Anti-pattern 2**: [Description and why to avoid]
- ...
```

---

## Integration Points

- **Prerequisite**: `codebase-mapping` to identify LLM client code
- **Related**: `tool-interface-analysis` for schema generation (this skill covers wire encoding)
- **Related**: `memory-orchestration` for context assembly patterns
- **Feeds into**: `comparative-matrix` for protocol decisions
- **Feeds into**: `architecture-synthesis` for abstraction layer design

## Key Questions to Answer

1. How does the framework translate between internal message types and provider-specific formats?
2. Does streaming handle partial tool calls correctly?
3. Are tool results properly attributed (tool_call_id matching)?
4. How are multi-turn tool conversations reconstructed for stateless APIs?
5. What agentic primitives (scratchpad, interrupt, confirmation) are supported?
6. How is the system prompt assembled and injected?
7. What happens when a provider doesn't support a feature (graceful degradation)?
8. Is there a universal message type or does the framework use provider-native types internally?
9. How are parallel tool calls handled (single message vs multiple)?
10. What streaming events are emitted and how can consumers subscribe?

## Files to Examine

When analyzing a framework, prioritize these file patterns:

| Pattern | Purpose |
|---------|---------|
| `**/llm*.py`, `**/model*.py` | LLM client code |
| `**/openai*.py`, `**/anthropic*.py`, `**/gemini*.py` | Provider adapters |
| `**/message*.py`, `**/types*.py` | Message type definitions |
| `**/stream*.py` | Streaming handlers |
| `**/prompt*.py`, `**/system*.py` | System prompt assembly |
| `**/chat*.py`, `**/conversation*.py` | Conversation management |
| `**/interrupt*.py`, `**/confirm*.py` | HITL mechanisms |
