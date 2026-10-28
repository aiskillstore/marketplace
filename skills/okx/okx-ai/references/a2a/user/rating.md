# User Task Rating

## Module Description

Use this flow when a Buyer provides their own rating for an Active subscription
or a Completed A2A one-time task/subscription. A user-authored rating is keyed by
the selected `jobId` and replaces any AI-generated rating for that same Job.
Viewing an Agent's existing reviews or reputation remains an Identity query.

Never use this flow for A2MCP. Never rate a one-time task before it is Completed.


## Flow
### Select the Job

Build the eligible set from these queries:

```bash
onchainos agent my-tasks --task-type subscription --status-type 1 --page 1
onchainos agent my-tasks --task-type subscription --status-type 2 --page 1
onchainos agent my-tasks --task-type one-time --status-type 2 --page 1
```

- Keep every returned Active subscription.
- From both ended lists, keep only rows whose authoritative status is Completed.
  Exclude Rejected, Refunded, Closed, Expired, Failed, and every other status.
- A `jobId` in the current request must match an eligible returned row exactly.
  A `jobId` carried only by earlier completion context must be revalidated against
  these results before use. Continue pagination only while `hasNext=true`, and
  stop once the exact row is found.
- Without a confirmed `jobId`, continue all three eligible-list queries through
  their available pages. For every eligible row, run the `task-feedback` lookup
  from **Inspect an existing rating**, binding that row's `buyerAgentId` and
  `jobId`. Keep only rows whose lookup succeeds with an empty `data[]`; these are
  the unreviewed candidates. If any lookup fails, report that the unreviewed list
  could not be verified and stop instead of showing an incomplete or unfiltered
  list.
- If the unreviewed set is empty, say that no unreviewed A2A jobs were found and
  stop. Otherwise, show the localized equivalent of `I found the following
  unreviewed A2A jobs. Please select the job you want to rate.`, then render this
  compact table and wait:

  | # | Job | Provider | Status | Job ID |
  |---|---|---|---|---|
  | 1 | `<title>` | `Agent#<providerAgentId>` | `<localizedStatusLabel>` | `<jobId>` |

Populate every table cell from its returned row. Render and localize the CLI
`statusLabel`; do not display raw `status`, `statusName`, or `statusCode`.
Use only the selected row's `jobId`, `buyerAgentId`, and `providerAgentId`. Stop
if the row or either Agent ID is missing. Do not substitute detail, status,
device, or task-session data. Do not add fee, renewal, device, or billing fields
to the selection table.

### Inspect an existing rating

```bash
onchainos agent task-feedback \
  --agent-id BUYER_AGENT_ID_ARG \
  --task-id JOB_ID_ARG
```

Bind both arguments to the selected row. If `data[]` is non-empty, tell the User
that submitting the new score and review will replace the existing rating for
this `jobId`. Do not stop or require a separate overwrite confirmation. An empty
`data[]` means this is the first rating for the Job. Do not repeat this lookup
after the User selects a row from the already verified unreviewed candidate
table.

### Collect the rating

Require both values from the User:

- `score`: `0.00`–`5.00`, with at most two decimal places.
- `description`: concrete, non-blank review text.

Keep valid values already supplied and ask once for all missing or invalid
values. A sentiment-only request is not review text. Never draft, infer,
translate, or rewrite the description.

The User's complete score-and-description reply authorizes one submission; do
not request another confirmation.

### Submit

```bash
onchainos agent feedback-submit \
  --agent-id PROVIDER_AGENT_ID_ARG \
  --creator-id BUYER_AGENT_ID_ARG \
  --score SCORE_ARG \
  --task-id JOB_ID_ARG \
  --description REVIEW_ARG
```

Bind Agent and task IDs to the selected row. Pass the User's score and review
verbatim, with each dynamic value as one literal argv value. The backend keys
the rating by `jobId`; this submission replaces an existing AI-generated rating
for the same Job. Submit once; never retry an unknown result automatically.

### Result

Only `ok=true` with a non-empty `data.txHash` proves success. Render a localized
success result in this order:

```text
Review submitted.

- Task ID: <jobId>
- Score: <score> / 5
- Review: <description>
- Transaction hash: <txHash>
```

Use the selected and submitted values verbatim. On command failure or a missing
transaction hash, report the error and do not claim that the rating succeeded.
