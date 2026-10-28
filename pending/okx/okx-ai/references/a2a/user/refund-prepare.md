# Buyer Refund Preparation

## Module Description

Use this leaf to resolve one Buyer-owned refund target and obtain a fresh,
read-only Refund result. Cancellation changes future renewal; a refund
returns the applicable original payment.

Resolve exactly one Job ID from the request or a fresh refund-task list. Run:

```text
onchainos agent refund-prepare <jobId> [--reason <verbatimReason>]
```

The CLI owns eligibility, ownership, task type, service-name fallback, payment
facts, billing period, deadlines, and available actions. Route only by the
returned `nextAction[].id`.

A subscription at Created(0), before ASP acceptance, may return the bound
`close_created_subscription` action. Treat it as immediate task closure, not
as an auto-renew setting change, and continue through the same fresh
confirmation and execution contract below.

- Use [`refund-confirm.md`](refund-confirm.md) for confirmation and reason collection.
- Use [`refund-execute.md`](refund-execute.md) only after the required intent and reason are complete.
- Use [`../refund-reconcile.md`](../refund-reconcile.md) for pending or terminal results.

For `refund_reason_required`, enter [`refund-confirm.md`](refund-confirm.md),
render the complete Template 6.1 confirmation from `payload.display`, and apply
its intent-and-reason response matrix. For `refund_reason_too_long`, re-render
the active confirmation and ask for a replacement reason within the
CLI-provided maximum length. Preserve every User-authored reason verbatim.
Render an unrecognized reason or action ID as a read-only result with its
returned guidance.
