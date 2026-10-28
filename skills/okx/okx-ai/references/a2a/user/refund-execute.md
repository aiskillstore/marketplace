# Buyer Refund Execution

## Module Description

Use this leaf only after confirmation governed by
[`refund-confirm.md`](refund-confirm.md).

Copy values unchanged from one latest write action:

```text
onchainos agent refund-execute JOB_ID_ARG \
  --operation OPERATION_ARG \
  --refund-context-id REFUND_CONTEXT_ID_ARG \
  [--reason REASON_ARG] \
  --confirm
```

`request-refund` must carry the exact prepared User reason; other operations
omit it. Pass each dynamic value as one literal argv element and never
interpolate User or CLI-returned text into shell source.

Execution re-reads authoritative state. Follow only returned actions. A
broadcast receipt is pending, not settlement, and must never trigger an
automatic retry.

For `refund_request_broadcast_submitted`, say concisely that the request was
submitted with the User's verbatim reason and that the ASP needs time. Do not
render a CLI command, code block, or other internal implementation detail.
Instead, give this friendly later-query guidance:

> Refund request submitted. Reason: {refundReason}. Awaiting ASP handling. You
> may ask me to view the selected task's details for the refund result.

If the User later asks for the result, route through `task-query.md` and run
the required status query internally.

For `created_subscription_close_broadcast_submitted`, say that the close was
submitted and remains pending until both the subscription lifecycle and wallet
order are reconciled. If the original payment is zero, say no refund is
required. Otherwise, do not claim that the refund completed merely because the
subscription reached Closed(7); report completion only from a later
`refund_confirmed` result.

Then end the current turn. Do not execute or resume `watch_task` automatically.
For other broadcast-submitted outcomes, state that the operation is pending and
follow only returned read/watch actions.

For stale, rejected, pre-broadcast failure, or confirmation-required results,
discard the old binding and use only a newly returned preparation action.
Read [`../refund-reconcile.md`](../refund-reconcile.md) for later progress and
terminal handling.
