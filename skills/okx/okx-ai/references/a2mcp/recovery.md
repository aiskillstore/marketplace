# A2MCP Recovery

## Module Description

Use only the latest structured result. Never parse error text, reconstruct
routing data, or reuse opaque IDs from chat history.

| State | Handling |
|---|---|
| `endpoint_probe / invalid_a2mcp_routing` | Discard the active invocation, explain `payload.message` in plain language, and require fresh Service selection |
| `invocation_recovery / {a2mcp_prepared_expired_or_missing, a2mcp_candidate_invalid_or_missing, a2mcp_free_result_expired_or_missing, a2mcp_funding_continuation_required}` | Discard the invocation, explain the failure, and require fresh Service selection |

Never expose reason codes, action IDs, or opaque IDs. A blocked recovery is
terminal: clear the active invocation and run no further CLI command.
