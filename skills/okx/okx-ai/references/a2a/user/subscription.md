# My Subscriptions

## Module Description

Browse my subscription task lists or details.


## Intent Routing

### Hot subscription reads

| User intent | Reference | Hot command |
|---|---|---|
| My subscriptions | — | `onchainos agent subscription-list --page-size 10` |
| Next page with the returned cursor | — | `onchainos agent subscription-list --cursor <nextCursor> --page-size <pageSize>` |
| Selected subscription name, provider, fee, trial, renewal, billing, or other metadata | — | `onchainos agent subscribe-detail <jobId> --format json` |
| Selected subscription progress, status, lifecycle, timeline, current stage, responsible party, or next step | — | `onchainos agent lifecycle <jobId>` |

These are read-only hot commands. Use the current Reference's result and
rendering rules directly; do not read the CLI Reference or run `--help` first.


## Flow
### Subscription detail query

Use this entry when the selected Job ID is already known to be a subscription,
or when `../task-query.md` has type-gated it as `subscription`. Run exactly one
subscription-native detail query:

```text
onchainos agent subscribe-detail <jobId> --format json
```

Render the successful result through §Detail below. Do not run lifecycle merely
to fill detail-card fields, and do not substitute `subscription-list` for a
selected Job ID.

### Subscription lifecycle query

Use this entry only for progress, status, lifecycle, timeline, current stage,
responsible party, or next-step intent. When `../task-query.md` supplies a
lifecycle result, reuse it and do not run another command. When this Reference is
entered directly for an already-established subscription, run exactly one
read-only query:

```text
onchainos agent lifecycle <jobId>
```

Require the returned `taskType` to equal `subscription` and
`display.templateId` to be non-empty before rendering the lifecycle template.
If the Copy ID is missing, report that the subscription lifecycle copy is
currently unavailable and do not render a partial template. Render every returned
`display.timeline` item in order, followed by every returned
`display.followUp` item in order. The CLI selects one of the approved
`Sub-Status-1` through `Sub-Status-18` templates. Normal subscription states
use four stages, pre-acceptance terminal states use three, and refund or
evaluation states use five; never add, remove, split, or rename stages.
Immediately after a confirmed `close_created_subscription` write, the CLI may
use its durable local broadcast receipt while the official `sub_cancel` event
is still propagating; a pre-acceptance Closed(7) result from that operation is
`Sub-Status-8`, never the ASP-declined `Sub-Status-6`.
While the authoritative status is still Created(0), the Copy ID remains
`Sub-Status-2`, but the CLI reports that closure was submitted, assigns the
pending reconciliation to the Platform, and returns no `Close task` choice.
Never invite or submit another close while that state is pending.

```text
{when display.templateId is non-empty}
Copy ID: {display.templateId}
Subscription progress  {display.progressStep} / {display.progressTotal}

{for each display.timeline item}
{item.marker} {localized item.title}
│  {localized item.detail, only when present}

{for each display.followUp item, only when returned}
{item.marker} {localized item.title}
│  {localized item.detail, only when present}

Current status: {localized display.currentSummary}
Handled by: {localized display.handledBy}
Next: {localized display.next}

{when display.choices is non-empty}
Please choose:
{render display.choices in order as A., B., ...}

{localized display.notice, only when present}
```

Preserve IDs, timestamps, amounts, hashes, and returned markers. Do not expose
raw `status`, `statusName`, `authoritativeStatus`, event names, confidence, or
storage paths. This query is read-only: do not start listening, modify receipt
devices, cancel, renew, sign, pay, or execute a returned next step. A displayed
choice is an invitation for a later user decision, not permission to execute it
during the lifecycle query.


## Output Rules
### List

Render only the current `payload.items` page. Keep CLI order. This section is
the single rendering contract for buyer subscription lists.

#### How to render list
This is a mandatory, exact rendering contract.
For every subscription-list result, render every non-empty section below.
Never summarize, shorten, reorder rows.
Always respond and render all user-facing content in the language currently used by the user.
##### template
```markdown
{When activeRows is non-empty}
#### Active Subscriptions ({payload.summary.activeCount})

| # | Job Name | Service Provider | Fee / Month | Next Charge | Auto-renewal | Billing Period | {payload.deviceColumns[].label} |
|---|---|---|---|---|---|---|---|
| {n} | {title} | Agent#{providerAgentId} | {feeLabel} | {nextChargeLabel} | {autoRenewLabel} | {billingPeriodLabel} | {deviceReceiptCells[column.key]} |
{End when activeRows is non-empty}

{When endedRows is non-empty}
#### Ended Subscriptions ({payload.summary.endedCount})

| # | Job Name | Service Provider | Fee / Month | Billing Period |
|---|---|---|---|---|
| {n} | {title} | Agent#{providerAgentId} | {feeLabel} | {billingPeriodLabel} |
{End when endedRows is non-empty}

{When both activeRows and endedRows are empty}
No subscriptions found.
{End when both activeRows and endedRows are empty}

{No Receiver Warning}

#### Next steps：
{Rendered nextAction list}
```
##### template rules
1. Group rows by `listStatus`, preserving CLI order.
2. Render the Active Subscriptions heading and table only when `activeRows` is
   non-empty. Render the Ended Subscriptions heading and table only when
   `endedRows` is non-empty. If both groups are empty, render only `No subscriptions found.`
3. For Active rows, render the returned `payload.deviceColumns` in order and
   use each row's `deviceReceiptCells[column.key]` directly. The CLI owns the
   device label, fallback to `deviceId`, and `(This Device)` marker.
4. If device data is unavailable, omit device columns and state that receipt
   status is unavailable.
5. Warn for each Active row with `hasNoReceivingDevices=true`.
6. Subscription lifecycle status is internal: never render a row's `status`,
   `statusName`, `statusLabel`, or `statusDescription`.

#### Constraints

- Use `nextCursor` unchanged to continue the list.
- The query and rendered recommendations are read-only. Never start listening,
  modify delivery, cancel, sign, pay, or trade from the list response.

### Detail

This is the Buyer-side detail card. ASP-side task details remain owned by
[`../provider/task-query.md`](../provider/task-query.md) and its `agent asp
status` contract; do not mix the two roles' fields. Render the selected
subscription as a vertical, single-record field list. Use the CLI-derived
display fields directly and translate their user-facing prose into the
conversation language:

```markdown
### Subscription Details · {jobId}

- Job Name: {title, when non-empty}
- Job Description: {description, when non-empty}
- Service Provider: {serviceProviderLabel, when non-null}
- Free Trial: {localized freeTrialLabel, when non-null}
- Fee: {localized feeLabel, when non-null}
- Auto-Renewal: {localized autoRenewLabel, when non-null}
- Billing Period: {localized billingPeriodLabel, when non-null}
- Current Period: {currentPeriodLabel, when non-null}
- Offline Message Handling: {localized offlineMessageHandlingLabel, when non-null}
- Receive on This Device: {localized receiveOnThisDeviceLabel, when non-null}
```

Require `displayReady=true` only as the minimum structural gate for a non-empty
Job ID. When false, report that the selected subscription identity is
incomplete and stop. Otherwise render every non-null template field; one
missing label must not suppress the remaining card. When a field explicitly
requested by the User appears in `displayMissingFields`, render the available
fields first, then state that the requested field is currently unavailable. Do
not reconstruct a missing value from conversation history or another task, and
do not replace a missing value with `—` unless that exact label was returned by
the CLI. Preserve `currentPeriodLabel` exactly because it already contains
formatted timestamps and an explicit UTC offset.

Subscription lifecycle status is internal: never render `status`, `statusName`,
`statusLabel`, or `statusDescription` in the detail card.

#### Constraints

- Use an explicit Job ID or the single unambiguous Job ID bound to the current
  subscription context. Never infer a Job ID from a title.
- Refresh the list only when the selected subscription is no longer available.
- Keep the detail layout vertical. Do not convert it to a Markdown table.
