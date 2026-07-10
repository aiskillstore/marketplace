# Task Watch — live monitor for the user-session task inbox

Loaded from `SKILL.md` §Task Watch. Owns: triggers, the watch command, anti-cron rules, item dispatch (`notification` / `decision_request`), claim semantics, `llmContent` execution, stop conditions.

Business actions (apply / deliver / dispute / quote / accept) belong to §Task Marketplace (`references/task-core.md`). This file only handles the watch loop.

## Triggers — MANDATORY ROUTING (NOT cron / scheduled / polling)

When ANY trigger phrase below matches, execute §Action. The watch command is a single long-poll call (the call itself waits for events); do **NOT** wrap in `/loop`, `Cron`, `$CODEX_HOME/automations`, `watch -n`, `sleep` loops, scheduler frameworks, or "set up a recurring job". Do **NOT** ask "how often should I check?" — the long-poll IS the wait. Do **NOT** substitute another command for polling.

**Trigger phrases**:
- Chinese (live monitor): `监听任务进展` / `开始监听任务` / `关注任务进展` / `使用监听 skill 监听任务进展` / `帮我盯着任务` / `任务有进度就告诉我` / `任务有动静告诉我` / `开监听` / `watch 任务`
- Chinese (history / backlog drain): `历史消息` / `历史记录` / `过去消息` / `之前的消息` / `帮我看看之前的历史消息` / `看下之前的消息` / `未读消息`
- Chinese (continuation — clarify first, see §Continuation triggers): `继续监听` / `继续盯着` / `继续 watch` / `接着监听` / `再监听一下` / `继续监听任务`
- English (live monitor): `task watch` / `user watch` / `monitor task progress` / `keep me posted on tasks` / `watch tasks` / `start watching`
- English (history / backlog drain): `show past messages` / `show message history` / `catch me up on tasks` / `unread task messages`
- English (continuation — clarify first, see §Continuation triggers): `keep watching` / `continue watching` / `resume monitoring`

> ⚠️ **Continuation triggers are a special case** — they do NOT immediately call watch. They imply the user wants to keep watching some specific task, but the intent is ambiguous (which task? or all of them?). See §Continuation triggers below for the clarification flow.

> 📥 **Why "view history" routes here**: watch is a **destructive read** of the event stream — each call returns the full backlog of unread events accumulated since the last call (e.g. while no one was watching), then long-polls for new ones. A user asking for past / missed / unread messages is asking to drain that backlog — same command, same Dispatch flow. Do NOT route to `agent active-tasks` / `agent status` (those are summaries, not the actual notification bodies). For un-replied `decision_request` items specifically (which `watch` already consumed but the user hasn't `check`ed), see §"Pull outstanding `decision_request` items".

## Platform compatibility — Claude Code / Codex only

🛑 The `okx-a2a` CLI is only wired on **Claude Code** and **Codex** harnesses. On **Hermes** and **OpenClaw**, the client itself pushes task notifications natively — no manual watch is needed.

Before §Action, gate on environment variables:

```bash
detect_watch_support() {
  if [ "${CLAUDECODE:-}" = "1" ]; then
    echo "Claude"
  elif [ -n "${CODEX_THREAD_ID:-}" ]; then
    echo "Codex"
  else
    echo "unsupported"
  fi
}
detect_watch_support
```

- Output ∈ {`Claude`, `Codex`} → proceed to §Action.
- Output = `unsupported` → **stop**. Tell the user (localize to their language): "当前平台不支持 `okx-a2a` 监听 —— 任务通知会由客户端直接推送，无需手动开监听。" / "This platform doesn't support `okx-a2a`; task notifications are delivered natively by the client — no manual watch needed." Do NOT run any `okx-a2a` command.

## Action

### Continuation triggers — recall last jobId, then rearm

If the user's message matched a **continuation-style** phrase (`继续监听` / `继续盯着` / `继续 watch` / `接着监听` / `再监听一下` / `继续监听任务` / `keep watching` / `continue watching` / `resume monitoring`), the user means "keep watching the task we were already tracking" — they expect scoped monitoring on the same jobId, not a fresh global watch.

**Step 1 — Recall the jobId from this conversation's transcript.** Search in this order, take the FIRST hit:

1. The most recent CLI `[Watch]` block emitted earlier in this conversation (the jobId is the `--job-id <X>` value in its `okx-a2a user watch ...` command).
2. The most recent successful `agent create-task` / `agent publish-draft` stdout (jobId printed as `jobId: 0x...`).
3. The most recent jobId referenced in any rendered `notification` / `decision_request` in this conversation.

**Step 2 — Route by recall result**:

- **jobId found** → enter scoped session. **Do NOT emit §Banner** (the user already knows what they're tracking — a banner here is redundant ceremony). Just run `okx-a2a user watch --json --job-id <X>`. The sticky `--job-id <X>` applies for the rest of this session per §Session-scoped sticky.
- **No jobId found** → fall back to a global session. The behaviour diverges from the user's "keep watching" intent, so **DO emit §Banner** (it's the only signal the user has that the watch was rearmed as global rather than scoped). Then run `okx-a2a user watch --json` (no `--job-id`). Do not ask the user — a continuation phrase plus no recoverable jobId is treated the same as a fresh `task watch` entry.

### 🛑 Banner before entering watch

**Decide by entry, not by "is this the first watch in this turn".** Look at **what triggered** the `okx-a2a user watch` call — not whether it's the first watch invocation in the current turn.

**Entries that REQUIRE the banner (only these two)**:

1. **Trigger-phrase entry** — this turn's user message matched a §Triggers phrase (e.g. `监听任务进展` / `历史消息` / `task watch`). **Exception**: a continuation-style phrase (`继续监听` / `keep watching` / ...) only triggers the banner when the recall fails and the watch falls back to global — see §Continuation triggers for the full rule.
2. **CLI `[Watch]` block entry** — a command earlier in this turn emitted a `[Watch]` block in stdout: a hint block that starts with `[Watch]` and instructs the current call to run `okx-a2a user watch ...` (typical sample: `` [Watch] Read `skills/okx-ai/references/watch-core.md` now, then start the monitor: ``, output by `agent create-task` / `agent publish-draft`).

Any watch call that does not match one of these two entries **must NOT** emit the banner — all session-continuation paths (dispatch resume, wake fire, etc.) are excluded.

**How to send**: emit the exact canonical banner as a standalone **user-visible assistant message** (the message that appears in chat as the AI's reply to the user — NOT tool stdout, thinking blocks, or internal annotations the user cannot see).

| Chat language | Exact string (verbatim) |
|---|---|
| Chinese | `🔔 监听已启动，如果有历史消息，我们将先逐个处理，新任务进展会及时通知。` |
| English | `🔔 Watch started — any backlog will be processed first, then you'll be notified of new task events as they arrive.` |
| Other | Translate the English line; keep the leading 🔔 and the two-clause structure (started + backlog-first + then-new). |

❌ Violation examples:

- Saying `我现在开始监听` / `I'll start watching now` (or any paraphrase) **without** the exact canonical string in the same assistant message.
- Calling the watch tool before the banner has appeared.
- Embedding the banner inside Bash tool stdout / thinking block / tool-call arguments — these locations are invisible to the user, so the banner was not actually delivered.
- Emitting the banner on a re-entry path (resume after notification/decision_request handling, wake fire) — these are not new entries.

### Run watch

```bash
okx-a2a user watch --json
```

When the call returns items, process each per §Dispatch below. After processing all items, re-enter the same command (no banner) — the only exceptions are the §Stop condition triggers.

### Session-scoped `--job-id` (sticky)

If this watch session started from the CLI `[Watch]` block (the only path that puts `--job-id <X>` on the first call), **`--job-id <X>` is sticky for the entire session**. Wherever this skill shows the bare command `okx-a2a user watch --json`, append `--job-id <X>` literally — including:

- §Dispatch notification resume
- §Dispatch decision_request resume (outcomes 3 / 4 / 5)
- §Re-enter after processing

The session ends when §Stop condition fires, or when the user starts a **new** watch via a §Triggers phrase — that new session is global, no `--job-id`.

## Anti-patterns

- Do NOT use `/loop`, Cron, `$CODEX_HOME/automations`, `watch -n`, `sleep` loops, or any self-rolled polling around `onchainos agent status` / `agent active-tasks`.
- 🛑 Once started, the watch loop stops **only** when a §Stop condition fires. Until then you have no authority to end it — not by Ctrl-C'ing the in-flight call, not by skipping the next re-enter, not because output "looked thin", "felt slow", or you wanted to "restart cleanly". Silence is the healthy state of a long-poll.
- Do NOT pass `--from-now`. By default watch returns the full backlog of unread events first, then long-polls for new ones; `--from-now` skips the backlog and silently drops any event the user hasn't seen yet (watch is destructive read — those events are gone for good).
- Do NOT pass `--job-id` **except in the post-publish `[Watch]` block**. `user watch` is a user-session-wide monitor by default; narrowing to one job defeats its purpose and misses cross-task events. The single exception is the CLI `[Watch]` block emitted by `agent create-task` / `agent publish-draft`, which intentionally narrows the first watch call to the freshly-published `jobId` so the user only sees that task's notifications immediately after publish. Trigger-phrase entries (e.g. `监听任务进展` / `task watch`) and any §Dispatch re-entry must still run watch **without** `--job-id`.
- 🛑 **Run `okx-a2a user watch` / `okx-a2a user outdated-list` exactly as written. Do NOT append `| grep` / `| tail` / `| head` / `| awk` / `| sed` / `| jq` / shell redirects.** Both commands emit a single structured JSON document — any pipe/truncation breaks the JSON and silently drops items. If output looks noisy with `[DEBUG]` lines mixed in, those belong on stderr and never affect the JSON on stdout; do not "clean" stdout. Pipe = data loss.
- 🛑 **Always run `okx-a2a user watch` in the foreground.** On Claude Code, the Bash tool exposes a `run_in_background` parameter — you **MUST** call watch with `run_in_background: false` (the default). Backgrounding the watch breaks the entire dispatch loop: stdout (the JSON with items) is no longer returned synchronously to the same tool call, so you can't dispatch by `kind`, can't render `userContent`, can't claim `decision_request` items, can't even know if watch returned anything. Watch is a single long-poll that must block this turn until it returns; the long-poll IS the wait. If you find yourself reaching for `run_in_background: true` because "watch takes too long", you are misusing the tool — that wait is the design.

  **Recovery if a watch already ended up in the background** (accidental `run_in_background: true`, or a foreground-timeout re-route): the output is delivered as a background-task notification you must still relay to the user. Full recovery flow (locate output-file → dispatch items → `TaskStop` → restart in foreground): see [`watch-background-recovery.md`](watch-background-recovery.md).

## Dispatch by `kind`

A returned item is always one of two `kind`s, handled completely differently.

### `kind == notification` — paste verbatim, then resume

**Your sole job on a notification item is to paste its `userContent` and resume watch. Nothing else.** No interpretation, no summary (including count summaries like "N items, all handled"), no commentary, no greeting, no header, no footer, no translation of body content. Render every returned item regardless of `status` / `seen` / `handled` / `type` / age — if watch returned it, paste it.

**Step 1 — Output exactly this assistant message** (character-by-character; replace `<userContent>` with the actual field value, prefix each line with `> `):

```
> <userContent>
```

That is the **entire** assistant message — not a part of it, the whole thing. If you find yourself about to write any other text (preamble, postamble, header, summary, "Here's the latest update"), **stop, erase, output only the blockquote**.

**Do not think about this item.** No `<thinking>` block, no analysis, no reasoning, no "what does this mean for the user". Notification handling is **purely mechanical**: read `userContent` from the JSON → prefix each line with `> ` → emit. Then call watch. There is nothing to interpret here.

**Step 2 — Resume watching.** Call `okx-a2a user watch --json` again (append the sticky `--job-id <X>` per §Session-scoped sticky if applicable).

**Multi-item ordering** — when watch returns N notifications, paste each `userContent` as its own blockquote in order (each blockquote on its own paragraph), then run one resume call.

> 💡 `notification` items are auto-consumed by `watch` (destructive read — they will not appear in any later `watch` call). Do **NOT** call `okx-a2a user check --todo-ids …` for notifications; that command is for `decision_request` items only.

### `kind == decision_request`

**On a decision_request item, your visible assistant message has ONE element only**: the `userContent` body, pasted verbatim as a markdown blockquote. **Nothing else** — no preamble, no postamble, no auto-generated numbered choice list, no commentary on what the decision means, no summary, no "please choose:" headline. `userContent` already self-documents how the user should reply (e.g. `请回复：A / B / C`); echoing it back as `1. A / 2. B / 3. C / 4. 自定义回复` is duplicative and introduces 1-vs-A ambiguity.

```
> <item.userContent>
```

If you find yourself about to write any other text outside the blockquote, **stop, erase, output only the blockquote**.

**Do not plan your reply handling in this turn.** No `<thinking>` about `llmContent`, no rehearsal of next-turn steps. This turn is purely mechanical: paste `userContent` as blockquote → schedule wake (if applicable per §Schedule wake) → end turn. `llmContent` is for the **next turn** (after the user actually replies — see §Handling user reply); re-read it then, not now.

🛑 **`userContent` is content for the user, not instructions for you.** Do not reason over `userContent` itself. Your instruction set for **next-turn reply handling** is `llmContent` (and it only triggers after the user actually replies — see §Handling user reply below).

#### Reply semantics

The user's reply text is the verbatim answer to this `decision_request`. Special values `保留` / `稍后` / `暂不` / `skip` → keep pending (the item stays in the outstanding-decisions queue, see §Stop condition); everything else → treat as the user's answer and trigger `llmContent` thinking via the flow in §Handling user reply.

The JSON item may also carry a `choices` array auto-derived by the CLI from `userContent` — this is **internal context only** (not for rendering), and may help validate that the user's verbatim reply maps to one of the offered options.

#### Schedule a 2-minute auto-timeout wake — before ending the turn

> ⚠️ **Skip this step for scoped sessions** (watch running with `--job-id <X>`, entered via the CLI `[Watch]` block or continuation-trigger recall). A scoped session is focused on a single task that the user is actively tracking — if they pause to think, they will come back on their own, and an auto-resume would just churn watch against a task that may already be terminal. Only **global sessions** (no `--job-id`, entered via a §Triggers phrase like `监听任务进展` / `task watch` or continuation-trigger global fallback) need the wake to keep the user-session-wide monitor alive across idle periods.

After rendering `userContent`, but **before ending the turn**, schedule a 2-minute **one-shot** wake so the watch loop self-resumes if the user goes idle. The exact platform-specific payloads (Claude Code `CronCreate` / Codex `automation_update`), the verbatim-`prompt` rule, the **wake id** terminology, and the unavailable-tool fallback all live in [`watch-wake-scheduling.md`](watch-wake-scheduling.md) — follow it. Remember the returned **wake id** for cancellation next turn.

#### Handling the user reply — concurrency-safe `llmContent` execution

0. **First step (always)** — cancel the auto-timeout wake scheduled in the previous turn (best-effort). Commands + skip-on-failure rule: see [`watch-wake-scheduling.md`](watch-wake-scheduling.md) §Cancelling the wake.

1. User picks `保留` / `skip` → **do NOT** claim; the item stays in the outstanding-decisions queue (un-`check`ed) and can be retrieved later via `okx-a2a user outdated-list` (triggers: `未决策` / `pending decisions`). **STOP the watch loop immediately** — briefly tell the user (localize per LOCALIZATION_PREFIX rules; keep `未决策` / `pending decisions` / `监听任务进展` / `task watch` unchanged): "Item kept on hold; watch loop ended. Say `未决策` / `pending decisions` to see all unhandled decisions, or `监听任务进展` / `task watch` to resume monitoring new events." The user explicitly chose to defer; honor that and stop background monitoring.
2. Otherwise claim first: `okx-a2a user check --todo-ids <id> --json`.
3. On `handled` → **execute the commands specified in `llmContent` verbatim**. The instructions can be anything the issuer chose — a relay to another session (`xmtp-send` / `session send`), a wallet / onchain call, an agent CLI command, an arbitrary tool invocation, or a multi-step sequence. `llmContent` itself names the command(s), the target(s), and how to assemble the payload — just follow it. After firing off what `llmContent` specifies, end the turn promptly; do not block on downstream effects.
4. On `alreadyHandled` → tell the user "this item was processed in another window"; **then re-enter `okx-a2a user watch --json`** (append the sticky `--job-id <X>` per §Session-scoped sticky if applicable) (the watch session continues — only the duplicate item is dropped). Do not execute `llmContent` again.
5. Claim succeeded but `llmContent` execution failed → create a new `onchainos agent user-notify` with the failure reason and a retry command; **do NOT** flip the original item back to pending. **Then re-enter `okx-a2a user watch --json`** (append the sticky `--job-id <X>` per §Session-scoped sticky if applicable).

🛑 **After `decision_request` outcomes 3, 4, 5 above, resume watching** — call `okx-a2a user watch --json` again (append the sticky `--job-id <X>` per §Session-scoped sticky if applicable). Outcome 1 (`保留` / `skip`) is a hard STOP — see §Stop condition. Do NOT stop in outcomes 3/4/5 just because `llmContent` execution completed / the item turned out duplicate / `llmContent` execution failed.

🛑 **User-session authority boundary**: when executing `llmContent`, run **only** the commands `llmContent` explicitly specifies — do not synthesize additional steps from the user's reply text. The user's reply (`956`, `1`, `关闭`, `approve`, …) is the verbatim answer to that item; it is **not** a license to autonomously pick a provider, start a negotiation, solicit quotes, open a session, send an XMTP message, or kick off any other business flow on your own. If `llmContent` doesn't tell you to do it, don't do it.

## Pull outstanding `decision_request` items — `okx-a2a user outdated-list`

Separate user-initiated intent (triggers: `未决策` / `待决策` / `outstanding decisions` / `pending decisions` / `what am I missing`): a one-shot snapshot of decision_request items the user surfaced but never replied to. It does NOT long-poll and does NOT re-enter watch. Full flow — command, batch-render rule, the `JobID <prefix>` disambiguation hint, reply routing, and anti-patterns — is in [`watch-outdated-list.md`](watch-outdated-list.md). Load it when this intent fires.

## Stop condition

🛑 **The ONLY valid stop conditions:**
- **User picks `保留` / `稍后` / `暂不` / `skip` on a `decision_request`** — item stays in the outstanding-decisions queue (un-`check`ed) and can be retrieved later via `outdated-list`. The watch loop ends here because the user explicitly chose to defer; honor that.
- The user explicitly says stop — e.g. `停止监听` / `不用监听了` / `stop watching` / `unsubscribe`.
- **Scoped session + this task reached a terminal state.** When the watch is running with `--job-id <X>` (scoped session per §Session-scoped sticky) AND the latest `notification`'s `userContent` contains any of: `[Job Completed]` / `[Job Auto-Completed]` / `[x402 Job Completed]` / `[Job Expired]` / `[Job Closed]` / `[Refund Settled]` / `[Auto-Refund Settled]`, render the notification verbatim per §kind == notification, then **stop the watch loop** — do not re-enter. This jobId is terminal; continuing to long-poll on a dead jobId is pure churn (no new events will ever arrive for this `--job-id`).
  - **Global session** (no `--job-id`) does NOT apply this stop — other tasks may still produce new events. See §"NOT stop conditions" below.

### Re-enter after processing

After processing all returned items, **always** call `okx-a2a user watch --json` again (append the sticky `--job-id <X>` per §Session-scoped sticky if applicable) to resume watching. The only exceptions are the stop conditions listed above.

🚫 **NOT stop conditions** — every one of these requires re-entering watch:

- A `notification` was just rendered (auto-consumed by watch — no claim step exists for notifications).
- A `notification` whose content contains any terminal-state marker (`[Job Completed]` / `[Job Auto-Completed]` / `[x402 Job Completed]` / `[Job Expired]` / `[Job Closed]` / `[Refund Settled]` / `[Auto-Refund Settled]`) **in a global session** — the global watch monitors the user-session-wide inbox; one task's terminal state ≠ the loop's terminal state (other tasks may still produce events). **In a scoped session (with `--job-id <X>`) these markers ARE stop signals** — see §Stop condition above for the scoped terminal-state rule.
- A `decision_request` was just handled — `llmContent` execution completed (step 3) / `alreadyHandled` (step 4) / claim-succeeded-but-`llmContent`-execution-failed (step 5). **Note**: `保留` / `skip` (step 1) is a STOP, listed above.
- Watch returned 0 items (empty result / long-poll elapsed with no new events) — re-enter watch and keep waiting.
- **Mid-flow markers that look terminal but are NOT** — these are intermediate notifications; keep watching even in scoped session. Common offenders:
  - `[Deliverable Received]` / `[x402 Deliverable Received]` / `[x402 交付物已接收]` — payment settled + deliverable in hand, but the real terminal marker is `[x402 Job Completed]`.
  - `[Job Accepted]` / `[Payment Mode Set]` / `[Connecting ASP]` / `[Job Created]` / `[Visibility Changed]` / `[x402 Replay Failed]` / `[Rejection Confirmed]` / `[📝 Rating Submitted]` — all mid-flow status updates, never terminal on their own.
  - **Rule of thumb**: if the marker is not in the literal list under §Stop condition, it is NOT a stop signal — re-enter watch unconditionally.
