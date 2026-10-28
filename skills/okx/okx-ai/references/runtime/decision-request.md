# Durable User Decision Request

## Module Description

Use this leaf when a task sub-session must request a User decision. Construct
one request from authoritative action parameters:

```text
onchainos agent pending-decisions-v2 request \
  --job-id <jobId> --role <role> --agent-id <agentId> \
  [--to-agent-id <peerAgentId>] \
  --source-event <sourceEvent> \
  --user-content "<localized card>" \
  --list-label "<localized short label>"
```

For structured choices and a durable decision ID, use the returned
`request-prompt` shape specified by the owning leaf. Preserve exact action IDs,
parameters, Job ID, Agent IDs, expiry, and binding keys. A successful request
ends the sub-session turn; it does not authorize the action being offered.

CLI/runtime failure cards use the same durable mechanism and the canonical
recovery content from [`recovery.md`](recovery.md). Never send technical error
details to the task peer.
