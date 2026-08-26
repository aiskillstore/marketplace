# GitHub MCP server reference

GitHub MCP tools and payload examples. Server: https://github.com/github/github-mcp-server

## Preferred tools

- `mcp_github::issue_write` — create/update issues
- `mcp_github::search_issues` — duplicates/context search
- `mcp_github::sub_issue_write` — add/remove/reprioritize sub-issues
- `mcp_github::search_users` — assignment candidates
- `mcp_github::add_issue_comment` — add comment
- `mcp_github::list_issue_types` — list issue types

## High-cost paths and mitigation

Expensive: repeated label lookups, repeated assignee searches, repeated `list_issue_types`, broad duplicate searches, second-pass updates for labels/assignees, GraphQL retry loops.

Mitigation:
- cache labels per `owner/repo` for session
- cache assignee candidates per `owner/repo+query` for session
- cache issue types per owner for session
- one focused duplicate search
- full payload in first `issue_write`
- GraphQL fallback only when MCP missing, no retry loops

## MCP readiness check

1. Try `mcp_github::search_issues` with lightweight query in target repo
2. Succeeds → MCP ready
3. Fails → run install-assist

## Install assist (VS Code)

1. Ensure VS Code supports remote MCP
2. Add to MCP config:

```json
{
  "servers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/"
    }
  }
}
```

3. Open Copilot Chat Agent mode, complete OAuth if prompted
4. Re-run readiness probe

No remote MCP available: use local server setup from GitHub MCP server README.

## Blocking dependency note

No dedicated blocking/blocked links tool. Use `mcp_github::sub_issue_write` for execution order; `mcp_github::add_issue_comment` or body text for blocker context.

## `type` parameter rule

Optional. Get valid values with `mcp_github::list_issue_types`. Send only when repo has issue types configured; omit otherwise.

## Label caching

Never one point lookup per label.

1. First label request for `owner/repo`: bulk fetch, cache for session
   - prefer `/memories/session/<owner>-<repo>-labels.json`
   - fallback: `.tmp/issue-authoring-labels-<owner>-<repo>.json` (never committed)
2. Cache hit: filter locally, send surviving set in first `issue_write`
3. Only point lookups + no cache: ask to skip optional labels or use user-confirmed only; no per-label loop
4. Refresh cache only on repo change or explicit user request

## Assignee caching

Never repeat same lookup per session.

1. `@me` or exact login → skip `mcp_github::search_users`
2. Lookup needed: cache by `owner/repo+query`
   - prefer `/memories/session/<owner>-<repo>-assignee-candidates.json` or `<owner>-assignee-candidates.json`
   - fallback: `.tmp/issue-authoring-assignee-candidates-<owner>-<repo>.json` (never committed)
3. Contributors/members available: hydrate cache once, reuse; otherwise reuse first `search_users` result
4. Rate limits block enrichment: ask to continue unassigned or with `@me`

## Issue type caching

Never call `mcp_github::list_issue_types` every request.

1. In-session cache: `owner → [types]`
2. Cache hit: validate locally. Cache miss: call, then cache
3. `issue_write` fails on `type` → mark owner `types_unsupported` for session, omit `type`

Optional: `.tmp/issue-type-cache.json` (never committed)
- refresh when owner changes or validation fails.

## Duplicate search minimization

- Prefer one focused query that combines key title terms and repository scope.
- Reuse the same duplicate search result set throughout draft review unless the problem statement changes.
- Avoid broad repeated searches after mutation failures; resolve auth/config first.

## Example props

### Create a Task issue

Only include `type` when issue types are supported.

```json
{
  "method": "create",
  "owner": "equinor",
  "repo": "fusion-skills",
  "title": "task: migrate issue-authoring flows to MCP",
  "body": "## Objective\nMove issue authoring from scripts to MCP-based operations.",
  "type": "Task",
  "assignees": ["odinr"]
}
```

### Update an issue and set type

Only include `type` when issue types are supported.

```json
{
  "method": "update",
  "owner": "equinor",
  "repo": "fusion-skills",
  "issue_number": 21,
  "type": "Task",
  "body": "Updated body with latest scope and checklist."
}
```

### Add a sub-issue to a parent issue

> **`sub_issue_id` is the GitHub object ID, NOT the issue number.**
>
> | Format | Example | Used in URLs / UI? |
> |---|---|---|
> | Issue number | `#79`, `79` | Yes |
> | Object ID | `3969391411` | No — internal only |
>
> **Always retrieve the object ID before calling `sub_issue_write`.**
>
> ```bash
> # Get the object ID for a sub-issue by its number
> gh api repos/OWNER/REPO/issues/NUMBER -q '.id'
> # Example: gh api repos/equinor/fusion-skills/issues/79 -q '.id'
> # Output: 3969391411
> ```

```json
{
  "method": "add",
  "owner": "equinor",
  "repo": "fusion-skills",
  "issue_number": 21,
  "sub_issue_id": 3969391411
}
```

#### Troubleshooting sub-issue linking

| Symptom | Likely cause | Fix |
|---|---|---|
| 404 error | Used issue number instead of object ID | Run `gh api repos/OWNER/REPO/issues/NUMBER -q '.id'` to get the correct ID |
| "Invalid input" error | `sub_issue_id` missing or wrong format | Confirm value is a numeric ID (e.g. `3969391411`), not a string or `#79` |
| Sub-issue not added silently | Parent issue or sub-issue does not exist, or insufficient permissions | Verify both issues exist and the token has write access |

### Reprioritize sub-issues

```json
{
  "method": "reprioritize",
  "owner": "equinor",
  "repo": "fusion-skills",
  "issue_number": 21,
  "sub_issue_id": 3969391411,
  "after_id": 3969391300
}
```

Use either `after_id` or `before_id` for reprioritization. Both `sub_issue_id` and `after_id`/`before_id` are object IDs, not issue numbers.

## Minimal task-batch order

1. `mcp_github::issue_write` create/update with full known fields (`title`, `body`, `labels`, `assignees`, optional `type`) using cache-backed label/assignee data when available
2. Optional single follow-up `mcp_github::issue_write` only for fields that were unavailable in step 1
3. `mcp_github::sub_issue_write` add/reprioritize children in execution order only when linkage changed
4. Optional: `mcp_github::add_issue_comment` to record blocker context when requested

## Rate-limit fallback behavior

GitHub GraphQL limits (summary from https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api):

| Limit | Value |
|---|---|
| Primary budget | 5,000 pts/hour per user (1,000 for `GITHUB_TOKEN` in Actions) |
| Mutation secondary cost | 5 pts per GraphQL mutation, 1 pt per read query |
| Secondary throughput | max 2,000 pts/minute; max 80 content-creating requests/minute |
| Concurrency | max 100 concurrent requests (shared REST + GraphQL) |
| Timeout | 10 s per request; timeout deducts extra points |

Behavior when limits are approached or hit:

- Check `x-ratelimit-remaining` and `retry-after` headers; respect the reset window.
- Stop optional label/assignee enrichments and avoid automatic retry loops.
- Pause at least 1 second between consecutive mutation calls.
- Preserve draft state and return a clear retry sequence to the user.
- Prefer MCP calls over ad hoc GraphQL retries when equivalent MCP tools are available.
- Never retry a request that returned a secondary rate-limit error without waiting for the `retry-after` period.

### Per-session budget estimate

A typical multi-issue authoring session with cache-first behavior:

| Activity | Calls (with caching) | Calls (without caching) |
|---|---|---|
| Label set fetch per repo | 1 | N × L (N issues × L labels each) |
| Issue-type lookup per org | 1 | N |
| Duplicate search per issue | N | N |
| Assignee lookup per session | 0–1 | N |
| Issue create/update | N | N |
| Sub-issue link | 0–N | 0–N |
| **Total for 3 issues, 3 labels each** | **~10** | **~25+** |

Stay under ~30 MCP calls per session for a typical 3-issue run. If the running total approaches this threshold, stop optional enrichment (extra label checks, assignee searches, duplicate re-scans) and proceed with the data already cached.
