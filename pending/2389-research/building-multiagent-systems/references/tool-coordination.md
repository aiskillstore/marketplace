# Tool Coordination in Multi-Agent Systems

## Permission Inheritance

Children inherit parent tools and permission scopes but cannot escalate privileges.

```typescript
// Parent agent with full toolset
const parent = new Agent({
  tools: [editTool, readTool, writeTool, bashTool, searchTool],
  permissions: ['file:read', 'file:write', 'shell:execute']
});

// Spawn sub-agent with SUBSET of tools
const codeAnalyzer = await parent.spawnSubAgent({
  name: 'code-analyzer',
  model: 'haiku',  // Cheaper model for simple tasks
  tools: [readTool, searchTool],  // Read-only tools
  permissions: ['file:read'],  // Cannot write or execute
  timeout: 120000  // 2 minute timeout
});

// Sub-agent CANNOT escalate privileges
// Attempting to use writeTool → Error: Tool not available
```

**Permission Inheritance Rules:**
1. Children inherit SUBSET of parent permissions (cannot escalate)
2. Children can only use tools parent has access to
3. Children cannot modify their own permission scope
4. Parent can revoke child permissions at any time

## Shared Resource Locking

Implement acquire/release patterns to prevent race conditions when multiple agents access the same resource.

```typescript
class ResourceLock {
  private locks = new Map<string, string>();  // resource → agentId

  async acquire(resource: string, agentId: string, timeout: number = 5000): Promise<boolean> {
    const start = Date.now();
    while (this.locks.has(resource)) {
      if (Date.now() - start > timeout) return false;
      await sleep(100);
    }
    this.locks.set(resource, agentId);
    return true;
  }

  release(resource: string, agentId: string): void {
    if (this.locks.get(resource) === agentId) {
      this.locks.delete(resource);
    }
  }
}
```

## Rate Limiting

Implement token bucket algorithm shared across all agents to coordinate API call throttling.

```typescript
class TokenBucket {
  private tokens: number;
  private lastRefill: number;

  constructor(
    private capacity: number,
    private refillRate: number  // tokens per second
  ) {
    this.tokens = capacity;
    this.lastRefill = Date.now();
  }

  async acquire(count: number = 1): Promise<boolean> {
    this.refill();
    if (this.tokens >= count) {
      this.tokens -= count;
      return true;
    }
    return false;
  }

  private refill(): void {
    const now = Date.now();
    const elapsed = (now - this.lastRefill) / 1000;
    this.tokens = Math.min(this.capacity, this.tokens + elapsed * this.refillRate);
    this.lastRefill = now;
  }
}

// Shared rate limiter for all agents
const apiRateLimiter = new TokenBucket(100, 10);  // 100 capacity, 10/sec refill
```

## Result Caching

Cache read-only, idempotent, expensive operations. Invalidate carefully for data freshness.

```typescript
class ResultCache {
  private cache = new Map<string, { result: any; timestamp: number }>();

  async getOrCompute<T>(
    key: string,
    compute: () => Promise<T>,
    ttlMs: number = 60000
  ): Promise<T> {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < ttlMs) {
      return cached.result as T;
    }

    const result = await compute();
    this.cache.set(key, { result, timestamp: Date.now() });
    return result;
  }

  invalidate(pattern: string): void {
    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key);
      }
    }
  }
}
```

## Sub-Agent as Tool Pattern

Treat specialized agents as tools that parent can call.

```typescript
// Define sub-agent as a tool
const codeReviewerTool = {
  name: "code_reviewer",
  description: "Reviews code for security, performance, and style issues",
  parameters: {
    type: "object",
    properties: {
      filePath: { type: "string" },
      focusAreas: { type: "array", items: { type: "string" } }
    }
  },
  execute: async ({ filePath, focusAreas }) => {
    // Spawn specialized agent
    const reviewer = await spawnAgent('code-reviewer', {
      model: 'sonnet',
      tools: [readTool, searchTool]
    });

    // Agent performs review
    const result = await reviewer.run(
      `Review ${filePath} focusing on: ${focusAreas.join(', ')}`
    );

    // Clean up
    await reviewer.stop();

    return { review: result };
  }
};

// Parent can now use code reviewer like any other tool
const review = await parent.executeTool('code_reviewer', {
  filePath: 'src/auth.ts',
  focusAreas: ['security', 'input-validation']
});
```

**Benefits:**
- Composable abstractions (agents using agents)
- Consistent tool interface across system
- Natural lifecycle management (spawn → execute → cleanup)
