# LogBrew MCP map for debugging

The hosted LogBrew MCP server is at `https://mcp.logbrew.co/mcp`. It can only
read, and only the projects that the person approved when they connected.

## Connect

Claude Code:

```bash
claude mcp add --transport http logbrew https://mcp.logbrew.co/mcp
claude mcp login logbrew
```

Codex:

```bash
codex mcp add logbrew --url https://mcp.logbrew.co/mcp
codex mcp login logbrew
```

Other clients: add the URL as a remote (HTTP) MCP server. See
[Connect an AI agent with MCP](https://docs.logbrew.co/guides/mcp).

## Tools

The server has 2 tools:

- `search` finds read operations and returns the input and output schema of
  1 operation.
- `execute` runs 1 operation that `search` found.

Call `search` before the first `execute` of each operation. Use the input
fields from the returned schema. Omit an optional field; do not send `null`.
If `search` returns a newer version of an operation in this table, use the
newer version and check its schema.

## Operations by step

| Operation | Input fields | Step |
| --- | --- | --- |
| `issues.list.v5` | `project_id`, `environment`, `release`, `service_name`, `status`, `priority`, `since`, `until`, `limit` | 1. Find the failing issue. 7. Check the new release. |
| `issues.investigate.v15` | `issue_id`, `selection`, `occurrence_id` | 2. Stack, first-seen release, impact, trace link. `selection` is `recommended`, `first`, or `latest`. |
| `traces.investigate.v3` | `trace_id`, `project_id`, `environment`, `release` | 3. The trace of the failing request. |
| `logs.list.v1` | `project_id`, `trace_id`, `service_name`, `environment`, `release`, `severity`, `search`, `since`, `until`, `limit` | 3. Logs of the trace or of a time window. |
| `issues.owners.v2` | `issue_id` | 4. Suggested owners of the failing code. |
| `releases.list.v1` | `project_id`, `environment`, `service_name`, `since`, `until` | 2. Releases and their health around the first event. |
| `summary.volume.v1` | `project_id`, `since`, `until`, `environment`, `release`, `service_name`, `interval` | 7. Event counts before and after a deploy. |

## Read the result

- Each result has `data`, `error`, and `provenance`. An operation error
  returns no data. Follow its `next_action`.
- A list page is not the full population. Send the cursor fields that the
  schema names, such as `cursor_time` and `cursor_id`, from `next_cursor`.
  Keep the same filters on each page.
- To read a fixed window, send `since` and `until` together. `since` is
  inclusive and `until` is exclusive.
- A read of a project that was not approved returns `permission_denied`. Do
  not try another project.
- The MCP server cannot record deployments or change issue status. Use the
  CLI for those, with permission.
