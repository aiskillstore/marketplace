---
name: notebooklm-manager
description: |
  Manages NotebookLM notebooks — query, add, list, search, enable/disable, remove.
  Use when a notebooklm.google.com URL appears or user mentions NotebookLM.
  Handles URLs through its own Chrome agent — do not navigate directly.
  Requires: claude-in-chrome MCP.
allowed-tools: Read, Write, Edit, Agent, AskUserQuestion
---

# NotebookLM Manager

Query orchestration and notebook registry management.

## Instructions

### Tool Boundaries
Chrome MCP tools (`mcp__claude-in-chrome__*`) aren't in this skill's allowed tool set — calling them directly will error. All browser interaction goes through the chrome-mcp-query agent via Task. If the agent returns an error, don't attempt Chrome tools yourself.

### 0. Data Path Resolution (run first)

Read `~/.claude-code-zero/notebooklm-connector/data-path` to obtain `DATA_DIR`.
The PreToolUse hook automatically detects install scope (project vs user) and writes the correct path.

- The file contains a single line: the absolute path to the data directory.
- Store this as `{DATA_DIR}` and use it for ALL subsequent file operations.
- **File read error → Tell user to restart the session (hook may not be loaded).**

### 0.1 Config

Read `{DATA_DIR}/config.json` for user preferences:
- `max_followups`: Maximum follow-up queries in coverage analysis (default: 3)
- `max_query_length`: Maximum characters per query sent to NotebookLM (default: 40000)
- `language`: Preferred response language (null = match user's language)
- `auto_coverage`: Enable automatic coverage analysis (default: true)

If the file is missing or a field is absent, use defaults above.

### 1. Query Detection

Extract from user message:
- `notebook_id`: Which notebook (e.g., "claude-docs")
- `question`: What to ask

### 2. Notebook Lookup

Read `{DATA_DIR}/library.json` to find notebook URL.
- **File not found → Re-run Step 0. If still missing, tell user to restart the session.**
- Not found → Show "Did you mean?" with similar IDs

### 3. Chat History

Default: `clearHistory: false` (keep previous context).

Set `clearHistory: true` only when the user explicitly requests it
(e.g., "clear history and query…", "start fresh on this notebook").

### 3.5 Input Length Validation

NotebookLM has a server-side character limit on chat input (~45,000–50,000 chars). There is no client-side enforcement — the textarea accepts any length, but the backend silently fails to respond beyond the limit, leaving the agent stuck in a polling loop.

Read `max_query_length` from config (default: 40000).

If `question.length > max_query_length`:
1. **Condense**: Rewrite the question to stay within the limit while preserving intent and key terms.
2. **Inform user**: Note that the question was condensed and show the shortened version.
3. If the question cannot be meaningfully condensed (e.g., a large code block the user wants analyzed), suggest breaking it into smaller, focused queries.

### 4. Agent Invocation

```
Task({
  subagent_type: "notebooklm-connector:chrome-mcp-query",
  prompt: `Execute the workflow: Input parsing → Tab setup → Title extraction → Submit question → Poll response → Output and exit

URL: {url}
Question: {question}
clearHistory: {true/false}

Output the response immediately upon receiving it and exit.`
})
```

**Follow-up queries** use the same Task format with the follow-up question.
The agent's STEP 1 automatically reuses the existing tab for the same URL.

#### 4.1 Agent Result Parsing

After Task returns, check the agent output:

| Agent Output Contains | Action |
|---|---|
| `ERROR_TYPE: CHROME_NOT_CONNECTED` | Show Chrome Connection Troubleshooting (below), stop |
| `ERROR_TYPE: AUTH_REQUIRED` | Tell user to log in to Google in Chrome, stop |
| `ERROR_TYPE:` (any other) | Show error details from agent output, stop |
| Task tool itself errors | Inform user the agent could not start. Check plugin installation. |
| `truncated: true` in agent output | Present the response but warn user that NotebookLM truncated the input. Suggest shortening the query or increasing `max_query_length` in config. |
| Response is empty or very short (< 20 chars) | Inform user that NotebookLM returned no meaningful response. Likely causes: input too long, no relevant content in notebook, or backend timeout. Do NOT proceed to coverage analysis. |
| Normal response (no ERROR_TYPE, ≥ 20 chars) | Proceed to Section 5 |

**Chrome Connection Troubleshooting** (show to user):
1. Verify Chrome or Edge browser is running
2. Chrome → `chrome://extensions` → Ensure "Claude in Chrome" extension is enabled
3. In Chrome, click extension icon → Side panel → Click **"Connect" button**
   - If a login screen appears, sign in with your Claude account (Pro/Max/Team/Enterprise required)
4. In Claude Code: `/chrome` → Select "Reconnect extension"
5. If this is your first time connecting, restart the browser to register the native messaging host, then repeat steps 3-4
6. Retry the query

### 5. Coverage Analysis

NotebookLM frequently answers only the first part of multi-topic questions. Without this check, users get incomplete answers and need to re-query manually.

If `auto_coverage` is `false` in config, skip to Section 6.

After every successful Task(chrome-mcp-query) return, check coverage before presenting the answer.
The PostToolUse hook will also remind you via `COVERAGE_REMINDER`.

#### STEP A: ANALYZE
Re-read user's original message. List ALL keywords/topics.

#### STEP B: VERIFY
Each keyword: ✅ covered / ❌ missing

#### STEP C: QUERY (if gaps)
Launch follow-up: `Task(subagent_type: "notebooklm-connector:chrome-mcp-query", same URL, missing topic question)`
Follow-ups are cheap — the same Chrome tab is reused.
Then return to STEP A.

#### STEP D: COMPLETE
All covered OR `max_followups` reached → Synthesize and present (Section 6 format).
After limit: AskUserQuestion to confirm whether to continue.

---

### 6. Response Format

```
**Notebook**: [Title] (`{id}`)

**Answer**: [response]

---
**Suggested follow-ups**:
- [question 1]
- [question 2]
```

If `language` is set in config, present the answer in that language.

---

## Commands

See [references/commands.md](references/commands.md) for full command reference.

| Command | Description |
|---------|-------------|
| `list` | Show active notebooks |
| `add <url>` | Smart add (auto-discover) |
| `show <id>` | Notebook details |
| `search <query>` | Find notebooks |

---

## Storage

Data is isolated per install scope. The hook resolves the correct path automatically.
When `${CLAUDE_PLUGIN_DATA}` is available, it is used as the base directory.
Otherwise falls back to `~/.claude-code-zero/notebooklm-connector/`.

```
{base}/
├── data-path                       # Always at ~/.claude-code-zero/notebooklm-connector/data-path
├── global/data/                    # User-level install (shared across projects)
│   ├── library.json
│   ├── archive.json
│   ├── config.json
│   └── notebooks/{id}.json
└── projects/<md5-hash>/data/       # Project-level install (per-project isolation)
    ├── library.json
    ├── archive.json
    ├── config.json
    └── notebooks/{id}.json
```

The `data-path` file is always at `~/.claude-code-zero/notebooklm-connector/data-path` (fixed location).
Data directory and default files are lazily created on first `data-path` read.

**Migration (automatic)**:
- `data/` → `global/data/`: Existing flat data layout is moved to the global subdirectory.
- Legacy paths (`~/.claude/plugins/...`, `~/.claude/claude-code-zero/...`) are copied to `global/data/`.
- `~/.claude-code-zero/` → `${CLAUDE_PLUGIN_DATA}/`: When the env var becomes available, data is migrated.

---

## Tool Boundaries

- **Use**: Read, Write (data dir), Edit (data dir), Task, AskUserQuestion
- **Do NOT use**: Chrome MCP tools directly (`mcp__claude-in-chrome__*`)

---

## References

- [references/commands.md](references/commands.md) — Full command reference
- [references/schemas.md](references/schemas.md) — JSON schemas
- [references/gotchas.md](references/gotchas.md) — Common pitfalls and failure modes
