# Task State Machine (Shared Blueprint)

## State Semantics

> **The single source of truth** — aligned with `cli/src/commands/agent_commerce/task/common/state_machine.rs`. All role skill files reference this diagram.
>
> The state machine itself is payment-mode-agnostic. Payment and entry
> eligibility come from the owning structured CLI flow, not from this table.
>
> **Important layering**: this system strictly distinguishes between **task status** (Status, 11 real enums) and **system events** (Event, 58 total). **Events are not states** — some events are transient (don't change status, e.g. `provider_applied` / `dispute_approved`), some trigger state transitions, and some are entirely decoupled from task status (e.g. staking events).

---


## Supported Capabilities
### Task Status (11 real enums)

Backend `status` int field → local `Status` enum mapping (`state_machine.rs::Status::from_int`):

| int | string | enum | Meaning | Entry event |
|---|---|---|---|---|
| `-1` | `init` | `Status::Init` | Internal initialization state | — |
| `0` | `created` | `Status::Created` | Task on-chain, awaiting acceptance | `job_created` |
| `1` | `accepted` | `Status::Accepted` | Designated ASP accepted the buyer-created-and-funded task; execution starts | `job_accepted` |
| `2` | `submitted` | `Status::Submitted` | ASP deliverable on-chain | `job_submitted` |
| `3` | `rejected` | `Status::Rejected` | User Agent rejected deliverable; 24h decision window (evaluation / agree-refund) | `job_rejected` |
| `4` | `disputed` | `Status::Disputed` | Evaluation in progress (evidence period + commit/reveal) | `job_disputed` |
| `5` | `admin_stopped` | `Status::AdminStopped` | Terminal: admin-stopped by the platform | — |
| `6` | `completed` | `Status::Completed` | Terminal: task completed (normal acceptance / evaluation favors ASP / review timeout auto-complete) | `job_completed` or `job_auto_completed` |
| `7` | `close` | `Status::Close` | Terminal close. Refund meaning depends on task kind and payment facts. | `job_closed` or `job_asp_reject_closed` |
| `8` | `expired` | `Status::Expired` | Terminal timeout. Paid non-trial tasks are refunded; trial and zero-amount tasks have no refundable funds. | `job_expired` or `job_asp_accept_expire` |
| `9` | `failed` | `Status::Failed` | Terminal refund-or-failure state; subscription cause can be ambiguous. | `job_refunded`, `job_auto_refunded`, `job_asp_reject_expire`, `sub_asp_agree`, `sub_reject_refund_notify`, `dispute_resolved`, or `sub_failed_notify` |

> Refund meaning must not be inferred from this table alone. Run the fresh
> Refund flow in [`../a2a/refund-reconcile.md`](../a2a/refund-reconcile.md); its structured
> result owns settlement, provenance, and terminal handling.
>
> ⚠️ **There is no `applied` status** — `provider_applied` is an event; when it fires, status is still `created`. Similarly when `dispute_approved` fires, status is still `rejected` (evaluation phase 1 approval). Events are just "what just happened" — they don't necessarily change status.

---
