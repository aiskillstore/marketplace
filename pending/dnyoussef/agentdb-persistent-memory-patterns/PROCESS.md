# AgentDB Persistent Memory - Process Guide

Complete walkthrough for implementing persistent memory patterns with AgentDB.

## Phase 1: Design Memory Architecture

```typescript
const memorySchema = {
  episodic: {
    dimensions: 768,
    ttl: 86400, // 24 hours
    consolidation: 'time-based'
  },
  semantic: {
    dimensions: 768,
    ttl: null, // Permanent
    consolidation: 'importance-based'
  },
  procedural: {
    dimensions: 512,
    ttl: null,
    consolidation: 'frequency-based'
  }
};
```

## Phase 2: Implement Storage Layer

```typescript
const memoryDB = new AgentDB({
  name: 'agent-memory',
  dimensions: 768,
  memory: { sessionTTL: 3600 }
});

const memoryManager = new MemoryManager({
  database: memoryDB,
  layers: ['episodic', 'semantic', 'procedural']
});

await memoryManager.initialize();
```

## Phase 3: Test Memory Operations

```typescript
// Store
await memoryManager.store({
  type: 'episodic',
  content: 'User likes dark theme',
  embedding: generateEmbedding('User likes dark theme')
});

// Retrieve
const results = await memoryManager.retrieve({
  query: 'user preferences',
  limit: 10
});
```

## Phase 4: Optimize Performance

```typescript
// Caching
memoryManager.setCache({
  maxSize: 1000,
  ttl: 600
});

// Indexing
await memoryManager.createIndex('hnsw');
```

## Phase 5: Document Patterns

Create usage documentation, examples, and API reference.

## Success Criteria

- Memory persists across restarts
- Retrieval < 50ms
- Patterns learned correctly
- Context maintained

## Resources

- Full docs: SKILL.md
- AgentDB Memory: https://agentdb.dev/docs/memory
