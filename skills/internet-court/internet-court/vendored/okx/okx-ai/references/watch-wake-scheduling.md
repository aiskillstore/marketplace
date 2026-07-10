# Auto-timeout wake scheduling (platform-specific payloads)

> Loaded from `watch-core.md` §`kind == decision_request` only when a fresh `decision_request` lands in a **global** session and you need to schedule the 2-minute self-resume wake. Skip entirely for scoped sessions (see the gating note in watch-core.md).

After rendering `userContent`, but **before ending the turn**, schedule a 2-minute **one-shot** wake so the watch loop self-resumes if the user goes idle. Pick the tool by platform (same env vars as `watch-core.md` §Platform compatibility).

> **Terminology**: the handle returned by either tool is called the **wake id** in this skill.

🛑 **Critical for both platforms**: the `prompt` field must be passed **verbatim** as the exact English string below. Do **NOT** localize it, paraphrase it, or rewrite it based on the current `decision_request`'s content (e.g. do not turn it into "请选择服务商" / "回复 1 或 1727"). The wake fires in a fresh turn; the agent reading the wake prompt must see a generic, content-free "re-enter watch" instruction so it routes back into this skill — a contextualized prompt confuses both the scheduler view and the next-turn agent.

- **Claude Code** (`CLAUDECODE=1`):
  ```
  CronCreate(
    recurring: false,
    cron: "<minute> <hour> <DoM> <Mon> *",
    prompt: "Pending decision_request auto-timeout reached. Re-enter watch now: okx-a2a user watch --json"
  )
  ```
  Field notes (do **not** inline these into the call):
  - `cron`: standard 5-field expression set to **now + 2 minutes in local time**. Example: if now is 14:28 local, use `30 14 <today_DoM> <today_Mon> *`.

  Remember the returned **wake id** (it stays in the assistant transcript and is visible in the next turn).

- **Codex** (`CODEX_THREAD_ID` non-empty):
  ```
  codex_app.automation_update(
    mode: "create",
    kind: "heartbeat",
    destination: "thread",
    rrule: "DTSTART:<YYYYMMDDTHHMMSS>\nRRULE:FREQ=MINUTELY;COUNT=1",
    prompt: "Pending decision_request auto-timeout reached. Re-enter watch now: okx-a2a user watch --json",
    status: "ACTIVE"
  )
  ```
  Field notes (do **not** inline these into the call):
  - `rrule`: iCalendar RRULE syntax — exactly two lines joined by a literal `\n`:
      1. `DTSTART:<YYYYMMDDTHHMMSS>` — UTC basic format (e.g. `20260607T143000`) set to **now + 2 minutes in UTC**.
      2. `RRULE:FREQ=MINUTELY;COUNT=1` — fires exactly once (the `COUNT=1` guarantees one-shot semantics).

  Remember the returned **wake id**.

If the scheduling tool is unavailable (unknown tool / returns an error) → **skip silently** and end the turn. The user can re-trigger watch manually if they ignore the item.

**When the wake fires (user idle 2 min)**: its prompt runs `okx-a2a user watch ...` in a fresh turn, which resumes monitoring for **new** events. The original `decision_request` item is **not** re-surfaced by watch — it was already consumed when it first appeared (watch is destructive read). But because the user never `check`ed it, it remains in the outstanding-decisions queue and can be retrieved on demand via `okx-a2a user outdated-list` (see `references/outdated-list.md`). No extra logic needed here.

**Cancelling the wake** (first step of reply handling, back in watch-core.md §Handling the user reply): best-effort cancel the wake scheduled in the previous turn:
- Claude Code: `CronDelete(<wake id>)`
- Codex: `codex_app.automation_update(mode: "delete", id: <wake id>)`
- If the **wake id** is not visible in the assistant transcript (context compacted) or the cancel call errors → **skip and proceed**. Do NOT search for the wake by name/prompt match. A stale wake firing afterwards is harmless: it just re-enters watch to monitor new events; the already-handled `decision_request` item does **not** reappear in watch (it was consumed on the original return — watch is destructive read).
