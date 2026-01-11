---
name: reflect-on-work
description: Pattern for producing quality reflections after completing work. Required for all agent outputs.
allowed-tools: Read
---

# Reflect on Work Skill

Pattern for producing quality reflections.

## When to Load This Skill

- You are completing any task
- You need to produce the mandatory reflection fields
- You want to contribute to system evolution

## Required Output Fields

EVERY agent output MUST include these fields in compact JSON:

```json
{"knowledge_updates":[{"category":"codebase","content":"What you learned","confidence":"certain"}],"reflection":{"what_worked":["string"],"what_failed":["string"],"patterns_noticed":["string"]}}
```

## Knowledge Updates

### Categories

- **codebase**: Discovered structure, components, data flow
- **convention**: Coding style, patterns, naming
- **decision**: Design choice and rationale
- **gotcha**: Pitfall, workaround, non-obvious behavior

### Confidence Levels

- **certain**: Verified, tested, documented
- **likely**: Strong evidence but not verified
- **uncertain**: Observed but needs confirmation

### Examples

```json
{"knowledge_updates":[{"category":"convention","content":"Project uses barrel exports in each directory","confidence":"certain"},{"category":"gotcha","content":"Must call init() before using AuthService","confidence":"certain"},{"category":"codebase","content":"API routes follow /api/v1/{resource} pattern","confidence":"likely"}]}
```

## Reflection Fields

### what_worked
- Strategies that succeeded
- Tools that helped
- Approaches worth repeating

### what_failed
- Strategies that didn't work
- Time wasted on wrong approaches
- Issues encountered

### patterns_noticed
- Repeated sequences (skill candidates)
- Common patterns in codebase
- Workflow improvements

### Example

```json
{"reflection":{"what_worked":["Parallel explorers found context quickly","Starting with types helped structure code"],"what_failed":["Initial approach missed edge case","Spent time on wrong file before exploring"],"patterns_noticed":["Error handling always uses Result type","Tests colocated with source files"]}}
```

## Complete Output Example

Minimal valid output with reflection:

```json
{"task_id":"task-001","status":"pre_complete","files_modified":[],"knowledge_updates":[],"reflection":{"what_worked":[],"what_failed":[],"patterns_noticed":[]}}
```

Full output with content:

```json
{"task_id":"task-001","status":"pre_complete","files_modified":[{"path":"src/auth.ts","change_type":"modified","summary":"Added login function"}],"knowledge_updates":[{"category":"convention","content":"Auth uses JWT tokens","confidence":"certain"}],"reflection":{"what_worked":["Found existing patterns quickly"],"what_failed":["Initial test approach was wrong"],"patterns_noticed":["All services use dependency injection"]}}
```

## Principles

- **Be honest** - Report failures, they're valuable
- **Be specific** - Actionable insights, not vague
- **Be brief** - Concise, not exhaustive
- **Use compact JSON** - Single line, no formatting
