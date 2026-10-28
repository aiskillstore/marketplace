# Subscription Creation

## Module Description

Enter from `create-prepare.md` only when the authoritative payload supports a
subscription. Complete `create-guide.md` when a non-blank Guide is present.
Retain any collected Guide Consent for the final card below without asking for
a separate confirmation. One-time tasks never configure automatic copy-trading.

## Flow
### Automatic copy-trading preference

Do not narrate internal preparation, classification, or local persistence steps
to the User. In particular, do not say that `task-create-prepare` is running,
that a Guide was classified, that `subscription-execution-config` was saved, or
that a subscription will or will not enter GuideDirect/claim. Surface only the
next User-facing question, the final confirmation card, or a real blocking
error returned by the CLI.

Subscription execution classification has three cases:

1. If `payload.serviceGuide` is blank or null, classify the subscription as
   pure signal. Silently save `subscription-execution-config=signal_only`,
   omit the entire Guide bundle, and do not ask automatic copy-trading or Guide
   Consent questions.
2. If `payload.serviceGuide` is non-blank and the Guide explicitly asks whether
   automatic copy-trading is enabled, save the User's unambiguous answer as
   `guide_direct` or `signal_only` and collect only the Guide-defined Consent
   values.
3. If `payload.serviceGuide` is non-blank and the Guide does not ask for
   automatic copy-trading, classify the subscription as pure signal. Silently
   save `subscription-execution-config=signal_only`; use `{}` only when the
   Guide asks no non-sensitive Consent fields. Do not explain this internal
   signal-only classification to the User, especially for non-trading Guides.

1. For a subscription without a Guide, save `signal_only` before the final
   confirmation and do not load `create-guide.md`.
2. For a subscription with a Guide, `create-guide.md` saves the User's explicit
   automatic copy-trading answer only when the Guide itself asks that question
   and the User gives an unambiguous answer.
3. Do not ask an additional platform-level mode question or save it again here.
4. Do not infer `guide_direct` from signal wording, amounts, leverage, target
   assets, or `serviceDescription`.

### Business data and confirmation

Derive `title` (≤30 characters) and Description (≤4096 characters) from the
selected Service and the User's confirmed Guide answers. They are required
subscription fields, not ASP configuration and not merely a local record. Do
not ask the User to supply them when they can be derived; ask only when a
required value is ambiguous or cannot be formed safely. Never require the User
to write a task/subscription description of any minimum length, including more
than 20 characters; the one-time-task 20–2000-character rule does not apply.
Collect explicit Service inputs and attachments. Ask exactly one subscription
preference question: whether to enable auto-renew, and retain the User's
explicit answer as `autoRenew`. Render this single-subscription confirmation as
a field list. Render [Subscription Creation Confirmation](#subscription-creation-confirmation).
Continue only after that final confirmation and the one-time communication
check defined by `create.md`.

### Create subscription

```bash
onchainos agent create-subscribe \
  --service-id <payload.serviceId> \
  --service-token-amount <payload.subscriptionInfo.feeAmount> \
  --service-token-address <payload.feeToken> \
  --auto-renew <retained-autoRenew> \
  --title <title> \
  --description <confirmed-description> \
  --provider-agent-id <payload.providerAgentId> \
  --service-interval <payload.subscriptionInfo.interval> \
  [--service-params <confirmed-non-empty-JSON>] \
  [--file <attachment> ...] \
  [--service-guide '<exact serviceGuide>' \
   [--service-guide-hash '<exact serviceGuideHash>'] \
   --guide-consent-json '<confirmed Consent JSON>'] \
  --format json
```

The CLI owns Guide execution-profile persistence and broadcast activation.
`type` and `bizType` must both be 204.

1. If the Guide collected an explicit automatic copy-trading preference, it was
   already saved before creation; do not save or migrate it by `jobId`.
2. If the Guide is blank or no Guide answer enabled automatic copy-trading,
   `signal_only` must already be saved before creation.
3. Do not create a subscription while `subscription-execution-config` is
   missing. For a blank Guide, create the missing config as `signal_only`; for a
   non-blank Guide, return to Guide classification/restoration.
4. On successful creation, follow `watch_task`, then enter
   `subscription-manage.md` for the post-creation offline-delivery and watch
   questions. Do not add another creation confirmation.

## Output Rules
### Subscription Creation Confirmation

```markdown
### Subscription Creation Confirmation

- Subscription Name: {title}
- Subscription Description: {confirmedDescription}
- Provider: {providerAgent}
- Service Price: {feeAmount} {feeTokenSymbol} / {interval}
- Trial: {trialDisplay}
- Auto-Renew: {OnOrOff}
- Service Guide Consent: {guideConsent} *(only when the Guide is non-blank)*

{payload.creationConfirmation}
```

Render attachments below the field list. Do not show Service Parameters or
internal follow-trade parameters. Omit the Service Guide Consent item when the
Guide is blank; otherwise preserve every collected Guide field and
User-authored value without rewriting them. Do not show a standalone Guide or
payment confirmation, and do not repeat the automatic copy-trading choice
already collected from the Guide. When no automatic copy-trading answer was
collected, do not mention copy-trading mode or internal signal-only defaults in
the card or surrounding prose. This card owns the one explicit final
confirmation for the subscription, displayed payment, and exact Guide Consent.
Any edit to a displayed fact or Guide answer invalidates that confirmation and
requires the complete updated card again.
