# Manage Project Learnings

Record important discoveries and learnings for this project that should persist across sessions.

## Check existing learnings

Project learnings are stored in `.claude/learnings.md` (create if it doesn't exist).

Global learnings (across all projects) are stored in `~/.claude/learnings.md`.

## Add a new learning

When you discover something important about this project (an optimization approach, a tricky pattern, a gotcha), record it in `.claude/learnings.md` with this format:

```markdown
## [Topic]: Brief title

**Context**: When/where this applies
**Discovery**: What was learned
**Solution/Pattern**: How to handle it
```

## Example learning entry

```markdown
## Database: Connection pooling optimization

**Context**: High-traffic API endpoints with PostgreSQL
**Discovery**: Default pool size of 5 was causing connection exhaustion under load
**Solution/Pattern**: Increase pool size to 20, add connection timeout of 30s, implement retry logic with exponential backoff
```

Learnings help Claude remember important project-specific knowledge across sessions.
