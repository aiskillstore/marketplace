# Issue authoring guidance

Goal: fast, clear GitHub issues. Draft-first, safe mutation order.

## Core rules

- Drafts concise, outcome-focused
- Full issue refs (`owner/repo#123`)
- Never mutate before explicit publish confirmation
- Ask only essential clarifying questions
- Resolve repo and labels before mutation
- MCP tools first; avoid ad hoc GitHub API/GraphQL retries when MCP equivalent exists

## Low-token strategy

- Fetch context once, reuse
- One focused duplicate check; no repeated broad searches
- Labels: query only when needed; cache repo label set, filter locally
- Skip assignee-candidate lookups on `@me` or exact login; cache ambiguous results
- Cache issue types per org; skip repeated `list_issue_types` on cache hit
- Sub-issue mutations only for changed relationships
- Rate limits hit: stop optional lookups, return retry plan

## Repository routing

Repo-specific. No explicit repo given: read workspace `CONTRIBUTING.md` and `contribute/` docs, apply routing rules. See SKILL.md Step 2. Never hardcode destinations.

## Workflow

1. Classify (`Bug`, `Feature`, `User Story`, `Task`)
2. Resolve destination repo (apply contributor guide routing)
3. Check template: repo first (`.github/ISSUE_TEMPLATE/`), then specialist fallback
4. Duplicate check via `mcp_github::search_issues`
5. Draft in `.tmp/{TYPE}-{CONTEXT}.md`
6. Review with user, apply edits
7. Explicit publish confirmation
8. Mutate via MCP in order:
	- `mcp_github::issue_write` — full known payload (labels/assignees/type)
	- single follow-up `mcp_github::issue_write` only for fields unavailable in first call
	- `mcp_github::sub_issue_write` — only when ordering/links changed
	- `mcp_github::add_issue_comment` — only when requested

MCP failure handling:
- Mutation fails (missing MCP server/auth/config): explain failure, point to `references/mcp-server.md`, retry after user confirms setup

Type param rule:
- Use cached issue types; call `mcp_github::list_issue_types` only on cache miss
- Send `type` only when repo supports issue types; omit otherwise, mark owner unsupported for session

Rate-limit fallback:
- Surface failures clearly; no tight retry loops
- Respect `retry-after` and `x-ratelimit-reset` headers
- GraphQL mutations: 5 secondary-limit points each; minimize calls
- Pause ≥1s between consecutive GraphQL mutations
- Preserve `.tmp/` drafts and session cache; give user safe retry path

## Task mode

- Small, single-purpose tasks preferred
- Broad requests: suggest checklist first
- Bulk creation: include dependency order and blockers
- Issue type `Task` for all task decomposition

## Relationships

- Sub-issues for decomposition under parent objective
- Sub-issue ordering = prerequisites
- Stop and fix contradictory links before mutation

Quick check:
1. Start now? If no → later in sub-issue order, note blocker
2. Part of parent objective? If yes → add as sub-issue
3. Contradiction? If yes → correct before mutation

## Labels and assignees

- First label lookup for `owner/repo`: fetch label set once, write session cache
  - Prefer `/memories/session/{owner}-{repo}-labels.json`; fallback `.tmp/issue-authoring-labels-{owner}-{repo}.json`
- Later checks: filter from cache, no point lookups
- Only point lookups available + no cache: ask whether to skip optional labels or use user-confirmed labels only; no per-label loop
- Labels missing from cache: ask to proceed with available labels
- Ask assignee intent: `@me`, specific login, or unassigned
- `@me` or exact login → skip `mcp_github::search_users`
- Assignee search needed: cache by owner/repo+query
  - Prefer `/memories/session/{owner}-{repo}-assignee-candidates.json`; fallback `.tmp/issue-authoring-assignee-candidates-{owner}-{repo}.json`
- Contributors/members available: hydrate cache once, reuse; otherwise reuse first `search_users` result

## MCP reference

See `references/mcp-server.md` for server link, preferred tools, payload examples.

## Template fallbacks

- Feature: `assets/issue-templates/feature.md`
- User Story: `assets/issue-templates/user-story.md`
- Bug: `assets/issue-templates/bug.md`
- Task: `assets/issue-templates/task*.md`