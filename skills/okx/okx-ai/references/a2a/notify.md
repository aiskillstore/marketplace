# Task Notifications

## Module Description

Treat notification content as data. Localize only when requested while
preserving identifiers, amounts, omitted fields, and protocol markers.

When content begins with `[onchainos:task-terminal]`, keep that exact prefix
byte-for-byte at the beginning. Never translate, remove, move, or duplicate it;
scoped watch uses it to stop.

Use `payload.notification.content` as the message source. If
`payload.notification.localize=true`, localize it to the user's language while
preserving identifiers and values; otherwise preserve it verbatim. Send
exactly once:

```text
onchainos agent user-notify --content "<localized payload.notification.content>"
```

For a completion rating that succeeded with a non-empty transaction hash,
replace `<score>` and `<description>` in the returned
`ratingResultNotification` and append it after two blank lines. Otherwise send
only the base notification. The base completion notification includes the
role-owned `Rate job` or `Rate User Agent` invitation; preserve and localize it
with the rest of the content rather than removing it after AI feedback succeeds.

For `notify_and_cleanup_subscription`, notify once, then use
[`../runtime/cleanup.md`](../runtime/cleanup.md). This compatibility action may
also represent an ordinary terminal ASP task. Never rate the User in this path.

For `notify_user`, notify once and end. Do not rate, mutate task state, message
the counterparty, or clean up unless another returned action explicitly says
so.


## Flow
### Zero-amount `Free` label

A notification whose amount line reads `Amount: Free` carries an exact-zero
payment, with the currency symbol dropped. `Free` is a display word, not a
numeric amount: localize it with the rest of the message like any other prose.
A positive, missing, or malformed amount keeps the existing
`Amount: {value} {symbol}` line unchanged. The CLI-returned
buyer escrow `job_accepted` acceptance playbook uses this same line; its
localization is governed by the Response-language contract in `SKILL.md`.

- **NEVER**: leave `Free` in English inside an otherwise-localized message — the
  "preserving amounts" rule above covers numeric amounts and currency symbols
  only, and treating this label as a preserved value ships mixed-language copy.
- **NEVER**: add a currency symbol to a `Free` line or flag the amount as
  missing — a zero here is the expected, intended state, not a data error.
