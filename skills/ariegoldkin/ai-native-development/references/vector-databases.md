# Vector Databases Reference

## Overview

Vector databases store and retrieve embeddings efficiently for semantic search. This reference covers setup, operations, and best practices for popular vector databases.

---

## Embeddings Creation

### OpenAI Embeddings

```typescript
import OpenAI from 'openai'

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY })

async function createEmbedding(text: string): Promise<number[]> {
  const response = await openai.embeddings.create({
    model: 'text-embedding-3-small', // Cheaper, faster (1536 dimensions)
    // model: 'text-embedding-3-large', // Better quality (3072 dimensions)
    input: text,
  })

  return response.data[0].embedding
}

// Batch processing for efficiency
async function createEmbeddings(texts: string[]): Promise<number[][]> {
  const response = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: texts, // Up to 2048 texts per request
  })

  return response.data.map(d => d.embedding)
}
```

### Similarity Search

```typescript
// Cosine similarity calculation
function cosineSimilarity(a: number[], b: number[]): number {
  const dotProduct = a.reduce((sum, val, i) => sum + val * b[i], 0)
  const magnitudeA = Math.sqrt(a.reduce((sum, val) => sum + val * val, 0))
  const magnitudeB = Math.sqrt(b.reduce((sum, val) => sum + val * val, 0))
  return dotProduct / (magnitudeA * magnitudeB)
}

// Find most similar documents
async function findSimilar(query: string, documents: Document[], topK = 5) {
  const queryEmbedding = await createEmbedding(query)

  const scores = documents.map(doc => ({
    document: doc,
    score: cosineSimilarity(queryEmbedding, doc.embedding)
  }))

  return scores
    .sort((a, b) => b.score - a.score)
    .slice(0, topK)
    .map(({ document, score }) => ({ ...document, similarity: score }))
}
```

---

## Pinecone (Serverless)

### Setup

```typescript
import { Pinecone } from '@pinecone-database/pinecone'

const pinecone = new Pinecone({
  apiKey: process.env.PINECONE_API_KEY!
})

// Create index (one-time setup)
async function createIndex() {
  await pinecone.createIndex({
    name: 'documents',
    dimension: 1536, // Match embedding dimension
    metric: 'cosine',
    spec: {
      serverless: {
        cloud: 'aws',
        region: 'us-east-1'
      }
    }
  })
}

const index = pinecone.index('documents')
```

### Operations

```typescript
// Upsert vectors
async function indexDocuments(documents: { id: string; text: string; metadata?: any }[]) {
  const embeddings = await createEmbeddings(documents.map(d => d.text))

  await index.upsert(
    documents.map((doc, i) => ({
      id: doc.id,
      values: embeddings[i],
      metadata: {
        text: doc.text,
        ...doc.metadata
      }
    }))
  )
}

// Query vectors
async function queryDocuments(query: string, topK = 5) {
  const queryEmbedding = await createEmbedding(query)

  const results = await index.query({
    vector: queryEmbedding,
    topK,
    includeMetadata: true
  })

  return results.matches.map(match => ({
    id: match.id,
    score: match.score,
    ...match.metadata
  }))
}

// Update metadata
async function updateMetadata(id: string, metadata: Record<string, any>) {
  await index.update({
    id,
    metadata
  })
}

// Delete vectors
async function deleteDocuments(ids: string[]) {
  await index.deleteMany(ids)
}
```

### Filtering

```typescript
// Query with metadata filters
async function queryWithFilter(query: string, filter: Record<string, any>) {
  const queryEmbedding = await createEmbedding(query)

  const results = await index.query({
    vector: queryEmbedding,
    topK: 10,
    filter: {
      category: { $eq: 'documentation' },
      createdAt: { $gte: '2024-01-01' }
    },
    includeMetadata: true
  })

  return results.matches
}
```

---

## Chroma (Open Source)

### Setup

```typescript
import { ChromaClient } from 'chromadb'

const client = new ChromaClient({ path: 'http://localhost:8000' })

// Create collection
const collection = await client.createCollection({
  name: 'documents',
  metadata: { 'hnsw:space': 'cosine' }
})
```

### Operations

```typescript
// Add documents
await collection.add({
  ids: documents.map(d => d.id),
  embeddings: await createEmbeddings(documents.map(d => d.text)),
  metadatas: documents.map(d => ({ text: d.text, ...d.metadata })),
  documents: documents.map(d => d.text) // Optional: store original text
})

// Query
const results = await collection.query({
  queryEmbeddings: [await createEmbedding(query)],
  nResults: 5,
  where: { category: 'documentation' } // Optional filter
})

// Update
await collection.update({
  ids: ['doc-1'],
  metadatas: [{ updated: true }]
})

// Delete
await collection.delete({
  ids: ['doc-1', 'doc-2']
})
```

---

## Weaviate (Open Source)

### Setup

```typescript
import weaviate from 'weaviate-ts-client'

const client = weaviate.client({
  scheme: 'http',
  host: 'localhost:8080',
})

// Create schema
await client.schema
  .classCreator()
  .withClass({
    class: 'Document',
    vectorizer: 'none', // Using custom embeddings
    properties: [
      { name: 'text', dataType: ['text'] },
      { name: 'category', dataType: ['string'] },
      { name: 'createdAt', dataType: ['date'] }
    ]
  })
  .do()
```

### Operations

```typescript
// Add documents
async function addDocuments(documents: any[]) {
  const embeddings = await createEmbeddings(documents.map(d => d.text))

  let batcher = client.batch.objectsBatcher()

  documents.forEach((doc, i) => {
    batcher = batcher.withObject({
      class: 'Document',
      properties: doc,
      vector: embeddings[i]
    })
  })

  await batcher.do()
}

// Query
async function searchDocuments(query: string, limit = 5) {
  const queryEmbedding = await createEmbedding(query)

  const result = await client.graphql
    .get()
    .withClassName('Document')
    .withFields('text category _additional { distance }')
    .withNearVector({ vector: queryEmbedding })
    .withLimit(limit)
    .do()

  return result.data.Get.Document
}
```

---

## Qdrant (Rust-based, High Performance)

### Setup

```typescript
import { QdrantClient } from '@qdrant/js-client-rest'

const client = new QdrantClient({ url: 'http://localhost:6333' })

// Create collection
await client.createCollection('documents', {
  vectors: {
    size: 1536,
    distance: 'Cosine'
  }
})
```

### Operations

```typescript
// Upsert points
await client.upsert('documents', {
  points: documents.map((doc, i) => ({
    id: i,
    vector: embeddings[i],
    payload: doc
  }))
})

// Search
const results = await client.search('documents', {
  vector: queryEmbedding,
  limit: 5,
  filter: {
    must: [
      { key: 'category', match: { value: 'documentation' } }
    ]
  }
})
```

---

## Best Practices

### Chunking Strategy

```typescript
function chunkDocument(text: string, chunkSize = 1000, overlap = 200): string[] {
  const chunks: string[] = []
  let start = 0

  while (start < text.length) {
    const end = Math.min(start + chunkSize, text.length)
    chunks.push(text.slice(start, end))
    start = end - overlap
  }

  return chunks
}

// Enhanced chunking with metadata
function chunkWithMetadata(document: Document) {
  const chunks = chunkDocument(document.text, 800, 150)

  return chunks.map((chunk, i) => ({
    id: `${document.id}-chunk-${i}`,
    text: chunk,
    metadata: {
      documentId: document.id,
      title: document.title,
      chunkIndex: i,
      totalChunks: chunks.length,
      source: document.source
    }
  }))
}
```

### Embedding Optimization

```typescript
// Cache embeddings
const embeddingCache = new Map<string, number[]>()

async function getCachedEmbedding(text: string): Promise<number[]> {
  const key = text.trim().toLowerCase()

  if (embeddingCache.has(key)) {
    return embeddingCache.get(key)!
  }

  const embedding = await createEmbedding(text)
  embeddingCache.set(key, embedding)
  return embedding
}

// Batch processing
async function batchIndex(documents: Document[], batchSize = 100) {
  for (let i = 0; i < documents.length; i += batchSize) {
    const batch = documents.slice(i, i + batchSize)
    const embeddings = await createEmbeddings(batch.map(d => d.text))

    await index.upsert(
      batch.map((doc, j) => ({
        id: doc.id,
        values: embeddings[j],
        metadata: doc.metadata
      }))
    )

    console.log(`Indexed batch ${i / batchSize + 1}`)
  }
}
```

### Re-ranking

```typescript
// Cross-encoder re-ranking for better results
import { pipeline } from '@xenova/transformers'

async function rerank(query: string, results: any[]) {
  const reranker = await pipeline('text-classification', 'cross-encoder/ms-marco-MiniLM-L-6-v2')

  const pairs = results.map(result => [query, result.text])
  const scores = await reranker(pairs)

  return results
    .map((result, i) => ({
      ...result,
      rerankScore: scores[i].score
    }))
    .sort((a, b) => b.rerankScore - a.rerankScore)
}
```

---

## Cost Comparison

| Provider | Free Tier | Pricing | Best For |
|----------|-----------|---------|----------|
| **Pinecone** | 1 index, 100K vectors | $0.096/hour pod | Production, serverless |
| **Chroma** | Unlimited (self-hosted) | Free (OSS) | Development, on-prem |
| **Weaviate** | Unlimited (self-hosted) | Cloud from $25/mo | Flexible schema |
| **Qdrant** | Unlimited (self-hosted) | Cloud from $25/mo | High performance |

---

## Troubleshooting

**High latency on queries**
- Reduce topK value
- Use metadata filters to narrow search space
- Consider using approximate nearest neighbor (ANN) indexes

**Poor retrieval quality**
- Try hybrid search (semantic + keyword)
- Experiment with different embedding models
- Adjust chunk size and overlap
- Use re-ranking

**Memory issues**
- Batch index operations
- Clear embedding cache periodically
- Use streaming for large datasets
