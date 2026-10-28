# One-Time Task Creation

## Module Description

Enter only from `create-prepare.md` with the latest bound Service payload.
`decision=ready` does not authorize creation. Subscription Services route to
`subscription-create.md` instead, before this file's input-collection rules
are applied. In particular, never apply this file's 20–2000-character
Description requirement to a subscription.

## Flow

### Collect inputs

If `payload.serviceGuide` is non-blank, complete and independently confirm
`create-guide.md` first. Then parse only `payload.serviceDescription` for
explicit required and optional inputs. Ignore promotional text and never invent
scope.

Fill values from the User's request or direct answers. Ask for all missing
required values together; re-ask only missing or invalid values. Produce:

- `title`: concise, at most 30 characters;
- `Description`: requested outcome plus confirmed inputs, 20–2000 characters;
- `serviceParams`: only confirmed inputs required by the Service description;
- attachments: each explicit local file, retained for repeated `--file` flags.

If supplementary files are implied but absent, ask once whether to add them now
or after creation. Do not show a second standalone parameter confirmation.

### Final confirmation

scene: One-time job creation confirmation

display template:

```markdown
### One-time Job Creation Confirmation

- Job Name: {title}
- Job Description: {Description}
- Service Provider: {providerAgentName}(Agent {providerAgentId})
- Fee: {feeAmount} {feeTokenSymbol}
- Service Parameters: {serviceParams}

{payload.creationConfirmation}
```

display rules:

1. Preserve the confirmed Job Name, Job Description, and Service Parameters.
2. Render the Service Provider as `{providerAgentName}(Agent {providerAgentId})` when the name is available, or `Agent {providerAgentId}` otherwise.
3. Render a zero Fee as `Free`; otherwise render the exact amount and token symbol.
4. Render the Service Parameters item only when `serviceParams` is non-empty. Omit the Service Parameters line entirely when `serviceParams` is empty — `null`, an empty or whitespace-only string, `{}`, or any field-less JSON object. Treat falsy-valued fields (`false`, `0`, `""`) as non-empty and show the line.
5. Render attachments below the field list.
6. Keep Guide Consent in its separate confirmation.
7. `Confirm` is the explicit final confirmation for only the current complete card. Apply edits and render the whole confirmation again.
8. Keep the confirmation vertical: render exactly one field per bullet line and
   never combine fields into a horizontal table or inline prose.
9. Guide only the `Confirm` action. Do not add a `Cancel` action or cancellation
   instruction to the confirmation copy.

### Communication check

After confirmation, run once:

```bash
onchainos agent communication-check
```

`data.ok=true` without a note continues silently. Otherwise show the returned
hint/note and ask the User to choose Repair communication or Continue creation.
Repair uses `../../shared/chat-comm-init.md`. Reuse the confirmed task parameters;
do not repeat this check or the confirmation afterward.

### Create once

Use `payload.serviceId` for `--service-id`; `sid` is never the Service UUID.

```bash
onchainos agent create-task \
  --title <title> \
  --description <confirmed-description> \
  --provider-agent-id <payload.providerAgentId> \
  --payment-token-symbol <payload.feeTokenSymbol> \
  --payment-token-amount <payload.feeAmount> \
  --service-id <payload.serviceId> \
  --service-params '<confirmed JSON or {}>' \
  --service-token-address <payload.feeToken> \
  --service-token-amount <payload.feeAmount> \
  [--file <attachment> ...] \
  [--service-guide '<exact serviceGuide>' \
   [--service-guide-hash '<exact serviceGuideHash>'] \
   --guide-consent-json '<confirmed Consent JSON>']
```

Include the complete Guide bundle only for a non-blank Guide. Pass confirmed
Service context unchanged; do not repeat price, balance, or provider checks.
On `broadcast_submitted/watch_task`, hand the complete structured result
unchanged to [`../../runtime/watch.md`](../../runtime/watch.md). This leaf owns
the creation command through receipt of that result; Runtime Watch owns the
post-result sequence: initial one-time progress, watch banner, creation-start
note, then the scoped watch call. Creation is final only after `job_created`.
For an uncertain mutation result, query fresh task state before considering any
retry.
