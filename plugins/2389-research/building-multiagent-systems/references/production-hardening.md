# Production Hardening for Multi-Agent Systems

## Cascading Stop Pattern

"Always stop children before stopping self." This prevents orphaned agents consuming resources.

```
1. Get all child agents
2. Stop all children in parallel
3. Stop self
4. Cancel ongoing work
5. Flush events
```

```typescript
async function cascadingStop(agent: Agent): Promise<void> {
  // 1. Get all child agents
  const children = await agent.getChildren();

  // 2. Stop all children in parallel
  await Promise.all(
    children.map(child => cascadingStop(child))
  );

  // 3. Stop self
  agent.setState('stopping');

  // 4. Cancel ongoing work
  agent.cancelPendingOperations();

  // 5. Flush events
  await agent.flushEventLog();

  agent.setState('stopped');
}
```

## Orphan Detection

Periodically scan for agents whose parents stopped. Clean them up automatically.

```typescript
// Heartbeat pattern
setInterval(async () => {
  const allAgents = await getRunningAgents();
  for (const agent of allAgents) {
    const parentAlive = await checkParentHeartbeat(agent.parentId);
    if (!parentAlive) {
      await agent.stop();
      await cleanupResources(agent.id);
    }
  }
}, 30000);  // Check every 30 seconds
```

## Cost Tracking Across Agent Hierarchy

Aggregate costs from all descendant agents using hierarchical IDs.

```typescript
// Hierarchical cost tracking
async function getTotalCost(agentId: string): Promise<number> {
  const directCost = await getAgentCost(agentId);
  const children = await getChildAgents(agentId);
  const childCosts = await Promise.all(
    children.map(child => getTotalCost(child.id))
  );
  return directCost + childCosts.reduce((sum, cost) => sum + cost, 0);
}

// Cost tracking in agent events
interface CostEvent {
  agentId: string;
  parentId: string;
  model: string;
  inputTokens: number;
  outputTokens: number;
  cost: number;
  timestamp: number;
}

// Aggregate costs by hierarchy
function aggregateCostsByHierarchy(events: CostEvent[]): Map<string, number> {
  const costs = new Map<string, number>();

  for (const event of events) {
    // Add to this agent
    costs.set(event.agentId, (costs.get(event.agentId) || 0) + event.cost);

    // Add to all ancestors (using hierarchical ID)
    let parentId = event.parentId;
    while (parentId) {
      costs.set(parentId, (costs.get(parentId) || 0) + event.cost);
      parentId = getParentFromId(parentId);
    }
  }

  return costs;
}
```

## Session vs Project Scope Workaround

Create project-level task store so agents can discover and claim work across sessions.

```typescript
// Persistent task store
class ProjectTaskStore {
  constructor(private dbPath: string) {}

  async addTask(task: Task): Promise<string> {
    const id = generateId();
    await this.db.insert({ ...task, id, status: 'pending', claimedBy: null });
    return id;
  }

  async claimTask(agentId: string): Promise<Task | null> {
    // Atomic claim to prevent race conditions
    const task = await this.db.findOneAndUpdate(
      { status: 'pending', claimedBy: null },
      { status: 'claimed', claimedBy: agentId, claimedAt: Date.now() }
    );
    return task;
  }

  async completeTask(taskId: string, result: any): Promise<void> {
    await this.db.update(
      { id: taskId },
      { status: 'completed', result, completedAt: Date.now() }
    );
  }

  async releaseStale(timeout: number = 300000): Promise<void> {
    // Release tasks claimed >5 min ago but not completed
    await this.db.updateMany(
      { status: 'claimed', claimedAt: { $lt: Date.now() - timeout } },
      { status: 'pending', claimedBy: null }
    );
  }
}
```

## Self-Modification Safety Protocol

When sub-agents can modify code, follow this safety protocol:

**Safety Protocol Checklist:**
1. **Assess blast radius** - What can break if this modification fails?
2. **Git branch isolation** - Each modification on separate branch
3. **Test-first** - Write tests before implementing changes
4. **Validation gates** - All tests must pass before commit
5. **Rollback capability** - Can undo if validation fails

```typescript
// Sub-agent fixing its own bug
async function fixOwnBug(bugReport: string) {
  // 1. Assess blast radius
  const affectedFiles = await identifyBugLocation(bugReport);
  const risk = assessRisk(affectedFiles);  // Low/Medium/High/Critical

  if (risk === 'Critical') {
    throw new Error('Cannot self-modify critical systems');
  }

  // 2. Create isolation
  await gitBranch(`fix-bug-${Date.now()}`);

  // 3. Write test for bug FIRST
  await writeTest({
    description: 'Test that reproduces the bug',
    shouldFail: true  // Test should fail initially
  });

  // 4. Implement fix
  await applyFix(affectedFiles);

  // 5. Validate
  const testsPass = await runAllTests();
  const typeCheckPass = await runTypeCheck();
  const lintPass = await runLint();

  if (testsPass && typeCheckPass && lintPass) {
    // 6. Commit
    await gitCommit('fix: resolve bug in tool execution');
  } else {
    // 6. Rollback
    await gitReset('--hard', 'main');
    throw new Error('Fix validation failed - rolled back');
  }
}
```

**When sub-agents should NOT self-modify:**
- During active operation (modifying code while running it)
- Without parent orchestrator approval
- Core reasoning logic (Layer 1) changes
- When blast radius is Critical

**When self-modification is appropriate:**
- Fixing bugs in tool implementations (Layer 4)
- Adding logging/debugging
- Optimizing performance with tests
- Adding new tools that follow existing patterns

## Checkpointing Strategy

Save after significant events to enable recovery.

```typescript
interface CheckpointTrigger {
  toolsExecuted: number;     // e.g., after 10+ tools
  costThreshold: number;     // e.g., after $1.00 spent
  timeElapsed: number;       // e.g., after 5 minutes
}

async function maybeCheckpoint(agent: Agent, triggers: CheckpointTrigger) {
  const metrics = agent.getMetrics();

  if (
    metrics.toolsExecuted >= triggers.toolsExecuted ||
    metrics.totalCost >= triggers.costThreshold ||
    metrics.elapsedMs >= triggers.timeElapsed
  ) {
    await saveCheckpoint({
      agentId: agent.id,
      state: agent.getState(),
      messages: agent.getMessages(),
      context: agent.getContext(),
      timestamp: Date.now()
    });
    agent.resetMetrics();
  }
}
```

## Coordination Primitives Workaround

Implement locks, semaphores, and barriers in-memory if unavailable in your framework.

```typescript
// Barrier: Wait for N agents to reach a point
class Barrier {
  private count = 0;
  private waiters: (() => void)[] = [];

  constructor(private threshold: number) {}

  async wait(): Promise<void> {
    this.count++;
    if (this.count >= this.threshold) {
      // Release all waiters
      this.waiters.forEach(resolve => resolve());
      this.waiters = [];
      this.count = 0;
    } else {
      // Wait for others
      await new Promise<void>(resolve => this.waiters.push(resolve));
    }
  }
}

// Semaphore: Limit concurrent access
class Semaphore {
  private permits: number;
  private waiters: (() => void)[] = [];

  constructor(permits: number) {
    this.permits = permits;
  }

  async acquire(): Promise<void> {
    if (this.permits > 0) {
      this.permits--;
    } else {
      await new Promise<void>(resolve => this.waiters.push(resolve));
    }
  }

  release(): void {
    const waiter = this.waiters.shift();
    if (waiter) {
      waiter();
    } else {
      this.permits++;
    }
  }
}
```
