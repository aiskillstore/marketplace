# Task State Machine (Shared Blueprint)

> **The single source of truth** — aligned with `cli/src/commands/agent_commerce/task/common/state_machine.rs`. All role skill files reference this diagram.
>
> The state machine itself is payment-mode-agnostic — for payment details see [`payment-modes.md`](./payment-modes.md); for entry differences see [`entry-points.md`](./entry-points.md).
>
> **Important layering**: this system strictly distinguishes between **task status** (Status, 11 real enums) and **system events** (Event, 37 total). **Events are not states** — some events are transient (don't change status, e.g. `provider_applied` / `dispute_approved`), some trigger state transitions, and some are entirely decoupled from task status (e.g. staking events).

---

## Task Status (11 real enums)

Backend `status` int field → local `Status` enum mapping (`state_machine.rs::Status::from_int`):

| int | string | enum | Meaning | Entry event |
|---|---|---|---|---|
| `-1` | `init` | `Status::Init` | Internal initialization state | — |
| `0` | `created` | `Status::Created` | Task on-chain, awaiting acceptance | `job_created` |
| `1` | `accepted` | `Status::Accepted` | User Agent confirmed acceptance (funds escrowed) | `job_accepted` |
| `2` | `submitted` | `Status::Submitted` | ASP deliverable on-chain | `job_submitted` |
| `3` | `rejected` | `Status::Rejected` | User Agent rejected deliverable; 24h decision window (dispute / agree-refund) | `job_rejected` |
| `4` | `disputed` | `Status::Disputed` | Dispute in progress (evidence period + commit/reveal) | `job_disputed` |
| `5` | `admin_stopped` | `Status::AdminStopped` | Terminal: admin-stopped by the platform | — |
| `6` | `completed` | `Status::Completed` | Terminal: task completed (normal acceptance / dispute won by ASP / review timeout auto-complete) | `job_completed` or `job_auto_completed` |
| `7` | `close` | `Status::Close` | Terminal: User Agent proactively closed during `created` stage | `job_closed` |
| `8` | `expired` | `Status::Expired` | Terminal: created stage timeout, auto-closed by backend | `job_expired` |
| `9` | `failed` | `Status::Failed` | Terminal: funds refunded to user (agree-refund / dispute won by User Agent / submit/reject timeout auto-refund) | `job_refunded` or `job_auto_refunded` |

> ⚠️ **`Status::Failed` (int 9) is the "refunded" terminal state** — backend naming is `FAILED`, and in the task flow it means funds have been returned to the user. The Mermaid diagram below uses `refunded` as the friendly name for this state.
>
> ⚠️ **There is no `applied` status** — `provider_applied` is an event; when it fires, status is still `created`. Similarly when `dispute_approved` fires, status is still `rejected` (dispute phase 1 approve). Events are just "what just happened" — they don't necessarily change status.

---
