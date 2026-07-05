# Agents Catalog

Complete reference for all available agents in the Task tool.

**Note:** Language and framework domains (Python, JavaScript, TypeScript, Go, Rust, React, Vue, Laravel, Astro, SQL, PostgreSQL) are covered by `-ops` skills, not agents — see `skills-catalog.md`. When subagent work is needed in those domains, dispatch `general-purpose` with an instruction to first read the relevant skill's SKILL.md and references (skill preloading).

**Skills-first domains:** Cloudflare/Workers, Cypress/E2E, shell scripting, AWS ECS/Fargate containers, and Claude Code extension work are now covered by `-ops` skills rather than dedicated agents:

| Former agent | Now use |
|--------------|---------|
| `cloudflare-expert`, `wrangler-expert` | `cloudflare-ops` skill |
| `cypress-expert` | `cypress-ops` skill |
| `bash-expert` | `bash-ops` skill |
| `aws-fargate-ecs-expert` | `container-orchestration` skill |
| `claude-architect` | `claude-code-ops` skill |
| `craftcms-expert` | `craftcms-ops` skill |
| `payloadcms-expert` | `payloadcms-ops` skill |
| `asus-router-expert` | `asus-router-ops` skill |

For these, invoke the skill directly, or dispatch `general-purpose` with an instruction to read the skill's SKILL.md first.

## Specialized Experts

### firecrawl-expert

**Triggers:** firecrawl, web scraping, crawl, anti-bot

**Capabilities:**
- Web scraping strategies
- Anti-bot bypass
- Dynamic content handling
- Structured data extraction
- API integration

**Best For:**
- Complex scraping tasks
- Blocked site access
- Data extraction pipelines
- Crawl architecture

---

### git-agent

**Triggers:** commit, push, PR, branch, rebase (dispatched by git-ops)

**Capabilities:**
- Background git write operations
- Commit and PR creation
- Branch and worktree management
- Safety-tiered execution

**Best For:**
- Dispatched git work from the git-ops skill
- Background commits and pushes

---

### project-organizer

**Triggers:** restructure, organize, cleanup, directory

**Capabilities:**
- Project structure analysis
- Directory reorganization
- Old file cleanup
- Git-aware operations
- Best practice structure

**Best For:**
- Project restructuring
- Codebase cleanup
- Structure standardization
- Tech debt reduction

---

## Built-in Agents

### Explore

**Triggers:** where is, find, locate, codebase search

**Capabilities:**
- Fast codebase exploration
- Pattern matching
- File discovery
- Quick answers

**Best For:**
- "Where is X defined?"
- "Find files matching Y"
- Quick codebase questions

---

### Plan

**Triggers:** plan, design, architect, strategy

**Capabilities:**
- Implementation planning
- Architecture design
- File identification
- Trade-off analysis

**Best For:**
- Feature planning
- Architectural decisions
- Implementation strategy

---

### general-purpose

**Triggers:** multi-step, complex, research

**Capabilities:**
- Autonomous research
- Multi-step tasks
- Code search
- Tool coordination

**Best For:**
- Complex investigations
- Open-ended research
- Multi-step operations

---

### claude-code-guide

**Triggers:** how to use claude code, can claude code, does claude code

**Capabilities:**
- Claude Code documentation
- Feature explanations
- Hook configuration
- MCP server setup
- Agent SDK guidance

**Best For:**
- Claude Code questions
- Configuration help
- Feature discovery
- SDK usage

---

## Selection Guide

| Need | First Try | Then Try |
|------|-----------|----------|
| "How to write X in Python" | python-* skill (e.g. python-pytest-ops) | general-purpose + skill preload |
| "Optimize this query" | postgres-ops skill | general-purpose + skill preload |
| "Find where X is defined" | Explore | general-purpose |
| "Plan feature implementation" | Plan | general-purpose |
| "Scrape this website" | firecrawl-expert | - |
| "Deploy to Cloudflare" | cloudflare-ops skill | general-purpose + skill preload |
| "Fix React performance" | react-ops skill | general-purpose + skill preload |
| "Write E2E tests" | cypress-ops skill | general-purpose + skill preload |
| "Restructure project" | project-organizer | - |
| "Go concurrency design" | go-ops skill | general-purpose + skill preload |
| "Rust lifetime issues" | rust-ops skill | general-purpose + skill preload |
| "Build a Claude Code skill" | claude-code-ops skill | general-purpose + skill preload |
