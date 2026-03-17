---
name: opencontext
description: Persistent memory and context management for AI agents using OpenContext. Keep context across sessions/repos/dates, store conclusions, and provide document search workflows.
allowed-tools: Read Write Bash Grep Glob
metadata:
  tags: opencontext, context-management, memory, knowledge-base, multi-agent
  platforms: Claude, Gemini, ChatGPT, Codex, Cursor
  version: 1.0.0
  source: OpenContext Multi-Agent Workflow Guide
---


# OpenContext Context Management (Persistent Memory)

> Give your AI assistant persistent memory.
> Stop repeating explanations, and build smarter.

## When to use this skill

- When you need to keep context across sessions
- When you need to record project background/decisions
- When you need to search prior conclusions/lessons
- When you need knowledge sharing in a Multi-Agent workflow
- When you want to reduce repetitive background explanations

---

## 1. Core concepts

### Problem
When working with an AI assistant, context gets lost (across sessions, repos, and dates). You end up repeating background, re-explaining decisions, and sometimes the assistant continues with incorrect assumptions.

### Solution
**OpenContext** is a lightweight personal context/knowledge store for AI assistants.

```
[Load context] → [Do work] → [Store conclusions]
```

### Default paths
| Item | Path |
|------|------|
| **Contexts** | `~/.opencontext/contexts` |
| **Database** | `~/.opencontext/opencontext.db` |

---

## 2. Install and initialize

### Install CLI
```bash
npm install -g @aicontextlab/cli
# Or use npx
npx @aicontextlab/cli <command>
```

### Initialize (run inside the repo)
```bash
cd your-project
oc init
```

**What `oc init` does:**
- Prepare the global context store (on first run)
- Generate user-level commands/skills + mcp.json for the selected tool
- Update the repo's AGENTS.md

---

## 3. Slash Commands

### Beginner-friendly commands

| Command | Purpose |
|---------|------|
| `/opencontext-help` | When you don't know where to start |
| `/opencontext-context` | **(Recommended default)** Load background before work |
| `/opencontext-search` | Search existing documents |
| `/opencontext-create` | Create a new document/idea |
| `/opencontext-iterate` | Store conclusions and citations |

### Install locations
```
# Slash Commands
Cursor:      ~/.cursor/commands
Claude Code: ~/.claude/commands

# Skills
Cursor:      ~/.cursor/skills/opencontext-*/SKILL.md
Claude Code: ~/.claude/skills/opencontext-*/SKILL.md
Codex:       ~/.codex/skills/opencontext-*/SKILL.md

# MCP Config
Cursor:      ~/.cursor/mcp.json
Claude Code: ~/.claude/mcp.json
```

---

## 4. Core CLI commands

### Folder/document management
```bash
# List folders
oc folder ls --all

# Create folder
oc folder create project-a -d "My project"

# Create document
oc doc create project-a design.md -d "Design doc"

# List documents
oc doc ls project-a
```

### Search & manifest
```bash
# Search (keyword/hybrid/vector)
oc search "your query" --mode keyword --format json

# Generate a manifest (list of files the AI should read)
oc context manifest project-a --limit 10
```

### Search modes
| Mode | Description | Requirements |
|------|------|----------|
| `--mode keyword` | Keyword-based search | No embeddings required |
| `--mode vector` | Vector search | Embeddings + index required |
| `--mode hybrid` | Hybrid (default) | Embeddings + index required |

### Embedding configuration (for semantic search)
```bash
# Set API key
oc config set EMBEDDING_API_KEY "<<your_key>>"

# (Optional) Set base URL
oc config set EMBEDDING_API_BASE "https://api.openai.com/v1"

# (Optional) Set model
oc config set EMBEDDING_MODEL "text-embedding-3-small"

# Build index
oc index build
```

---

## 5. MCP Tools

### OpenContext MCP Tools
```bash
oc_list_folders    # List folders
oc_list_docs       # List documents
oc_manifest        # Generate manifest
oc_search          # Search documents
oc_create_doc      # Create document
oc_get_link        # Generate stable link
```

### Multi-Agent integration
```bash
# Gemini: large-scale analysis
ask-gemini "Analyze the structure of the entire codebase"

# Codex: run commands
shell "docker-compose up -d"

# OpenContext: store results
oc doc create project-a conclusions.md -d "Analysis conclusions"
```

---

## 6. Multi-Agent workflow integration

### Orchestration Pattern
```
[Claude] Plan
    ↓
[Gemini] Analysis/research + OpenContext search
    ↓
[Claude] Write code
    ↓
[Codex] Run/test
    ↓
[Claude] Synthesize results + store in OpenContext
```

### Practical example: API design + implementation + testing
```bash
# 1. [Claude] Design API spec using the skill
/opencontext-context   # Load project background

# 2. [Gemini] Analyze a large codebase
ask-gemini "@src/ Analyze existing API patterns"

# 3. [Claude] Implement code based on the analysis
# (Use context loaded from OpenContext)

# 4. [Codex] Test and build
shell "npm test && npm run build"

# 5. [Claude] Create final report + store conclusions
/opencontext-iterate   # Store decisions and lessons learned
```

---

## 7. Recommended daily workflow

### Before work (1 min)
```bash
/opencontext-context
```
- Load project background + known pitfalls

### During work
```bash
/opencontext-search
```
- Search existing conclusions when unsure

### After work (2 min)
```bash
/opencontext-iterate
```
- Record decisions, pitfalls, and next steps

### High-ROI document types
- **Acceptance Criteria** - acceptance criteria
- **Common Pitfalls** - common pitfalls
- **API Contracts** - API contracts
- **Dependency Versions** - dependency versions

---

## 8. Stable links (Stable Links)

Keep links stable across renames/moves by referencing document IDs:

```markdown
[label](oc://doc/<stable_id>)
```

### Generate a link via CLI
```bash
oc doc link <doc_path>
```

### Generate a link via MCP
```bash
oc_get_link doc_path="Product/api-spec"
```

---

## 9. Desktop App & Web UI

### Desktop App (recommended)
- Manage/search/edit context with a native UI
- Use without the CLI
- Automatic index builds (in the background)

**Citation features:**
| Action | How | Result |
|------|------|------|
| Cite text snippet | Select text → right-click → "Copy Citation" | Agent reads the snippet + source |
| Cite document | Click the citation icon next to the document title | Agent reads the full document + obtains stable_id |
| Cite folder | Right-click folder → "Copy Folder Citation" | Agent bulk-reads all docs in the folder |

### Web UI
```bash
oc ui
# Default URL: http://127.0.0.1:4321
```

---

## Quick Reference

### Essential workflow
```
Before: /opencontext-context (load background)
During: /opencontext-search (search)
After: /opencontext-iterate (store)
```

### Core CLI commands
```bash
oc init              # Initialize project
oc folder ls --all   # List folders
oc doc ls <folder>   # List documents
oc search "query"    # Search
oc doc create ...    # Create document
```

### MCP Tools
```
oc_list_folders  list folders
oc_list_docs     list documents
oc_search        search
oc_manifest      manifest
oc_create_doc    create document
oc_get_link      generate link
```

### Paths
```
~/.opencontext/contexts      context store
~/.opencontext/opencontext.db  database
```

---

## References

- [OpenContext Website](https://0xranx.github.io/OpenContext/en/)
- [Usage Guide](https://0xranx.github.io/OpenContext/en/usage/)
- [Download Desktop](https://github.com/0xranx/OpenContext/releases)
- [GitHub Repository](https://github.com/0xranx/OpenContext)
