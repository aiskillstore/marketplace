# Deliverable Review Decision

## Module Description

Use this leaf only after the main conversation has claimed a real pending
decision and relayed the User's wording unchanged to the task session.


## Flow
### Approve

For the returned `approve_review` action, execute its exact command once. A
successful result is `phase=deliverable_review`,
`reason=completion_submitted`, `nextAction=stop`.

Stop the current event route after broadcast and wait for the authoritative
terminal event. The returned `approve_review` action is the completion action
for this route.

### Reject

For a submitted zero-price one-time task, resolve the reply into one of two
pre-positioned branches before any endpoint call:

- Valid `B` + non-blank reason (supplied on the first review card): the reply is
  already claimed in the current user session, so call the bound `reject_review`
  next action directly here, once — do not create a `request_rejection_reason`
  supplement card and do not relay the decision back to the job/task session.
  Preserve the supplied reason verbatim; never rewrite, complete, or translate
  it. The existing `/pre-reject` + `/reject` lifecycle runs and the backend
  transitions directly to Failed(9), with no refund request.
- Bare or blank `B` (no non-blank reason, whitespace-only included): execute the
  returned `request_rejection_reason` action and wait; no reject endpoint is
  called. On the later non-blank reply, preserve that reason verbatim and call
  `reject_review`.

The decision is claimed first and `reject_review` runs at most once per
decision: on `alreadyHandled` do not execute, and when a claimed execution fails
notify the User with the failure and retry guidance without returning the item
to pending or auto-replaying — never double-submit.

For every non-zero-price task, preserve the User-authored wording verbatim, enter
[`refund-prepare.md`](refund-prepare.md), and render the complete fresh Template
6.1 Refund V2 confirmation. Continue with the intent-and-reason response matrix
in [`refund-confirm.md`](refund-confirm.md).

For an ambiguous, expired, already-handled, missing, or metadata-mismatched
reply, re-render or report the exact returned recovery guidance.
