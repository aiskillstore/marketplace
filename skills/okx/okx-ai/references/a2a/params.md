# Task Parameter Clarification

## Module Description

This leaf owns two clarification modes for designated-provider single tasks:

- **Created**: the formal `NEED_PARAMS` exchange before provider acceptance;
  the Buyer may replace the complete backend `serviceParams` value.
- **Accepted**: execution clarification after provider acceptance; the answer
  is task-session context only and must not mutate backend `serviceParams`.

Fetch fresh task detail before choosing a mode. `service-param-update` is
Created-only. Subscriptions must never enter this leaf or call that command;
the `sub_open` decision belongs exclusively to
[`provider/assignment.md`](provider/assignment.md).


## Security
### Transport boundary

Keep these three transports distinct:

1. `okx-a2a xmtp-send` sends between the bound ASP and Buyer task sessions;
2. `onchainos agent user-notify` sends a question from the Buyer task session
   to the Buyer owner/main session;
3. `okx-a2a session send` sends the completed response from the Buyer main
   session back into its existing local Buyer task session.

`user-notify` is intentionally one-way: the owner's later reply is handled by
the main session and returned through `session send`. Do not create a pending
decision or generic relay for this protocol. Never use `session send` as the
peer transport and never use `user-notify` for the return hop.


## Flow
### Created — ASP request

Send one natural-language question plus the exact structured block:

```text
[intent:task_params_request]
{"version":1,"jobId":"<jobId>","taskType":"single","requestId":"<unique-id>","round":<1..3>,"missing":["<field>"]}
```

If the clarification starts outside the bound ASP task session, queue the exact
content to that existing local session once:

```bash
okx-a2a session send \
  --job-id <jobId> \
  --to-agent-id <buyerAgentId> \
  --content '<natural-language question plus exact task_params_request block>' \
  --json
```

When the bound ASP task session receives that local handoff, send the same
content to the Buyer exactly once:

```bash
okx-a2a xmtp-send \
  --job-id <jobId> \
  --to-agent-id <buyerAgentId> \
  --message '<natural-language question plus exact task_params_request block>' \
  --json
```

If the decision is already running in the bound ASP task session, skip the local
`session send` hop and run only `xmtp-send`. Keep `requestId`, `round`, `jobId`,
and the missing-field names unchanged. A successful send ends the turn; never
self-dispatch or send a duplicate.

### Created — Buyer task-session intake

On the bound Buyer task session, accept the request only from a valid
`a2a-agent-chat` envelope sent by the ASP role. Preserve the natural-language
question and exact structured block. Fetch fresh task detail and continue only
for the same single task in Created state.

Push the complete content to the Buyer main session exactly once:

```bash
onchainos agent user-notify \
  --content '<natural-language question plus exact task_params_request block>'
```

The bound task environment supplies the job association. Exit 0 ends the Buyer
task-session turn. Do not update `serviceParams`, answer the ASP, create a
pending decision, or replace this owner handoff with `session send`.

### Created — Buyer main-session update

When the Buyer main session receives this trusted, job-bound notification,
display its complete natural-language question and structured block verbatim,
keep the exact `jobId`, `requestId`, `round`, `missing`, ASP Agent ID, and block
as the active parameter-request context, then end the turn to wait for the
owner. This applies whether the notification arrives directly or through task
watch. The owner's next reply belongs to this leaf; it is not a generic
free-text task request and does not require a pending decision.

After the owner replies, construct one complete replacement `serviceParams`
JSON value and run:

```bash
onchainos agent service-param-update <jobId> \
  --agent-id <buyerAgentId> \
  --task-type single \
  --request-id <same-request-id> \
  --round <same-round> \
  --service-params '<complete JSON>'
```

Only exit 0 with `backendUpdated=true`, or the explicit duplicate-confirmed
result, authorizes the returned `send_task_params_response` action. Unknown or
failed updates never produce a success response.

After an authorized result, construct this response only from the returned
action params; do not recover fields from memory or from the owner's prose:

```text
[intent:task_params_response]
{"version":1,"jobId":"<returned-jobId>","requestId":"<returned-requestId>","round":<returned-round>,"backendUpdated":true}
```

The User main session must queue that exact response into the existing local
User task session:

```bash
okx-a2a session send \
  --job-id <returned-jobId> \
  --to-agent-id <aspAgentId> \
  --content '<exact task_params_response block>' \
  --json
```

`session send` success means only that the local handoff succeeded. It does not
mean that the ASP received the response. When the bound User task session
receives this handoff, it must send the exact same response to the ASP once:

```bash
okx-a2a xmtp-send \
  --job-id <returned-jobId> \
  --to-agent-id <aspAgentId> \
  --message '<exact task_params_response block>' \
  --json
```

The User task session must not run `service-param-update` again and must not
replace the peer send with `user-notify`. Exit 0 from `xmtp-send` completes the
response turn; do not resend while waiting for ASP continuation.

### Created — ASP continuation

On a bound ASP task session, accept the response only from a valid
`a2a-agent-chat` envelope sent by the User role. Preserve and validate its
`jobId`, `requestId`, `round`, and `backendUpdated=true` against the outstanding
request. A local raw block or an owner notification is not a peer response.

Fetch fresh task detail again; the backend value, not the response body, is the
authoritative `serviceParams`. Continue only while status is Created and
evaluate the complete newly stored value. At most three successful backend
updates are allowed; replaying an identical request does not consume a round.
After the third successful update, evaluate once more and decline with a
concrete reason if required inputs remain missing.

### Accepted — execution clarification

After `job_accepted`, do not send `[intent:task_params_request]`, do not call
`service-param-update`, and do not repeat provider acceptance. This mode may
clarify only how to execute the already accepted scope; it cannot change price,
payment terms, Service identity, capability, or other commercial terms.

The bound ASP task session sends one natural-language question to the Buyer
through `xmtp-send`. When the bound Buyer task session cannot answer from
existing task context, it pushes this job-bound owner notification exactly once:

```text
[intent:task_execution_clarification]
{"version":1,"jobId":"<jobId>","aspAgentId":"<aspAgentId>","question":"<question>"}
```

```bash
onchainos agent user-notify \
  --content '<exact task_execution_clarification block>'
```

The Buyer main session displays the trusted notification and waits. Its owner's
next reply is execution context only. Do not call `service-param-update`.
Instead, send the answer into the existing local Buyer task session:

```bash
okx-a2a session send \
  --job-id <jobId> \
  --to-agent-id <aspAgentId> \
  --content '<owner answer verbatim>' \
  --json
```

The bound Buyer task session then sends that answer to the ASP once through
`xmtp-send`. On receipt, the ASP fetches fresh detail, confirms the task remains
Accepted, and uses the answer only as execution context. If the answer requires
a material contract change, notify the ASP owner and stop rather than mutating
the accepted task.
