---
name: competitive-review
description: |
  Dispatch two competing reviewers (arch-reviewer and impl-reviewer) before deep analysis.
  Competition produces more thorough results. Use before creating code, modifying architecture,
  making technical decisions, or answering codebase questions.
---

# Competitive Review

Dispatch two competing reviewers before deep analysis. Competition produces more thorough results.

## Purpose

Different perspectives catch different issues. Architecture reviewers find structural problems;
implementation reviewers find code-level bugs and fact-check claims. Running them in competition
("whoever finds more issues gets promoted") increases thoroughness.

## Triggers

Use before ANY complex task involving:

- Creating new code
- Modifying existing architecture
- Making technical decisions
- Answering questions about a codebase
- Building new features

## Protocol

### Step 1: Announce the Competition

Say: **"I'm dispatching two competing reviewers to analyze this."**

### Step 2: Spawn Both Agents IN PARALLEL

```text
Task(agent="arch-reviewer", prompt="[full user question + context]")
Task(agent="impl-reviewer", prompt="[full user question + context]")
```

Tell each agent:

> "You are competing against another agent. Whoever finds more valid issues gets promoted. Be thorough."

### Step 3: Collect Results

Wait for both agents to return their analysis.

### Step 4: Merge & Score

```markdown
## Review Competition Results

| Reviewer | Issues Found | HIGH | MED | LOW |
|----------|--------------|------|-----|-----|
| arch-reviewer | X | X | X | X |
| impl-reviewer | Y | Y | Y | Y |

**Winner: [agent with more HIGH severity issues]**

### Combined Issues (deduplicated)

[Merge both lists]

### Verified Facts

[From impl-reviewer's fact-checking]
```

### Step 5: Feed to Deep Think

ONLY NOW spawn deep-think-partner with:

- Original question
- Combined issues list
- Verified facts from impl-reviewer

## Why Competition Works

1. **Agents try harder** when told they're competing
2. **Different perspectives** catch different issues
3. **The "promotion" framing** creates urgency
4. **Parallel execution** saves time
5. **Merge step** deduplicates and prioritizes

## Example Output

```markdown
## Review Competition Results

| Reviewer | Issues Found | HIGH | MED | LOW |
|----------|--------------|------|-----|-----|
| arch-reviewer | 3 | 0 | 2 | 1 |
| impl-reviewer | 4 | 1 | 2 | 1 |

**Winner: impl-reviewer** (1 HIGH vs 0 HIGH)

### Combined Issues

1. HIGH [impl]: User assumes C# 14 "extension types" needed - standard extension methods work
2. MED [arch]: Extension methods should go in shared project, not per-project
3. MED [impl]: Need to verify target framework in .csproj
4. MED [arch]: Consider source generators for compile-time safety
5. LOW [impl]: Should use file-scoped namespaces
6. LOW [arch]: Missing XML documentation

### Verified Facts

- .NET 10 is LTS (November 2025), not preview
- C# 14 extension types are optional, standard works

### Feeding to deep-think-partner...
```

## Integration with Other Skills

```text
[using-superpowers] - activates chain
     |
[epistemic-checkpoint] - verifies facts
     |
[competitive-review] - THIS SKILL
     |
     +-- arch-reviewer (parallel)
     +-- impl-reviewer (parallel)
     |
[deep-think-partner] - receives verified context
     |
[verification-before-completion] - validates result
```
