# Two-Stage Review Pattern

Separate code review into two distinct passes to catch different failure modes.

## The Pattern

```
Implementation Complete
        ↓
┌─────────────────────────────┐
│  Stage 1: Spec Compliance   │
│  Does it match requirements?│
│  Nothing extra? Nothing     │
│  missing?                   │
└─────────────────────────────┘
        ↓ must pass first
┌─────────────────────────────┐
│  Stage 2: Code Quality      │
│  Is it well-built?          │
│  Clean, tested, maintainable│
└─────────────────────────────┘
```

## Why Two Stages?

| Stage | Catches | Missed by Other Stage |
|-------|---------|----------------------|
| Spec Compliance | Over-building (added unrequested features) | Quality review says "nice feature!" |
| Spec Compliance | Under-building (missing requirements) | Quality review focuses on what exists |
| Code Quality | Poor implementation of correct spec | Spec review says "requirements met" |
| Code Quality | Technical debt, test gaps | Spec review doesn't check how |

## Stage 1: Spec Compliance

Questions to ask:
- Does it implement ALL requirements from spec?
- Does it implement ONLY requirements from spec?
- Any unrequested features added?
- Any requirements interpreted loosely?

**Pass criteria:** Spec requirements = implemented behavior (exact match)

## Stage 2: Code Quality

Questions to ask:
- Is the implementation clean and readable?
- Are there adequate tests?
- Any magic numbers, poor naming, duplication?
- Would you want to maintain this?

**Pass criteria:** Implementation is well-crafted

## Key Rule

**Never start code quality review before spec compliance passes.**

Reviewing quality of wrong implementation wastes time. Fix what's built first, then review how it's built.

## When to Use

- Subagent-based development (reviewer per stage)
- PR reviews (two passes through same PR)
- Self-review (check spec first, then quality)
