# User Intent Routing

User-session needs to forward free-form user instructions targeting a specific task (e.g. "re-upload the dispute evidence for the cat-picture job", "remind ASP 963 that the deliverable is overdue", "switch to a different ASP") to the **specific sub session that owns that task**, when there's no matching active pending decision.

**Trigger phrases** — when the user says any of the following AND no matching entry exists in `pending-decisions-v2`, **MUST** enter this flow:

| Intent | Chinese phrases | English phrases |
|---|---|---|
| 重新提交 / 补充内容 | "重新提交 X / 再上传 / 重发 / 给我改 / 补充证据 / 改一下" | "re-submit / re-upload / resubmit / add more / append / change my X" |
| 催促 / 让 sub 主动同步状态 | "提醒 / 催一下 / 让卖家知道一下 X / 跟买家说一下 X" | "remind / nudge / chase up / tell the ASP X" |
| 变更条款 | "改 provider / 换服务商" | "use a different provider / switch provider" |

🛑🛑🛑 **CRITICAL — do NOT make domain assumptions on behalf of the user**: when the queue is empty and the user issues a task-scoped instruction, your job is to **route**, not to **adjudicate**. **Do NOT** reply "the evidence phase is over" / "this state doesn't allow that". Only the sub session can query the chain and know for sure. Forward the user's verbatim wording and let the sub respond authoritatively. (🔴 I-15: user typed "重新提交证据" → user session refused with "证据阶段已结束"; correct path: route to sub.)

**Decision tree** (apply in order, stop at first hit):

1. `onchainos agent active-tasks` → flat array of non-terminal tasks (with `myRole` / `counterpartyAgentId`).
2. `onchainos agent user-notify` a numbered list (`shortJobId` + status + role + counterparty + title) → end turn, wait for user's pick.
3. **Later turn after pick**: read `myAgentId` / `counterpartyAgentId` / `jobId` from the chosen row. If `counterpartyAgentId == null` → ask the user for it, else proceed.
4. `okx-a2a session query --job-id <jobId> --my-agent-id <myAgentId> --to-agent-id <counterpartyAgentId>` → confirms an active session exists. Empty → notify "no active conversation" via `onchainos agent user-notify` and end turn.
5. Dispatch the user's instruction to the sub via `okx-a2a session send` — the daemon resolves the session from `--job-id` + `--to-agent-id`:

   ```bash
   okx-a2a session send --no-wait \
     --job-id <jobId> --to-agent-id <counterpartyAgentId> \
     --content '<user verbatim>

   ---
   Reply to the user via `onchainos agent user-notify --content "<localized natural-language reply>"`. If a user decision is needed (A/B/C / approve / reject / etc.), use `pending-decisions-v2 request` instead (see `task-user-sub-playbook.md` §Communication Contract).'
   ```

   Forward verbatim then append reply-path instruction. End turn.

**Hard rules**:
- ❌ Do NOT pass `--session-key` you composed by string concatenation — always let the daemon resolve from `--job-id` + `--to-agent-id`.
- ❌ Do NOT call `active-tasks` proactively for general chitchat — only when task-scoped.
- ❌ Do NOT paraphrase / translate / reformat the user's instruction — pass verbatim.
- ❌ Do NOT call `okx-a2a session send` multiple times in one turn.

**Output schema of `active-tasks`**: see [`task-cli-reference.md → active-tasks`](task-cli-reference.md#active-tasks).

---

## Multi-task disambiguation

When the user has multiple active tasks, every routing decision **must** anchor to a specific `jobId`:

- **Always confirm `jobId` before acting**. If ambiguous → ask which task or render an `active-tasks` numbered list. Never assume the most-recent task is the one they mean.
- **Track each task's state independently**. Don't apply task A's context to task B.
- **Echo the `jobId` in every reply that touches a task** — `<title> (Job <shortId>)` is the standard prefix.

See [`entry-points.md`](./entry-points.md#multi-task-context-management) for the full deep-dive.

---

## Task list / "what am I working on"

When the user asks for **their tasks list without a specific jobId**, the user session answers directly (do NOT 6-step forward). Triggers:
- Chinese: `我的任务` / `接了哪些任务` / `我接的活` / `有哪些任务` / `进行中的任务` / `还在跑的任务` / `所有任务` / `任务列表`
- English: `my tasks` / `what am I working on` / `list my tasks` / `active tasks` / `show all tasks`

**Action — pick the right CLI by intent**:
- **All non-terminal tasks across accounts**: `onchainos agent active-tasks` — use for "what am I working on / 还在跑的".
- **Tasks tied to a specific agent**: `onchainos agent tasks --agent-id <agentId> [--status <s>] [--page <n>] [--limit <m>]` — historical + active for that agent's role.

Render as numbered list. ❌ Do NOT 6-step forward. ❌ Do NOT mix with "decision list".

⚠️ **Disambig — `所有任务` vs `我所有任务`**: "所有任务" = marketplace pool (→ `task-search`); "我所有任务" = own tasks (→ this section).

---

## Close a task (irreversible)

Triggers (only when there's no active card the user might be answering):
- Chinese: `关掉这个任务` / `不要这个任务了` / `取消任务` / `关闭这个 job` / `撤回任务`
- English: `close this task` / `cancel the task` / `drop this job` / `withdraw the task`

**Preconditions**: clear jobId in context; status must be `created` (no provider accepted yet).

**Action**: `onchainos agent close <jobId> --agent-id <agentId>` after explicit user confirmation.

🛑 **CRITICAL ambiguity — `close` vs `resolve C`**:
- `关闭` / `close` is overloaded:
  1. **In "Waiting for user reply" state** on a `recommend_pick` card → run the block's pre-filled `resolve-prompt` command with `--user-reply "关闭"` (CLI maps to `close`).
  2. **Outside Waiting state** → `onchainos agent close <jobId>` directly.
- 🔴 I-9: case (1) mistakenly mis-routed. **Default when in doubt**: prefer `resolve-prompt`.

---

## Entry intents (start something new)

| Intent                                                                        | Action | Detail |
|-------------------------------------------------------------------------------|---|---|
| Publish task — `发布任务` / `创建任务` / `帮我发任务` / `publish a task` / `create a task` | `onchainos agent next-action --role user --agentId <X> --message '{"event":"create_task","jobId":"_"}'` → follow script | user publish flow |
| Designate an ASP — `指定卖家` / `use the service of Agent X`                      | Gather params → designated-provider flow | [`task-user-actions-publish.md`](task-user-actions-publish.md) §5 |
| Find tasks (ASP) — `接单` / `找任务` / `start accepting jobs`                      | [`task-asp-accept.md`](task-asp-accept.md) §2 (Path A). Do NOT route to `task-search`. | task-asp-accept.md §2 |
| Take specific task (ASP) — `接 {jobId}` / `contact the User Agent of {jobId}`  | `onchainos agent contact-user <jobId> --agent-id <chosen agentId>` (single CLI: session create + canonical opener) | task-asp-accept.md §3 |
| Browse marketplace — `搜索任务` / `browse marketplace` / `按关键字搜任务`                | `onchainos agent task-search` | [`task-cli-reference.md#task-search`](task-cli-reference.md#task-search) |
| Stake (Evaluator) — `I want to stake`                                         | `staking-config` + `my-stake` → confirm → `stake` (do NOT hardcode 100 OKB) | [`task-evaluator-staking.md §2`](task-evaluator-staking.md) |
| Direct help — "help me check…" **without** hiring intent                      | Route to appropriate skill; do NOT suggest task creation | — |

⚠️ **Disambig — `接单` vs `搜索任务`**: skill-profile match ("用 X 接单") → `recommend-task`; explicit filters → `task-search`.
🛑 **ASP constraint**: "take task X" → must run `onchainos agent contact-user <jobId>` (cold-start opener) and wait for user designation; do NOT directly `apply` — `apply` is `JobAspSelected`-system-event-triggered only.

---

## Status / progress query (specific task)

| Trigger | Action |
|---|---|
| **Chain-state snapshot** — `查询任务 {jobId}` / `what's the status of {jobId}` | `onchainos agent status <jobId>`. User session answers directly. |
| **Negotiation / chat-context detail** — `上次卖家说了什么` / `价格谈到多少了` | 6-step forward to sub (sub has chat history). |
| `view deliverables` / `查看交付物` | `task-deliverable-list [--job-id <jobId>] --role <user|asp>` |
| `upload evidence` / `补证据` | **Friendly-reject** — evidence auto-submitted by CLI on `job_disputed`. |

---

## Replying to pending decisions (when `[USER_DECISION_REQUEST]` is in context)

If your context contains an active `[USER_DECISION_REQUEST]` block (you're in "Waiting for user reply" state from a recent push), the user's reply routes via the matching block's pre-filled `resolve-prompt` command:

- **Single active card** (latest block below the stale-notice line): run its `resolve-prompt` with `--user-reply "<user's verbatim text>"`.
- **Multiple blocks visible, user disambiguates with a jobId/label** (e.g. `Job 0x4652 选 1500`): scan context for the block whose `[job: <jobId>]` matches, then run THAT block's `resolve-prompt` with the user's verbatim text as `--user-reply`.
- **Truly ambiguous** (no jobId, no label hint, multiple cards): ask the user "which task?" via plain text reply.

---

## Decision list

Triggers (only when there's no active `[USER_DECISION_REQUEST]` block the user might be answering):
- Chinese: `查看决策列表` / `决策列表` / `决策` / `决策项` / `决策卡` / `待办决策` / `我的决策` / `查看决策` / `看决策` / `有什么待办` / `有什么要处理的`
- English: `decision list` / `show decision list` / `list decisions` / `pending decisions` / `what's pending`

**Action**: `onchainos agent pending-decisions-v2 list --format markdown` → **follow the CLI's returned playbook verbatim**. The playbook includes both the user-facing rendering instructions AND the routing rules for the user's subsequent reply. Do NOT improvise — only do what the playbook prints.

---

## Task watch / history / outstanding decisions

When the user wants to monitor task progress, drain unread/missed events, or list un-replied decision cards → route to **§Task Watch** (`watch-core.md`). Do NOT inline `okx-a2a user watch` / `okx-a2a user outdated-list` from here; load that file and follow it.

Triggers:
- **Live monitor**: `监听任务进展` / `开始监听任务` / `帮我盯着任务` / `开监听` / `继续监听` / `task watch` / `user watch` / `monitor task progress` / `watch tasks` / `keep me posted on tasks`
- **History / backlog drain**: `历史消息` / `历史记录` / `过去消息` / `未读消息` / `show past messages` / `catch me up on tasks`
- **Outstanding (un-replied) decisions**: `未决策` / `待决策` / `没有决策` / `未处理` / `待处理` / `outstanding decisions` / `unhandled decisions` / `what am I missing`

**Platform gate**: only Claude Code (`CLAUDECODE=1`) and Codex (`CODEX_THREAD_ID`); other platforms push natively and the skill stops with an unsupported-platform message.

🛑 Watch is itself a long-poll — the long-poll IS the wait. Do NOT wrap it in `/loop` / Cron / `sleep` / any scheduler.

⚠️ **Disambig — "decision list" vs "outstanding decisions"**: `决策列表` / `decision list` → §Decision list above (`pending-decisions-v2 list`, the full queue). `未决策` / `outstanding decisions` → this section (`outdated-list`, only un-`check`ed `decision_request` items).
