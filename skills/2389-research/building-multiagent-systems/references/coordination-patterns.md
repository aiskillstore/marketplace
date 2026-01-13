# Seven Core Coordination Patterns

## 1. Fan-Out/Fan-In (Parallel Independent Work)

Spawn agents for each item, execute in parallel with `Promise.all()`, then gather results. Use batching to prevent resource exhaustion.

**Critical gotchas:**
- Orphaned children if orchestrator aborts
- Resource exhaustion from spawning too many agents simultaneously
- Cost explosion (N agents × cost per agent)

```typescript
// Fan-out with batching
async function fanOutWithBatching(items: string[], batchSize: number = 10) {
  const results = [];
  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    const batchResults = await Promise.all(
      batch.map(item => spawnAgentForItem(item))
    );
    results.push(...batchResults);
  }
  return results;
}
```

## 2. Sequential Pipeline

Multi-stage transformations where each stage receives accumulated context from previous stages. Add checkpointing between stages to survive failures.

**Trade-offs:**
- Bottleneck: pipeline speed equals slowest stage
- Context growth can become problematic—prune between stages

```typescript
// Pipeline with checkpointing
async function pipeline(input: Data) {
  let context = { original: input };

  for (const stage of stages) {
    context = await stage.process(context);
    await saveCheckpoint(stage.name, context);
  }

  return context.result;
}
```

## 3. Recursive Delegation

Complex tasks break down hierarchically into subtasks. Delegate recursively or to specialists. Track via hierarchical thread IDs.

**Critical**: Must add max-depth limits to prevent infinite recursion.

```typescript
// Recursive with depth limit
async function delegate(task: Task, depth: number = 0): Promise<Result> {
  if (depth > MAX_DEPTH) {
    throw new Error('Max delegation depth exceeded');
  }

  if (isAtomic(task)) {
    return await executeDirectly(task);
  }

  const subtasks = await decompose(task);
  const results = await Promise.all(
    subtasks.map(st => delegate(st, depth + 1))
  );
  return combine(results);
}
```

## 4. Work-Stealing Queue

Large batches (1000+ tasks) use shared queue. Multiple workers pull tasks, execute independently. Implements load balancing naturally.

**Gotcha**: No built-in priority or retry mechanism—implement separately if needed.

```typescript
// Work-stealing queue
class WorkQueue {
  private queue: Task[] = [];
  private workers: Worker[] = [];

  async steal(): Promise<Task | null> {
    return this.queue.shift() || null;
  }

  async runWorkers(count: number) {
    this.workers = Array(count).fill(null).map(() =>
      this.workerLoop()
    );
    await Promise.all(this.workers);
  }

  private async workerLoop() {
    while (true) {
      const task = await this.steal();
      if (!task) break;
      await this.execute(task);
    }
  }
}
```

## 5. Map-Reduce

Map phase uses cheap models (Haiku, GPT-4o-mini) for simple per-item analysis. Reduce phase uses smart models (Sonnet, GPT-4) for synthesis.

**Cost example:**
```
100 files at $0.01 per map + $0.15 per reduce = $1.15
vs $15 using all smart models
```

```typescript
// Map-reduce with model selection
async function mapReduce(items: Item[]) {
  // Map: cheap models
  const mapResults = await Promise.all(
    items.map(item =>
      spawnAgent('mapper', { model: 'haiku' }).run(item)
    )
  );

  // Reduce: smart model
  const reducer = await spawnAgent('reducer', { model: 'sonnet' });
  return reducer.run({ results: mapResults });
}
```

## 6. Peer Collaboration (LLM Council)

Multiple models provide independent responses, review others anonymously, then synthesize results.

**Trade-offs:**
- Expensive (3N+1 API calls)
- Slow (15-30 seconds)
- But reduces bias significantly

**Not hierarchical agent relationships**—peers are equal.

```typescript
// LLM Council pattern
async function council(question: string, models: string[]) {
  // Round 1: Independent responses
  const responses = await Promise.all(
    models.map(m => getResponse(m, question))
  );

  // Round 2: Anonymous peer review
  const reviews = await Promise.all(
    models.map((m, i) =>
      reviewOthers(m, responses.filter((_, j) => j !== i))
    )
  );

  // Round 3: Synthesis
  return synthesize(responses, reviews);
}
```

## 7. MAKER (Million-Agent Voting for Zero Errors)

See `references/maker-pattern.md` for detailed implementation.

**Overview**: Combines extreme decomposition, microagents, and multi-agent voting to solve tasks requiring 100K+ steps with zero errors.

**When to Use:**
- Tasks requiring >100,000 LLM steps
- Zero error tolerance (medical, financial, legal domains)
- Subtasks are independently verifiable with deterministic checks
- Cost is secondary to correctness
