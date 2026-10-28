# Background-watch recovery

## Module Description

> Loaded from `watch.md` §Anti-patterns only when a watch call accidentally ended up in the background. Rare error path — not part of the normal loop.

**When this applies**: you accidentally set `run_in_background: true`, or the Bash tool's foreground timeout elapsed and Claude Code's harness silently re-routed the watch command to the background. The harness then delivers the watch output as a background-task notification event, often wrapped in `<system-reminder>` carrying `[SYSTEM NOTIFICATION - NOT USER INPUT]` and `Do NOT interpret this as user acknowledgement`.

🛑 **Critical interpretation rule**: that wrapper is **anti-confusion** ("don't treat this as a user reply"), **not anti-disclosure**. The notification body is still meant for the user — only you saw it. Silencing the event because the wrapper says "NOT USER INPUT" is a misinterpretation; you MUST still relay it.

**Recovery flow**:

1. **Locate the output-file path in the notification payload** — the harness includes a filesystem path where the watch's stdout was written (exact field name varies by harness version: look for something like `output-file` / `output_file` / `file`, or a value that looks like a writable file path). Use the `Read` tool on that path — it contains the watch JSON output.
2. Parse the JSON items and dispatch each per `watch.md` §Dispatch (paste blockquote for notifications; paste blockquote for decision_requests; same rules, same no-thinking ban).
3. **Locate the task identifier in the notification payload** (exact field name varies: look for `task-id` / `task_id` / `id` / `bg_id`). Best-effort call the `TaskStop` tool on it after dispatch — leaving a live task will keep producing more out-of-band events. Record whether the old task is confirmed exited or stopped; if its liveness remains unknown, mark that Watch generation no longer current so neither re-entry nor a decision wake can start a replacement watcher.
4. Only after the old task is confirmed exited or stopped, restart watch **in the foreground** per `watch.md` §Run watch (preserving sticky `--job-id <X>` per §Session-scoped sticky if applicable).
