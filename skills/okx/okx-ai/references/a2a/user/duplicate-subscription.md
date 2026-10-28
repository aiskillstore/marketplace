# Duplicate Subscription Guide

## Module Description

Use this guide only when `reason=duplicate_subscription`.

## State Routing

| Input or state | Reference |
|---|---|
| `restoreListeningAvailable=true` | [Restore listening](#restore-listening) |
| `restoreListeningAvailable=false` | [Stop](#stop) |

## Flow

### Input

Require non-empty `payload.jobId` and `payload.title`, plus boolean
`payload.restoreListeningAvailable`. Missing or invalid fields are a hard stop;
never guess the subscription from history or run another task list.

### Restore listening

When `restoreListeningAvailable=true`, render this pattern in the user's language,
substituting the payload values. Use exactly:
`A subscription task for this service already exists. Job ID: <jobId>. Task name: <title>. Another subscription cannot be created. Restore listening?`
Offer only the returned `nextAction` entries and wait for an explicit choice.

- `restore_subscription`: retain `payload.jobId` as the explicit current
  subscription and enter `subscription-manage.md` **Signal-receipt watch
  entry**. This restores receiving only. If the User also explicitly asks to
  resume automatic copy-trading on this device, enter
  `restore-copytrade.md` after receipt is restored; never treat
  `restore_subscription` alone as permission to recreate an execution
  contract.
- `stop`: end the current flow without creating or watching a subscription.

### Stop

When `restoreListeningAvailable=false`, render this pattern in the user's language,
substituting the payload values. Use exactly:
`A subscription task for this service already exists. Job ID: <jobId>. Task name: <title>. Another subscription cannot be created.`
Do not enter watch; only `stop` is valid.

Do not add a separate `userFacingPrompt` field and do not omit the task name from
the rendered message.
