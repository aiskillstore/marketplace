---
name: verify-release
description: Decide go or rollback after a deploy. Compare the new release's issues, error logs, and trace error rate with the previous release, then report the decision with evidence. Use when someone asks if a deploy is safe, whether a release broke anything, to check a canary or rollout, to compare 2 versions, or whether to roll back. Reads LogBrew release comparisons through the logbrew CLI or MCP server, and works from exported error and request counts when no tool is connected.
license: MIT
---

# Verify a release

Give 1 of 3 decisions: **Go**, **Rollback**, or **Wait**. Back each one
with numbers from both releases. A release comparison is evidence, not
proof that the new code caused a change.

## Choose the evidence source

1. **LogBrew CLI** with account access (`logbrew status --json`) or a
   project read key in `LOGBREW_TOKEN`. The CLI can also record deployments.
2. **LogBrew MCP server** (`search` and `execute` tools from
   `https://mcp.logbrew.co/mcp`). It reads only; it cannot record a
   deployment.
3. **No tool.** Ask the person for these numbers for the new and the
   previous release, over windows of the same length: request count, error
   count, new error types, and the deploy times. Use the same decision
   rules.

Commands and operations for each step are in
[references/operations.md](references/operations.md).

## Steps

### 1. Name the release exactly

List recent releases and copy the exact project, release, environment, and
service of the new release. Note the previous release of the same service
and environment.

```bash
logbrew read releases --project "$PROJECT_ID" --environment production --since 24h --json
```

### 2. Make sure the deployments are recorded

The comparison uses deployment records, not version labels or event times.
If the release pipeline does not record deployments yet, record the new
one now (account access is required). Use the exact values from step 1.

```bash
logbrew deploy "$DEPLOYMENT_ID" --project "$PROJECT_ID" --release "$RELEASE" --environment production --service "$SERVICE" --status succeeded --started-at "$STARTED_AT" --finished-at "$FINISHED_AT" --json
```

Add this command to the pipeline so that every later release is recorded.

### 3. Read the release comparison

```bash
logbrew explain release "$RELEASE" --project "$PROJECT_ID" --environment production --service "$SERVICE" --json
```

Record:

- `analysis.status`: `failures_observed`, `no_failures_observed`,
  `telemetry_observed`, or `insufficient_evidence`;
- `comparison.reason`; continue with the comparison only when it is
  `deployment_comparison_available`;
- `comparison.details.changes`: the count differences and the trace error
  rates of both releases;
- `comparison.details.assessment`: `improved`, `regressed`, `unchanged`, or
  `not_determined`, for the trace error rate only;
- `comparison.details.limitations`;
- `subject.trace_health`: the trace count and `error_rate_basis_points`
  of the new release (divide by 100 for a percentage). Read the trace count
  before you compare rates.

If `comparison.reason` names a missing deployment, record it (step 2) and
read again.

### 4. Find issues that are new in this release

List unresolved issues for the new release. For each issue with more than a
few events, read its first-seen release. An issue first seen in the new
release is a regression candidate. An older issue is not new, but check
whether its rate went up.

```bash
logbrew read issues --project "$PROJECT_ID" --release "$RELEASE" --environment production --service "$SERVICE" --status unresolved --since "$DEPLOYED_AT" --json
logbrew investigate issue "$ISSUE_ID" --occurrence first --json
```

### 5. Compare error logs

Read error logs of each release over windows of the same length. Divide by
the trace count or request count of the same window. Raw counts are not
adjusted for traffic.

```bash
logbrew read logs --project "$PROJECT_ID" --release "$RELEASE" --environment production --service "$SERVICE" --severity error --since "$DEPLOYED_AT" --json
logbrew read logs --project "$PROJECT_ID" --release "$PREVIOUS_RELEASE" --environment production --service "$SERVICE" --severity error --since "$PREVIOUS_START" --until "$DEPLOYED_AT" --json
```

### 6. Decide

| Decision | When |
| --- | --- |
| **Rollback** | An issue first seen in the new release fails a main user flow (sign-in, checkout, data save) and its events keep coming. Or the assessment is `regressed` with enough traffic, and the error rate is clearly higher. |
| **Go** | No new issue on a main user flow, the assessment is `improved` or `unchanged`, error logs per trace did not go up, and the new release has enough traffic. |
| **Wait** | Too little traffic, no comparison (`comparison.reason` is not `deployment_comparison_available`), the assessment is `not_determined`, or evidence is `unavailable`. Say what to check and when. |

Enough traffic: each release has at least 100 traces in the compared
window, so 1 more error trace changes the rate by 1 percentage point or
less. If the team has its own threshold, use it. A rollback of a release
with a database migration needs a person's decision; say so.

Never treat `not_found` or an empty list as zero errors when the release
also has no traffic. `unavailable` means LogBrew could not read the
evidence, not that there is none.

### 7. Report

```text
Decision: Go | Rollback | Wait
Release: <new> vs <previous>, <project>, <environment>, <service>
Traffic: <trace or request count> vs <count>
Trace error rate: <new %> vs <previous %> (assessment: <value>)
Error logs per trace: <new> vs <previous>
New issues: <issue, first seen release, events> or none
Limitations: <comparison limitations, missing evidence>
Next check: <what and when>, for Wait
```

For a failed release, the debug-production skill finds the cause of each
new issue.
