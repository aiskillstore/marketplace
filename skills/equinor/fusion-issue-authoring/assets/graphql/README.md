# GraphQL fallback queries

These GraphQL documents are fallback helpers for environments where GitHub MCP write tools are unavailable or incomplete for parent/sub-issue and issue-type operations.

## Files

- `issue_lookup.github.graphql`: fetch issue id/type/parent/labels by issue number.
- `issue_types_list.github.graphql`: list organization issue types and ids.
- `issue_type_update.github.graphql`: set issue type by ids.
- `sub_issue_write.github.graphql`: add child issue to parent issue.
- `sub_issue_remove.github.graphql`: remove child issue from parent issue.
- `sub_issue_reprioritize.github.graphql`: reprioritize child issue order.
- `linkage_verify.github.graphql`: verify parent/child linkage and child type.

## Usage note

When running these files via `gh api graphql`, include:

- `-H "GraphQL-Features: issue_types,sub_issues"`

without this header, issue type and sub-issue fields may fail schema validation.

Prefer MCP tools first when available; use these files as explicit fallback.

## GraphQL cost awareness

GitHub GraphQL rate limits (https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api):

- **Primary budget**: 5,000 points/hour per user (10,000 for GitHub Enterprise Cloud). Each query costs at least 1 point; nested connections multiply.
- **Secondary limits**: mutations cost 5 points, read queries cost 1 point. Max 2,000 points/minute. Max 100 concurrent requests. Max 60 seconds GraphQL CPU time per 60 seconds real time.
- **Content creation cap**: max 80 content-generating requests/minute, 500/hour.
- **Timeouts**: requests exceeding 10 seconds are terminated and deduct additional points from the hourly budget.
- **Node limit**: max 500,000 nodes per call; `first`/`last` must be 1–100. Keep connection page sizes small (prefer `first: 10` or `first: 20` over `first: 100`) unless you need bulk data.

## Fallback guardrails

- Run only the minimum GraphQL file required for the current missing capability.
- Reuse ids returned from prior responses instead of repeating lookup queries.
- Do not execute retry loops for GraphQL failures.
- Pause at least 1 second between consecutive mutation calls.
- Keep `first`/`last` arguments small to reduce point cost and avoid timeouts.
- If rate limits are hit (`x-ratelimit-remaining: 0` or `retry-after` header present), stop optional fallback operations, respect the reset/retry-after window, and return a clear retry plan.
- Switch back to MCP tools immediately when equivalent MCP coverage is available.
