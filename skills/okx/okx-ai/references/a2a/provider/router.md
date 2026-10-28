# A2A Provider Router

## State Routing

Use this router only after `../router.md` identifies the receiving role as
ASP/Provider. Select exactly one final business Reference and stop routing.


### System events

| Input or state | Reference |
|---|---|
| `job_asp_selected`, `sub_open` | [`assignment.md`](assignment.md) |
| `task_params_request`, `task_params_response`, `task_params_update` | [`../params.md`](../params.md) |
| `job_accepted` | [`execution.md`](execution.md) |
| `job_submitted` | [`../notify.md`](../notify.md) |
| `job_completed`, `job_auto_completed` | [`../completion.md`](../completion.md) |
| `job_rejected` | Fresh zero-price one-time task at Failed(9) → [`../completion.md`](../completion.md) using the returned terminal notification-and-cleanup action; otherwise → [`arbitration-decision.md`](arbitration-decision.md) |
| `job_refunded`, `job_auto_refunded`, `job_closed`, `job_expired`, `job_asp_reject_expire`, `job_asp_reject_closed` | [`../refund-reconcile.md`](../refund-reconcile.md) |
| `dispute_approved` | [`dispute.md`](dispute.md) |
| `job_disputed` | [`evidence-upload.md`](evidence-upload.md) |
| `[ARBITRATION_REASON_CONTEXT]` | [`dispute.md`](dispute.md) |
| `sub_asp_dispute` | [`evidence-upload.md`](evidence-upload.md) |
| `sub_user_reject` | [`arbitration-decision.md`](arbitration-decision.md) |
| `sub_created`, `sub_asp_selected`, other `sub_*` | [`subscription.md`](subscription.md) |

## Intent Routing

### Free-text intents

| User intent | Reference |
|---|---|
| Assignment decision | [`assignment.md`](assignment.md) |
| Missing-parameter negotiation | [`../params.md`](../params.md) |
| Execute accepted work | [`execution.md`](execution.md) |
| Submit a deliverable | [`delivery.md`](delivery.md) |
| List ASP tasks or saved deliverables; query a provided one-time task lifecycle/current stage | [`task-query.md`](task-query.md) |
| Query the refund status or refund result of a provided task | [`task-query.md`](task-query.md) |
| List or manage provided subscriptions | [`subscription.md`](subscription.md) |
| Respond to a rejection, open a selected rejected task for evaluation, or continue its refund-or-evaluation decision | [`arbitration-decision.md`](arbitration-decision.md) |
| Pending, available, required, or in-progress evaluations and evaluation detail | [`arbitration-query.md`](arbitration-query.md); first query the rejected-task set for pending/available/required evaluation, then query filed evaluations only when requested |
| Execute the refund or evaluation action returned by the current decision | [`dispute.md`](dispute.md) |
| Upload evaluation evidence | [`evidence-upload.md`](evidence-upload.md) |


## Action Routing

| Action ID | Reference |
|---|---|
| `send_task_params_response` | [`../params.md`](../params.md) |
| `notify_user` | [`../notify.md`](../notify.md) |
| `finalize_asp_task`, `notify_and_cleanup_subscription` | [`../completion.md`](../completion.md) |
| `agree_refund`, `sub_agree_refund` | [`dispute.md`](dispute.md) |
| `raise_arbitration`, `raise_subscription_arbitration` | [`dispute.md`](dispute.md) |
| `view_arbitration` | [`arbitration-query.md`](arbitration-query.md) |
| `view_provider_task` | [`task-query.md`](task-query.md) |

Cross-domain actions are intercepted before this router is loaded.

## Troubleshooting
### Coverage failure

Unknown actions are coverage failures; report them and stop. Never infer a
replacement from prose.
