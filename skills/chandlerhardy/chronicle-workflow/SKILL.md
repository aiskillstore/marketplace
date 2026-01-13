---
name: chronicle-workflow
description: Complete workflow for tracking development work with Chronicle - session recording, git tracking, AI summarization, and Obsidian documentation. Works with CLI commands (portable) or MCP tools (faster). Use when starting a new development session, setting up project tracking, or when user wants comprehensive session management.
---

# Chronicle Workflow

This skill guides you through the complete Chronicle workflow for tracking and documenting development work. Primarily uses CLI commands for portability, with optional MCP tools for faster programmatic access.

## Auto-Activation

> **This skill auto-activates!** (Milestone #13)
>
> Prompts like "start a new session" or "is this tracked?" automatically trigger this skill. No manual loading needed!
>
> **Trigger patterns:** start session, is this tracked, chronicle workflow, setup
> **See:** `docs/HOOKS.md` for full details

## When to Use This Skill

Use this skill when:
- User is starting a new development session
- Setting up Chronicle for the first time
- Want to ensure all work is being tracked
- Need guidance on Chronicle best practices
- Building a comprehensive development knowledge base

## Complete Workflow

### 1. Session Start (If Not Already Tracking)

**Check if in Chronicle session:**
- Current session is likely NOT being tracked unless started with `chronicle start claude`
- To track current work, user must exit and restart with Chronicle

**Guide user:**
```bash
# Exit current session
exit

# Start new Chronicle-tracked session
chronicle start claude

# Or for other tools:
chronicle start gemini
```

**Important:** Chronicle sessions must be started explicitly - they don't auto-track.

### 2. During Development

**Best Practices:**
- Work naturally - Chronicle captures everything automatically
- Make frequent git commits with descriptive messages
- Chronicle links commits to sessions automatically (±30 min window)

**Available Commands (don't interrupt work to run these):**
```bash
chronicle sessions              # List recent sessions
chronicle show today           # See today's commits
chronicle timeline today       # Combined view
```

### 3. Session End

**Automatic on Exit:**
- Full transcript captured to `~/.ai-session/sessions/session_N.log`
- Metadata saved (duration, timestamp, repo)
- Session record created in database

**What happens:**
```
📊 Session #{id} complete! Duration: {minutes} minutes
💾 Full transcript saved
✨ Use 'chronicle session {id}' to view
```

### 4. Post-Session Documentation

**Generate Summary (Automatic on first view):**
```bash
# View session and auto-generate summary
chronicle session {id}

# For very large sessions (>50K lines)
chronicle summarize-chunked {id}
```

**Document to Obsidian:**
Use the `chronicle-session-documenter` skill or manually:
```
"Document session {id} to my Obsidian vault"
```

### 5. Retrieval & Context

**Find Past Work:**
Use the `chronicle-context-retriever` skill:
```
"How did I implement authentication last time?"
"What was the blocker with database migrations?"
"Show me all work on the API refactor"
```

**Browse Sessions (CLI):**
```bash
# Filter by repo
chronicle sessions --repo /path/to/project

# View timeline
chronicle timeline week

# Search sessions
chronicle search "authentication" --limit 5
```

**Browse Sessions (MCP - if available):**
```python
# Faster programmatic access
sessions = mcp__chronicle__get_sessions(repo_path="/path/to/project", limit=20)
results = mcp__chronicle__search_sessions(query="authentication", limit=5)
```

## Workflow Patterns

### Pattern 1: Quick Feature Work
```
1. chronicle start claude
2. [Make changes, commit]
3. exit
4. [Summary auto-generates on next view]
```

### Pattern 2: Multi-Session Project
```
1. chronicle start claude (Day 1)
2. [Work, commit]
3. exit
4. Document to Obsidian
5. chronicle start claude (Day 2)
6. "What did I do yesterday?" (retrieves context)
7. [Continue work]
```

### Pattern 3: Research & Context
```
1. "Show me all sessions about X" (context retriever)
2. Review past approaches and decisions
3. chronicle start claude
4. [Implement with informed approach]
```

## Multi-Project Tracking

**Automatic Detection:**
- Sessions detect working directory and git repo
- Stored in database for filtering

**Filter by Project:**
```bash
chronicle sessions --repo /path/to/project
chronicle timeline today --repo /path/to/project
chronicle summarize today --repo /path/to/project
```

## Key Features to Highlight

### Chunked Summarization
- Handles sessions of **unlimited size**
- Tested with 83,000+ line sessions
- Uses rolling summaries (10,000 lines/chunk)
- No rate limit issues

### Obsidian Integration
- Full MCP server integration
- Create structured session notes
- Search past work
- Build knowledge graph
- Wikilinks between sessions/commits/repos

### Local-First
- Everything stored locally (`~/.ai-session/`)
- SQLite database
- No data leaves your machine (except AI summarization)

## Common Questions

**Q: "Is this session being tracked?"**
A: Only if started with `chronicle start claude`. Must be explicit.

**Q: "Can I track a session retroactively?"**
A: No - must start with Chronicle from the beginning.

**Q: "How do I see what I did yesterday?"**
A: Use `chronicle timeline yesterday` or search Obsidian vault

**Q: "How do I link commits to sessions?"**
A: Automatic! Commits within ±30 minutes of session are linked.

## Database Location

All data stored at:
```
~/.ai-session/
├── sessions.db              # Main database
├── sessions/
│   ├── session_N.log       # Transcripts
│   └── session_N.meta      # Metadata
└── config.yaml             # Configuration
```

## Pro Tips

1. **Start Chronicle early** - Can't retroactively track
2. **Commit frequently** - Better session-commit linking
3. **Document important sessions** - Build knowledge base in Obsidian
4. **Search before building** - Use context retriever to avoid repeating work
5. **Use tags in Obsidian** - Makes finding past work easier
6. **Review summaries** - Helps remember key decisions

## Integration with Other Skills

- Use `chronicle-session-documenter` after completing sessions
- Use `chronicle-context-retriever` when starting related work
- Combine with git workflows for comprehensive tracking
