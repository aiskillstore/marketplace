# Buyer Refund Reconciliation

## Module Description

Use this leaf for refund events, progress queries, recovery, and terminal
rendering. Events are wake-up signals only: always re-read fresh authoritative
state and apply [`../shared/refund-contract.md`](../shared/refund-contract.md).

Relevant signals include `job_closed`, `job_refunded`, `job_auto_refunded`,
`job_expired`, `submit_expired`, `job_asp_accept_expire`,
`job_asp_reject_expire`, `sub_asp_agree`, `sub_reject_refund_notify`, and
`dispute_resolved`.


## Flow
### Result families

- `refund_confirmed`: render the full original-token refund as terminal only
  after the finality matrix passes. Translate `Refund completed` into the
  user's language. Raw `statusName=failed` and `rawStatus=9` remain
  backend lifecycle keys; the displayed business result is the localized
  `statusLabel` and `statusDescription`.
- `expired_without_refundable_payment`: render terminal
  `settlement.state=not_required`; never claim funds moved.
- `zero_amount_task_failed`: render the free one-time task as terminal Failed,
  with `settlement.state=not_required`; do not request refund provenance,
  invoke `refund-prepare`, offer evaluation, or continue watching.
- `refund_operation_pending_reconciliation` or `refund_outcome_unknown`: stay
  pending/read-only and never repeat a write.
- `zero_amount_task_closed`, `trial_subscription_closed_without_refund`, or
  `refund_not_approved_or_task_completed`: render the returned terminal
  no-refund outcome and offer no write.
- `trial_conversion_already_cancelled`, `trial_conversion_state_unknown`, or
  `zero_amount_subscription_not_refundable`: explain the current fact and stay
  read-only.

Keep valid `request-refund` provenance across Rejected(3), Disputed(4), process
restart, polling, and recovery. It proves the request path, not settlement; a
core mismatch or definitive rejection disqualifies it.

For a direct `refund-prepare` terminal result, render and follow its returned
`stop`; no cleanup is implied. For the same result during a scoped watch event,
emit the stable terminal marker, use [`../runtime/cleanup.md`](../runtime/cleanup.md),
and do not re-enter scoped watch. Global watch continues for other tasks.

Missing proof produces no verdict, rating, notification, terminal marker, or
cleanup. This missing-proof rule does not apply to a fresh buyer-owned,
zero-amount one-time task at Failed(9), because that outcome requires no refund
settlement. A later explicit query may inspect pending work; elapsed time alone
never establishes finality.
