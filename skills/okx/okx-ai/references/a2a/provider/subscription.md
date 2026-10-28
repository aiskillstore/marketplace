# A2A Provider Subscription

## Module Description

This file covers only ASP subscription behavior. Envelope routing, trust
boundaries, and action selection live in [`router.md`](router.md).

> **Fully gas-free**: every on-chain action by the ASP (`apply` / `deliver` / evaluation / refund / claim, etc.) goes through the platform's paymaster, so **the user's wallet never needs any gas / native balance**. **Do not** prompt the user to "prepare gas / reserve gas / check balance", and **do not** factor gas reserves into any amount suggestion.

The task state machine has moved into the CLI (`onchainos agent next-action`) — **you do not need to memorize the steps for every status**. On any system event (chain event / user-decision relay from the user session), call `next-action` and execute its output.

For provider-side `job_asp_reject_expire`, a subscription at Failed(9) is not
by itself proof that the Buyer received a refund: the same status also covers
charge or conversion failure, and the replayable event input cannot create
settlement provenance. Render the CLI's neutral result-unverified notification
verbatim (or faithfully localized); never upgrade it to refund-complete copy.
The User-side checkout applies its separate durable request-provenance gate.

---


## Flow
### Deposit-address QR (insufficient-balance — MANDATORY)

🛑 **Rule:** when any ASP command (`dispute raise`, `subscribe-dispute`, etc.) returns a JSON error containing a non-empty `depositAddress` field:
1. **Build notice**: run `onchainos agent funding-notice --chain <chain> --currency <symbol> --shortfall <amount> --deposit-address <addr> --format json` (add optional balance fields only if present).
2. **Relay**: `displayMode=terminal-unicode` → show `terminalQr` + full notice; `displayMode=image-notify` → localize `contentCanonical`, run `notifyCommandArgs`, put `markdownImage` under option 1.

---

### My Provided Subscriptions (provider view)

Trigger: `my provided subscriptions` / `subscriptions I provide`. Command: `onchainos agent my-subscriptions --role provider` → JSON `{ "list": [ … ] }`. Render each item. **Never drop Subscriber, Current Period, or Billing Period.**

| # | Service | Subscriber | Status | Current Period | Billing Period |
|---|------|--------|------|---------|------|
| 1 | {title} | Agent#{buyerAgentId} | {localizedStatusLabel} | {subStartTime}–{subEndTime} (render as dates) | {billingPeriod} |

- **Status**: render and localize the CLI-provided `statusLabel`; localize
  `statusDescription` when it is available. Do not display raw `status`,
  `statusName`, or `statusCode`. Billing Period distinguishes trial from paid.
- **Billing Period**: `trialType==1` → `Trial Period`; else positive integer `periodIndex` → `Billing Period {periodIndex}`; else null/non-positive → `—`.
- Timestamps are **epoch seconds** — render as locale dates.
- Empty list → "You have no provided subscriptions." Do NOT invent rows.
- Read-only display; ASP takes no on-chain action here.

### Subscription events (`sub_*`)

For the ASP, most later subscription events are display-only notifications. Two
events are action-required: `sub_open` owns the initial provider decision and
`sub_user_reject` owns the later refund/evaluation decision.

The ASP runtime owns this lifecycle end to end. An external dashboard,
dispatcher, simulator, or hook must not accept the subscription, synthesize a
deliverable, or send XMTP in response to these events. Such tooling may observe
state only.

For `job_asp_accept_expire`, `job_expired`, and legacy `submit_expired`, always
dispatch the CLI's structured result. Fresh provider-owned Expired(8) is
terminal: notify the ASP from authoritative task fields, then follow the
returned job-scoped `notify_and_cleanup_subscription` action. Paid non-trial
tasks state that the backend refund reached the Buyer; trial and zero-amount
tasks state that no refundable funds existed. Caller event fields, including a
nonzero caller-supplied code, cannot override a fresh matching Expired(8).

| Event | Action |
|---|---|
| `sub_open` | **Run the §1.3 provider decision inside the ASP runtime.** The backend sends this event to both Buyer and ASP after the Buyer's create-subscribe transaction is confirmed. Fetch latest subscription detail, require CREATED, verify the exact registered Service, then return exactly `ACCEPT / REJECT` and follow [assignment.md](assignment.md). Do not inspect or render `serviceParams`; missing or empty values are valid and must not trigger parameter clarification. |
| `sub_created` | Buyer-only acceptance event. Silently ignore if it is unexpectedly delivered to the ASP; `sub_asp_selected` owns the ASP acceptance-confirmed flow. |
| `sub_asp_selected` | **Run §1.5 inside the ASP runtime.** This is the current backend subscription-acceptance event; the Lark flow calls the stage `sub_accepted`, but do not wait for a separate event with that name. The CLI fetches authoritative subscription detail, renders the fixed acceptance notice to the ASP owner, then starts the registered Service's existing AI/Skill workflow. If output is ready now, hand it to §1.6 delivery; for schedule/event-driven services initialize that workflow without inventing an empty deliverable. |
| `sub_complete_notify` | Route the structured result through [`../completion.md`](../completion.md). |
| `sub_close_notify` | Render the CLI's canonical terminal `Content:` per the language rule below, then follow `session-cleanup`. End turn. |
| `sub_failed_notify` | The current event/status combination does not carry trustworthy charge-failure cause provenance. Fail closed: render only the CLI's incomplete/read-only result, emit no terminal marker, and do not run `session-cleanup`. Only a CLI result that independently establishes trustworthy cause provenance may use the canonical terminal charge-failure copy. End turn. |
| `sub_asp_agree` | The refund action is complete. End the turn after the action-command result. |
| `sub_asp_dispute` | Read [`evidence-upload.md`](evidence-upload.md) and continue the reason-and-evidence lifecycle; the existing evaluation request remains authoritative. |
| `sub_user_reject` | Read [`arbitration-decision.md`](arbitration-decision.md) and use its refund-or-evaluation decision template. |
| `sub_cancel` / `sub_trial_into_active` | **Not handled on the ASP side in this slice — silently ignore. End turn.** Buyer-only. |
| `sub_renew` | Renewal → the **previous period's income is now claimable**. Run `onchainos agent subscribe-asp-claim <jobId> --agent-id <yours>` (claims your own funds — no buyer action, do not send a peer message), then push a short localized note via `onchainos agent user-notify`; if the CLI reports nothing claimable, end the turn silently. |

##### ASP `sub_*` language rule

- **English ASP** → send the CLI `Content:` **verbatim**.
- **Any other language** → translate the CLI English content faithfully, preserving every field and omitted-clause behavior.
