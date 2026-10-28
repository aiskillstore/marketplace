# A2A User Router

## State Routing

Use this router only after `../router.md` identifies the receiving role as
User/Buyer. Select exactly one final business Reference per intent and stop routing; the
explicit multi-intent read-only exception is defined below.


### System events

| Input or state | Reference |
|---|---|
| `job_created` | [`created.md`](created.md) |
| `task_params_request`, `task_params_response`, `task_params_update` | [`../params.md`](../params.md) |
| `job_submitted`, `deliverable_received` | [`intake.md`](intake.md) |
| `job_completed`, `job_auto_completed` | [`../completion.md`](../completion.md) |
| `job_refunded`, `job_auto_refunded`, `job_closed`, `job_expired`, `job_asp_reject_expire`, `job_asp_reject_closed` | [`../refund-reconcile.md`](../refund-reconcile.md) |
| `sub_open`, `sub_created`, `sub_asp_selected`, other `sub_*` | [`subscription-events.md`](subscription-events.md) |
| Active subscription signal | [`subscription-signal.md`](subscription-signal.md) |

## Intent Routing

### Free-text intents

| User intent | Reference |
|---|---|
| Continue a selected Service after `task-create-prepare` | [`create-prepare.md`](create-prepare.md) |
| Create a one-time task or answer its Guide | [`create.md`](create.md); Guide-only step → [`create-guide.md`](create-guide.md) |
| Create a subscription | [`subscription-create.md`](subscription-create.md) |
| Direct reply to the Runtime Watch creation-start note using `Check subscription task status` or its localized rendering; or query local follow-trade results for a subscription Signal by `jobId` or `deliveryId` | [`subscription-trade-records.md`](subscription-trade-records.md) |
| View or configure subscription receipt devices, delivery destinations, or whether this device receives messages | [`receipt.md`](receipt.md) |
| View a known subscription's name, provider, fee, trial, billing period, auto-renewal state, or other metadata | [`subscription.md`](subscription.md), Subscription detail query |
| View a known subscription's progress, status, lifecycle, timeline, current stage, responsible party, or next step | [`subscription.md`](subscription.md), Subscription lifecycle query |
| List or manage subscriptions | [`subscription.md`](subscription.md) or [`subscription-manage.md`](subscription-manage.md) |
| Explicitly resume or restore **automatic copy-trading** for one existing subscription, including after signing in on a new device | [`restore-copytrade.md`](restore-copytrade.md) |
| Ask about a task's progress, status, lifecycle, timeline, current stage, current responsible party, or next step when its type is not already known | [`../task-query.md`](../task-query.md); it type-gates before selecting the matching lifecycle rendering |
| Explicitly ask for task details, basic information, attributes, type, fee, provider, description, or delivery content; list or inspect tasks, saved deliverables, pending evaluations, or tasks the User rejected | [`../task-query.md`](../task-query.md); use its detail or list branch |
| Change task visibility | [`visibility.md`](visibility.md) |
| Review a deliverable or continue approval/rejection | [`review.md`](review.md) or [`review-decision.md`](review-decision.md) |
| Refund, close, or inspect refund status | [`refund-prepare.md`](refund-prepare.md) |
| Rate an Active subscription or a Completed one-time task/subscription | [`rating.md`](rating.md) |
| Continue an active subscription signal | [`subscription-signal.md`](subscription-signal.md) |

The fixed `Check subscription task status` phrase enters
`subscription-trade-records.md` only as a direct reply to the Runtime Watch
creation-start note. All other subscription lifecycle/status wording uses the
subscription lifecycle query in `subscription.md`.

Prefer the most specific matching row. Receipt/device wording wins over generic
subscription metadata wording, and Signal, copy-trade-result, or `deliveryId`
wording wins over both. When the User explicitly requests fields owned by more
than one read-only Reference, execute each required read-only query and combine the
results in one response. Never drop an explicitly requested field merely to
select one Reference.


## Action Routing
### Progression actions

| Action ID | Reference |
|---|---|
| `restore_subscription` | [`duplicate-subscription.md`](duplicate-subscription.md) |
| `open_create_playbook` | [`create.md`](create.md) |
| `send_task_params_response` | [`../params.md`](../params.md) |
| `request_rejection_reason`, `approve_review` | [`review-decision.md`](review-decision.md) |
| `finalize_user_task`, `finalize_user_subscription` | [`../completion.md`](../completion.md) |
| `resolve_refund_target`, `prepare_refund`, `view_refund_status` | [`refund-prepare.md`](refund-prepare.md) |
| `provide_refund_reason` | [`refund-confirm.md`](refund-confirm.md) |
| `cancel_trial_conversion`, `close_created_subscription`, `close_zero_price`, `execute_direct_refund`, `submit_refund_request` | [`refund-confirm.md`](refund-confirm.md); after the bound confirmation load [`refund-execute.md`](refund-execute.md) |

Cross-domain actions are intercepted before this router is loaded.

## Troubleshooting
### Coverage failure

Treat an unknown action as a coverage failure: report it and stop routing.
