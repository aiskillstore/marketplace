---
name: notebooklm-manager
description: |
  This skill should be used when the user wants to interact with NotebookLM notebooks
  via Claude Code's Chrome integration.

  Trigger phrases: "Query my NotebookLM", "Ask my notebook about X", "query [id] about X",
  "list my notebooks", "add notebook URL", "show notebook details", "search notebooks for X",
  "Check my docs", "what does my [topic] notebook say about",
  "remove notebook", "delete notebook", "disable notebook", "enable notebook".

  Also triggers when user: (1) mentions NotebookLM explicitly, (2) shares NotebookLM URL
  (https://notebooklm.google.com/notebook/...).

  Do NOT use for: general web searches, local file reading, or non-NotebookLM documentation queries.

  Requires: claude --chrome with claude-in-chrome MCP.
allowed-tools:
  - Read
  - Write
  - Task
  - AskUserQuestion
---

# NotebookLM Manager

Query orchestration and notebook registry management.

## Instructions

### CRITICAL CONSTRAINT
This skill MUST NOT call any `mcp__claude-in-chrome__*` tools.
These tools DO NOT EXIST in this skill's allowed tool set.
All Chrome interaction is delegated to the agent via Task.
After receiving an agent error, do NOT attempt to use Chrome tools yourself.

### 1. Query Detection

Extract from user message:
- `notebook_id`: Which notebook (e.g., "claude-docs")
- `question`: What to ask

### 2. Notebook Lookup

Read `${SKILL_ROOT}/data/library.json` to find notebook URL.
- **File not found → Create `data/` folder and files with `[]`**
- Not found → Show "Did you mean?" with similar IDs

### 3. Chat History Confirmation (First Query Only)

**Before the first query to a notebook**, ask user about chat history:

```
AskUserQuestion({
  questions: [{
    question: "Clear NotebookLM chat history before querying?",
    header: "History",
    options: [
      { label: "No (Recommended)", description: "Keep previous context, faster response" },
      { label: "Yes", description: "Start fresh, may involve UI modal interaction" }
    ],
    multiSelect: false
  }]
})
```

Pass result to agent as `clearHistory: true/false` in the prompt.

**Note**: Clearing history may trigger a confirmation modal in NotebookLM, which can slow down automation. Default "No" is recommended.

Track per-notebook first-query status within the current conversation.
After asking once for a given notebook URL, skip the confirmation for
subsequent queries to the same URL in the same session.

### 4. Agent Invocation

```
Task({
  subagent_type: "notebooklm-connector:chrome-mcp-query",
  prompt: `Execute the workflow: Input parsing → Tab setup → Title extraction → Submit question → Poll response → Output and exit

URL: {url}
Question: {question}
mode: query
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
| Normal response (no ERROR_TYPE) | Proceed to Section 5 |

**Chrome Connection Troubleshooting** (show to user):
1. Verify Chrome or Edge browser is running
2. Chrome → `chrome://extensions` → Ensure "Claude in Chrome" extension is enabled
3. In Chrome, click extension icon → Side panel → Click **"Connect" button**
   - If a login screen appears, sign in with your Claude account (Pro/Max/Team/Enterprise required)
4. In Claude Code: `/chrome` → Select "Reconnect extension"
5. If this is your first time connecting, restart the browser to register the native messaging host, then repeat steps 3-4
6. Retry the query

### 5. Post-Query Coverage Analysis (MANDATORY — DO NOT SKIP)

**After EVERY successful Task(chrome-mcp-query) return, perform this checklist BEFORE presenting any answer.**
The PostToolUse hook will also remind you via `COVERAGE_REMINDER` message.

**DO NOT present the answer yet. DO NOT generate "Suggested follow-ups" yet.**

#### STEP A: ANALYZE
Re-read user's original message. List ALL keywords/topics.

#### STEP B: VERIFY
Each keyword: ✅ covered / ❌ missing

#### STEP C: QUERY (if gaps)
Launch follow-up: `Task(subagent_type: "notebooklm-connector:chrome-mcp-query", same URL, missing topic question)`
Follow-ups are cheap — the same Chrome tab is reused.
Then return to STEP A.

#### STEP D: COMPLETE
All covered OR 3 follow-ups → Synthesize and present (Section 6 format).
Max 3 follow-ups. After limit: AskUserQuestion to confirm whether to continue.

---

### 6. Response Format

```
**Notebook**: [Title] (`{id}`)

**Answer**: [response]

**Citations**:
[1] "quote" - Source: [doc]

---
**Suggested follow-ups**:
- [question 1]
- [question 2]
```

---

## Commands

See `references/commands.md` for full command reference.

| Command | Description |
|---------|-------------|
| `list` | Show active notebooks |
| `add <url>` | Smart add (auto-discover) |
| `show <id>` | Notebook details |
| `search <query>` | Find notebooks |

---

## Storage

Location: `${SKILL_ROOT}/data/`

```
data/
├── library.json        # Active notebooks (index)
├── archive.json        # Archived notebooks
└── notebooks/{id}.json # Full metadata (on-demand)
```

**Initialization**:
- If `data/` folder does not exist, create it
- If `library.json` does not exist, create with:
  `{"notebooks": {}, "schema_version": "1.0", "updated_at": "<ISO timestamp>"}`
- If `archive.json` does not exist, create with:
  `{"notebooks": {}, "schema_version": "1.0", "updated_at": "<ISO timestamp>"}`
- If `notebooks/` folder does not exist, create it
- Each `notebooks/{id}.json` must include `"schema_version": "1.0"` as the first field

---

## Tool Boundaries

- **Use**: Read, Write, Task, AskUserQuestion
- **Do NOT use**: Chrome MCP tools directly (`mcp__claude-in-chrome__*`)

---

## References

- `references/commands.md` - Full command reference
- `references/schemas.md` - JSON schemas
