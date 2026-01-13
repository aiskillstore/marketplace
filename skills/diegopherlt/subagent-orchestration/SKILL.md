---
name: subagent-orchestration
description: |
  This skill should be used when coordinating multiple subagents, implementing orchestrator
  patterns, or managing parallel agent workflows.
  Trigger phrases: "orchestrate agents", "coordinate subagents", "parallel agents",
  "multi-agent workflow", "delegate to agents", "run agents in parallel", "launch multiple agents".
---

# Orchestrating Subagents

## Core Principles

- Always suggest subagent invocation when task matches their expertise
- User has final decision on invocation
- Prefer multiple parallel invocations for independent tasks with strict scopes
- ALWAYS define: files to modify, files NOT to touch, specific task boundaries

## When to Use Parallel Invocation

Invoke multiple subagents in a single message when:

- Tasks are completely independent
- Each task has strict, non-overlapping scope
- No task depends on another's results

**Examples:**

- ✓ "Explore authentication flow" + "Review recent auth changes" (parallel)
- ✗ "Explore auth flow then refactor based on findings" (sequential - second depends on first)

## Scope Definition Template

When proposing subagent invocation, use this structure:

```
Task: [Clear, single-sentence description]

Files to modify: [Explicit list with paths]

Files NOT to touch: [Explicit exclusions - be specific]

Constraints: 
- [Business rules to follow]
- [Patterns to maintain]
- [Technical requirements]

Reference docs: [@AGENTS.md, @docs/architecture.md, etc.]
```

## Decision Framework

Before suggesting subagents, verify:

1. **Is the scope clearly bounded?** Can you define exact files and boundaries?
2. **Is it independent?** Does it require results from another task first?
3. **Is it delegable?** Would a subagent have enough context?

If any answer is "no", handle the task directly or break it down further.

## Anti-patterns to Avoid

- Vague file specifications ("update related files")
- Missing exclusions (failing to specify what NOT to touch)
- Sequential tasks disguised as parallel (one depends on the other)
- Unbounded scopes ("refactor the codebase")
- Missing context references (no @file references for subagent to read)
