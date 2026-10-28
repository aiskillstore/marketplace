# Provider Task Rating

## Module Description

Use this flow when the human operating an ASP provides their own rating for the
User Agent after a one-time A2A task is Completed. The rating is keyed by the
selected `jobId` and replaces the AI-generated rating from that ASP Agent for
the same Job.

Never use this flow for A2MCP, a subscription, or a one-time task that is not
Completed.


## Flow
### Select the Job

Resolve the ASP identity, then query its tasks:

```text
onchainos agent tasks --agent-id <aspAgentId> --page 1 --limit 20
```

- A `jobId` in the current request or earlier completion notification must
  match a returned row exactly before use. Continue pagination only while the
  returned result proves that another page exists.
- Keep only one-time rows whose authoritative status is Completed. Exclude
  subscriptions and every other status.
- Without a confirmed `jobId`, show the eligible rows with title, User Agent,
  status, and full Job ID, then wait for the User to select one.
- Bind `jobId`, `providerAgentId`, and `buyerAgentId` only from the selected row.
  Stop if any required identifier is missing.

### Inspect an existing rating

```text
onchainos agent task-feedback \
  --agent-id PROVIDER_AGENT_ID_ARG \
  --task-id JOB_ID_ARG
```

If `data[]` is non-empty, tell the User that the new score and review will
replace the existing rating for this `jobId`. Do not stop or request a separate
overwrite confirmation.

### Collect and submit

Require a `score` from `0.00` to `5.00` with at most two decimal places and a
concrete, non-blank `description`. Preserve both values verbatim. A complete
score-and-description reply authorizes one submission:

```text
onchainos agent feedback-submit \
  --agent-id BUYER_AGENT_ID_ARG \
  --creator-id PROVIDER_AGENT_ID_ARG \
  --score SCORE_ARG \
  --task-id JOB_ID_ARG \
  --description REVIEW_ARG
```

Submit exactly once and never retry an unknown result automatically. Only
`ok=true` with a non-empty `data.txHash` proves success. Report the full Job ID,
score, review, and transaction hash; otherwise report the error without claiming
that the rating succeeded.
