# Subscription Management

## Module Description

Use this Reference after `subscription.md` identifies one exact subscription. Device
receipt changes are owned by `receipt.md`; refunds are owned by
`refund-prepare.md`.


## Flow
### Post-creation handoff

After `create-subscribe` succeeds, state that messages go to all logged-in
devices and can be changed later. Then ask, without waiting before watch:

- Replay missed deliverables (default): background receipt continues and
  deliverables appear when the User returns.
- Discard offline deliverables: save the preference; the subscription remains
  active.

If the returned `offlineReplaySupported=false`, include the exact returned fix
commands and explain that the preference takes effect after upgrade. Never run
an independent capabilities probe.

Immediately process the returned `[Watch]` block and enter the exact scoped
runtime watch. Absence of the block ends the turn. The preference question must
not delay the initial watch or `sub_open` event.

For a `guide_direct` subscription, after the initial successful subscription
confirmation and immediately before entering that watch, render the localized
copy-trade status reminder in §Copy-trade status reminder. This is a
user-visible reminder, not part of the offline-delivery preference question.

### Management actions

| Intent | Command/boundary |
|---|---|
| Enable auto-renew | `onchainos agent start-autorenew <jobId>`; use the CLI confirmation/signing flow. |
| Cancel a subscription | See [Cancel subscription](#cancel-subscription) below. |
| Active subscription cost | `onchainos agent subscribe-cost` |
| Replay offline deliverables | Fresh-read; when changed, `subscribe-offline-update --job-id <jobId> --flag 0`, then reread. |
| Discard offline deliverables | Fresh-read; when changed, use flag 1, then reread and report support state. |
| Pause listening / stop receiving Signals on this device | Fresh-read the subscription and list devices, then use `subscribe-device-update --job-id <jobId> --device-list <all current receiver device IDs except this device>`. This overwrites the complete receiver list; preserve every other receiver and confirm before leaving no receiver. |
| Pause copy-trading but keep receiving Signals | Persist this device's signal-only preference: `subscription-execution-config-set --service-id <serviceId> --execution-mode signal_only`. |
| Receive/resume/listen for signals | Follow the scoped receipt flow below. |

Do not write when the fresh value already matches. A preference-write failure
does not roll back creation and does not authorize a retry.

### Scoped receipt flow

1. Resolve exactly one Active buyer subscription from an explicit Job ID/title
   or fresh current list/detail. Historical recency is not enough.
2. Run `subscribe-detail <jobId> --format json`.
3. Require Active status. Ensure this device receives using `receipt.md`; never
   collapse `deviceList:null` and `[]`, and never drop other device IDs.
4. Immediately before watch, fresh detail must show
   `thisDeviceReceives=true`.
5. For a `guide_direct` subscription, render the localized copy-trade status
   reminder in §Copy-trade status reminder after receipt is restored and before
   watch.
6. Enter `../../runtime/watch.md` with sticky `--job-id <jobId>`. Never substitute
   a global watch or claim that starting watch proves a new signal exists.

Restoring receipt does not recreate or modify Guide Consent. A missing Guide
or Consent keeps signals visible but disables local automatic execution. When
the User explicitly asks to resume automatic copy-trading on this device, use
`restore-copytrade.md`; it rebuilds the missing local Consent and execution
configuration from the runtime-recovered Guide.

### Copy-trade status reminder

When the fresh local execution configuration is `guide_direct`, render this as
a standalone user-visible message, localized to the conversation language:

> Automatic copy-trading is enabled. You can ask me about the copy-trading status at any time.

Show this reminder once after the initial successful subscription confirmation,
and once after a successful listening/receipt restoration. Do not show it for a
`signal_only` subscription, before the receipt gate succeeds, or on watch-loop
re-entry.

### Cancel subscription

Intent: cancel a subscription. Confirm `trialType` and `autoRenew` from the
fresh list/detail in hand.

- When the fresh status is Created(0), before ASP acceptance, do not run the
  standalone cancellation flow. Route to [`refund-prepare.md`](refund-prepare.md)
  and use only its bound `close_created_subscription` action. This closes the
  task; an exact-zero payment needs no refund, while a paid original amount is
  returned only after lifecycle and wallet-order reconciliation.

- When trial, or formal with `autoRenew=1`: run
  `onchainos agent subscribe-cancel <jobId>` — revokes a trial immediately, or
  stops a formal subscription's future auto-renew. A renewal change, not a
  refund.
- When formal with `autoRenew=0`, render:

  `{jobName} ({jobId}) already has auto-renew off. The service stays usable
  through {periodEnd}, then ends on its own with no further charge. Ending it
  sooner may require the refund/close flow.`

  `{periodEnd}`: locale date from `subEndTime` (fallback `subBufferEndTime`).
  Immediate termination → [`refund-prepare.md`](refund-prepare.md).


## Security
### Device and execution safety

- `deviceList:null` means default-all; `[]` means explicitly none.
- Any explicit receiver update is built from a fresh complete read and
  overwrites the entire list.
- Confirm before a removal that would leave no receiving device.
- "Pause listening" changes the server-side receiver list; "pause copy-trading" writes this device's `signal_only` execution preference. Neither action
cancels the subscription.
- Creation-time device selection is unsupported; configure it only after
  successful creation.
