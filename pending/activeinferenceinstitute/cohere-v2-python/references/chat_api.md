# Cohere Chat API v2 Reference

## Overview

The Cohere Chat API v2 enables conversational text generation through Cohere's LLMs. It supports multi-turn conversations, system messages for instruction following, streaming responses, and advanced features like tool use and structured outputs.

## Installation

```bash
pip install cohere
```

## Basic Setup

```python
import cohere

# Initialize client
co = cohere.ClientV2(api_key="<YOUR API KEY>")

# Or use environment variable CO_API_KEY
co = cohere.ClientV2()
```

## Message Structure

Messages are the core of the Chat API. Each message requires:
- **content**: The message text
- **role**: The sender (`user`, `assistant`, `system`, or `tool`)

### Message Roles

- **user**: Messages from the end user
- **assistant**: Model-generated responses
- **system**: Instructions that guide model behavior (highest priority)
- **tool**: Results from tool/function calls

## Basic Chat

### Simple Request

```python
import cohere

co = cohere.ClientV2(api_key="<YOUR API KEY>")

response = co.chat(
    model="command-a-03-2025",
    messages=[
        {
            "role": "user",
            "content": "Write a title for a blog post about API design."
        }
    ],
)

print(response.message.content[0].text)
```

### Response Structure

```python
# Response object contains:
response.message.content[0].text  # Generated text
response.id                       # Unique response ID
response.finish_reason           # "COMPLETE" or "MAX_TOKENS"
response.meta.tokens             # Token usage information
response.meta.billed_units       # Billing information
```

## System Messages

System messages provide instructions that override other instructions. Place them first in the messages array:

```python
response = co.chat(
    model="command-a-03-2025",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant that speaks like a pirate."
        },
        {
            "role": "user",
            "content": "Tell me about the weather."
        }
    ],
)
```

## Multi-Turn Conversations

Include conversation history in the messages array:

```python
messages = [
    {"role": "user", "content": "What is the capital of France?"},
    {"role": "assistant", "content": "The capital of France is Paris."},
    {"role": "user", "content": "What is its population?"}
]

response = co.chat(
    model="command-a-03-2025",
    messages=messages,
)
```

## API Parameters

### Core Parameters

**model** (required, string)
- Model identifier for the request
- Examples: `"command-a-03-2025"`

**messages** (required, array)
- Array of message objects with `role` and `content`

**stream** (boolean, default: false)
- Enable streaming responses

### Generation Control

**temperature** (float, range: 0.0 - 2.0)
- Controls randomness in outputs
- Lower values (0.0-0.5): More deterministic, focused responses
- Higher values (0.8-2.0): More creative, diverse responses

**max_tokens** (integer)
- Maximum number of tokens to generate
- Does not include input tokens

**stop_sequences** (array of strings)
- Custom sequences where generation should stop
- Example: `["END", "\n\n"]`

**seed** (integer)
- For reproducible outputs
- Same seed with same inputs produces same output

### Sampling Parameters

**k** (integer, default: 0, range: 0-500)
- Top-k sampling: limits token candidates to top k options
- 0 disables top-k sampling

**p** (float, default: 0.75, range: 0.01-0.99)
- Top-p (nucleus) sampling: cumulative probability threshold
- Lower values: More focused outputs

**frequency_penalty** (float, default: 0.0, range: 0.0-1.0)
- Reduces repetition of frequently occurring tokens
- Higher values: Less repetition

**presence_penalty** (float, default: 0.0, range: 0.0-1.0)
- Penalizes tokens that have already appeared
- Higher values: Encourages more diverse vocabulary

### Advanced Features

**response_format** (object)
- Controls output structure
- Options: `{"type": "text"}` or `{"type": "json_object"}`
- For JSON schema mode, add `"schema"` field (see structured_outputs.md)

**tools** (array)
- Define functions the model can call
- Enables function calling and tool use
- Each tool has: `name`, `description`, `parameters`

**strict_tools** (boolean)
- Enforces strict tool parameter validation

**documents** (array)
- Provide external documents for RAG
- Each document has: `id`, `content`, optionally `title`

**safety_mode** (string)
- Options: `"CONTEXTUAL"`, `"STRICT"`, `"OFF"`
- Controls content safety filtering

**logprobs** (boolean)
- Returns log probabilities for generated tokens
- Useful for confidence scoring

**thinking** (object)
- Enables extended reasoning mode
- Configure with `{"enabled": true, "budget_tokens": 1000}`

**priority** (integer)
- Request priority level for queue management

## Streaming

Enable streaming for real-time token generation:

```python
response = co.chat_stream(
    model="command-a-03-2025",
    messages=[
        {"role": "user", "content": "Write a long story about a robot."}
    ],
)

for event in response:
    if event.type == "content-delta":
        print(event.delta.message.content.text, end="")
```

## RAG (Retrieval-Augmented Generation)

Provide external documents for context:

```python
documents = [
    {
        "id": "doc1",
        "title": "Product Documentation",
        "content": "Our API uses REST endpoints..."
    },
    {
        "id": "doc2",
        "content": "Authentication requires an API key..."
    }
]

response = co.chat(
    model="command-a-03-2025",
    messages=[
        {"role": "user", "content": "How do I authenticate?"}
    ],
    documents=documents,
)
```

## Tool Use (Function Calling)

Define tools for the model to call:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"]
            }
        }
    }
]

response = co.chat(
    model="command-a-03-2025",
    messages=[
        {"role": "user", "content": "What's the weather in Paris?"}
    ],
    tools=tools,
)

# Check if model wants to call a tool
if response.message.tool_calls:
    for tool_call in response.message.tool_calls:
        print(f"Tool: {tool_call.function.name}")
        print(f"Arguments: {tool_call.function.arguments}")
```

## Error Handling

```python
import cohere
from cohere.errors import CohereError

try:
    response = co.chat(
        model="command-a-03-2025",
        messages=[{"role": "user", "content": "Hello"}],
    )
except CohereError as e:
    print(f"Error: {e}")
```

## Best Practices

### Temperature Selection
- **Factual tasks** (0.0-0.3): Q&A, classification, extraction
- **Balanced** (0.5-0.7): General conversation, summaries
- **Creative** (0.8-1.5): Writing, brainstorming, storytelling

### Token Management
- Set `max_tokens` to prevent excessive costs
- Monitor `response.meta.tokens` for usage tracking
- Use `stop_sequences` for precise control

### Conversation Management
- Keep conversation history concise
- Summarize older messages to save tokens
- System messages override user instructions

### RAG Optimization
- Chunk documents appropriately (500-1000 tokens)
- Provide relevant documents only
- Include document IDs for citation tracking

### Tool Use
- Provide clear, detailed descriptions
- Use strong typing in parameter schemas
- Handle tool call responses properly

## Model Options

Available models (as of 2025):
- **command-a-03-2025**: Latest generation model

Check official documentation for current model availability and pricing.

## Rate Limits and Quotas

- Monitor `response.meta.billed_units` for usage
- Implement exponential backoff for rate limit errors
- Consider caching responses for repeated queries

## Additional Resources

- **API Reference**: https://docs.cohere.com/v2/reference/chat
- **Python SDK**: https://github.com/cohere-ai/cohere-python
- **PyPI Package**: https://pypi.org/project/cohere/
