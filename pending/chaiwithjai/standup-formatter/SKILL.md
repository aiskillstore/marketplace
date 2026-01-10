---
name: standup-formatter
description: Use when generating standup reports, daily updates, or team status summaries. Formats work activity into concise standup format.
---

<essential_principles>
## Standup Philosophy

### Purpose
Standups exist to:
1. Share blockers that need help
2. Coordinate on dependencies
3. Keep work visible

Standups do NOT exist to:
- Report hours worked
- Justify existence
- Detail every task

### The Ideal Standup

**Done**: What you completed (outcomes, not activities)
**Today**: What you're working on (1-2 focus items)
**Blockers**: What's preventing progress (specific, actionable)

### Time Budgets

- Speaking: 60 seconds max per person
- Written: 3-5 bullet points total
- Detail level: Enough to understand, not to replicate

## Format Guidelines

### Good Examples
```
Done: Merged PR for user auth (#234)
Today: Starting payment integration
Blockers: Waiting on API spec from backend team
```

### Bad Examples
```
Done: Worked on stuff, had meetings, reviewed some code,
      wrote tests, fixed bugs, updated docs, etc.
Today: More of the same
Blockers: Nothing
```

### Async vs Sync

**Async (written):**
- More detail acceptable
- Include links to PRs/tickets
- Post by 9am team time

**Sync (spoken):**
- Extremely concise
- No reading from notes
- Save details for follow-ups
</essential_principles>

<intake>
What standup format do you need?

1. **Individual** - Your personal standup
2. **Team** - Aggregate team status
3. **Project** - Status for specific project

**For what timeframe?**
- Yesterday/today (daily)
- This week (weekly)
- Custom dates

**Source data?**
- Git activity
- Calendar events
- Manual input
</intake>

<templates>
## Individual Standup

```markdown
## Standup - [Date]

### Done
- [Completed item 1]
- [Completed item 2]

### Today
- [Focus item 1]
- [Focus item 2]

### Blockers
- [Blocker with specific need] / None
```

## Team Standup

```markdown
## Team Standup - [Date]

### [Person 1]
- Done: [summary]
- Today: [focus]
- Blockers: [if any]

### [Person 2]
...
```
</templates>
