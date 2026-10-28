# Runtime Decision Backlog

## Module Description

Use this leaf for one-shot decision-list reads and replies. It never starts a
long poll or schedules a wake. Message history/unread event requests instead
use [`watch.md`](watch.md), which drains the event backlog before waiting.


## Flow
### Durable CLI queue

For the full pending-decision queue, run:

```text
onchainos agent pending-decisions-v2 list --format markdown
```

With one active `[USER_DECISION_REQUEST]`, pass the reply verbatim to its
pre-filled `resolve-prompt`. With multiple cards, select by explicit Job ID or
label and ask only when still ambiguous.

### Surfaced but unanswered watch decisions

For "outstanding/pending/unhandled decisions", run exactly, without pipes or
redirects:

```text
okx-a2a user outdated-list --json
```

Filter only items whose `llmContent` contains exact retired source event
`autotrade_consent` or `autotrade_config_required`: check those IDs and do not
display or execute them. Do not apply the filter to other `autotrade_*` events.

Render all remaining items in one message, numbered in order, with each
`userContent` copied verbatim as a blockquote. Append once:

```text
💡 When replying, identify the item with either (1) list index + answer, e.g. "1 close" / "2: approve" / "3 — 956"; or (2) JobID prefix + answer, e.g. "JobID 0x49fa — 1" (first 6 jobId characters).
```

Localize the hint but preserve `JobID` and examples. End the turn without
watching or scheduling a wake.

### Reply binding

Map a leading list index or `JobID <prefix>` to the rendered item. If only one
item exists, an unqualified reply belongs to it. For multiple items, require a
binding; an index without an answer asks for the answer.

After binding, use [`decision-relay.md`](decision-relay.md). This list origin
has no active-watch origin, so handling or deferring it never starts watch.
