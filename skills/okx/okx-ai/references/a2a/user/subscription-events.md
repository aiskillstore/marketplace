# User Subscription Events

## Module Description

Use this leaf for User-side `sub_*` system events after `next-action` has fetched
fresh authoritative detail. Execute only the returned result; never invent a
decision card or state transition.

| Event | Required behavior |
|---|---|
| `sub_open` | Require Created state, establish/restore the session and pending attachments through the CLI playbook, notify that ASP acceptance is pending, then stop. |
| `sub_created` | Require Active state, render the returned content including its `Rate job` invitation, notify once, then stop. |
| `sub_trial_into_active`, `sub_renew` | Require Active state, render the returned content, notify once, then stop. |
| `sub_user_reject`, `sub_asp_dispute` | Require fresh ownership and Rejected/Disputed state before notification, ASP evaluation decision, or evidence side effects. |
| `sub_cancel` | When `trialType=1` and cancellation succeeds, display that the trial was revoked and finish the scoped session. Otherwise display formal-period auto-renew cancellation; the current formal period remains live. |
| `sub_asp_agree`, `sub_reject_refund_notify`, `sub_failed_notify`, `sub_close_notify` | Enter [`../refund-reconcile.md`](../refund-reconcile.md); event name or Closed/Failed status alone never proves settlement. |
| `sub_complete_notify` | Enter [`../completion.md`](../completion.md). |
| `sub_asp_selected` unexpectedly received by User | Ignore and stop. |

For English, send CLI `Content:` verbatim. Otherwise translate faithfully while
preserving fields and omitted clauses. Preserve backend `failReason` verbatim.
Never append terminal effects unless the structured result explicitly provides
them.
