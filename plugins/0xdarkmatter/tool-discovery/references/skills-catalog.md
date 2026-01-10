# Skills Catalog

Complete reference for all available skills.

## Pattern Skills

Quick reference for common patterns and syntax.

### rest-patterns

**Triggers:** rest api, http methods, status codes, api design, endpoint design

**Use For:**
- HTTP method semantics (GET, POST, PUT, PATCH, DELETE)
- Status code selection
- API versioning strategies
- Caching and rate limiting
- Error response formats

**References:** status-codes.md, caching-patterns.md, rate-limiting.md, response-formats.md

---

### sql-patterns

**Triggers:** sql patterns, cte example, window functions, sql join, index strategy

**Use For:**
- CTE (Common Table Expressions)
- Window functions (ROW_NUMBER, LAG, running totals)
- JOIN reference
- Pagination patterns
- Index strategies

**References:** window-functions.md, indexing-strategies.md

---

### tailwind-patterns

**Triggers:** tailwind, utility classes, responsive design, tailwind config, dark mode

**Use For:**
- Responsive breakpoints
- Layout patterns (flex, grid)
- Component patterns (cards, forms, navbars)
- Dark mode configuration
- State modifiers

**References:** component-patterns.md

---

### sqlite-ops

**Triggers:** sqlite, sqlite3, aiosqlite, local database, database schema

**Use For:**
- Schema design patterns (state, cache, events)
- Python sqlite3 usage
- Async operations with aiosqlite
- WAL mode configuration
- Migration patterns

**References:** schema-patterns.md, async-patterns.md, migration-patterns.md

---

### mcp-patterns

**Triggers:** mcp server, model context protocol, tool handlers

**Use For:**
- MCP server structure
- Tool handler patterns
- Resource configuration
- Protocol implementation

**References:** server-patterns.md, tool-handlers.md, resources.md

---

## CLI Tool Skills

Modern command-line tools for development workflows.

### file-search

**Triggers:** fd, ripgrep, rg, find files, search code, fzf, fuzzy find

**Use For:**
- Finding files by name (fd)
- Searching file contents (rg)
- Interactive selection (fzf)
- Combined workflows

**References:** advanced-workflows.md

---

### find-replace

**Triggers:** sd, find replace, batch replace, string replacement

**Use For:**
- Modern find-and-replace with sd
- Regex patterns
- Batch operations
- Preview before applying

**References:** advanced-patterns.md

---

### code-stats

**Triggers:** tokei, difft, line counts, code statistics, semantic diff

**Use For:**
- Codebase statistics (tokei)
- Semantic diffs (difft)
- Language breakdown
- Before/after comparisons

**References:** tokei-advanced.md, difft-advanced.md

---

### data-processing

**Triggers:** jq, yq, json, yaml, toml

**Use For:**
- JSON processing and transformation
- YAML/TOML operations
- Structured data queries
- Config file manipulation

**References:** jq-patterns.md, yq-patterns.md, shell-integration.md

---

### structural-search

**Triggers:** ast-grep, sg, ast pattern, find function calls, semantic search

**Use For:**
- Search by AST structure
- Pattern matching in code
- Refactoring operations
- Security scans

**References:** js-ts-patterns.md, python-patterns.md, go-rust-patterns.md, security-patterns.md, advanced-usage.md

---

## Workflow Skills

Project and development workflow automation.

### git-workflow

**Triggers:** lazygit, gh, delta, pr, rebase, stash, bisect

**Use For:**
- Interactive git operations (lazygit)
- GitHub CLI (gh) commands
- Syntax-highlighted diffs (delta)
- Rebase and stash patterns
- Bug hunting with bisect

**References:** rebase-patterns.md, stash-patterns.md, advanced-git.md

---

### python-env

**Triggers:** uv, venv, pip, pyproject, python environment

**Use For:**
- Fast environment setup with uv
- Virtual environment creation
- Dependency management
- pyproject.toml configuration

**References:** pyproject-patterns.md, dependency-management.md

---

### task-runner

**Triggers:** just, justfile, run tests, build project, list tasks

**Use For:**
- Project task execution
- Justfile configuration
- Common development commands

---

### doc-scanner

**Triggers:** AGENTS.md, conventions, scan docs, project documentation

**Use For:**
- Finding project documentation
- Synthesizing AI agent instructions
- Consolidating multiple doc files
- Creating AGENTS.md

**References:** file-patterns.md, templates.md

---

### project-planner

**Triggers:** plan, sync plan, track, project planning

**Use For:**
- Session state with /save and /sync
- Progress tracking
- Context preservation

---

## Selection Guide

### By File Type

| Working With | Skill |
|--------------|-------|
| JSON files | data-processing |
| YAML/TOML | data-processing |
| SQL databases | sql-patterns, sqlite-ops |
| TypeScript/JS | file-search, structural-search |
| Python | python-env, structural-search |
| API endpoints | rest-patterns |
| CSS/Tailwind | tailwind-patterns |

### By Task

| Task | Skill |
|------|-------|
| Find files by name | file-search |
| Search code content | file-search |
| Replace across files | find-replace |
| Count lines of code | code-stats |
| Compare code changes | code-stats |
| Process JSON/YAML | data-processing |
| Git operations | git-workflow |
| Set up Python project | python-env |
| Run project tasks | task-runner |
| Find project docs | doc-scanner |
| Plan implementation | project-planner |

### By Complexity

**Quick Lookups (< 1 min):**
- rest-patterns: Status code lookup
- sql-patterns: CTE syntax
- tailwind-patterns: Breakpoint reference
- file-search: Basic fd/rg commands

**Medium Tasks (1-5 min):**
- find-replace: Batch replacements
- data-processing: JSON transformations
- git-workflow: Rebase operations
- python-env: Project setup

**Complex Workflows (5+ min):**
- structural-search: Security scans
- doc-scanner: Documentation consolidation
- project-planner: Session planning

## When to Use Skills vs Agents

**Use a Skill when:**
- You need quick reference (syntax, patterns)
- Task is well-defined (replace X with Y)
- Looking up how to do something
- Executing a known workflow

**Use an Agent when:**
- Requires reasoning or decisions
- Complex problem-solving needed
- Multiple approaches to evaluate
- Architecture or optimization

**Example:**
- "What's the HTTP status for unauthorized?" → rest-patterns (skill)
- "Design authentication for my API" → python-expert or relevant framework agent
