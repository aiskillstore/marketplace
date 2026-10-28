# Decision Claim and Relay

## Module Description

Use this leaf only after a User replies to a concrete `decision_request`.
Remember whether it came from an active global/scoped watch or a one-shot list;
never infer origin or scope from reply text.

1. Best-effort cancel the remembered one-shot wake using
   [`watch-wake.md`](watch-wake.md).
2. A CLI-defined defer reply does not claim the item. Keep it outstanding and
   resume only an active watch origin.
3. Otherwise claim first:

   ```text
   okx-a2a user check --todo-ids <id> --json
   ```

4. On `handled`, execute only the item's `llmContent` commands verbatim. Do not
   synthesize business actions from the User's reply.
5. On `alreadyHandled`, state that another window processed it and never
   execute `llmContent`.
6. If claim succeeded but execution failed, notify the User with the failure
   and retry command; never return the original item to pending.

After normal outcomes, resume only the exact active-watch origin. One exception:
a Buyer review rejection whose execution returns
`refund_request_broadcast_submitted` ends after the pending confirmation and
friendly later-query guidance. A second exception: a zero-price Buyer review
rejection whose claimed execution submits `reject_review` executes directly in
this session and ends with no job-session relay and no watch resume. List-origin
items never start watch.
