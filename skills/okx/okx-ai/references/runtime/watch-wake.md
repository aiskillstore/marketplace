# Auto-timeout wake scheduling (platform-specific payloads)

## Module Description

> Loaded from `watch.md` when a fresh `decision_request` comes from an active global or scoped
> watch. A decision opened independently through `outdated-list` / a decision list has no active-watch
> origin: do not schedule a wake for it.


## Flow
### Entry routing and scope

Remember the exact command that produced the decision:

- global: `okx-a2a user watch --json`
- scoped: `okx-a2a user watch --json --job-id <X>`

The wake must carry that exact scope. Never infer a jobId from the decision body, the user's later
reply, or history; never drop a remembered `--job-id` and fall back to global watch.

### Scheduling the wake

After rendering `userContent`, but before ending the turn, schedule a 2-minute **one-shot** wake.
The prompt is one of these exact English strings:

- global: `Pending decision_request auto-timeout reached. Re-enter watch now: okx-a2a user watch --json`
- scoped: `Pending decision_request auto-timeout reached. Re-enter watch now: okx-a2a user watch --json --job-id <X>`

Do not localize, paraphrase, or replace `<X>` with anything except the originating scoped jobId.
The handle returned by either platform tool is the **wake id**.

- **Claude Code** (`CLAUDECODE=1`):

  ```text
  CronCreate(
    recurring: false,
    cron: "<minute> <hour> <DoM> <Mon> *",
    prompt: "<exact global-or-scoped prompt above>"
  )
  ```

  Set the standard five-field expression to now + 2 minutes in local time.

- **Codex** (`CODEX_THREAD_ID` non-empty):

  ```text
  codex_app.automation_update(
    mode: "create",
    kind: "heartbeat",
    destination: "thread",
    rrule: "DTSTART:<YYYYMMDDTHHMMSS>\nRRULE:FREQ=MINUTELY;COUNT=1",
    prompt: "<exact global-or-scoped prompt above>",
    status: "ACTIVE"
  )
  ```

  `DTSTART` is now + 2 minutes in UTC basic format. `COUNT=1` is mandatory.

If the scheduling tool is unavailable or errors, skip silently. Do not replace it with a recurring
cron, sleep loop, or a different prompt.

### When the wake fires

First apply a chronology guard. The wake is stale and must do nothing if, after it was scheduled, any
of these occurred in the conversation:

- the user replied to that decision;
- the decision was claimed, deferred, or otherwise handled;
- a newer explicit watch entry replaced the active global/scoped scope;
- the user explicitly stopped watching; or
- a newer watch invocation already resumed the same origin.

If it is still current, run the exact command embedded in the prompt, without a banner. Preserve global
versus scoped origin exactly. The consumed decision itself will not reappear in watch; while unclaimed it
remains available through `okx-a2a user outdated-list` (see
[`backlog.md`](backlog.md)).


## Troubleshooting
### Cancelling the wake

Reply handling and scope replacement best-effort cancel the remembered wake before continuing:

- Claude Code: `CronDelete(<wake id>)`
- Codex: `codex_app.automation_update(mode: "delete", id: <wake id>)`

If the wake id is unavailable after context compaction, or cancellation errors, proceed without searching
for a matching automation. The chronology guard prevents a stale wake from reviving an obsolete scope.
