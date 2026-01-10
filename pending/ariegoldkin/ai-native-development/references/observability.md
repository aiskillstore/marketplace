# AI Observability & Cost Management Reference

## Overview

AI observability tracks LLM performance, costs, and quality. This reference covers monitoring patterns, cost optimization, and debugging strategies for production AI applications.

---

## LangSmith Integration

### Setup

```typescript
import { Client } from 'langsmith'

const langsmith = new Client({
  apiKey: process.env.LANGSMITH_API_KEY
})
```

### Tracing LLM Calls

```typescript
async function tracedLLMCall(input: string) {
  const runId = await langsmith.createRun({
    name: 'chat_completion',
    run_type: 'llm',
    inputs: { prompt: input },
    tags: ['production', 'chatbot']
  })

  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages: [{ role: 'user', content: input }]
    })

    const output = response.choices[0].message.content!

    await langsmith.updateRun(runId, {
      outputs: { response: output },
      end_time: Date.now(),
      extra: {
        model: 'gpt-4-turbo-preview',
        tokens: response.usage
      }
    })

    return output
  } catch (error) {
    await langsmith.updateRun(runId, {
      error: error.message,
      end_time: Date.now()
    })
    throw error
  }
}
```

### Tracing RAG Pipelines

```typescript
async function tracedRAG(question: string) {
  const pipelineRunId = await langsmith.createRun({
    name: 'rag_pipeline',
    run_type: 'chain',
    inputs: { question }
  })

  try {
    // 1. Retrieval step
    const retrievalRunId = await langsmith.createRun({
      name: 'retrieval',
      run_type: 'retriever',
      inputs: { query: question },
      parent_run_id: pipelineRunId
    })

    const docs = await queryDocuments(question, 5)

    await langsmith.updateRun(retrievalRunId, {
      outputs: { documents: docs },
      end_time: Date.now()
    })

    // 2. Generation step
    const generationRunId = await langsmith.createRun({
      name: 'generation',
      run_type: 'llm',
      inputs: { question, context: docs },
      parent_run_id: pipelineRunId
    })

    const answer = await ragQuery(question, docs)

    await langsmith.updateRun(generationRunId, {
      outputs: { answer },
      end_time: Date.now()
    })

    await langsmith.updateRun(pipelineRunId, {
      outputs: { answer },
      end_time: Date.now()
    })

    return answer
  } catch (error) {
    await langsmith.updateRun(pipelineRunId, {
      error: error.message,
      end_time: Date.now()
    })
    throw error
  }
}
```

---

## LangFuse Integration

### Setup

```typescript
import { Langfuse } from 'langfuse'

const langfuse = new Langfuse({
  publicKey: process.env.LANGFUSE_PUBLIC_KEY,
  secretKey: process.env.LANGFUSE_SECRET_KEY
})
```

### Tracking Generations

```typescript
async function langfuseTracking(userMessage: string) {
  const trace = langfuse.trace({
    name: 'chat-completion',
    userId: 'user-123',
    sessionId: 'session-456'
  })

  const generation = trace.generation({
    name: 'openai-call',
    model: 'gpt-4-turbo-preview',
    input: userMessage
  })

  const response = await openai.chat.completions.create({
    model: 'gpt-4-turbo-preview',
    messages: [{ role: 'user', content: userMessage }]
  })

  const output = response.choices[0].message.content!

  generation.end({
    output,
    usage: {
      promptTokens: response.usage!.prompt_tokens,
      completionTokens: response.usage!.completion_tokens,
      totalTokens: response.usage!.total_tokens
    }
  })

  await langfuse.flushAsync()

  return output
}
```

### Scoring & Feedback

```typescript
async function scoreGeneration(traceId: string, generationId: string, feedback: any) {
  langfuse.score({
    traceId,
    observationId: generationId,
    name: 'user-feedback',
    value: feedback.rating, // 1-5
    comment: feedback.comment
  })

  await langfuse.flushAsync()
}
```

---

## Custom Logging

### Structured Logger

```typescript
interface LLMLog {
  timestamp: Date
  traceId: string
  model: string
  prompt: string
  response: string
  tokens: { input: number; output: number; total: number }
  latency: number
  cost: number
  metadata?: Record<string, any>
}

class LLMLogger {
  private logs: LLMLog[] = []

  async log(entry: Omit<LLMLog, 'timestamp' | 'traceId'>) {
    const log: LLMLog = {
      ...entry,
      timestamp: new Date(),
      traceId: generateTraceId()
    }

    this.logs.push(log)

    // Persist to database
    await db.llmLogs.create({ data: log })

    // Send to analytics
    await analytics.track('llm_call', log)

    return log.traceId
  }

  async query(filters: Partial<LLMLog>) {
    return this.logs.filter(log =>
      Object.entries(filters).every(([key, value]) => log[key] === value)
    )
  }

  async aggregate(timeRange: { start: Date; end: Date }) {
    const filtered = this.logs.filter(
      log => log.timestamp >= timeRange.start && log.timestamp <= timeRange.end
    )

    return {
      totalCalls: filtered.length,
      totalTokens: filtered.reduce((sum, log) => sum + log.tokens.total, 0),
      totalCost: filtered.reduce((sum, log) => sum + log.cost, 0),
      avgLatency: filtered.reduce((sum, log) => sum + log.latency, 0) / filtered.length,
      modelBreakdown: this.groupBy(filtered, 'model')
    }
  }

  private groupBy(logs: LLMLog[], key: keyof LLMLog) {
    return logs.reduce((acc, log) => {
      const value = log[key]
      if (!acc[value]) acc[value] = []
      acc[value].push(log)
      return acc
    }, {} as Record<string, LLMLog[]>)
  }
}
```

### Usage Tracking Wrapper

```typescript
const logger = new LLMLogger()

async function loggedLLMCall(prompt: string, metadata?: Record<string, any>) {
  const startTime = Date.now()

  const response = await openai.chat.completions.create({
    model: 'gpt-4-turbo-preview',
    messages: [{ role: 'user', content: prompt }]
  })

  const latency = Date.now() - startTime
  const output = response.choices[0].message.content!

  await logger.log({
    model: 'gpt-4-turbo-preview',
    prompt,
    response: output,
    tokens: {
      input: response.usage!.prompt_tokens,
      output: response.usage!.completion_tokens,
      total: response.usage!.total_tokens
    },
    latency,
    cost: estimateCost(response.usage!),
    metadata
  })

  return output
}
```

---

## Token Counting

### Accurate Token Counting

```typescript
import { encoding_for_model } from 'tiktoken'

function countTokens(text: string, model = 'gpt-4'): number {
  const encoder = encoding_for_model(model)
  const tokens = encoder.encode(text)
  encoder.free()
  return tokens.length
}

// Count tokens in messages
function countMessageTokens(messages: Message[], model = 'gpt-4'): number {
  const encoder = encoding_for_model(model)

  let numTokens = 0

  for (const message of messages) {
    numTokens += 4 // Every message has 4 tokens overhead
    numTokens += encoder.encode(message.content).length

    if (message.role === 'system') {
      numTokens += 1
    }
  }

  numTokens += 2 // Every reply is primed with 2 tokens

  encoder.free()
  return numTokens
}
```

### Cost Estimation

```typescript
interface PricingTable {
  [model: string]: {
    input: number // per 1K tokens
    output: number // per 1K tokens
  }
}

const PRICING: PricingTable = {
  'gpt-4-turbo-preview': { input: 0.01, output: 0.03 },
  'gpt-3.5-turbo': { input: 0.0005, output: 0.0015 },
  'claude-3-5-sonnet-20241022': { input: 0.003, output: 0.015 }
}

function estimateCost(usage: { prompt_tokens: number; completion_tokens: number }, model: string): number {
  const pricing = PRICING[model]

  if (!pricing) {
    console.warn(`No pricing for model: ${model}`)
    return 0
  }

  const inputCost = (usage.prompt_tokens / 1000) * pricing.input
  const outputCost = (usage.completion_tokens / 1000) * pricing.output

  return inputCost + outputCost
}

// Budget tracking
class BudgetTracker {
  private spent = 0
  private limit: number

  constructor(dailyLimit: number) {
    this.limit = dailyLimit
  }

  async track(cost: number): Promise<boolean> {
    this.spent += cost

    if (this.spent >= this.limit) {
      await this.alert(`Daily budget exceeded: $${this.spent.toFixed(4)}`)
      return false
    }

    return true
  }

  private async alert(message: string) {
    // Send alert to monitoring system
    console.error(message)
    await notifyOncall(message)
  }
}
```

---

## Performance Monitoring

### Latency Tracking

```typescript
class LatencyMonitor {
  private measurements: Map<string, number[]> = new Map()

  measure(operation: string, latency: number) {
    if (!this.measurements.has(operation)) {
      this.measurements.set(operation, [])
    }

    this.measurements.get(operation)!.push(latency)
  }

  getStats(operation: string) {
    const latencies = this.measurements.get(operation) || []

    if (latencies.length === 0) return null

    const sorted = latencies.sort((a, b) => a - b)

    return {
      count: latencies.length,
      mean: latencies.reduce((a, b) => a + b, 0) / latencies.length,
      median: sorted[Math.floor(sorted.length / 2)],
      p95: sorted[Math.floor(sorted.length * 0.95)],
      p99: sorted[Math.floor(sorted.length * 0.99)],
      min: sorted[0],
      max: sorted[sorted.length - 1]
    }
  }
}

const latencyMonitor = new LatencyMonitor()

async function monitoredCall(prompt: string) {
  const start = Date.now()

  const response = await openai.chat.completions.create({
    model: 'gpt-4-turbo-preview',
    messages: [{ role: 'user', content: prompt }]
  })

  const latency = Date.now() - start

  latencyMonitor.measure('openai-gpt4', latency)

  if (latency > 10000) {
    console.warn(`Slow LLM call: ${latency}ms`)
  }

  return response.choices[0].message.content!
}
```

### Quality Metrics

```typescript
interface QualityMetrics {
  relevance: number // 0-1
  coherence: number // 0-1
  factuality: number // 0-1
  citations: number // count
}

async function evaluateQuality(question: string, answer: string, sources: any[]): Promise<QualityMetrics> {
  const evaluation = await openai.chat.completions.create({
    model: 'gpt-4-turbo-preview',
    messages: [
      {
        role: 'system',
        content: `Evaluate this answer on a scale of 0-1:
- Relevance: Does it answer the question?
- Coherence: Is it well-structured and logical?
- Factuality: Is it accurate based on sources?

Return JSON: { relevance: number, coherence: number, factuality: number, citations: number }`
      },
      {
        role: 'user',
        content: `Question: ${question}\nAnswer: ${answer}\nSources: ${JSON.stringify(sources)}`
      }
    ],
    response_format: { type: 'json_object' }
  })

  return JSON.parse(evaluation.choices[0].message.content!)
}
```

---

## Debugging

### Prompt Logging

```typescript
function logPrompt(messages: Message[]) {
  console.log('\n=== PROMPT ===')
  messages.forEach((msg, i) => {
    console.log(`[${i}] ${msg.role}:`)
    console.log(msg.content)
    console.log('---')
  })
  console.log('=== END PROMPT ===\n')
}

async function debuggableLLMCall(messages: Message[]) {
  if (process.env.DEBUG_PROMPTS === 'true') {
    logPrompt(messages)
  }

  const response = await openai.chat.completions.create({
    model: 'gpt-4-turbo-preview',
    messages
  })

  if (process.env.DEBUG_PROMPTS === 'true') {
    console.log('RESPONSE:', response.choices[0].message.content)
    console.log('USAGE:', response.usage)
  }

  return response.choices[0].message.content!
}
```

### Error Analysis

```typescript
class ErrorAnalyzer {
  private errors: Map<string, number> = new Map()

  track(error: Error, context: any) {
    const key = `${error.name}:${error.message}`

    this.errors.set(key, (this.errors.get(key) || 0) + 1)

    if (this.errors.get(key)! > 10) {
      this.alert(`Recurring error: ${key}`, context)
    }
  }

  private async alert(message: string, context: any) {
    console.error(message, context)
    // Send to monitoring system
  }

  getTopErrors(limit = 10) {
    return Array.from(this.errors.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, limit)
  }
}
```

---

## Best Practices

### Sampling for Cost Reduction

```typescript
// Only trace 1% of production traffic
async function sampledTracing(input: string) {
  const shouldTrace = Math.random() < 0.01

  if (shouldTrace) {
    return tracedLLMCall(input)
  }

  return simpleLLMCall(input)
}
```

### Alerts & Thresholds

```typescript
class AlertManager {
  private thresholds = {
    latency: 5000, // ms
    errorRate: 0.05, // 5%
    costPerHour: 10 // dollars
  }

  checkLatency(latency: number) {
    if (latency > this.thresholds.latency) {
      this.sendAlert('high_latency', { latency })
    }
  }

  checkErrorRate(errors: number, total: number) {
    const rate = errors / total

    if (rate > this.thresholds.errorRate) {
      this.sendAlert('high_error_rate', { rate, errors, total })
    }
  }

  private async sendAlert(type: string, data: any) {
    // Send to PagerDuty, Slack, etc.
    console.error(`ALERT [${type}]:`, data)
  }
}
```

### Dashboard Metrics

Key metrics to track:
- **Throughput**: Requests per minute
- **Latency**: P50, P95, P99 response times
- **Token Usage**: Input/output tokens per hour
- **Cost**: Hourly/daily spend
- **Error Rate**: % of failed requests
- **Quality**: User feedback scores
- **Model Distribution**: % usage by model
