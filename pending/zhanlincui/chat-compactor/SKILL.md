---
name: chat-compactor
description: Generate structured session summaries optimized for future AI agent consumption. Use when (1) ending a coding/debugging session, (2) user says "compact", "summarize session", "save context", or "wrap up", (3) context window is getting long and continuity matters, (4) before switching tasks or taking a break. Produces machine-readable handoff documents that let the next session start fluently without re-explaining.
---

# Chat Compactor

Generate structured summaries optimized for AI agent continuity across sessions.

## Why This Exists

Human-written summaries and ad-hoc AI summaries lose critical context:
- **Decision rationale** gets lost (why X, not Y)
- **Dead ends** get forgotten (agent re-tries failed approaches)
- **Implicit knowledge** isn't captured (file locations, naming conventions, gotchas)
- **State** is unclear (what's done, what's pending, what's blocked)

This skill produces **agent-optimized handoff documents** that prime the next session.

## Output Format

Generate a markdown file with this structure:

```markdown
# Session: [Brief Title]
Date: [YYYY-MM-DD]
Duration: ~[X] messages

## Context Snapshot
[1-2 sentences: What project/task, what state it's in right now]

## What Was Accomplished
- [Concrete outcome 1]
- [Concrete outcome 2]

## Key Decisions & Rationale
| Decision | Why | Alternatives Rejected |
|----------|-----|----------------------|
| [Choice] | [Reason] | [What didn't work and why] |

## Current State
- **Working**: [files/features that are functional]
- **Broken/Blocked**: [what's not working and why]
- **Modified files**: [list with brief note on changes]

## Dead Ends (Don't Retry)
- ❌ [Approach that failed] — [why it failed]

## Next Steps (Prioritized)
1. [ ] [Most important next action]
2. [ ] [Second priority]

## Environment & Gotchas
- [Any setup notes, versions, quirks discovered]

## Key Code/Commands Reference
[Only if there are non-obvious commands or snippets the next session needs]
```

## Workflow

1. **Scan conversation** for: decisions, outcomes, failures, file changes, blockers
2. **Identify the "handoff moment"** — what would a fresh agent need to continue?
3. **Generate structured summary** using format above
4. **Save to file**: `session-[topic]-[date].md` in project root or `/home/claude/sessions/`

## Compaction Triggers

Invoke this skill when:
- User says: "compact", "wrap up", "save session", "summarize for next time"
- Context window exceeds ~50% capacity and task is ongoing
- Before major context switches
- End of debugging/implementation session

## Quality Criteria

Good compactions are:
- **Scannable**: Next agent gets orientation in <30 seconds
- **Actionable**: Clear next steps, not vague summaries
- **Defensive**: Dead ends documented to prevent re-exploration
- **Minimal**: No fluff, every line earns its tokens

## Anti-Patterns

Avoid:
- Narrative prose ("First we tried X, then Y, then Z...")
- Redundant context (don't repeat what's in code comments)
- Vague summaries ("Made good progress on the feature")
- Missing failure documentation (most valuable part!)

## Example Trigger & Response

**User**: "Let's wrap up, compact this session"

**Agent**:
1. Reviews conversation for key decisions, outcomes, failures
2. Generates structured markdown per format above
3. Saves to `session-[topic]-[date].md`
4. Confirms: "Session compacted to `session-auth-refactor-2025-01-06.md` — ready for next time."
