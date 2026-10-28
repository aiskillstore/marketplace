# ASP Task and Deliverable Queries

## Module Description

This Reference performs read-only queries for the selected ASP identity. The User
router never loads this file.


## Flow
### Task list and details

Resolve the explicit or bound ASP identity. If multiple identities remain,
show them and wait for a selection.

```text
onchainos agent asp list-tasks --agent-id <aspAgentId> --page 1 --limit 20
```

The ASP list combines the same-numbered page from the subscription and one-time
task sources. `payload.pageSize` applies independently to each source
(`payload.paginationScope=per_task_type`), so a page can contain up to twice
that many rows. Subscription rows appear first, followed by one-time rows.
Render only `payload.items`, in CLI order, and number the rows from 1.
Render [Task List](#task-list).

`payload.total` is the sum of `payload.subscriptionTotal` and
`payload.oneTimeTotal`. `payload.hasMore` is true while either
`payload.subscriptionHasMore` or `payload.oneTimeHasMore` is true.

For a selected row, use its `taskType` only as a routing key and run:

```text
onchainos agent asp status <jobId> --agent-id <aspAgentId>
```

Render the returned `payload.task` with [Task Details](#task-details).

Pending refund requests and filed evaluations are different datasets. Route
both through [`arbitration-query.md`](arbitration-query.md).

For the refund status or result of a known provided Job ID, run:

```text
onchainos agent refund-detail <jobId> --role provider --agent-id <aspAgentId>
```

The same command returns the pending decision for `Rejected(3)`, the current
Evaluation result for `Disputed(4)`, and a read-only refund result for terminal
states. Render [Refund Request Details](#refund-request-details) from its
`payload.display` fields.

### Saved deliverables

```text
onchainos agent task-deliverable-list --job-id <jobId> --role asp
onchainos agent task-deliverable-list --role asp [--search <keyword>]
```

For one task, show the original name, type, human-readable size, absolute path,
and saved time. For multiple tasks, group by title and full Job ID. An empty
result means no saved deliverables were found.


## Output Rules
### Task List

scene: ASP task list

```markdown
### Tasks for {aspName} (Agent ID: {agentId})

You currently have {jobCount} tasks:

| # | Job Name | Job ID | User | Task Type | Status | Fee | Billing Period | Next Charge | Auto-renewal |
|---|---|---|---|---|---|---|---|---|---|
| {n} | {jobName} | {jobId} | {userName} (Agent ID: {userAgentId}){platformReviewTag} | {localizedTaskTypeLabel} | {localizedStatusLabel} | {localizedFeeLabel} | {localizedBillingPeriodLabel} | {nextChargeAt} | {localizedAutoRenewLabel} |

Reply with a number or Job ID to view the task details. {morePrompt}
```

1. Set `jobCount` from `payload.total`. Preserve every Job Name exactly. Display every Job ID in full and allow a
   reply by row number or Job ID only for an ID in
   `nextAction[id=view_provider_task].params.allowedJobIds`.
2. Render User as `{userName} (Agent ID: {userAgentId})`. When `testFlag=true`,
   set `platformReviewTag` to ` [Platform-reviewed User]`, including the leading
   space. When false, set it to an empty string. Never place this tag on Job
   Name and never expose the raw `testFlag` key.
3. Translate `taskTypeLabel` into the user's language. Use only the localized
   equivalents of `Subscription` or `One-time`; never show `subscription`,
   `one_time`, `Subscription Task`, `One-time Task`, or backend enum values.
4. Translate the CLI-provided `statusLabel`; never show raw `status` or
   `statusCode`.
5. Render `feeLabel` with one space between amount and token. Translate
   `Free`, `/ month`, and `/ task` while preserving amount and token symbol.
6. If `payload.hasSubscriptionTasks=false`, omit Billing Period, Next Charge,
   and Auto-renewal from the header and every row. Otherwise retain all three
   columns and leave their one-time-task cells empty; never render `—` there.
7. For subscription rows, translate `billingPeriodLabel` (`Trial Period` or
   `Billing Period N`) and `autoRenewLabel` (`Enabled` or `Disabled`). Render
   `nextChargeAt` only when returned. Preserve its minute precision and UTC
   offset.
8. Do not display device names, receiving-device state, or any other
   subscription delivery-routing data in an ASP task list.
9. When `payload.hasMore=true`, set `morePrompt` to the localized equivalent of
   `Reply "More" to see more tasks.` When false, set it to an empty string. A
   More reply increments `--page` and keeps the same `--limit`, ASP Agent ID,
   and optional `--status` filter.

### Task Details

```markdown
### Task Details

| Job Name | Job ID | User | Task Type | Status | Fee | Billing Period | Current Period | Next Charge | Auto-renewal | Created At |
|---|---|---|---|---|---|---|---|---|---|---|
| {jobName} | {jobId} | {userName} (Agent ID: {userAgentId}){platformReviewTag} | {localizedTaskTypeLabel} | {localizedStatusLabel} | {localizedDetailFeeLabel} | {localizedBillingCycleLabel} | {currentPeriod} | {nextChargeAt} | {localizedAutoRenewLabel} | {createdAt} |

{recommendedActions}
```

1. Apply the list's Job Name, full Job ID, User, platform-review tag, Task Type,
   and Status rules unchanged. Render `detailFeeLabel`: subscription fees retain
   `/ month`; one-time fees contain only amount and token symbol; zero is `Free`.
2. For a one-time task, omit Billing Period, Current Period, Next Charge, and
   Auto-renewal columns entirely.
3. For a subscription, render `billingCycleLabel` as the localized equivalent
   of `Monthly`. Render `currentPeriod` only for a formal paid period, using the
   complete start and end dates returned by the CLI.
4. Render `nextChargeAt` only when returned. Render `autoRenewLabel` only for a
   subscription, translated as `Enabled` or `Disabled`.
5. Preserve the CLI-formatted `nextChargeAt` and `createdAt` exactly: minute
   precision with an explicit UTC offset.
6. Render only returned next actions after the table as `recommendedActions`.
   Never infer an action from status prose.

### Refund Request Details

```markdown
### Refund Request Details

- Service Name: {serviceName}
- Job ID: {jobId}
- Service Provider: {serviceProviderName} (Agent ID: {agentId})
- Requested Refund: {refundAmount}
- Reason for Refund: {reasonForRefund}
- Response Deadline: {responseDeadline}
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
