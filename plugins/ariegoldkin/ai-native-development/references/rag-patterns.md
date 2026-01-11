# RAG (Retrieval-Augmented Generation) Patterns

## Overview

RAG combines retrieval systems with LLMs to provide accurate, grounded answers. This reference covers RAG architectures, implementation patterns, and optimization strategies.

---

## Basic RAG Pattern

### Simple RAG Query

```typescript
import OpenAI from 'openai'
import { queryDocuments } from './vectordb'

const openai = new OpenAI()

async function ragQuery(question: string): Promise<string> {
  // 1. Retrieve relevant documents
  const relevantDocs = await queryDocuments(question, 5)

  // 2. Construct context
  const context = relevantDocs
    .map((doc, i) => `[${i + 1}] ${doc.text}`)
    .join('\n\n')

  // 3. Generate answer with context
  const response = await openai.chat.completions.create({
    model: 'gpt-4-turbo-preview',
    messages: [
      {
        role: 'system',
        content: `You are a helpful assistant. Answer questions based ONLY on the provided context. If the answer is not in the context, say "I don't have enough information to answer that."`
      },
      {
        role: 'user',
        content: `Context:\n${context}\n\nQuestion: ${question}`
      }
    ],
    temperature: 0.1 // Low temperature for factual responses
  })

  return response.choices[0].message.content!
}
```

---

## RAG with Citations

### Citation-Based Answers

```typescript
async function ragQueryWithCitations(question: string) {
  const relevantDocs = await queryDocuments(question, 5)

  const context = relevantDocs
    .map((doc, i) => `[${i + 1}] ${doc.text}\nSource: ${doc.source}`)
    .join('\n\n')

  const response = await openai.chat.completions.create({
    model: 'gpt-4-turbo-preview',
    messages: [
      {
        role: 'system',
        content: `Answer questions based on the provided context. ALWAYS cite your sources using [1], [2], etc. Format your answer as:

Answer: [your response with inline citations]

Sources:
- [1]: [source 1]
- [2]: [source 2]`
      },
      {
        role: 'user',
        content: `Context:\n${context}\n\nQuestion: ${question}`
      }
    ]
  })

  return {
    answer: response.choices[0].message.content!,
    sources: relevantDocs.map((doc, i) => ({
      index: i + 1,
      text: doc.text,
      source: doc.source,
      similarity: doc.score
    }))
  }
}
```

### Structured Citations with JSON Mode

```typescript
async function ragWithStructuredCitations(question: string) {
  const relevantDocs = await queryDocuments(question, 5)

  const response = await openai.chat.completions.create({
    model: 'gpt-4-turbo-preview',
    messages: [
      {
        role: 'system',
        content: 'Provide answers with citations in JSON format.'
      },
      {
        role: 'user',
        content: `Context: ${JSON.stringify(relevantDocs)}\n\nQuestion: ${question}`
      }
    ],
    response_format: { type: 'json_object' }
  })

  return JSON.parse(response.choices[0].message.content!)
}
```

---

## Hybrid Search

### Semantic + Keyword Search

```typescript
async function hybridSearch(query: string, topK = 5) {
  // 1. Semantic search with embeddings
  const semanticResults = await queryDocuments(query, topK * 2)

  // 2. Keyword search (BM25, Elasticsearch, etc.)
  const keywordResults = await keywordSearch(query, topK * 2)

  // 3. Combine and re-rank using Reciprocal Rank Fusion (RRF)
  const combined = reciprocalRankFusion(semanticResults, keywordResults)

  return combined.slice(0, topK)
}

function reciprocalRankFusion(
  semanticResults: any[],
  keywordResults: any[],
  k = 60
): any[] {
  const scores = new Map()

  semanticResults.forEach((doc, rank) => {
    const score = 1 / (k + rank + 1)
    scores.set(doc.id, (scores.get(doc.id) || 0) + score)
  })

  keywordResults.forEach((doc, rank) => {
    const score = 1 / (k + rank + 1)
    scores.set(doc.id, (scores.get(doc.id) || 0) + score)
  })

  return Array.from(scores.entries())
    .map(([id, score]) => ({
      id,
      score,
      doc: semanticResults.find(r => r.id === id) || keywordResults.find(r => r.id === id)
    }))
    .sort((a, b) => b.score - a.score)
    .map(({ doc }) => doc)
}
```

### Weighted Hybrid Search

```typescript
async function weightedHybridSearch(
  query: string,
  semanticWeight = 0.7,
  keywordWeight = 0.3
) {
  const semanticResults = await queryDocuments(query, 10)
  const keywordResults = await keywordSearch(query, 10)

  const scores = new Map()

  semanticResults.forEach((doc, i) => {
    const normalizedRank = 1 - (i / semanticResults.length)
    scores.set(doc.id, (scores.get(doc.id) || 0) + normalizedRank * semanticWeight)
  })

  keywordResults.forEach((doc, i) => {
    const normalizedRank = 1 - (i / keywordResults.length)
    scores.set(doc.id, (scores.get(doc.id) || 0) + normalizedRank * keywordWeight)
  })

  return Array.from(scores.entries())
    .sort((a, b) => b[1] - a[1])
    .map(([id]) => semanticResults.find(r => r.id === id) || keywordResults.find(r => r.id === id))
}
```

---

## Advanced RAG Patterns

### Multi-Query RAG

Generate multiple query variations for better recall:

```typescript
async function multiQueryRAG(question: string) {
  // 1. Generate query variations
  const variations = await openai.chat.completions.create({
    model: 'gpt-3.5-turbo',
    messages: [
      {
        role: 'system',
        content: 'Generate 3 different phrasings of the user question for better document retrieval.'
      },
      { role: 'user', content: question }
    ]
  })

  const queries = variations.choices[0].message.content!.split('\n')

  // 2. Retrieve for each query
  const allResults = await Promise.all(
    queries.map(q => queryDocuments(q, 3))
  )

  // 3. Deduplicate and merge
  const uniqueDocs = new Map()
  allResults.flat().forEach(doc => {
    if (!uniqueDocs.has(doc.id) || doc.score > uniqueDocs.get(doc.id).score) {
      uniqueDocs.set(doc.id, doc)
    }
  })

  const topDocs = Array.from(uniqueDocs.values())
    .sort((a, b) => b.score - a.score)
    .slice(0, 5)

  // 4. Generate answer
  return ragQuery(question, topDocs)
}
```

### HyDE (Hypothetical Document Embeddings)

Generate a hypothetical answer and use it for retrieval:

```typescript
async function hydeRAG(question: string) {
  // 1. Generate hypothetical answer
  const hypothetical = await openai.chat.completions.create({
    model: 'gpt-3.5-turbo',
    messages: [
      {
        role: 'system',
        content: 'Write a detailed answer to this question as if you had the information.'
      },
      { role: 'user', content: question }
    ]
  })

  const hypotheticalAnswer = hypothetical.choices[0].message.content!

  // 2. Use hypothetical answer for retrieval
  const relevantDocs = await queryDocuments(hypotheticalAnswer, 5)

  // 3. Generate real answer from retrieved docs
  return ragQuery(question, relevantDocs)
}
```

### Contextual Compression

Filter retrieved chunks to only relevant sentences:

```typescript
async function compressiveRAG(question: string) {
  const relevantDocs = await queryDocuments(question, 10)

  // Extract only relevant sentences from each document
  const compressed = await Promise.all(
    relevantDocs.map(async doc => {
      const response = await openai.chat.completions.create({
        model: 'gpt-3.5-turbo',
        messages: [
          {
            role: 'system',
            content: 'Extract ONLY the sentences relevant to answering the question. Return them as-is.'
          },
          {
            role: 'user',
            content: `Question: ${question}\n\nDocument: ${doc.text}`
          }
        ]
      })

      return {
        ...doc,
        text: response.choices[0].message.content!
      }
    })
  )

  return ragQuery(question, compressed)
}
```

---

## Conversation Memory

### Chat with Memory

```typescript
interface ConversationMemory {
  messages: Message[]
  summary?: string
}

async function ragChat(
  question: string,
  memory: ConversationMemory
): Promise<{ answer: string; memory: ConversationMemory }> {
  // 1. Retrieve relevant docs
  const relevantDocs = await queryDocuments(question, 5)
  const context = relevantDocs.map((d, i) => `[${i + 1}] ${d.text}`).join('\n\n')

  // 2. Build messages with memory
  const messages = [
    {
      role: 'system',
      content: `Answer based on provided context and conversation history.`
    },
    ...(memory.summary
      ? [{ role: 'system', content: `Previous conversation summary: ${memory.summary}` }]
      : []),
    ...memory.messages.slice(-5), // Last 5 messages
    {
      role: 'user',
      content: `Context:\n${context}\n\nQuestion: ${question}`
    }
  ]

  // 3. Generate answer
  const response = await openai.chat.completions.create({
    model: 'gpt-4-turbo-preview',
    messages
  })

  const answer = response.choices[0].message.content!

  // 4. Update memory
  const updatedMemory = {
    messages: [
      ...memory.messages,
      { role: 'user', content: question },
      { role: 'assistant', content: answer }
    ].slice(-10), // Keep last 10 messages
    summary: memory.summary
  }

  return { answer, memory: updatedMemory }
}
```

---

## Error Handling

### Fallback Strategies

```typescript
async function robustRAG(question: string) {
  try {
    // Try semantic search
    const results = await queryDocuments(question, 5)

    if (results.length === 0) {
      // Fallback to keyword search
      return await keywordSearchRAG(question)
    }

    if (results[0].score < 0.7) {
      // Low confidence - try hybrid search
      return await hybridSearchRAG(question)
    }

    return await ragQuery(question, results)
  } catch (error) {
    console.error('RAG query failed:', error)
    return 'I apologize, but I encountered an error while searching for information.'
  }
}
```

### Answer Validation

```typescript
async function validatedRAG(question: string) {
  const { answer, sources } = await ragQueryWithCitations(question)

  // Validate answer is grounded in sources
  const validation = await openai.chat.completions.create({
    model: 'gpt-3.5-turbo',
    messages: [
      {
        role: 'system',
        content: 'Check if the answer is supported by the sources. Return "yes" or "no".'
      },
      {
        role: 'user',
        content: `Answer: ${answer}\n\nSources: ${JSON.stringify(sources)}`
      }
    ]
  })

  const isValid = validation.choices[0].message.content?.toLowerCase().includes('yes')

  return {
    answer,
    sources,
    validated: isValid,
    confidence: isValid ? 'high' : 'low'
  }
}
```

---

## Performance Optimization

### Caching

```typescript
import { LRUCache } from 'lru-cache'

const ragCache = new LRUCache<string, string>({
  max: 1000,
  ttl: 1000 * 60 * 60 // 1 hour
})

async function cachedRAG(question: string) {
  const cacheKey = question.toLowerCase().trim()

  if (ragCache.has(cacheKey)) {
    return ragCache.get(cacheKey)!
  }

  const answer = await ragQuery(question)
  ragCache.set(cacheKey, answer)

  return answer
}
```

### Parallel Retrieval

```typescript
async function parallelRAG(question: string) {
  // Fetch from multiple sources simultaneously
  const [vectorResults, keywordResults, graphResults] = await Promise.all([
    queryDocuments(question, 5),
    keywordSearch(question, 5),
    queryKnowledgeGraph(question, 5)
  ])

  const allResults = [...vectorResults, ...keywordResults, ...graphResults]
  const deduped = deduplicateResults(allResults)

  return ragQuery(question, deduped.slice(0, 10))
}
```

---

## Best Practices

### Context Window Management

- Keep total context under 75% of model limit
- Prioritize most relevant chunks
- Use compression for long documents
- Summarize when context exceeds limit

### Quality Metrics

- **Retrieval Precision**: % of retrieved docs that are relevant
- **Retrieval Recall**: % of relevant docs that are retrieved
- **Answer Accuracy**: Validate against ground truth
- **Citation Accuracy**: Check if citations match claims

### Prompt Engineering for RAG

```typescript
const RAG_SYSTEM_PROMPTS = {
  strict: `Answer ONLY using information from the provided context. If the answer is not in the context, say "I don't have enough information."`,

  conversational: `Use the provided context to answer the question. Be helpful and conversational, but always cite your sources.`,

  analytical: `Analyze the provided context and synthesize an answer. Explain your reasoning and cite specific evidence.`
}
```
