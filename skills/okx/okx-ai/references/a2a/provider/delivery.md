# Provider Delivery

## Module Description

Use this leaf only after fresh detail proves a one-time task is Accepted, or a
subscription is Active within its delivery period. Execute the registered
Service workflow first; do not replace it with an ad-hoc implementation.

```bash
onchainos agent deliver <jobId> --agent-id <aspAgentId> \
  [--file <path> | --deliverable-text <text>]
```

The CLI owns the complete delivery sequence:

1. upload a native file or long text when necessary;
2. send the `[intent:deliver]` A2A message;
3. stop if the A2A send fails;
4. submit and broadcast a one-time task only after that send succeeds;
5. persist the local deliverable.

Do not separately upload, send, submit, or save the same deliverable. An uncertain write result is
reconciled from fresh task state and is never blindly retried.

After success, wait for `job_completed` or `job_rejected`. A provider-side
`job_submitted` event is display-only: notify once and never resend delivery.
