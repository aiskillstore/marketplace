# Function Calling & Tool Use Reference

## Overview

Function calling enables LLMs to use external tools and APIs reliably. This reference covers tool definitions, calling patterns, and best practices for function-calling workflows.

---

## Function Definitions

### Basic Tool Definition

```typescript
const tools = [
  {
    type: 'function',
    function: {
      name: 'get_weather',
      description: 'Get current weather for a location',
      parameters: {
        type: 'object',
        properties: {
          location: {
            type: 'string',
            description: 'City and state, e.g., San Francisco, CA'
          },
          unit: {
            type: 'string',
            enum: ['celsius', 'fahrenheit'],
            description: 'Temperature unit'
          }
        },
        required: ['location']
      }
    }
  }
]
```

### Complex Tool with Nested Objects

```typescript
const complexTool = {
  type: 'function',
  function: {
    name: 'create_calendar_event',
    description: 'Create a new calendar event',
    parameters: {
      type: 'object',
      properties: {
        title: {
          type: 'string',
          description: 'Event title'
        },
        datetime: {
          type: 'object',
          properties: {
            start: {
              type: 'string',
              format: 'date-time',
              description: 'Event start time (ISO 8601)'
            },
            end: {
              type: 'string',
              format: 'date-time',
              description: 'Event end time (ISO 8601)'
            }
          },
          required: ['start', 'end']
        },
        attendees: {
          type: 'array',
          items: {
            type: 'string',
            format: 'email'
          },
          description: 'List of attendee email addresses'
        },
        reminders: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              method: {
                type: 'string',
                enum: ['email', 'popup']
              },
              minutes: {
                type: 'number',
                description: 'Minutes before event'
              }
            }
          }
        }
      },
      required: ['title', 'datetime']
    }
  }
}
```

---

## Function Calling Patterns

### Basic Function Calling Loop

```typescript
async function chatWithTools(userMessage: string) {
  const messages = [
    { role: 'system', content: 'You are a helpful assistant.' },
    { role: 'user', content: userMessage }
  ]

  while (true) {
    const response = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages,
      tools
    })

    const message = response.choices[0].message

    // No tool calls - return final answer
    if (!message.tool_calls) {
      return message.content
    }

    // Execute tool calls
    messages.push(message)

    for (const toolCall of message.tool_calls) {
      const functionName = toolCall.function.name
      const functionArgs = JSON.parse(toolCall.function.arguments)

      // Execute the function
      const result = await executeFunction(functionName, functionArgs)

      // Add result to messages
      messages.push({
        role: 'tool',
        tool_call_id: toolCall.id,
        content: JSON.stringify(result)
      })
    }

    // Loop continues to get final answer
  }
}
```

### Parallel Function Calling

```typescript
async function parallelToolCalling(userMessage: string) {
  const response = await openai.chat.completions.create({
    model: 'gpt-4-turbo-preview',
    messages: [{ role: 'user', content: userMessage }],
    tools,
    parallel_tool_calls: true // Allow multiple tools at once
  })

  const message = response.choices[0].message

  if (message.tool_calls) {
    // Execute all tool calls in parallel
    const results = await Promise.all(
      message.tool_calls.map(async toolCall => {
        const result = await executeFunction(
          toolCall.function.name,
          JSON.parse(toolCall.function.arguments)
        )

        return {
          tool_call_id: toolCall.id,
          role: 'tool',
          content: JSON.stringify(result)
        }
      })
    )

    // Continue with results
    const finalResponse = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages: [
        { role: 'user', content: userMessage },
        message,
        ...results
      ],
      tools
    })

    return finalResponse.choices[0].message.content
  }

  return message.content
}
```

### Streaming with Function Calls

```typescript
async function* streamWithTools(userMessage: string) {
  const stream = await openai.chat.completions.create({
    model: 'gpt-4-turbo-preview',
    messages: [{ role: 'user', content: userMessage }],
    tools,
    stream: true
  })

  let currentToolCall: any = null

  for await (const chunk of stream) {
    const delta = chunk.choices[0]?.delta

    // Tool call started
    if (delta.tool_calls) {
      const toolCall = delta.tool_calls[0]

      if (toolCall.function?.name) {
        currentToolCall = {
          id: toolCall.id,
          name: toolCall.function.name,
          arguments: ''
        }
      }

      if (toolCall.function?.arguments) {
        currentToolCall.arguments += toolCall.function.arguments
      }
    }

    // Regular content
    if (delta.content) {
      yield delta.content
    }
  }

  // Execute tool if present
  if (currentToolCall) {
    const result = await executeFunction(
      currentToolCall.name,
      JSON.parse(currentToolCall.arguments)
    )

    yield `\n\n[Tool: ${currentToolCall.name}]\n${JSON.stringify(result, null, 2)}`
  }
}
```

---

## Tool Implementation

### Function Registry

```typescript
type ToolFunction = (args: any) => Promise<any>

class ToolRegistry {
  private tools = new Map<string, ToolFunction>()

  register(name: string, fn: ToolFunction) {
    this.tools.set(name, fn)
  }

  async execute(name: string, args: any) {
    const tool = this.tools.get(name)

    if (!tool) {
      throw new Error(`Unknown tool: ${name}`)
    }

    try {
      return await tool(args)
    } catch (error) {
      return {
        error: error.message,
        tool: name,
        args
      }
    }
  }

  getDefinitions(): any[] {
    return Array.from(this.tools.keys()).map(name => ({
      type: 'function',
      function: this.getDefinition(name)
    }))
  }
}

// Usage
const registry = new ToolRegistry()

registry.register('get_weather', async ({ location, unit = 'fahrenheit' }) => {
  const response = await fetch(`https://api.weather.com/v1/location/${location}`)
  const data = await response.json()

  return {
    location,
    temperature: unit === 'celsius' ? data.tempC : data.tempF,
    condition: data.condition,
    unit
  }
})

registry.register('search_database', async ({ query, limit = 10 }) => {
  const results = await db.search(query, limit)
  return { results, count: results.length }
})
```

### Input Validation

```typescript
import { z } from 'zod'

const schemas = {
  get_weather: z.object({
    location: z.string().min(1),
    unit: z.enum(['celsius', 'fahrenheit']).default('fahrenheit')
  }),
  search_database: z.object({
    query: z.string().min(1),
    limit: z.number().int().min(1).max(100).default(10)
  })
}

async function executeWithValidation(name: string, args: any) {
  const schema = schemas[name]

  if (!schema) {
    throw new Error(`No schema for tool: ${name}`)
  }

  // Validate and parse
  const validated = schema.parse(args)

  // Execute with validated args
  return await registry.execute(name, validated)
}
```

---

## Advanced Patterns

### Conditional Tool Availability

```typescript
async function contextAwareTools(userMessage: string, context: any) {
  // Provide different tools based on context
  const availableTools = getToolsForContext(context)

  const response = await openai.chat.completions.create({
    model: 'gpt-4-turbo-preview',
    messages: [{ role: 'user', content: userMessage }],
    tools: availableTools
  })

  // ... handle response
}

function getToolsForContext(context: any) {
  const baseTools = [searchTool, calculatorTool]

  if (context.user?.isPremium) {
    baseTools.push(advancedAnalyticsTool)
  }

  if (context.permissions?.includes('admin')) {
    baseTools.push(adminTool)
  }

  return baseTools
}
```

### Tool Chaining

```typescript
async function chainTools(userMessage: string) {
  const messages = [{ role: 'user', content: userMessage }]
  const executedTools: string[] = []
  const maxChainLength = 5

  while (executedTools.length < maxChainLength) {
    const response = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages,
      tools
    })

    const message = response.choices[0].message

    if (!message.tool_calls) {
      return {
        answer: message.content,
        toolChain: executedTools
      }
    }

    messages.push(message)

    for (const toolCall of message.tool_calls) {
      const result = await executeFunction(
        toolCall.function.name,
        JSON.parse(toolCall.function.arguments)
      )

      executedTools.push(toolCall.function.name)

      messages.push({
        role: 'tool',
        tool_call_id: toolCall.id,
        content: JSON.stringify(result)
      })
    }
  }

  return {
    answer: 'Max tool chain length reached',
    toolChain: executedTools
  }
}
```

### Fallback Mechanisms

```typescript
async function robustToolCalling(userMessage: string) {
  try {
    return await chatWithTools(userMessage)
  } catch (error) {
    if (error.message.includes('tool')) {
      // Tool execution failed - try without tools
      const response = await openai.chat.completions.create({
        model: 'gpt-4-turbo-preview',
        messages: [
          {
            role: 'system',
            content: 'Tools are unavailable. Answer to the best of your ability.'
          },
          { role: 'user', content: userMessage }
        ]
      })

      return response.choices[0].message.content
    }

    throw error
  }
}
```

---

## Anthropic Claude Function Calling

### Tool Definitions for Claude

```typescript
const claudeTools = [
  {
    name: 'get_weather',
    description: 'Get current weather for a location',
    input_schema: {
      type: 'object',
      properties: {
        location: {
          type: 'string',
          description: 'City and state, e.g., San Francisco, CA'
        },
        unit: {
          type: 'string',
          enum: ['celsius', 'fahrenheit'],
          description: 'Temperature unit'
        }
      },
      required: ['location']
    }
  }
]
```

### Claude Tool Calling Loop

```typescript
import Anthropic from '@anthropic-ai/sdk'

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })

async function claudeWithTools(userMessage: string) {
  const messages = [{ role: 'user', content: userMessage }]

  while (true) {
    const response = await anthropic.messages.create({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 1024,
      tools: claudeTools,
      messages
    })

    // Check if tool use is present
    const toolUse = response.content.find(block => block.type === 'tool_use')

    if (!toolUse) {
      // No more tools - return final text
      const textBlock = response.content.find(block => block.type === 'text')
      return textBlock?.text || ''
    }

    // Execute tool
    const result = await executeFunction(toolUse.name, toolUse.input)

    // Add tool result
    messages.push(
      { role: 'assistant', content: response.content },
      {
        role: 'user',
        content: [
          {
            type: 'tool_result',
            tool_use_id: toolUse.id,
            content: JSON.stringify(result)
          }
        ]
      }
    )
  }
}
```

---

## Best Practices

### Tool Description Quality

```typescript
// ❌ Bad: Vague description
const badTool = {
  name: 'search',
  description: 'Search for stuff'
}

// ✅ Good: Specific, clear description
const goodTool = {
  name: 'search_products',
  description: 'Search the product catalog by name, category, or SKU. Returns product details including price, availability, and description.',
  parameters: {
    type: 'object',
    properties: {
      query: {
        type: 'string',
        description: 'Search query. Can be product name (e.g., "iPhone 15"), category (e.g., "smartphones"), or SKU (e.g., "IPH15-BLK-256").'
      }
    }
  }
}
```

### Error Handling

```typescript
async function safeToolExecution(name: string, args: any) {
  try {
    const result = await executeFunction(name, args)

    return {
      success: true,
      data: result
    }
  } catch (error) {
    // Return structured error for LLM to handle
    return {
      success: false,
      error: {
        message: error.message,
        type: error.name,
        recoverable: isRecoverableError(error)
      }
    }
  }
}

function isRecoverableError(error: Error): boolean {
  // Timeout, rate limit, etc. can be retried
  return ['ETIMEDOUT', 'ECONNRESET', 'RATE_LIMIT'].some(code =>
    error.message.includes(code)
  )
}
```

### Rate Limiting

```typescript
import pLimit from 'p-limit'

const limit = pLimit(5) // Max 5 concurrent tool calls

async function rateLimitedToolExecution(toolCalls: any[]) {
  return Promise.all(
    toolCalls.map(toolCall =>
      limit(() =>
        executeFunction(
          toolCall.function.name,
          JSON.parse(toolCall.function.arguments)
        )
      )
    )
  )
}
```
