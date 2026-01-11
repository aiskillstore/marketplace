---
name: chronicle-session-documenter
description: Document AI-assisted development sessions to Obsidian vault using Chronicle data. Works with MCP (fastest) or CLI commands (portable). Use when completing a coding session, creating development logs, or maintaining a knowledge base of past work. Automatically creates structured notes with metadata, summaries, and wikilinks.
---

# Chronicle Session Documenter

This skill helps you document development sessions to your Obsidian vault using Chronicle's database. Works with both MCP server (fast, structured) or CLI commands (portable, everywhere).

## Auto-Activation

> **This skill auto-activates!** (Milestone #13)
>
> Prompts like "document session 75" or "export to Obsidian" automatically trigger a recommendation to use this skill. No need to manually load it!
>
> **Trigger patterns:** document session, export to obsidian, save to vault
> **See:** `docs/HOOKS.md` for full details

## When to Use This Skill

Use this skill when:
- A development session has just completed
- User wants to document what was accomplished in a session
- Creating a development log or journal entry
- Building a searchable knowledge base of past work
- Need to link related sessions, commits, or decisions

## How It Works

**Option 1: With MCP (Preferred)**
1. **Query Chronicle** - `mcp__chronicle__get_session_summary(session_id)` → Get structured JSON with full summary
2. **Create Note** - `mcp__obsidian__write_note(...)` → Write directly to Obsidian vault
3. **Link Work** - Use session relationships from JSON to create wikilinks

**Option 2: With CLI (Portable)**
1. **Query Chronicle** - `chronicle session <id>` → Get formatted session details and summary
2. **Parse Output** - Extract summary, files, duration from CLI output
3. **Create Note** - `mcp__obsidian__write_note(...)` OR manually create note file
4. **Link Work** - Use parsed data to create wikilinks

**Decision Tree:**
```
Document session to Obsidian
├─ MCP available? → Use mcp__chronicle__get_session_summary() + mcp__obsidian__write_note()
└─ CLI only? → Use `chronicle session <id>`, parse output, write note
```

**Note**: Summaries are automatically generated in background when session ends (may still be processing for recent sessions)

## Note Structure

Create notes in `Chronicle/Sessions/Session-{id}.md` with this format:

```markdown
---
session_id: {id}
date: "{YYYY-MM-DD}"
started: "{HH:MM AM/PM}"
duration_minutes: {minutes}
ai_tool: "{tool}"
repo: "{repo_name}"
tags: ["chronicle-session", "{ai_tool}", "{topics}"]
---

# Session {id} - {Brief Title}

**Duration:** {duration}
**Repository:** [[{repo_name}]]
**Tool:** {AI Tool Name}

## Summary
{AI-generated summary from Chronicle}

## What Was Accomplished
- {Key accomplishment 1}
- {Key accomplishment 2}

## Key Technical Decisions
- {Decision 1 and rationale}

## Files Created or Modified
- `path/to/file.py` - {what changed}

## Issues & Blockers
- {Any problems encountered}

## Related
- Previous: [[Session-{prev_id}]]
- Commits: [[Commit-{sha}]]
- Repository: [[{repo_name}]]
```

## Workflow Examples

### Option 1: With MCP (Fast, Structured)

**After completing a session:**

```python
# Step 1: Get session data from Chronicle MCP
session_data = mcp__chronicle__get_session_summary(session_id=10)

# Step 2: Extract key information
session_id = session_data["id"]
timestamp = session_data["timestamp"]  # "2025-10-24T14:30:00"
tool = session_data["tool"]  # "claude-code"
duration = session_data["duration_minutes"]  # 45
repo_path = session_data["repo_path"]  # "/Users/.../my-project"
summary = session_data["summary"]  # AI-generated summary (multi-paragraph)

# Step 3: Format note content
note_content = f"""# Session {session_id} - {brief_title}

**Duration:** {duration} minutes
**Repository:** [[{repo_name}]]
**Tool:** {tool_emoji} {tool_name}

## Summary
{summary}

## What Was Accomplished
- {extracted_accomplishments}

## Key Technical Decisions
- {extracted_decisions}

## Files Created or Modified
- {extracted_files}

## Issues & Blockers
- {extracted_blockers}

## Related
- Previous: [[Session-{prev_id}]]
"""

# Step 4: Prepare frontmatter
frontmatter = {
    "session_id": session_id,
    "date": "2025-10-24",
    "started": "14:30",
    "duration_minutes": duration,
    "ai_tool": tool,
    "repo": repo_name,
    "tags": ["chronicle-session", tool, "feature-work"]
}

# Step 5: Write to Obsidian vault (if MCP available)
mcp__obsidian__write_note(
    path="Chronicle/Sessions/Session-10.md",
    content=note_content,
    frontmatter=frontmatter,
    mode="overwrite"
)
```

### Option 2: With CLI (Portable, No MCP Required)

**After completing a session:**

```bash
# Step 1: Get session data from Chronicle CLI
chronicle session 10 > /tmp/session_10.txt

# Step 2: Parse the output to extract:
# - Session ID, timestamp, tool, duration
# - Repository path
# - AI-generated summary
# - Files mentioned
# - Keywords/tags

# Step 3: Create note content using parsed data
# (Similar structure to MCP approach above)

# Step 4: If Obsidian MCP available, use it to write note:
# mcp__obsidian__write_note(...)
#
# OR manually create file in Obsidian vault:
# Write to ~/Documents/Obsidian/Chronicle/Sessions/Session-10.md
```

**Note**: CLI approach requires parsing Chronicle's formatted output, which is less elegant but fully portable to any system with Chronicle installed.

## Example Usage

**User:** "Can you document session 10 to my Obsidian vault?"

**Assistant (with MCP):**
1. Calls `mcp__chronicle__get_session_summary(session_id=10)`
2. Parses structured JSON to extract accomplishments, decisions, files, blockers
3. Creates structured Markdown content with wikilinks
4. Calls `mcp__obsidian__write_note(...)` to save to vault
5. Confirms: "Documented Session 10 to Chronicle/Sessions/Session-10.md"

**Assistant (without MCP):**
1. Runs `chronicle session 10` to get formatted output
2. Parses CLI output to extract summary and metadata
3. Creates structured Markdown content with wikilinks
4. Either uses `mcp__obsidian__write_note(...)` if available, or creates file manually
5. Confirms: "Documented Session 10 to Chronicle/Sessions/Session-10.md"

## Tools to Use (MCP or CLI)

### Chronicle Database Operations

**MCP Approach (Preferred):**
- `mcp__chronicle__get_session_summary(session_id)` - Get full session details with AI summary
- `mcp__chronicle__get_sessions(limit, days, tool, repo_path)` - List recent sessions to find session ID
- `mcp__chronicle__search_sessions(query, limit)` - Search for sessions by keyword
- `mcp__chronicle__get_commits(repo_path, days, limit)` - Get related commits for linking
- `mcp__chronicle__get_sessions_summaries(session_ids)` - Batch get summaries (up to 20 at once)

**CLI Alternatives:**
- `chronicle session <id>` - Get session details with summary
- `chronicle sessions --limit 10` - List recent sessions
- `chronicle search "keyword" --limit 10` - Search sessions
- `chronicle show today` - Get commits for linking

### Obsidian Vault Operations

**MCP Approach (Preferred):**
- `mcp__obsidian__write_note(path, content, frontmatter, mode)` - Write note to vault
- `mcp__obsidian__read_note(path)` - Check if note already exists (optional)
- `mcp__obsidian__list_directory(path)` - List existing session notes (optional)

**Manual Alternative (No MCP):**
- Create file directly: `~/Documents/Obsidian/<vault>/Chronicle/Sessions/Session-<id>.md`
- Write YAML frontmatter + markdown content manually

## Tips

- **Summary generation is automatic** - Summarization starts in background immediately when session ends (may take a few minutes for large sessions)
- **Parse summaries intelligently** - AI summaries often have sections like "Accomplishments:", "Technical Decisions:", "Issues/Blockers:"
- **Use wikilinks** - Link to `[[Session-{id}]]`, `[[{repo_name}]]`, `[[Commit-{short_sha}]]` for navigation
- **Extract repo name** - Parse from `repo_path`: `/Users/.../my-app` → `my-app`
- **Handle missing data** - Some sessions may not have summaries yet (still processing in background), or durations (still running)
- **Batch document** - Use `get_sessions()` to find recent sessions, then document each in loop
- **Check existing notes** - Use `read_note()` to avoid overwriting manually edited notes (ask user first)
- **Tool emojis** - Use 🎯 for claude-code, ✨ for gemini-cli, 🔮 for qwen-cli
- **Frontmatter tags** - Always include `["chronicle-session", "{tool}", ...]` for filtering in Obsidian
- **Date formatting** - Parse ISO timestamp `2025-10-24T14:30:00` → date: "2025-10-24", started: "14:30"

## Common Patterns

### Document Today's Sessions

**With MCP:**
```python
# Get today's sessions
sessions = mcp__chronicle__get_sessions(days=1, limit=20)
# Document each to vault
for session in sessions:
    if session["is_session"]:  # Only full sessions, not one-shots
        document_to_vault(session["id"])
```

**With CLI:**
```bash
# List today's sessions
chronicle sessions --days 1 --limit 20

# Manually document each one
chronicle session 10  # View details
# Parse and create Obsidian note
```

### Document Specific Session

**With MCP:**
```python
# Direct documentation
session = mcp__chronicle__get_session_summary(session_id=10)
# Create note from structured data
```

**With CLI:**
```bash
# Get session details
chronicle session 10

# Parse output and create note
```

### Find and Document Sessions About a Topic

**With MCP:**
```python
# Search first
results = mcp__chronicle__search_sessions(query="authentication", limit=5)
# Document each match
for result in results:
    document_to_vault(result["id"])
```

**With CLI:**
```bash
# Search for sessions
chronicle search "authentication" --limit 5

# Document each match
chronicle session <id>
# Create note from parsed output
```