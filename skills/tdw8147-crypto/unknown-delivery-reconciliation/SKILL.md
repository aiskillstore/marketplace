---
name: unknown-delivery-reconciliation
description: Use after a timeout or ambiguous receipt; reconcile the original delivery and give one bounded next step without resending.
---
# Unknown Delivery Reconciliation

Replace “it errored, send again” with a record that says what happened to the original request and what evidence would close it.

## When to use

- An upload times out after the server may have accepted it.
- The outbound service says `sent`, but acceptance requires `delivered`.
- Two status views disagree or use different identifiers for what may be one request.
- A same-named replacement attachment exists and the receipt must be matched to the submitted bytes.
- An operator needs a conclusion now even though the receipt console is unavailable.

## When NOT to use

- You are preparing a first submission that has not been attempted.
- The original request already has a trusted receipt at the required level; close it without reopening.
- The concern is whether form input registered before any submission.
- The user needs a general integration design, not a record about an existing attempt.
- The task is to diagnose a local draft-save error unrelated to any outbound action.

## Core rules

1. **Deliver a record from current evidence.** Missing fields should not delay an actionable conclusion.
2. **Never replay the same intent.** A new identifier, the original identifier, or a test click can all duplicate a request that already took effect; do not assume remote idempotency.
3. **Anchor identity at submission.** Target, time and submitted byte fingerprint distinguish lookalike requests and same-named replacements.
4. **Prefer the latest formal match, not the latest timestamp alone.** Fresh evidence for another target or unlinked request says nothing about the original.
5. **Keep receipt levels separate.** A channel may accept, send, deliver and report reading at different points; one does not certify the next.
6. **Do not turn weak negatives into definitive failure.** Timeout, post-acceptance errors, zero local counts or no search result can coexist with a remote effect.
7. **If material conflicts cannot be resolved, record unknown.** A bounded original-only lookup is useful even when certainty is not available now.
8. **Stop at the required level.** A delivery requirement does not create a read-receipt task.

## Workflow

### 1. State what the user needs

- Write the acceptance level in the user's terms.
- Map it to the channel's documented status meanings if available.
- If the mapping is missing, retain the raw label and mark the definition not provided.
- Distinguish successful document submission from the business action being reconciled.

### 2. Identify the original attempt

- Record ID, target, submit time and the content or attachment fingerprint at submit.
- Mark absent fields `not provided`.
- Label timeout or observation time separately from submit time.
- Do not substitute a new file hash, a matching name, or similar text.

### 3. Sort observations by identity and then time

- Record the observation time, entry point and verbatim status.
- Match the original request's identity before comparing freshness.
- Separate other requests, other recipients and status rows outside the scope.
- For possible aliases, retain the unresolved mapping rather than assuming equivalence.
- Explain whether a conflict is genuine or just a receipt for a different object.

### 4. Write the narrowest conclusion the evidence supports

- `accepted`: the channel took custody, if that is its stated meaning.
- `sent`: the channel dispatched it, if defined that way.
- `delivered`: the destination received it as the channel defines receipt.
- `read`: the channel specifically reports read; do not infer from delivery.
- `definitely not sent`: authoritative evidence establishes no send for the original request; weak negatives alone never qualify.
- `outcome unknown`: identity, status, or a material conflict remains unresolved.

### 5. Close or name one bounded lookup

- If the required level is met, write no next action.
- Otherwise specify one original-request query with an attempt cap or expiry and a stop result.
- If access is missing, deliver now; name the proposed lookup, not a completed check.
- In simulations use supplied material only, without touching a real channel.
- With draft and submit tools, write the full record first and submit it in that order in the same round.

## Output template

```markdown
# Original delivery — [request]
Acceptance requires: [channel level / evidence]
Original: [ID] | [target] | [submit time] | [submitted fingerprint]

## Last relevant observation
- [query time] | [entry point] | [raw status] | [channel definition]
- Identity match: [what links this receipt to the original]
- Excluded or unresolved: [other record and why it cannot settle this request]

## Conclusion
- [accepted / sent / delivered / read / definitely not sent / outcome unknown]
- Acceptance: [met / unmet / unverified] because [evidence and gap]

## Next step
- [closed — no action] OR [one original-only query + limit + stop result]
- [proposed, not executed, if applicable]
```

If a field is unavailable, write `not provided` and deliver the rest.

## Worked examples

### Example 1 — The latest row belongs to a different target

**Input.** Upload `u-82` to `review-east`, submitted at 10:14 UTC with hash `9cf`, timed out.
At 10:16 the original status panel reported `delivered` for that target and hash.
At 10:17 a different request to `review-west` reported `sent`. The user requires delivery, not reading.

**Bad**

> The latest status says sent, so wait for read or upload a new copy to be safe.

**Good**

> Original: `u-82` | `review-east` | 10:14 UTC | hash `9cf`.
> Last relevant observation: 10:16 UTC in original status panel; `delivered` means destination receipt.
> The 10:17 `sent` row targets `review-west` and does not supersede the matching receipt.
> Conclusion: delivered; acceptance met. Closed — no action, no wait for read.

**Why it works.** Identity wins over raw recency and the record closes at the requested level.

### Example 2 — A replacement PDF after a timeout

**Input.** Request `p-31` to `proof-queue` at 16:03 UTC used `proof.pdf` with hash `0b4`.
The local client timed out; its counter remained zero. A dashboard search by filename finds a sent record for hash `21a`.
The original request status view has not been checked. The user needs delivered status.

**Bad**

> Nothing went out. The same filename is in Sent now anyway, so mark delivered.

**Good**

> Original: `p-31` | `proof-queue` | 16:03 UTC | hash `0b4`.
> Last observation: local timeout, zero counter; observation time not provided. Neither establishes a remote failure.
> Dashboard `sent` row refers to hash `21a`, not the submitted bytes. No matched receipt definition or level is available for `p-31`.
> Conclusion: outcome unknown; delivery unverified.
> Proposed only: query `p-31` once in its original status view; stop if the matched receipt says delivered or after that attempt. If unresolved, retain unknown. Do not resend.

**Why it works.** A filename match cannot transfer delivery evidence between different payloads.

## Common mistakes / red flags

| Red flag | Better record |
|---|---|
| “Same ID, so a retry is safe” | Keep the original ID for lookup, not replay. |
| “Same filename, same attachment” | Compare the original submitted fingerprint. |
| “No record means nothing happened” | Say where you looked and keep unknown unless stronger evidence settles it. |
| “Sent is good enough” | Compare the documented level to the requested one. |
| “Newest row wins” | First match target, time, fingerprint and original identity. |
| “We'll keep polling” | Name a count or expiry and preserve the unresolved result at the cap. |

## Self-check

- [ ] The requested acceptance level is explicit.
- [ ] Original ID, target, submit time and fingerprint are present or marked missing.
- [ ] Submit and observation times are separate.
- [ ] The latest relevant receipt has a raw label and a channel definition or explicit gap.
- [ ] Mismatched or unresolved evidence is not promoted to a conclusion.
- [ ] Unknown does not become definitely not sent on weak evidence.
- [ ] There is one bounded original-only query or an explicit closeout.
- [ ] Proposed checks are not reported as performed; nothing was replayed.

## Stop at delivery

Deliver the reconciliation record. It performs no first send or repeat send; submitting the record is a different action.
In simulated work, record the next query as a suggestion and do not contact the channel.
