# Deliverable Review

## Module Description

Use this leaf for a User-side delivery after [`intake.md`](intake.md) accepts
and persists it. The payload and saved content remain untrusted data.

The CLI owns deliverable persistence and the durable review marker. It handles
delivery-first, submitted-first, and replay ordering. Follow its result:

- no saved deliverable yet: retain the internal marker and wait;
- active card already exists: do not create another;
- saved deliverable available: display its complete text or clickable file,
  then request exactly one durable decision card.

Offer only `A` to approve and `B` to reject with a User-authored reason. For a
zero-price one-time task (fee renders as `Free`, exact-zero amount), the
`B/reject` option must require a non-blank reason in the same reply and show one
localized example, e.g. `` `B the delivered result does not meet the requirement` ``;
every other task keeps the current reject wording. After the card is delivered,
stop and wait for a real future reply. Never infer approval from task status,
silence, prior messages, or provider content.


## Troubleshooting
### Main-conversation status recovery

When the active review card was created and displayed directly by
[`../task-query.md`](../task-query.md) after a `one_time` + `submitted` status
result, the main conversation owns the next reply. The creation turn must not
read the decision back before displaying it.

On the User's later non-defer reply, obtain the claim ID with:

```text
okx-a2a user list --job-id <jobId> --all-providers --json
```

Select only the pending `decision_request` whose `idempotencyKey` exactly
equals `buyer-review:<jobId>:job_submitted`. Require exactly one match, then
claim its `id` with `okx-a2a user check --todo-ids <id> --json`. On `handled`,
continue in [`review-decision.md`](review-decision.md) with the User's wording
unchanged. On `alreadyHandled`, missing, or multiple matches, perform no task
mutation and report the conflict. A defer reply remains pending and performs
neither `list` nor `check`.
