---
name: streaming-api-patterns
description: Implement real-time data streaming with Server-Sent Events (SSE), WebSockets, and ReadableStream APIs. Master backpressure handling, reconnection strategies, and LLM streaming for 2025+ real-time applications.
version: 1.0.0
author: AI Agent Hub
tags: [streaming, sse, websocket, real-time, api, 2025]
---

# Streaming API Patterns

## Overview

Modern applications require real-time data delivery. This skill covers Server-Sent Events (SSE) for server-to-client streaming, WebSockets for bidirectional communication, and the Streams API for handling backpressure and efficient data flow.

**When to use this skill:**
- Streaming LLM responses (ChatGPT-style interfaces)
- Real-time notifications and updates
- Live data feeds (stock prices, analytics)
- Chat applications
- Progress updates for long-running tasks
- Collaborative editing features

## Core Technologies

### 1. Server-Sent Events (SSE)

**Best for**: Server-to-client streaming (LLM responses, notifications)

```typescript
// Next.js Route Handler
export async function GET(req: Request) {
  const encoder = new TextEncoder()

  const stream = new ReadableStream({
    async start(controller) {
      // Send data
      controller.enqueue(encoder.encode('data: Hello\n\n'))

      // Keep connection alive
      const interval = setInterval(() => {
        controller.enqueue(encoder.encode(': keepalive\n\n'))
      }, 30000)

      // Cleanup
      req.signal.addEventListener('abort', () => {
        clearInterval(interval)
        controller.close()
      })
    }
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    }
  })
}

// Client
const eventSource = new EventSource('/api/stream')
eventSource.onmessage = (event) => {
  console.log(event.data)
}
```

### 2. WebSockets

**Best for**: Bidirectional real-time communication (chat, collaboration)

```typescript
// WebSocket Server (Next.js with ws)
import { WebSocketServer } from 'ws'

const wss = new WebSocketServer({ port: 8080 })

wss.on('connection', (ws) => {
  ws.on('message', (data) => {
    // Broadcast to all clients
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(data)
      }
    })
  })
})

// Client
const ws = new WebSocket('ws://localhost:8080')
ws.onmessage = (event) => console.log(event.data)
ws.send(JSON.stringify({ type: 'message', text: 'Hello' }))
```

### 3. ReadableStream API

**Best for**: Processing large data streams with backpressure

```typescript
async function* generateData() {
  for (let i = 0; i < 1000; i++) {
    await new Promise(resolve => setTimeout(resolve, 100))
    yield `data-${i}`
  }
}

const stream = new ReadableStream({
  async start(controller) {
    for await (const chunk of generateData()) {
      controller.enqueue(new TextEncoder().encode(chunk + '\n'))
    }
    controller.close()
  }
})
```

## LLM Streaming Pattern

```typescript
// Server
import OpenAI from 'openai'

const openai = new OpenAI()

export async function POST(req: Request) {
  const { messages } = await req.json()

  const stream = await openai.chat.completions.create({
    model: 'gpt-4-turbo-preview',
    messages,
    stream: true
  })

  const encoder = new TextEncoder()

  return new Response(
    new ReadableStream({
      async start(controller) {
        for await (const chunk of stream) {
          const content = chunk.choices[0]?.delta?.content
          if (content) {
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({ content })}\n\n`))
          }
        }
        controller.enqueue(encoder.encode('data: [DONE]\n\n'))
        controller.close()
      }
    }),
    {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache'
      }
    }
  )
}

// Client
async function streamChat(messages) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages })
  })

  const reader = response.body.getReader()
  const decoder = new TextDecoder()

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    const chunk = decoder.decode(value)
    const lines = chunk.split('\n')

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6)
        if (data === '[DONE]') return

        const json = JSON.parse(data)
        console.log(json.content) // Stream token
      }
    }
  }
}
```

## Reconnection Strategy

```typescript
class ReconnectingEventSource {
  private eventSource: EventSource | null = null
  private reconnectDelay = 1000
  private maxReconnectDelay = 30000

  constructor(private url: string, private onMessage: (data: string) => void) {
    this.connect()
  }

  private connect() {
    this.eventSource = new EventSource(this.url)

    this.eventSource.onmessage = (event) => {
      this.reconnectDelay = 1000 // Reset on success
      this.onMessage(event.data)
    }

    this.eventSource.onerror = () => {
      this.eventSource?.close()

      // Exponential backoff
      setTimeout(() => this.connect(), this.reconnectDelay)
      this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay)
    }
  }

  close() {
    this.eventSource?.close()
  }
}
```

## Best Practices

### SSE
- ✅ Use for one-way server-to-client streaming
- ✅ Implement automatic reconnection
- ✅ Send keepalive messages every 30s
- ✅ Handle browser connection limits (6 per domain)
- ✅ Use HTTP/2 for better performance

### WebSockets
- ✅ Use for bidirectional real-time communication
- ✅ Implement heartbeat/ping-pong
- ✅ Handle reconnection with exponential backoff
- ✅ Validate and sanitize messages
- ✅ Implement message queuing for offline periods

### Backpressure
- ✅ Use ReadableStream with proper flow control
- ✅ Monitor buffer sizes
- ✅ Pause production when consumer is slow
- ✅ Implement timeouts for slow consumers

### Performance
- ✅ Compress data (gzip/brotli)
- ✅ Batch small messages
- ✅ Use binary formats (MessagePack, Protobuf) for large data
- ✅ Implement client-side buffering
- ✅ Monitor connection count and resource usage

## Resources

- [Server-Sent Events Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)
- [Streams API](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API)
- [Vercel AI SDK](https://sdk.vercel.ai/docs)
