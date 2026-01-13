---
name: chronicle-context-retriever
description: Search and retrieve context from past development sessions using Chronicle data. Works with MCP (fast, structured) or CLI commands (portable). Use when user asks about previous work, wants to recall past decisions, needs to understand codebase history, or wants to avoid repeating past approaches.
---

# Chronicle Context Retriever

This skill helps you search and retrieve context from past development sessions using Chronicle's database. Works with both MCP server (fast, structured JSON) or CLI commands (portable, everywhere).

## Auto-Activation

> **This skill auto-activates!** (Milestone #13)
>
> Prompts like "how did I implement auth?" or "what did I do yesterday?" automatically trigger this skill. No manual loading needed!
>
> **Trigger patterns:** how did I, what did I do, find sessions about, search past work
> **See:** `docs/HOOKS.md` for full details

## When to Use This Skill

Use this skill when:
- User asks "what did I do yesterday/last week?"
- Need to recall how a feature was implemented
- Want to understand why a decision was made
- Looking for similar past work or patterns
- Avoiding repeating past mistakes or approaches
- Need context before starting related work

## How It Works

**Option 1: With MCP (Preferred)**
1. **Parse User Query** - Understand what context is needed
2. **Search Chronicle** - `mcp__chronicle__search_sessions()` returns structured JSON (fast!)
3. **Get Details** - `mcp__chronicle__get_session_summary()` for full summaries
4. **Extract Information** - Parse JSON for decisions, blockers, solutions
5. **Present Context** - Summarize findings with session IDs

**Option 2: With CLI (Portable)**
1. **Parse User Query** - Understand what context is needed
2. **Search Chronicle** - `chronicle search "keywords"` returns formatted output
3. **Get Details** - `chronicle session <id>` for full summaries
4. **Extract Information** - Parse CLI output for key details
5. **Present Context** - Summarize findings with session IDs

**Decision Tree:**
```
Search past work
├─ MCP available? → Use mcp__chronicle__search_sessions() for fast JSON
└─ CLI only? → Use `chronicle search` and parse output
```

## Search Strategies

### ⭐ Two-Phase Search Workflow (RECOMMENDED)

The most effective way to search Chronicle is using a two-phase approach:

**Phase 1: Broad Discovery**
- Use OR search (implicit or explicit) to cast a wide net
- Find the relevant area/timeframe
- Get 5-10 potential sessions

**Phase 2: Deep Dive**
- Review session summaries to identify most relevant ones
- Use precise AND searches to narrow down
- Extract specific information needed

**Example workflow:**
```python
# Phase 1: Broad OR search (multiple words = implicit OR)
results = mcp__chronicle__search_sessions(query="hooks json output", limit=10)
# → Returns sessions 108, 109, 110, 111, 112 (any word matches)

# Review the results - which sessions look most relevant?
# Get full summaries for promising sessions
summaries = mcp__chronicle__get_sessions_summaries(session_ids=[110, 111, 112])

# Phase 2: After reading summaries, dig deeper with AND
# Now you know the exact terms to search for
precise_results = mcp__chronicle__search_sessions(
    query="hookSpecificOutput AND decision/reason/systemMessage",
    limit=5
)
# → Returns only sessions with BOTH terms (precise match)
```

**Why this works:**
- ✅ Phase 1 finds the general area (prevents missing relevant sessions)
- ✅ Phase 2 finds exact solutions (prevents information overload)
- ✅ 2-3 searches total vs 10+ narrow searches that might miss context
- ✅ ROI: 1-2 minutes to find exact solution vs 10-20 minutes reinventing

### By Topic/Keywords

**With MCP:**
```python
# Search session summaries and prompts for keywords
mcp__chronicle__search_sessions(query="authentication", limit=10)
mcp__chronicle__search_sessions(query="database migration", limit=5)
```

**With CLI:**
```bash
# Search sessions
chronicle search "authentication" --limit 10
chronicle search "database migration" --limit 5
```

### By Time Period

**With MCP:**
```python
# Get sessions from specific time periods
mcp__chronicle__get_sessions(days=7, limit=20)  # Last week
mcp__chronicle__get_timeline(days=1)  # Yesterday with commits
```

**With CLI:**
```bash
# View recent sessions
chronicle sessions --days 7 --limit 20
chronicle timeline yesterday  # Yesterday with commits
```

### By Repository

**With MCP:**
```python
# Filter sessions by repository path
mcp__chronicle__get_sessions(repo_path="/Users/.../my-app", limit=20)
```

**With CLI:**
```bash
# Sessions command supports repo filtering via config
chronicle sessions --limit 20  # Defaults to current repo
```

### By Tool

**With MCP:**
```python
# Filter by AI tool used
mcp__chronicle__get_sessions(tool="claude-code", limit=10)
mcp__chronicle__get_sessions(tool="gemini-cli", limit=10)
```

**With CLI:**
```bash
# Filter by tool
chronicle sessions --tool claude-code --limit 10
chronicle sessions --tool gemini-cli --limit 10
```

## Example Queries

### "How did I implement authentication last time?"

**With MCP:**
```python
# Search for authentication-related sessions
sessions = mcp__chronicle__search_sessions(query="authentication", limit=5)
# Get full details of relevant sessions
for session in sessions:
    details = mcp__chronicle__get_session_summary(session_id=session["id"])
# Extract implementation approach and decisions
```

**With CLI:**
```bash
# Search for authentication work
chronicle search "authentication" --limit 5

# View specific session details
chronicle session <id>
# Parse output for approach and decisions
```

### "What was the blocker we hit with the database migration?"

**With MCP:**
```python
# Search for database migration issues
sessions = mcp__chronicle__search_sessions(query="database migration blocker", limit=5)
# Find relevant session and extract problem + solution
```

**With CLI:**
```bash
# Search for migration blockers
chronicle search "database migration blocker" --limit 5

# View session with blocker
chronicle session <id>
```

### "Show me all work on the user-dashboard feature"

**With MCP:**
```python
# Search for user-dashboard work
sessions = mcp__chronicle__search_sessions(query="user-dashboard", limit=10)
# List chronological sessions and summarize progress
```

**With CLI:**
```bash
# Search for dashboard work
chronicle search "user-dashboard" --limit 10

# View sessions chronologically
chronicle sessions --limit 10
```

## Response Format

When retrieving context, structure the response like:

```markdown
## Context from Past Sessions

### Session {id} - {date}
**What was done:** {summary}
**Key decision:** {decision and rationale}
**Outcome:** {result}
**Related:** [[Session-{id}]]

### Session {id} - {date}
...

## Relevant for Current Work
- {How this context applies}
- {What to keep in mind}
- {What to avoid based on past experience}
```

## Tools to Use (MCP or CLI)

### Chronicle Database Operations

**MCP Approach (Preferred):**
- `mcp__chronicle__search_sessions` - Search session summaries and prompts (fast JSON)
- `mcp__chronicle__get_session_summary` - Get full summary for specific session
- `mcp__chronicle__get_sessions` - List sessions with filters (tool, repo, days)
- `mcp__chronicle__get_timeline` - Get sessions + commits for time period
- `mcp__chronicle__search_commits` - Search git commit messages
- `mcp__chronicle__get_commits` - List commits with filters

**CLI Alternatives (Portable):**
- `chronicle search "query"` - Search sessions by keywords
- `chronicle session <id>` - Get full session summary
- `chronicle sessions --limit 10` - List recent sessions
- `chronicle timeline today` - View sessions + commits
- `chronicle search "commit message"` - Search commits
- `chronicle show today` - List recent commits

### Obsidian Vault Operations (Optional)

**Only if user wants vault notes:**
- `mcp__obsidian__search_notes` - Find documented sessions in vault
- `mcp__obsidian__read_note` - Read Obsidian note for session

## Tips

- **Chronicle database first!** - Faster than Obsidian vault search
- **MCP when available** - Structured JSON is easier to parse than CLI output
- **CLI works everywhere** - Use as reliable fallback when MCP not configured
- Always search broadly first, then narrow down with specific session IDs
- Check multiple related sessions for patterns
- Look at both successful and blocked approaches
- Note dates and repositories to understand context evolution
- Combine timeline views to see commits + sessions together
- When using CLI, parse output carefully for session IDs and summaries
