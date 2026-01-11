---
name: ultrathink-trigger
description: Auto-escalate reasoning depth for complex problems. Use proactively when encountering architecture, debugging, or unfamiliar code.
---

# Ultrathink Trigger

Automatically invoke maximum reasoning depth for complex problems.

## Complexity Indicators

| Signal                         | Weight | Example                            |
| ------------------------------ | ------ | ---------------------------------- |
| Files affected > 5             | +2     | Refactoring across modules         |
| Unfamiliar language/framework  | +3     | First time with codebase           |
| Architecture decision          | +4     | Choosing patterns                  |
| 2+ failed fix attempts         | +3     | Root cause unclear                 |
| Multi-domain interaction       | +2     | Frontend + Backend + DB            |
| Security implications          | +3     | Auth, permissions, secrets         |
| Performance-critical code      | +2     | Hot paths, algorithms              |
| Breaking change potential      | +3     | API changes, schema migrations     |

## Threshold

**If total weight >= 5**: Trigger ultrathink mode

## Invocation

Prefix complex analysis with one of:

- "Think harder about this:"
- "ultrathink:"
- "Take your time to deeply analyze:"

These phrases trigger Claude's extended thinking mode for more thorough analysis.

## Integration Points

### With /fix command

After 2 failed attempts, automatically invoke:

```
ultrathink: What are all the possible root causes?
What assumptions am I making? What haven't I checked yet?
```

### With /brainstorm command

Auto-triggers when topic complexity >= 5 (or `--deep` flag). Applied to EVALUATE and SYNTHESIZE phases:

```
ultrathink: Deeply analyze these options considering trade-offs,
edge cases, maintainability, and long-term implications.
```

Flags:

- `--deep` - Force ultrathink regardless of complexity
- `--quick` - Suppress auto-detect, stay fast

### With orchestrator INNOVATE phase

For architecture decisions:

```
ultrathink: Evaluate these approaches considering
maintainability, performance, security, and complexity.
```

### With sequential-thinking

For multi-step complex analysis:

```javascript
mcp__sequential_thinking__sequentialthinking({
  thought: "ultrathink: [complex problem]",
  thoughtNumber: 1,
  totalThoughts: 10, // More steps for deep analysis
  nextThoughtNeeded: true
})
```

## When to Use Proactively

1. **Architecture Decisions**: Before proposing patterns or structure
2. **Debugging Deadlock**: After 2+ failed fix attempts
3. **Security Analysis**: Any auth, permission, or secret handling
4. **Performance Optimization**: Before optimizing hot paths
5. **Breaking Changes**: Before proposing API/schema changes
6. **Unfamiliar Code**: First encounter with a new codebase area

## Example Workflow

```
1. Encounter complex problem
2. Calculate complexity weight:
   - Multi-file change: +2
   - Architecture decision: +4
   - Total: 6 (>= 5, triggers ultrathink)
3. Invoke: "ultrathink: Design the data flow for..."
4. Extended analysis produces thorough solution
5. Proceed with implementation
```

## Anti-Patterns

- Using ultrathink for simple, well-understood tasks
- Skipping ultrathink for complex problems to "save time"
- Not recalculating complexity when scope changes
