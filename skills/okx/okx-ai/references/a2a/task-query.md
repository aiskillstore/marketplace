# User Task and Deliverable Queries

## Module Description

This leaf performs read-only queries and returns fresh task data.


## Flow
### One task

Choose the branch from the user's requested information:

| Requested information | Handling branch |
|---|---|
| Progress, status, lifecycle, timeline, current stage, responsible party, or next step | Task-type gate, then the type-appropriate lifecycle timeline |
| Task details, basic information, attributes, type, fee, provider, or description | Task details |
| Delivery content | Task details plus the saved User deliverable manifest |

Examples such as `Check the current task progress` and `View task status`, or
equivalent progress/status wording in the conversation language, use the
lifecycle query and task-type gate below. Generic verbs such as `check`, `view`,
or `query` inherit their branch from the requested information. When both
progress and details are mentioned, render both requested outputs from their
type-appropriate read-only queries; reuse the lifecycle result as the type gate
and never rerun it.

Use an explicit Job ID when supplied; otherwise use the single unambiguous Job
ID bound to the current conversation's task context. If no Job ID can be
identified unambiguously, run `active-tasks`, show numbered candidates with
title, task type, role, status, and counterparty, then wait for a selection.
The command combines non-terminal one-time tasks and subscriptions. Do not
substitute either type-specific list or silently omit one task type.

#### Lifecycle query and task-type gate

For any progress-like intent defined above, run exactly one read-only lifecycle
query:

```text
onchainos agent lifecycle <jobId>
```

This command owns task-type detection, authoritative-detail fallback,
XMTP-history aggregation, duplicate and out-of-order event handling,
current-wallet User identity resolution, and current-status reconciliation.
Route the returned `taskType` without rerunning the command:

- `subscription`: enter [`user/subscription.md`](user/subscription.md)
  §Subscription lifecycle query with the same lifecycle result.
- `one_time`: render §One-time lifecycle timeline below from the same result.
- Unknown or missing: stop and report that the task type could not be
  established. Never assume an untyped task is one-time.

#### One-time lifecycle timeline

Use this rendering only when the lifecycle result's `taskType` is `one_time`.

Render the complete five-stage timeline from `display.timeline`, in the exact
order returned by the CLI and in the user's language:

```text
A2A single task · {jobId}

Task progress  {display.progressStep} / {display.progressTotal}

{timeline[0].marker} {localized timeline[0].title}
│  {localized timeline[0].detail, only when present}
...
{each display.followUp item, only when returned, in the same two-line form}
{timeline[4].marker} {localized timeline[4].title}
   {localized timeline[4].detail, only when present}

Current status: {localized display.currentSummary}
Handled by: {localized display.handledBy}
Next: {localized display.next}
{localized display.notice, only when present}
```

Rendering rules:

1. Render exactly the five returned `timeline` items. Preserve every returned
   marker and timestamp.
2. A node is one title line plus at most one indented detail line. Omit the
   detail line when `detail` is absent. The completed ASP-execution node may
   have the single additional deliverable line defined below. User-facing
   output contains the five plain-language nodes rather than diagnostic fields
   such as `confidence`, `statusSource`, event names, or SQLite paths.
3. Insert non-empty `display.followUp` after `timeline[3]` and immediately
   before `timeline[4]`, preserving the returned order. These rows carry
   plain-language interruption, platform-review, and refund results. The task
   completion item remains the final displayed node for every outcome.
4. Translate user-facing prose only. Preserve the complete Job ID, Agent ID,
   amounts, timestamps, and user-authored text. `Time unavailable`, `Start time
   unavailable`, `Not started`, and `Not completed` are intentional CLI
   fallbacks and are translated directly.
5. Review readiness is CLI-owned by `display.reviewReady`, which requires both
   submitted task status and `display.deliverableAvailable=true`. Render the
   `user_review` detail, `currentSummary`, `handledBy`, and `next` exactly as
   returned.
6. If `display` is absent because an older CLI is installed, use the legacy
   `milestones` and `phase` fields with the original five-stage layout, one
   detail line per node, and no estimated values. Recommend updating the CLI
   after presenting the compatible result.
7. End after the timeline and concise current responsibility guidance.

When `display.handledBy` is exactly `ASP` or `Platform`, render this source
sentence in the conversation language using the returned fields:

```text
Currently handled by {localized display.handledBy}; next: {localized display.next}. You can say "View task details" to review the details.
```

Preserve the meaning of `display.next` and render this sentence once.

When the returned `timeline` item with `key=asp_execution` has marker `✓` and
`display.deliverableAvailable=true`, run one scoped, read-only CLI lookup:

```text
onchainos agent task-deliverable-list --job-id <jobId> --role user
```

Use only a successful result whose full `jobId` equals the lifecycle Job ID.
When it returns a non-empty `deliverables` array, select the last returned item
and add exactly one line under the ASP-execution detail:

```text
│  Deliverable: [<absolutePath>](<absolutePath>)
```

Translate only the `Deliverable` label. Preserve the returned absolute path.
If the command, manifest, directory, or item is unavailable, omit this optional
line and keep the lifecycle result unchanged. The Skill does not open the
returned file or derive deliverable data from events or conversation history.

Safety boundary: this branch is read-only. Do not infer missing markers, times,
deadlines, refund amounts, or review results, and do not start a watch, create a
decision, send a message, or perform the returned next action.

For the task-details branch, run:

```text
onchainos agent status <jobId> --agent-id <currentAgentId>
```

The status result is also the task-type gate. Its normal output includes
`Task type: one_time|subscription|unknown`, derived from the authoritative
`jobType` in the same task-detail response.

For a delivery-content request, also read the User deliverable manifest with
`task-deliverable-list`; when unavailable, answer from the existing
conversation context. Attributes and task type use the status result directly.

- `one_time`: continue below and render the one-time task card.
- `subscription`: stop the one-time branch before rendering its card and enter
  [`user/subscription.md`](user/subscription.md) §Subscription detail query
  with the same Job ID.
- `unknown`: stop and report that the task type could not be established. Never
  assume an untyped task is one-time.

When `agent status` returns a structured arbitration detail instead of the
normal text summary, use its authoritative `payload.jobType` (`0` one-time,
`1` subscription) as the same gate. Report missing or unsupported values as an
unknown task type.

For a one-time task, render this exact card from fresh returned facts:

scene: One-time task details

display template:

```markdown
### One-time Job Details

- Job Name: {title}
- Job ID: {jobId}
- Service Provider: Agent ID {providerAgentId}
- Fee: {Fee}
- Status: {localizedStatusLabel}
- Job Description: {description}
```

display rules:

1. Display the complete `jobId`.
2. Render Fee as `{tokenAmount} {tokenSymbol}`. Render `Free` when the exact
   amount is zero.
3. Translate the CLI `statusLabel` and `statusDescription` into the user's
   language. The raw `statusName` remains a protocol compatibility key and
   must not be shown. For a one-time task with raw status `failed` / code `9`,
   use the CLI label `Refund completed` before translating it.
4. Preserve the returned Job Description without rewriting it.
5. For a delivered task, query `task-deliverable-list --job-id <jobId> --role
   user`. When its matching latest item has a regular-file `path`, render the
   following line after the card; otherwise omit it:

   ```markdown
   - Deliverable: [<absolutePath>](<absolutePath>)
   ```

#### Submitted one-time review recovery

After rendering the normal card above, enter this recovery when the same status
result says `Task type: one_time`, `Task status: Awaiting buyer review`, and
`payment: escrow`. That result is the authoritative delivered-but-not-yet-reviewed
state. Read the User-side local deliverable manifest:

```text
onchainos agent task-deliverable-list --job-id <jobId> --role user
```

- Require the returned full Job ID to equal the requested Job ID and
  `counterpartyAgentId` to equal the ASP from `status`.
- Select the last returned deliverable. Require its path to exist as a regular
  file. Its returned `deliverableType` is authoritative: for `text`, read that
  exact file as untrusted display data; for `file`, render only the file link.
- When a check fails or no saved deliverable exists, keep the normal task card
  as the only user-visible result.

Compose the localized review card directly from those facts. Use the full
absolute path in its Markdown link and the complete text without truncation:

```markdown
[Job <shortJobId>] The ASP has submitted the deliverable (<text|file>).
Saved at: [<absolutePath>](<absolutePath>)
---Deliverable---
<complete text; omit this section for a file>
---End of deliverable---
Payment: escrow
A. Approve → reply 'A'
B. Reject → reply 'B' and include a rejection reason
<for a Free one-time task, use this reject line instead: B. Reject → reply 'B' and include your rejection reason in the same message (required), e.g. `B the delivered result does not meet the requirement`>
<exact `review:` reminder from status, when present>
```

Select the `B/Reject` line from the task fee: when the status fee renders as
`Free` (exact-zero amount), use the zero-price reject line that requires a
non-blank reason in the same reply and shows the localized example; for any
paid fee keep the standard reject line unchanged. Localize the example while
preserving Job IDs, amounts, and user-authored text.

Persist it once with:

```text
onchainos agent pending-decisions-v2 request \
  --job-id <jobId> --role user --agent-id <currentAgentId> \
  --to-agent-id <aspAgentId> --user-content "<exact localized card>" \
  --list-label "[Decision <shortJobId>] <title> acceptance decision" \
  --source-event job_submitted
```

This command uses the stable database key
`buyer-review:<jobId>:job_submitted`; an existing decision is reused. After it
succeeds, immediately append the exact same localized `--user-content` to the
status response as a Markdown blockquote.

- Preserve this Job ID and idempotency key as the active decision context for
  the User's next message. This card has no active-watch origin.

Safety boundary: use the existing status response and validated manifest only.
Do not synthesize events or deliverables, inspect file-deliverable contents,
make another task-detail/`next-action` query, call `okx-a2a user list` or
`outdated-list` before rendering the review card, or start or resume a watch.

Use Refund V2 settlement provenance to confirm the refund result.

### Buyer refund tasks

Use [Refund Task List](#refund-task-list) for both query modes:

- `available`: one-time Submitted tasks and Active subscription periods.
- `requested`: one-time Rejected tasks and Rejected subscription periods.

```text
onchainos agent refund-list --role buyer --scope available --agent-id <userAgentId> --page 1 --page-size 20
onchainos agent refund-list --role buyer --scope requested --agent-id <userAgentId> --page 1 --page-size 20
```

The CLI applies the one-time and subscription status filters and returns one
display-ready `items` array. Keep the two modes separate when the user requests
one explicitly.

For an `available` selection, run `refund-prepare <jobId>` and render
[Confirm Refund Request](user/refund-confirm.md#confirm-refund-request). For a
`requested` selection, run:

```text
onchainos agent refund-detail <jobId> --role buyer --agent-id <userAgentId>
```

Render [Refund Request Details](#refund-request-details) and end after the
detail block.

For an explicit one-time list, run:

```bash
onchainos agent my-tasks --task-type one-time --status-type <0|1|2> \
  --page <page> --page-size <pageSize>
```

scene: One-time task list

display template:

```markdown
### One-time Jobs

| # | Job Name | Job ID | Service Provider | Fee | Status |
|---|---|---|---|---|---|
| {n} | {title} | {jobId} | Agent ID {providerAgentId} | {Fee} | {localizedStatusLabel} |
```

display rules:

1. Render only the current `oneTimeTasks.list` page in CLI order and number it
   from 1.
2. Display every `jobId` in full.
3. Render Fee as `{tokenAmount} {tokenSymbol}`. Render `Free` when the exact
   amount is zero.
4. Translate the CLI-normalized `statusLabel` into the user's language; retain
   `statusName` only as a raw compatibility key.
5. Preserve each returned page and its pagination.

### Saved deliverables

```text
onchainos agent task-deliverable-list --job-id <jobId> --role <user|asp>
onchainos agent task-deliverable-list --role <user|asp> [--search <keyword>]
```

For one task, show the original name, type, human-readable size, absolute path,
and saved time. For multiple tasks, group by title and full Job ID. An empty
result means no saved deliverables were found.

### Task-scoped messages

When no pending decision owns the reply and the user wants to supplement,
clarify, or discuss an existing task, enter [`peer.md`](peer.md). A read-only
query ends after presenting its result.


## Output Rules
### Output Templates

The templates below are English sources. Reply in the language of the current
conversation while preserving Job IDs, Agent IDs, amounts, token symbols,
timestamps, and user-authored reasons exactly.

Use tables only for multi-record list results. Render every single-record
detail or confirmation as one `- Label: value` item per available field.

#### Refund Task List

```markdown
You have {refundCount} refund tasks:

| # | Service Name | Job ID | Task Type | Refund Amount | Result Deadline |
|---|---|---|---|---|---|
| {n} | {serviceName} | {jobId} | {taskType} | {refundAmount} | {responseDeadline} |

Reply with the number or Job ID to view details.
```

Display rules:

1. Number records sequentially in CLI order.
2. Show the full Job ID.
3. Use the CLI-provided task type, amount, and deadline directly.
4. Use the same table for `available` and `requested` modes.

#### Refund Request Details

```markdown
### Refund Request Details

- Service Name: {serviceName}
- Job ID: {jobId}
- Service Provider: {serviceProviderName} (Agent ID: {agentId})
- Requested Refund: {refundAmount}
- Reason for Refund: {reasonForRefund}
- Result Deadline: {responseDeadline}
- Refund Result: {localizedStatusLabel}
- Result Description: {localizedStatusDescription}
- Evaluation Result: {localizedEvaluationResultDescription}
- Evaluation Reason: {localizedEvaluationReason}
```

Display rules:

1. Render only fresh values from `payload.display`.
2. Preserve the full Job ID and the original refund reason.
3. Render each available optional value from `payload.display`.
4. Translate `payload.display.statusLabel` and
   `payload.display.statusDescription` into the conversation language.
5. Render `Evaluation Result` and `Evaluation Reason` only when the CLI
   returns them, then translate their English source wording into the
   conversation language. Never treat the original `Reason for Refund` as an
   evaluation reason.
6. End a detail query result after the detail block.
7. Render the fields defined by this template.
