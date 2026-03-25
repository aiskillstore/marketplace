# Ask GraphQL MCP Tools And Prompts

This reference is for agents using Ask GraphQL MCP to solve user questions on user-provided endpoints.

## Agent-first operating pattern

1. Read user goal and target endpoint.
2. Verify MCP connectivity (session tool or HTTP JSON-RPC).
3. Send natural-language task to MCP.
4. Send follow-up clarification to MCP only when needed.
5. Explain MCP result with assumptions.

## Transport fallback

If `graphql_agent` is unavailable in session tool list, call Ask MCP over HTTP JSON-RPC:

1. `tools/list` request to gateway URL
2. `tools/call` with `name=graphql_agent` and natural-language `question`

Required headers:
- `X-ENDPOINT`: user-provided GraphQL endpoint
- `X-ENDPOINT-AUTHORIZATION`: optional, for private upstream endpoint
- `X-API-KEY`: paid mode only

## Tool usage intent

Use Ask GraphQL MCP to:
- handle schema/query reasoning on MCP side
- answer analysis/debugging questions based on current schema

## Prompt pack: first-run

- `Check MCP connectivity for this endpoint and confirm available tools.`
- `Please inspect this endpoint and tell me what this project indexes.`
- `Confirm this endpoint is queryable and summarize available data domains.`
- `Run a basic analysis task and show the result format you can provide.`

## Prompt pack: analysis

- `Find the most active accounts by transaction count in the last 7 days. Show query and assumptions.`
- `Provide a query for daily volume trend and explain each selected field.`
- `Suggest three dashboard metrics and give exact queries for this schema.`

## Prompt pack: debugging

- `This query fails. Explain error cause and rewrite a compatible query.`
- `Check whether field <field_name> exists. If not, provide alternatives.`
- `Optimize this query for large datasets using cursor pagination.`

## Output standard

Prefer this output shape:
1. Assumptions
2. MCP answer summary
3. Optional query/details provided by MCP
4. Optional fallback or retry direction

## Mode-switch rule

- Start in free mode by default.
- Move to paid mode only when free-tier limit is hit or user requests paid.
