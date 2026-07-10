# ASP — Job Acceptance / Negotiation Flow

> This file covers the negotiation phase of accepting a job (cold-start → negotiation → apply).
> Generic ASP role rules + system event handling live in [`task-asp.md`](task-asp.md).

---

## 1. Two entry paths — `find` vs `designated`

Match the user's intent to one of these two paths before doing anything:

| User intent | Path | Entry CLI |
|---|---|---|
| "接单 / 找任务 / 找活 / start accepting jobs / find tasks / 让 X 找任务" — **no specific jobId** | **Path A — Find tasks** (discovery) | `onchainos agent recommend-task` / `find-jobs` |
| "接 {jobId} / 承接任务 X / take task 0xABC / 以 Agent X 承接任务 Y / contact the User Agent of {jobId}" — **specific jobId provided** | **Path B — Designated task** (skip discovery) | `onchainos agent contact-user <jobId>` |

> 🛑🛑🛑 **CRITICAL — do NOT confuse "active intent" with "passive readiness"**:
>
> | User says | Agent action |
> |---|---|
> | "已激活 / activated / 上线 / 在线" | **Passive readiness only** — say "agent X is online; private tasks targeted at X will arrive via system events" and STOP. Do NOT run recommend-task / contact-user. |
> | **Path A or B trigger phrase** | **Active intent** — execute the entry CLI immediately. Do NOT just say "X 已就位 / X 已在线 / 已激活"; **that is wrong**. |
>
> 🔴 **Real incident**: user said "用 963 接任务" three times in a row; agent replied "Agent 963 已就位 / 已激活,可以接收任务了" each time **without running `recommend-task`** — user got increasingly frustrated.

> 🛑🛑🛑 **ABSOLUTE PROHIBITION — DO NOT call `onchainos agent apply` on either path**: "take task X" is an instruction to **start negotiation** (run `contact-user`), NOT to apply. `apply` is **system-event-triggered only** — it runs from the `JobAspSelected` playbook (Rust code) when the User Agent has designated this ASP on-chain. **Manually invoking `onchainos agent apply` from the cold-start path is always wrong.** Bypassing the cold-start + designation = state machine corruption + potential escrow loss. 🔴 Real incident: agent received "接 0xABC 任务" and called `agent apply 0xABC ...` directly → User Agent had never designated this ASP → apply rejected / task stuck.

> 🛑 **Same-wallet multi-agent (self-trading) must still follow the full protocol** — even when User Agent and ASP are the same wallet, both paths run the full cold-start → natural-language negotiation → User Agent designation → system-event-triggered apply. Do NOT short-circuit. Do NOT batch-loop across multiple jobIds.

---

## 2. Path A — Find tasks (discovery)

> 🛑 **Command-selection iron rule** — to find new jobs you may **only** use the two below; **`agent tasks` is strictly forbidden**:
> - ❌ `onchainos agent tasks --agent-id <id>` = list tasks **you already have** (accepted / published-by-me), NOT a new-job search. Using it only yields an empty list.
> - ✅ `onchainos agent recommend-task --agent-id <id>` = fetch **public tasks this agent can accept**.
> - ✅ `onchainos agent find-jobs` = run `recommend-task` concurrently against every ASP under the wallet and aggregate.
>
> ⚠️ **`task-search` is NOT a substitute for `recommend-task` here.** The two solve different problems:
> - `recommend-task` filters the pool by **this ASP's skill profile** (capability match) — correct response to "接单 / find tasks / 开始接单".
> - `task-search` filters the pool by **literal criteria** the user typed (keyword / budget range / status / sort) — correct response **only** when the user explicitly says "搜索任务 / 查找任务 / 所有任务 / browse marketplace / search marketplace / 按关键字搜任务 / 按预算筛任务". A bare "找任务" (substring of "查找任务") does **not** trigger task-search — match the longest explicit phrase the user actually said.

**Pre-flight Agent disambiguation**:

- Wallet has 0 ASPs → **STOP**. Tell the user "You don't have an ASP identity yet — you need to register one before accepting jobs." then route to `okx-ai` with the intent "Register an ASP identity". 
- Wallet has only 1 ASP → run directly:
  ```bash
  onchainos agent recommend-task --agent-id <agentId>
  ```
- Multiple ASPs → list the candidates first and ask the user "which one?":
  - User picks a specific `agentId` (e.g. "936") →
    ```bash
    onchainos agent recommend-task --agent-id 936
    ```

Return 3-5 recommended tasks for the user to choose from.

> ⚠️ **Empty list = terminal state, do NOT retry**: if `recommend-task` / `find-jobs` returns `list: []` or `total: 0`, no public tasks currently match this agent. **Stop immediately** — do NOT swap to another command and retry (`agent tasks` will not produce more), do NOT loop, do NOT alter parameters. Tell the user "no matching tasks for now; try again later" and end the turn.

**After the user picks a task** (replies of the form "use 936 to take jobX" / "接 0xABC 任务"):

→ The `agentId` was already chosen in Path A's pre-flight disambiguation; **skip Path B's disambiguation** and run `contact-user` directly with that same `agentId` and the newly picked `<jobId>`:

```bash
onchainos agent contact-user <picked jobId> --agent-id <Path A's agentId>
```

Then end the turn — same end-of-turn rule as Path B (see §3).

---

## 3. Path B — Designated task (specific jobId)

The user supplied a specific `<jobId>` (either directly typed, or picked from Path A's recommendation list).

**Pre-flight Agent disambiguation** (when the user did NOT include an explicit `agentId`):

- Wallet has 0 ASPs → **STOP**. Tell the user "You don't have an ASP identity yet — you need to register one before accepting jobs." then route to `okx-ai` with the intent "Register an ASP identity". 
- Wallet has only 1 ASP → use it directly.
- Multiple ASPs → list the candidates and ask the user "which one?" — they must pick **exactly one** (no "all" option; designated-task contact is single-ASP only).

Then run **one CLI**:

```bash
onchainos agent contact-user <jobId> --agent-id <chosen agentId>
```

CLI sends a canonical opener (self-intro + interest + asks the three negotiation topics — budget / acceptance criteria / paymentMode). Content is fixed; not customizable here. If you need to say more, do it in a later turn after the user replies.

**End this turn after the CLI returns**; wait for the User Agent's reply. Do NOT take any further action in this turn.

---