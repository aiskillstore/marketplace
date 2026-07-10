# Pull outstanding `decision_request` items — `okx-a2a user outdated-list`

> Loaded from `watch-core.md` when the user explicitly asks to see decision_request items they have **not yet replied to**. This is a user-initiated one-shot query, separate from the live watch loop — it does NOT long-poll and does NOT re-enter watch.

## Triggers
- Chinese: `未决策` / `待决策` / `没有决策` / `未处理` / `待处理` / `没有处理`
- English: `outstanding decisions` / `pending decisions` / `unhandled decisions` / `what am I missing`

## Action

```bash
okx-a2a user outdated-list --json
```

> 🛑 Run exactly as written — no `| grep` / `| jq` / redirects (same JSON-integrity rule as watch; see `watch-core.md` §Anti-patterns).

Returns the set of `decision_request` items the user has **not yet `check`ed** (i.e. watch has already surfaced them but the user never committed a reply). These items stay in the outstanding-decisions queue until `okx-a2a user check --todo-ids …` commits a decision. (Notifications are not included — watch consumes them on return and they have no outstanding state.)

## Rendering — batch, not per-item

Unlike watch's per-item flow, render **all returned items in a single assistant message**:

1. Number each item (`1`, `2`, `3`, ...) so the user can disambiguate.
2. For each item, paste its `userContent` as a markdown blockquote (same copy-not-rewrite rule as `watch-core.md` §Dispatch — no wrapper sentences, no summarization, no cross-item merging).
3. After the last item, append this disambiguation hint **exactly once** (translate to the user's language per LOCALIZATION_PREFIX rules; keep the literal token `JobID` and the examples unchanged):
   `💡 When replying, use either form to indicate which item you're answering: (1) list index + answer, e.g. "1 关闭" / "2: approve" / "3 — 956"; (2) JobID prefix + answer, e.g. "JobID 0x49fa — 1" (first 6 chars of jobId).`
4. End turn. Do **NOT** auto-re-enter `watch` or any other command — `outdated-list` is a one-shot query, not a loop.

## Handling the user's reply

Route in the following order:

1. **Reply starts with a list index** (digit `1` / `2` / `3` / ..., followed by separator `:` / `—` / space / newline, or standing alone):
   - Map the index back to the Nth `decision_request` rendered.
   - The text after the index (if any) is the verbatim answer for that item.
   - If the user sent only an index with no answer content (e.g. just `1`), **ask the user to supplement the answer** ("Please add your reply for decision 1, e.g. `1 关闭` / `1 956` / `1 自定义回复`") rather than guessing.

2. **Reply starts with `JobID <prefix>`** (or variants `JobID <prefix> — <answer>` / `<prefix>: <answer>`, etc.):
   - Match `<prefix>` against the listed items' jobIds (first 6 chars of jobId).
   - The text after the prefix is the verbatim answer for that item.

3. **Only one item is outstanding** → no ambiguity; treat the reply as belonging to that item whether or not it carries an index / prefix.

4. **Multiple outstanding items AND the reply carries neither an index nor a prefix** → ask the user to re-send using one of the forms above.

Once the item is identified, claim it and execute its `llmContent` using the same flow as `watch-core.md` §Handling the user reply (claim via `okx-a2a user check --todo-ids <id> --json`, then run whatever commands `llmContent` specifies).

## Anti-patterns
- Do NOT call `okx-a2a user watch` for this intent — `watch` long-polls; `outdated-list` is a snapshot.
- Do NOT auto-re-enter any command after rendering. Wait for the user's reply (either an index or a JobID prefix is accepted).
- Do NOT schedule a 2-minute wake here — the wake belongs to the live watch flow for fresh `decision_request` items, not to a static list.
- Do NOT render items one by one across multiple assistant messages — batch them into a single message.
