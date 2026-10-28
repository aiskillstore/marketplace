# ASP Evaluation Actions

## Module Description

Execute only the action returned by the latest bound refund-or-evaluation
decision.

| Action ID | Command |
|---|---|
| `agree_refund` | `onchainos agent agree-refund <params.jobId> --agent-id <aspAgentId>` |
| `raise_arbitration` | `onchainos agent dispute raise <params.jobId> --reason <params.reason> --agent-id <aspAgentId>` |
| `sub_agree_refund` | `onchainos agent subscribe-agree-refund <params.jobId> --agent-id <aspAgentId>` |
| `raise_subscription_arbitration` | `onchainos agent subscribe-dispute <params.jobId> --reason <params.reason> --agent-id <aspAgentId>` |

Both evaluation commands use one combined `approveAndCreateDispute`
transaction in the current conversation. Preserve the user-authored evaluation
reason verbatim.


## Flow
### Reason handoff

Before broadcasting, each command sends one task-scoped session message so the
later evidence event receives the same reason without machine persistence.

One-time task:

```text
[ARBITRATION_REASON_CONTEXT]
{"version":1,"intent":"arbitration_reason_context","taskType":"one_time","jobId":"<jobId>","providerAgentId":"<aspAgentId>","reason":"<exact reason>","reasonB64":"<URL-safe base64>","resumeEvent":"job_disputed"}
```

Subscription:

```text
[ARBITRATION_REASON_CONTEXT]
{"version":1,"intent":"arbitration_reason_context","taskType":"subscription","jobId":"<jobId>","providerAgentId":"<aspAgentId>","reason":"<exact reason>","reasonB64":"<URL-safe base64>","resumeEvent":"sub_asp_dispute"}
```

Match Job ID, ASP Agent ID, task type, and resume event before using the reason.
`job_disputed` and `sub_asp_dispute` continue through
[`evidence-upload.md`](evidence-upload.md). A `dispute_approved` compatibility
receipt has no write action.

After a successful command, state that the evaluation request was submitted
and that progress will update in the task. Display the current source status as
`Evaluation request submitted` and translate it into the user's language. Add
a friendly sentence explaining that the user may ask to view the selected task's
details for the result. Do
not display a CLI command, code block, or other internal implementation detail.
For a later explicit query, route through `arbitration-query.md` and run its
detail query internally.
