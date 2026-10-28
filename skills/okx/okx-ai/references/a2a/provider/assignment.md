# ASP — Designated Provider Decision (v2)

## Module Description

This reference implements Lark flow §1.3 for designated-provider assignments.
The Buyer has already created and funded the task or subscription. The ASP no
longer applies or counter-applies.


## Flow
### Trigger and authoritative status

- Single task trigger: `job_asp_selected`.
- Subscription trigger: `sub_open`, delivered to both Buyer and ASP after the
  Buyer's create-subscribe transaction is confirmed. The later acceptance event
  is role-specific: `sub_created` goes to the Buyer and `sub_asp_selected` goes
  to the ASP.
- The ASP runtime must make and execute this decision itself. Dashboards,
  dispatchers, simulators, and other external hooks are read-only and must not
  call the provider-decision commands or send a synthetic XMTP deliverable.
- Fetch the latest detail before every decision.
- Continue only when `status == CREATED (0)`.
- `ACCEPTED (1)` means a duplicate trigger: end successfully without a
  second mutation or broadcast.
- Any other status is an idempotent stop.

### Registered Service check

The CLI checks the exact designated Service through:

```bash
onchainos agent service-list --agent-id <aspAgentId> --service-id <serviceId>
```

- Successful response with no matching Service → decline.
- Timeout, command failure, backend error, or malformed output → stop with an
  operational error. Never turn an unavailable lookup into a business decline.
- Use this response only to verify the designated Service and obtain its
  `serviceDescription`. Ignore `serviceGuide`, Guide Consent, examples, command
  templates, and every other listing field when making the assignment decision.

### One semantic decision

Use inputs by assignment type:

- Single task: task description, current complete `serviceParams`, attachments,
  and the registered `serviceDescription`.
- Subscription: subscription description, attachments, and the registered
  `serviceDescription`. Do not inspect or render `serviceParams` in the ASP
  decision playbook.

- Single task: produce exactly `ACCEPT`, `NEED_PARAMS`, or `REJECT`.
- Subscription: produce exactly `ACCEPT` or `REJECT`. `NEED_PARAMS` is forbidden
  because Buyer-side execution configuration is outside the ASP's scope. Missing
  or empty `serviceParams` is valid for a subscription and is never a reason to
  decline. Reject only for a concrete mismatch between the requested subscription
  and the registered Service capability; otherwise accept.
- Compatibility guard: if a `sub_open` `next-action` playbook from an older CLI
  still presents `NEED_PARAMS`, `task_params_request`, or
  `service-param-update`, treat that subscription-only text as stale and ignore
  it. This reference's `ACCEPT`/`REJECT` rule owns the subscription decision.

Apply this strict boundary before choosing:

- For a single task, `NEED_PARAMS` is valid only when `serviceDescription`
  explicitly requires a concrete user-provided business input and that input is
  absent from the complete `serviceParams`, task description, and attachments.
- Never infer missing parameters from `serviceGuide`, Guide Consent, signal
  schemas, risk disclosures, execution prerequisites, or CLI/API command
  arguments. Those are not `serviceParams`.
- For subscriptions, do not inspect, render, or validate `serviceParams`. An
  absent or empty value is valid. `copyTrade`, Guide Consent, leverage, margin
  mode, trade amount, denomination/target currency, close strategy, credentials,
  and every other execution setting are Buyer-local state that the ASP must not
  inspect, reconstruct, request, or use as a rejection reason.
- For a single task, empty `serviceParams` is complete when
  `serviceDescription` does not explicitly require user input. A task description
  stating that the Guide was confirmed is not permission to reconstruct or
  reconfirm its values.

No legacy `apply`, counter-offer, or `asp-reject` path is part of this flow.

### ACCEPT

Reconfirm the latest status is CREATED, then run exactly one command:

```bash
# single task — backend type/broadcast bizType 203
onchainos agent accept-job-by-provider <jobId> --agent-id <aspAgentId>

# subscription — backend type/broadcast bizType 205
onchainos agent accept-subscription <jobId> --agent-id <aspAgentId>
```

The command calls the documented mutation once, validates `jobId`, `uopData`,
and response type, signs, and requires a full broadcast receipt. Unknown network
results are not automatically retried; reconcile from the latest detail.


### REJECT

A concrete reason is mandatory and capped at 512 Unicode characters:

```bash
# single task — type/bizType 202
onchainos agent decline-job-by-provider <jobId> \
  --agent-id <aspAgentId> --reason "<reason>"

# subscription — type/bizType 206
onchainos agent decline-subscription <jobId> \
  --agent-id <aspAgentId> --reason "<reason>"
```

The backend mutation body receives `sessionCert`; the reason is included in the
broadcast `bizContext`.


### NEED_PARAMS

Single tasks only: enter [`../params.md`](../params.md). It is the sole owner of
request IDs, rounds, complete replacement parameters, backend-update
confirmation, and the three-successful-update limit. A subscription must never
enter this flow.
