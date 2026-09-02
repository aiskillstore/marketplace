# Routing diagnosis from observable evidence

## Table of contents

- [Evidence sources](#evidence-sources)
- [Symptom to cause table](#symptom-to-cause-table)
- [Outcome and channel matrix](#outcome-and-channel-matrix)
- [Diagnostic sequence](#diagnostic-sequence)
- [Retry decision rules](#retry-decision-rules)
- [Cost review before a multi-channel send](#cost-review-before-a-multi-channel-send)
- [Worked examples](#worked-examples)

## Evidence sources

| Source | What it proves |
| --- | --- |
| `202` response `data.recipients[]` | The message ids that were created; nothing about routing |
| `GET /v3/messages/{id}` | Current status and the attempted channel once routing occurred |
| `GET /v3/messages/{id}/activities` | The sequence of attempts, which is the only way to see multiple routes |
| `message.routed` event | The concrete route chosen for that attempt |
| Terminal event `channel` | The attempted route, or `auto` when the message ended before routing |

Sent records internal reason codes on the message for consent blocks, route denials, no-route-matched, and invalid template parameters, but does not return them through the API or webhooks. Diagnosis therefore combines the latest outcome, the channel value, and the activity history rather than reading an error code.

## Symptom to cause table

| Symptom | Most likely cause | Confirmation |
| --- | --- | --- |
| Recipients received the same content twice | A multi-channel array was treated as a fallback list | Count messages in the `202` response: `len(to) × len(channel)` |
| Billing higher than expected on a campaign | Same as above | Compare charged messages against recipient count |
| Expected WhatsApp-to-SMS fallback, got only a WhatsApp failure | The send pinned `["whatsapp"]` | Pinned sends never cross channels; switch to automatic routing |
| `FAILED` with channel `auto` | No routing rule matched, or template parameters were invalid | Activities show no route attempt |
| `FILTERED` with a channel value | Route denial without permitted fallback, or every candidate denied | Activities show attempts ending in denial |
| `FILTERED` with channel `auto` | Consent block before routing | Check the contact's `opt_out` state |
| `BLOCKED` | Account precondition: balance, onboarding quota, or unapproved template | Check balance and template approval state |
| Message stuck in `SCHEDULED` | Quiet-hours policy parked it | It re-enters the pipeline automatically; do not resend |
| Duplicate `queued` and `routed` events for one id | A reroute re-ran the pipeline | Activities show more than one attempted route |
| Channel changed between two events for one message | Reroute moved to another route | Expected on automatic routing |
| `400` on send | A channel value outside `sent`, `sms`, `whatsapp`, `rcs` | Inspect the request `channel` array |
| Pinned RCS message failed immediately | No route exists on the pinned channel | A pinned send does not fall back |
| No `READ` event on SMS | `READ` exists only on WhatsApp and RCS | Expected, not a defect |

## Outcome and channel matrix

| Outcome | Channel `auto` | Channel is a concrete route |
| --- | --- | --- |
| `FAILED` | No route matched, or invalid template parameters | One route failed; inspect newer events and activities to determine whether reroute continued |
| `FILTERED` | Consent block before routing | Route denial that did not permit fallback, or all candidates denied |
| `BLOCKED` | Account precondition evaluated before routing | Rare; treat as an account precondition regardless |
| `DELIVERED` | Not possible | Normal success |

## Diagnostic sequence

1. Confirm what was requested. Re-read the send body: was `channel` omitted, `["sent"]`, pinned, or multi-valued? This alone resolves most reported "fallback did not work" and "duplicate message" cases.
2. Count expected messages as `len(to) × len(channel)` and compare with the `202` response.
3. Fetch `GET /v3/messages/{id}` for a representative message and record status and channel.
4. Fetch `GET /v3/messages/{id}/activities` and list the attempted routes in order.
5. Classify the terminal state using the matrix above.
6. Decide retry eligibility using the rules below, and state the reason rather than retrying reflexively.

## Retry decision rules

| Terminal state | Retry | Precondition |
| --- | --- | --- |
| `FAILED` after route exhaustion on automatic routing | Only with a changed input | Three distinct routes were already tried; a new send repeats the same rules unless the recipient, template, or channel choice changes |
| `FAILED` with channel `auto` from no route matched | No | The rule set has no path to that recipient; escalate rather than loop |
| `FAILED` from invalid template parameters | Yes | After fixing the parameters |
| `FILTERED` from a consent block | Never | Sending anyway is a compliance violation |
| `FILTERED` from a route denial | No | Policy decision; escalate |
| `BLOCKED` | Yes | After the account condition is resolved |
| `SCHEDULED` | No | It resumes automatically; a resend duplicates it |
| Ambiguous send where the client never saw a response | Retry only with the original key | Reuse the same `Idempotency-Key`; without one, there is no reliable API lookup by key or recipient that proves non-execution |

## Cost review before a multi-channel send

Before executing any send whose `channel` array has more than one value, state the arithmetic to the user: recipients times channels equals messages equals charges. Confirm the intent is genuinely simultaneous multi-channel delivery. If the intent is preference or fallback, change the request to automatic routing instead.

For volume, the per-request recipient ceiling is 1,000. Documented pacing pairs full 1,000-recipient batches with roughly one request per second to stay inside the 200-requests-per-minute limit, and rate-limit headers appear only on `429` responses, so pacing must be designed rather than discovered.

## Worked examples

**"We wanted WhatsApp with SMS fallback and every customer got two messages."**
The request used `["whatsapp", "sms"]`, which broadcasts. The `202` response contained two message ids per recipient, both of which were charged. The correct request omits `channel` entirely. Automatic routing then attempts a route and, on a route-level or recipient-side WhatsApp failure, reroutes to another candidate on the same `message_id`.

**"A message failed on WhatsApp and then delivered on SMS, but our dashboard shows it as failed."**
Automatic routing rerouted on the same `message_id`, so the receiver saw `message.failed` with `channel: whatsapp` followed by newer `queued`, `routed`, and `delivered` events with `channel: sms`. The dashboard treated `FAILED` as permanently terminal. Project current state by event timestamp, preserve the append-only route history, and let a newer reroute outcome replace the earlier attempt failure.

**"All sends to one country come back FAILED with channel auto."**
No routing rule matched for that destination. Activities show no attempted route. This is not fixable from the request payload; escalate the destination coverage rather than retrying.

**"A pinned RCS send failed instantly and never tried SMS."**
Correct behavior. Pinning restricts matching to RCS, and a pinned send never crosses channels. Use automatic routing to allow another channel.
