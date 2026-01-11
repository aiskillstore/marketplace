# ReasoningBank Adaptive Learning - Process Guide

## Phase 1: Initialize ReasoningBank

```typescript
const db = new AgentDB({
  name: 'reasoning-db',
  dimensions: 768,
  features: { reasoningBank: true }
});

const reasoningBank = new ReasoningBank({
  database: db,
  trajectoryWindow: 1000,
  verdictThreshold: 0.7
});
```

## Phase 2: Track Trajectories

```typescript
await reasoningBank.trackTrajectory({
  agent: 'agent-1',
  decision: 'action-A',
  reasoning: 'Because X and Y',
  context: { state: currentState },
  outcome: null // To be filled later
});
```

## Phase 3: Judge Verdicts

```typescript
const verdict = await reasoningBank.judgeVerdict({
  trajectory: trajectoryId,
  outcome: { success: true, reward: 10 },
  criteria: ['efficiency', 'correctness', 'novelty']
});

// Store verdict
await reasoningBank.storeVerdict(verdict);
```

## Phase 4: Distill Memory

```typescript
const patterns = await reasoningBank.distillPatterns({
  minSupport: 0.1,
  confidence: 0.8,
  method: 'pattern-mining'
});

// Consolidate successful strategies
await reasoningBank.consolidate(patterns);
```

## Phase 5: Apply Learning

```typescript
const decision = await reasoningBank.makeDecision({
  context: currentContext,
  useLearned: true,
  patterns: learnedPatterns
});

// Measure improvement
const improvement = await reasoningBank.measureImprovement({
  baseline: initialPerformance,
  current: currentPerformance
});
```

## Success Criteria

- Trajectories tracked > 95% accuracy
- Verdicts judged correctly > 90%
- Patterns learned and applied
- Decision quality improves

## Resources

- Full docs: SKILL.md
- ReasoningBank: https://reasoningbank.dev
