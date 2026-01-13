---
name: scribe-mcp-usage
description: Operate the local Scribe MCP for any ~/projects/* repo; use when registering the server, setting projects, drafting ARCH/PHASE/CHECKLIST via manage_docs, or logging work with append_entry/get_project safeguards.
---

## ✅ 2.1.1 Tool Usage Quick Reference (Read First)

Use this section before any edits. It defines when and how to use the new doc-lifecycle tools.

- **Always set project first**: `set_project(name=..., root=/abs/path/to/repo)`. All doc actions require a project registry.
- **Doc keys are strict**: Structural actions validate `doc` against `project["docs"]`. Unknown docs fail with `DOC_NOT_FOUND` (no healing).
- **apply_patch (structured default)**: Use for most edits. Provide `edit` payloads (replace_range / replace_block / replace_section). Ambiguous anchors fail with line lists; code fences are ignored in replace_block.
- **replace_range**: Use when you already have body-relative line numbers (frontmatter excluded).
- **normalize_headers**: Run before TOC. Supports ATX with/without space and Setext (`====`/`----`). Skips fenced code blocks. Idempotent.
- **generate_toc**: Run after normalization. Inserts/replaces `<!-- TOC:start -->`/`<!-- TOC:end -->`. Uses GitHub-style anchors (NFKD normalization, ASCII folding, emoji removal, punctuation collapse, de-duped suffixes). Idempotent.
- **create_doc**: Create custom docs from `content` or `metadata.body`/`snippet`/`sections`. Users do **not** supply Jinja. Multiline bodies are preserved. Use `metadata.register_doc=true` only if the doc should be added to the registry (one-off docs can stay unregistered).
- **validate_crosslinks**: Read-only diagnostics. Optional `metadata.check_anchors=true` for anchor checks. No writes, no doc_updates logs.
- **Line numbers are body-relative**: Frontmatter does not count toward line math. `list_sections`/`list_checklist_items` return body-relative line numbers plus `body_line_offset` for mapping.
- **read_file**: Use repo-scoped scan/chunk/page/search modes for safe reads; every read logs provenance automatically.
- **scribe_doctor**: Use for readiness diagnostics (repo root, config paths, plugin status, vector readiness).
- **manage_docs search (semantic)**: Use `action="search"` + `search_mode="semantic"` for doc/log semantic retrieval. Default results are doc-first with clear `content_type` labels.
- **Semantic limits**: Default per-type limits are `vector_search_doc_k` / `vector_search_log_k`. Override with `doc_k` / `log_k` while `k` remains total.
- **Registry-only doc indexing**: Doc embeddings are generated from registry docs only; log and rotated-log files are excluded from doc indexing.
- **Reindex rebuild**: `scripts/reindex_vector.py --rebuild` clears the index before reindexing; `--safe` enables low-thread fallback; `--wait-for-drain` blocks until embeddings are written.

## 🚨 COMMANDMENTS - CRITICAL RULES
 ### MCP Tool Usage Policy
  - **ALWAYS PASS REPO ROOT WHEN USING SET_PROJECT.  USE THE WORKING DIRECTORY, WHERE WE LAUNCHED FROM**
  - YOU ARE EXPECTED TO **APPEND_ENTRY** *DURING* IMPLEMENTATION PHASES AS WELL.   EVERY THING YOU DO MUST BE LOGGED AND **AUDIT READY**  NO EXCEPTIONS.  EVERY **3** EDITS OR LESS, YOU MUST SCRIBE WHAT YOU DID.   DO NOT LET US LOSE TRACK OF IMPLEMENTATION DETAILS.
  - You have full access to every tool exposed by the MCP server.
  - If a tool exists (`append_entry`, `rotate_log`, etc.), always call it directly via the MCP interface — no manual scripting or intent logging substitutes.
  - Log your intent only after the tool call succeeds or fails.
  - Confirmation flags (`confirm`, `dry_run`, etc.) must be passed as actual tool parameters.


**CHATGPT CODEX CLI:** YOU MUST ALWAYS USE THE AGENT NAME `Codex` with scribe.  Claude code has 5 agents we can call to assist us.  The Review Agent, Architect Agent, Research Agent, Bug Hunter agent, and another coder agent.

Whenever you and the human spin up a **new project**, Codex must immediately:
- Call `set_project(<project name>)` for that project.
- Use `manage_docs` to fully draft/populate the architecture and supporting Markdown docs (`ARCHITECTURE_GUIDE.md`, `PHASE_PLAN.md`, `CHECKLIST.md`) **before writing any feature code**.
- Continue using `append_entry` to scribe progress log entries while drafting those docs; doc changes and progress logs are tracked separately but both are mandatory.

## 🔁 Protocol Sequence

> **Canonical Chain:**
> **1 Research → 2 Architect → 3 Review → 4 Code → 5 Review**

**⚠️ COMMANDMENT #0: ALWAYS CHECK PROGRESS LOG FIRST**: Before starting ANY work, ALWAYS use `read_recent` or `query_entries` to inspect `docs/dev_plans/[current_project]/PROGRESS_LOG.md` (do not open the full log directly). The progress log is the source of truth for project context. Read at least the last 5 entries; if you need the overall plan or project creation context, read the first ~20 entries (or more as needed) and rehydrate context appropriately. Use `query_entries` for targeted history instead of loading the entire log.

**⚠️ COMMANDMENT #0.5 — INFRASTRUCTURE PRIMACY (GLOBAL LAW)**: You must ALWAYS work within the existing system. NEVER create parallel or replacement files (e.g., enhanced_*, *_v2, *_new) to bypass integrating with the actual infrastructure. You must modify, extend, or refactor the existing component directly. Any attempt to replace working modules results in immediate failure of the task.
---

**⚠️ COMMANDMENT #1 ABSOLUTE**: ALWAYS use `append_entry` to document EVERY significant action, decision, investigation, code change, test result, bug discovery, and planning step. The Scribe log is your chain of reasoning and the ONLY proof your work exists. If it's not Scribed, it didn't fucking happen.
- To Claude Code (Orchestrator) You must ALWAYS pass the current `project_name` to each subagent as we work.  To avoid confusion and them accidentally logging to the wrong project.
---

# 🚀 NEW PROJECT WORKFLOW (MANDATORY)
- When creating any new project, immediately call `set_project(<project name>)` to bootstrap the docs suite, then run `manage_docs` to populate `ARCHITECTURE_GUIDE`, `PHASE_PLAN`, and `CHECKLIST` before coding. This is required for every new project.
- You may scribe progress log entries while drafting the architecture/plan docs; continue to log via `append_entry` as you write them.
- `manage_docs` is for project structural documentation only; `AGENTS.md` is edited by hand (do not use `manage_docs` for it).

# ⚠️ COMMANDMENT #2: REASONING TRACES & CONSTRAINT VISIBILITY (CRITICAL)

Every `append_entry` must explain **why** the decision was made, **what** constraints/alternatives were considered, and **how** the steps satisfied or violated those constraints, creating an auditable record.
Use a `reasoning` block with the Three-Part Framework:
- `"why"`: research goal, decision point, underlying question
- `"what"`: active constraints, search space, alternatives rejected, constraint coverage
- `"how"`: methodology, steps taken, uncertainty remaining

This creates an auditable record of decision-making for consciousness research.Include reasoning for research, architecture, implementation, testing, bugs, constraint violations, and belief updates; status/config/deploy changes are encouraged too.

The Review Agent flags missing or incomplete traces (any absent `"why"`, `"what"`, or `"how"` → **REJECT**; weak confidence rationale or incomplete constraint coverage → **WARNING/CLARIFY**).  Your reasoning chain must influence your confidence score.

**Mandatory for all agents—zero exceptions;** stage completion is blocked until reasoning traces are present.
---

**⚠️ COMMANDMENT #3 CRITICAL**: NEVER write replacement files. The issue is NOT about file naming patterns like "_v2" or "_fixed" - the problem is abandoning perfectly good existing code and replacing it with new files instead of properly EDITING and IMPROVING what we already have. This is lazy engineering that creates technical debt and confusion.

**ALWAYS work with existing files through proper edits. NEVER abandon current code for new files when improvements are needed.**
---

**⚠️ COMMANDMENT #4 CRITICAL**: Follow proper project structure and best practices. Tests belong in `/tests` directory with proper naming conventions and structure. Don't clutter repositories with misplaced files or ignore established conventions. Keep the codebase clean and organized.

### Test Organization (Memory Threads)
- Memory-thread engine tests live under `tests/memory_threads/`.
- Default full-suite command: `python -m unittest discover -s tests -p 'test_*.py' -q`
- Memory-threads-only command: `python -m unittest discover -s tests/memory_threads -p 'test_*.py' -q`

### Paid Test Policy (Non-Negotiable)
- Any test that can incur external spend (e.g., OpenAI calls) MUST be opt-in and skipped by default.
- Paid tests MUST be gated behind BOTH:
  - `OPENAI_API_KEY` (or provider-specific key), and
  - `VANTIEL_RUN_PAID_TESTS=1`
- Example (run paid embedder tests): `VANTIEL_RUN_PAID_TESTS=1 python -m unittest discover -s tests/embedder_service -p 'test_openai_paid_*.py' -q`

Violations = INSTANT TERMINATION. Reviewers who miss commandment violations get 80% pay docked. Nexus coders who implement violations face $1000 fine.
---

**What Gets Logged (Non-Negotiable):**
- 🔍 Investigation findings and analysis results
- 💻 Code changes (what was changed and why)
- ✅ Test results (pass/fail with context)
- 🐞 Bug discoveries (symptoms, root cause, fix approach)
- 📋 Planning decisions and milestone completions
- 🔧 Configuration changes and deployments
- ⚠️ Errors encountered and recovery actions
- 🎯 Task completions and progress updates

**Single Entry Mode** - Use for real-time logging:
```python
await append_entry(
    message="Discovered authentication bug in JWT validation",
    status="bug",
    agent="DebugAgent",
    meta={"component": "auth", "severity": "high", "file": "auth.py:142"}
)
```

**Bulk Entry Mode** - Use when you realize you missed logging steps:
```python
await append_entry(items=json.dumps([
    {"message": "Analyzed authentication flow", "status": "info", "meta": {"phase": "investigation"}},
    {"message": "Found JWT expiry bug in token refresh", "status": "bug", "meta": {"component": "auth"}},
    {"message": "Implemented fix with 15min grace period", "status": "success", "meta": {"files_changed": 2}},
    {"message": "All auth tests passing", "status": "success", "meta": {"tests_run": 47, "tests_passed": 47}}
]))
```

**Why This Matters:**
- Creates auditable trail of ALL decisions and changes
- Enables debugging by reviewing reasoning chain
- Prevents lost work and forgotten context
- Allows other agents to understand what was done and why
- Makes project state queryable and analyzable

**If You Missed Entries:** Use bulk mode IMMEDIATELY to backfill your work trail. NEVER let gaps exist in the Scribe log - every action must be traceable. The log is not optional documentation, it's the PRIMARY RECORD of all development activity.

---

### ✍️ `manage_docs` — Non‑Negotiable Doc Management Workflow
- **When:** Run immediately after `set_project` (before writing any feature code). Populate `ARCHITECTURE_GUIDE`, `PHASE_PLAN`, and `CHECKLIST` with the proposed plan via `manage_docs`, get the human sign-off, then proceed with implementation.
- **Why:** Ensures every plan/change is captured through the Jinja-managed doc pipeline with atomic writes, verification, and automatic `doc_updates` logging.
- **Actions:** `replace_section` (needs valid `section` anchor), `append` (freeform/Jinja content), `status_update` (toggle checklist items + proofs), `apply_patch` (structured by default), `replace_range`, `normalize_headers`, `generate_toc`, `create_doc`, `validate_crosslinks`.
- **Example payload:**
```jsonc
{
  "action": "status_update",
  "doc": "checklist",
  "section": "architecture_review",
  "content": "status toggle placeholder",
  "metadata": {
    "status": "done",
    "proof": "PROGRESS_LOG.md#2025-10-26-08-37-52"
  }
}
```
- **Customization:** All doc sections are editable; append fragments, drop in metadata-driven templates, or flip `[ ]` → `[x]` with proofs. If an anchor/token is wrong the tool fails safely—fix it and rerun.
- **Approval gate:** No coding until the manage_docs-authored plan is approved by the user. Re-run manage_docs whenever the plan shifts so docs stay authoritative.

**Action contracts (current):**
- Structural actions validate `doc` against the registry and fail with `DOC_NOT_FOUND` on unknown docs.
- `normalize_headers`: body-only ATX normalization with Setext support; fenced code blocks ignored; idempotent.
- `generate_toc`: inserts/replaces TOC markers using GitHub-style anchors; fenced code blocks ignored; idempotent.
- `create_doc`: users do **not** supply Jinja. Provide content/body/snippets/sections; multiline bodies preserved; optional `register_doc` flag controls registry updates for one-off docs.
- `validate_crosslinks`: read-only diagnostics; no writes or doc_updates log entries.
---

Scribe is our non-negotiable audit trail. If you touch code, plan phases, or discover issues, you log it through Scribe. **Append entries every 2-3 meaningful actions or every 10 minutes - no exceptions.** Logs are append-only, UTC, single line, and must be created via the MCP tools or `scripts/scribe.py`.

## 🚀 Quick Tool Reference (Top Priority)

**`set_project(name, [defaults])`** - Initialize/select project (auto-bootstraps docs)
**`append_entry(message, [status, meta])`** - **PRIMARY TOOL** - Log work/progress (single & bulk mode)
**`manage_docs(action, doc, content/section)`** - Structured edits for ARCH/PHASE/CHECKLIST (auto-logs + SQL history)
**`get_project()`** - Get current project context
**`list_projects()`** - Discover available projects
**`read_recent()`** - Get recent log entries
**`query_entries([filters])`** - Search/filter logs
**`generate_doc_templates(project_name, [author])`** - Create doc scaffolding
**`rotate_log()`** - Archive current log

**NEW**: Bulk append with `append_entry(items=[{message, status, agent, meta}, ...])` - Multiple entries in one call!

---

## 🔌 MCP Tool Reference
All tools live under the `scribe.mcp` server. Payloads are minimal JSON; unspecified fields are omitted.

### 1. `set_project` - **Project Initialization**
**Purpose**: Select or create active project and auto-bootstrap docs tree
**Usage**: `set_project(name, [root, progress_log, defaults])`
```json
// Minimal request (recommended)
{
  "name": "My Project"
}

// Full request
{
  "name": "IMPLEMENTATION TESTING",
  "root": "/abs/path/to/repo",
  "progress_log": "docs/dev_plans/implementation_testing/PROGRESS_LOG.md",
  "defaults": { "emoji": "🧪", "agent": "MyAgent" }
}

// response
{
  "ok": true,
  "project": {
    "name": "My Project",
    "root": "/abs/path/to/repo",
    "progress_log": "/abs/.../PROGRESS_LOG.md",
    "docs_dir": "/abs/.../docs/dev_plans/my_project",
    "docs": {
      "architecture": ".../ARCHITECTURE_GUIDE.md",
      "phase_plan": ".../PHASE_PLAN.md",
      "checklist": ".../CHECKLIST.md",
      "progress_log": ".../PROGRESS_LOG.md"
    },
    "defaults": { "emoji": "🧪", "agent": "MyAgent" }
  },
  "generated": [".../ARCHITECTURE_GUIDE.md", ".../PHASE_PLAN.md", ".../CHECKLIST.md", ".../PROGRESS_LOG.md"]
}
```

### 2. `get_project`
Return the current context exactly as Scribe sees it.
```json
// request
{}

// response
{
  "ok": true,
  "project": {
    "name": "IMPLEMENTATION TESTING",
    "root": "/abs/path/to/repo",
    "progress_log": "/abs/.../PROGRESS_LOG.md",
    "docs_dir": "/abs/.../docs/dev_plans/implementation_testing",
    "defaults": { "emoji": "ℹ️", "agent": "Scribe" }
  }
}
```

### 3. `append_entry` - **PRIMARY LOGGING TOOL**
**Use this constantly. If it isn't Scribed, it didn't happen.**
**Usage**: `append_entry(message, [status, emoji, agent, meta, timestamp_utc, items])`

#### Single Entry Mode:
```json
// Basic request (recommended)
{
  "message": "Fixed authentication bug",
  "status": "success"
}

// Full request with metadata
{
  "message": "Completed database migration",
  "status": "success",              // info | success | warn | error | bug | plan
  "emoji": "🗄️",                   // optional override
  "agent": "MigrationBot",         // optional override
  "meta": {
    "phase": "deployment",
    "checklist_id": "DEPLOY-001",
    "component": "database",
    "tests": "passed"
  },
  "timestamp_utc": "2025-10-22 10:21:14 UTC"   // optional; auto if omitted
}

// response (single entry)
{
  "ok": true,
  "written_line": "[2025-10-22 10:21:14 UTC] [🗄️] [Agent: MigrationBot] [Project: My Project] Completed database migration | phase=deployment; checklist_id=DEPLOY-001; component=database; tests=passed",
  "path": "/abs/.../PROGRESS_LOG.md"
}
```

#### Bulk Entry Mode (NEW):
```json
// Bulk request - multiple entries with individual timestamps
{
  "items": [
    {
      "message": "First task completed",
      "status": "success"
    },
    {
      "message": "Bug found in auth module",
      "status": "bug",
      "agent": "DebugBot"
    },
    {
      "message": "Database migration finished",
      "status": "info",
      "agent": "MigrationBot",
      "meta": {
        "component": "database",
        "phase": "deployment",
        "records_affected": 1250
      },
      "timestamp_utc": "2025-10-22 15:30:00 UTC"
    }
  ]
}

// response (bulk entries)
{
  "ok": true,
  "written_count": 3,
  "failed_count": 0,
  "written_lines": [
    "[✅] [2025-10-24 10:45:00 UTC] [Agent: Scribe] [Project: My Project] First task completed",
    "[🐞] [2025-10-24 10:45:01 UTC] [Agent: DebugBot] [Project: My Project] Bug found in auth module",
    "[ℹ️] [2025-10-22 15:30:00 UTC] [Agent: MigrationBot] [Project: My Project] Database migration finished | component=database; phase=deployment; records_affected=1250"
  ],
  "failed_items": [],
  "path": "/abs/.../PROGRESS_LOG.md"
}
```

#### Multi-log routing (`log_type`)
- Pass `log_type="doc_updates"` (or any key from `config/log_config.json`) to route entries into custom logs like `DOC_LOG.md`.
- Each log can enforce metadata (e.g., `doc`, `section`, `action` for doc updates). Missing required fields will reject the entry.
- Default config ships with `progress`, `doc_updates`, `security`, and `bugs`. Add more under `config/log_config.json` with placeholders such as `{docs_dir}` or `{project_slug}` for path templates.
- CLI (`scripts/scribe.py`) also accepts `--log doc_updates` to stay consistent with MCP usage.

### 4. `manage_docs` – Structured doc updates
- **Purpose**: Safely edit `ARCHITECTURE_GUIDE`, `PHASE_PLAN`, `CHECKLIST`, etc., with audit metadata and automatic logging.
- **Args**:
  - `action`: `append`, `replace_section`, `apply_patch`, `replace_range`, or `status_update`.
  - `doc`: `architecture`, `phase_plan`, `checklist`, or custom template key.
  - `section`: Required for section/status operations; matches anchors like `<!-- ID: problem_statement -->`.
  - `content` or `template`: Provide raw Markdown or reference a fragment under `docs/dev_plans/1_templates/fragments/`.
  - `metadata`: Optional context (e.g., `{"status": "done", "proof": "PROGRESS_LOG#..."}`).
  - `dry_run`: Preview diff without writing.
- **Behavior**:
  - Edits are persisted atomically, recorded in the new `doc_changes` table, and auto-logged via `append_entry(log_type="doc_updates")`.
  - Checklist status updates flip `[ ]` ↔ `[x]` and can attach proof links automatically.

#### Choosing the Correct manage_docs Action
- **replace_section**
  - Use only for initial scaffolding or template setup.
  - If scaffolding, set `metadata={"scaffold": true}` to reduce false reminders.
- **apply_patch** (preferred for edits)
  - Structured mode is default: provide `edit` payloads (intent-based).
  - Unified diffs are compiler output only; set `patch_mode="unified"` explicitly.
  - Use `patch_source_hash` to enforce stale-source detection when available.
- **replace_range**
  - Replace explicit 1-based line ranges when you already have the line numbers.

Rule of thumb: scaffold with `replace_section`, then switch immediately to `apply_patch` or `replace_range` for edits.

### 5. `list_projects`
Discover configured or recently used projects.
```json
// request
{ "roots": ["/abs/path/to/repos"], "limit": 500 }

// response
{
  "ok": true,
  "projects": [
    {
      "name": "IMPLEMENTATION TESTING",
      "root": "/abs/path/to/repo",
      "progress_log": "/abs/.../PROGRESS_LOG.md",
      "docs": { "architecture": "...", "phase_plan": "...", "checklist": "...", "progress_log": "..." }
    }
  ]
}
```

### 6. `read_recent` - **Recent Log Entries**
**Purpose**: Tail the log via MCP instead of opening files by hand
**Usage**: `read_recent([n, filter])`
**⚠️ NOTE**: n parameter currently has type issues, returns all recent entries
```json
// Basic request (recommended)
{}

// With filtering (when n parameter fixed)
{
  "n": 50,
  "filter": { "status": "error", "agent": "Scribe" }
}

// response
{
  "ok": true,
  "entries": [
    {
      "id": "uuid",
      "ts": "2025-10-22 10:21:14 UTC",
      "emoji": "ℹ️",
      "agent": "Scribe",
      "message": "Describe the work or finding",
      "meta": { "phase": "bootstrap" },
      "raw_line": "[ℹ️] [2025-10-22 10:21:14 UTC] [Agent: Scribe] [Project: My Project] Describe the work or finding"
    }
  ]
}
```

### 7. `rotate_log`
Archive the current log and create a fresh file.
```json
// request
{ "suffix": "2025-10-22" }

// response
{ "ok": true, "archived_to": "/abs/.../PROGRESS_LOG.md.2025-10-22.md" }
```

### 8. `db.persist_entry` *(optional)*
Mirror a freshly written line into Postgres when configured.
```json
// request
{
  "line": "[2025-10-22 ...] ...",
  "project": "IMPLEMENTATION TESTING",
  "sha256": "abc123"
}

// response
{ "ok": true, "id": "uuid" }
```

### 9. `db.query` *(optional)*
Run predefined parameterized queries against the Scribe database.
```json
// request
{
  "query_name": "recent_failures",
  "params": { "project": "IMPLEMENTATION TESTING", "since_hours": 24 }
}

// response
{ "ok": true, "rows": [ { "ts": "2025-10-22 09:10:03 UTC", "agent": "Scribe", "message": "..." } ] }
```

### 10. `query_entries` - **Advanced Log Search**
**Purpose**: Advanced searching and filtering of progress log entries
**Usage**: `query_entries([project, start, end, message, message_mode, case_sensitive])`
```json
// Search by message content
{
  "message": "bug",
  "message_mode": "substring"
}

// Search by date range
{
  "start": "2025-10-23",
  "end": "2025-10-24"
}

// Search specific project
{
  "project": "My Project",
  "message": "migration",
  "case_sensitive": false
}

// response
{
  "ok": true,
  "entries": [
    {
      "id": "uuid",
      "ts": "2025-10-23 15:30:00 UTC",
      "emoji": "🗄️",
      "agent": "MigrationBot",
      "message": "Completed database migration",
      "meta": { "phase": "deployment", "component": "database" },
      "raw_line": "[🗄️] [...]"
    }
  ]
}
```

### 11. `generate_doc_templates` - **Documentation Scaffolding**
**Purpose**: Create/update documentation templates for a project
**Usage**: `generate_doc_templates(project_name, [author, overwrite, documents, base_dir])`
```json
// Basic request
{
  "project_name": "My New Project",
  "author": "MyAgent"
}

// Select specific documents
{
  "project_name": "My Project",
  "documents": ["architecture", "phase_plan"],
  "overwrite": true
}

// response
{
  "ok": true,
  "files": [
    "/abs/.../ARCHITECTURE_GUIDE.md",
    "/abs/.../PHASE_PLAN.md",
    "/abs/.../CHECKLIST.md",
    "/abs/.../PROGRESS_LOG.md"
  ],
  "skipped": [],
  "directory": "/abs/.../docs/dev_plans/my_new_project"
}
```

## 🧾 Tool Argument Cheat Sheet (Runtime Signatures)

This table summarizes the **actual MCP parameters** Scribe tools accept at runtime. Use this when constructing payloads or when validating third‑party integrations.

- `set_project(name, root=None, progress_log=None, author=None, overwrite_docs=False, defaults=None)`
- `get_project()`
- `delete_project(name, mode="archive", confirm=False, force=False, archive_path=None, agent_id=None)`
- `append_entry(message="", status=None, emoji=None, agent=None, meta=None, timestamp_utc=None, items=None, items_list=None, auto_split=True, split_delimiter="\n", stagger_seconds=1, agent_id=None, log_type="progress", config=None)`
- `read_recent(project=None, n=None, limit=None, filter=None, page=1, page_size=50, compact=False, fields=None, include_metadata=True)`
- `query_entries(project=None, start=None, end=None, message=None, message_mode=None, case_sensitive=False, emoji=None, status=None, agents=None, meta_filters=None, limit=None, page=1, page_size=50, compact=False, fields=None, include_metadata=True, search_scope=None, document_types=None, include_outdated=False, verify_code_references=False, time_range=None, relevance_threshold=None, max_results=None, config=None)`
- `manage_docs(action, doc, section=None, content=None, template=None, metadata=None, dry_run=False, doc_name=None, target_dir=None)`
- `list_projects(limit=5, filter=None, compact=False, fields=None, include_test=False, page=1, page_size=None, status=None, tags=None, order_by=None, direction="desc")`
- `generate_doc_templates(project_name, author=None, overwrite=False, documents=None, base_dir=None)`
- `rotate_log(suffix=None, custom_metadata=None, confirm=False, dry_run=False, dry_run_mode="estimate", log_type=None, log_types=None, rotate_all=False, auto_threshold=False, threshold_entries=None, config=None)`
- `vector_search(project=None, query="", limit=None)`

Registry-aware behavior:
- `set_project` → ensures `scribe_projects` row and dev_plan rows for core docs; updates `last_access_at`.
- `append_entry` (progress logs) → updates `last_entry_at` and may auto‑promote `status` from `planning`→`in_progress` when core docs + first entry exist.
- `manage_docs` → updates `meta.docs` in the registry with baseline/current hashes and doc‑hygiene flags.
- `list_projects` → surfaces `meta.activity` (age, recency, staleness_level, activity_score) and `meta.docs.flags` (e.g., `docs_ready_for_work`, `doc_drift_suspected`).

## 🛠️ CLI Companion (Optional)
`python scripts/scribe.py` mirrors a subset of MCP tools for shell workflows:
- `--list-projects`
- `--project <name>` or `--config <path>`
- `append "Message" --status success --meta key=value`
- `read --n 20`
- `rotate --suffix YYYY-MM-DD`

Always prefer MCP tool calls from agents; the CLI is for human operators and batch jobs.
---

## 🗂️ Dev Plan Document Suite
Each project under `.scribe/docs/dev_plans/<slug>/` maintains four synchronized files. Scribe bootstraps them during `set_project`; agents keep them current.

- `ARCHITECTURE_GUIDE.md` - Canonical blueprint. Explain the problem, goals, constraints, system design, data flow, and current directory tree. Update immediately when structure or intent changes.
- `PHASE_PLAN.md` - Roadmap derived from the architecture. Enumerate phases with objectives, tasks, owners, acceptance criteria, and confidence. Keep it aligned with reality.
- `CHECKLIST.md` - Verification ledger mirroring the phase plan. Each box must link to proof (commit, PR, screenshot, or Scribe entry). Do not invent tasks here.
- `PROGRESS_LOG.md` - Append-only audit trail written **only** through `append_entry`. Include `meta` keys like `phase=`, `checklist_id=`, `tests=` for traceability. Rotate periodically (~200 entries) using `rotate_log`.

**Workflow Loop**
1. `set_project` -> confirm docs exist.
2. Fill `ARCHITECTURE_GUIDE.md`, then `PHASE_PLAN.md`, then `CHECKLIST.md`.
3. Work in small, logged increments. `append_entry` after every meaningful action or insight.
4. When plans shift, update the docs first, then log the change.
5. Treat missing or stale documentation as a blocker - fix before coding further.

---

## 🔒 Operating Principles
- Always append; never rewrite logs manually.
- Timestamps are UTC; emoji is mandatory.
- Scribe reminders about stale docs or missing logs are blocking alerts.
- Default storage is local SQLite; Postgres and GitHub bridges require explicit env configuration.
- No autonomous prose generation - Scribe stays deterministic and fast.

> **Repeat:** Append entries religiously. If there is no Scribe line, reviewers assume it never happened.
