---
name: orca-cli
description: >-
  Use the `h0x` CLI to operate h0x-ADE-managed worktrees, folder contexts,
  terminals, repos, automations, artifacts, skill sharing, worktree comments, and h0x-ADE's
  embedded browser. Use when the user says "$orca-cli", "use h0x cli",
  "h0x-ADE worktree", "child worktree", "cardStatus", "spawn codex/claude in a worktree",
  "read/wait/send h0x-ADE terminal", "terminal send", "full handoff", "handover",
  "give this to another agent", "another worktree", "h0x-ADE browser", "h0x artifacts",
  "share HTML/Markdown", "public artifact link", "share skills", or "control the browser inside
  h0x-ADE". Prefer this over raw `git worktree`, ad hoc
  PTYs, Playwright, or Computer Use when the task touches h0x-ADE-managed state.
  Use Computer Use for external browser windows, webviews, or desktop UI only
  when the task requires OS/window-level control such as focus, menus, dialogs,
  coordinates, or screenshots. Use `orca-cli` for h0x-ADE's embedded pages and a
  page-automation tool such as Playwright or CDP for external pages.
---

# h0x CLI

This file is a discovery stub, not the usage guide. The full, version-matched h0x CLI
reference is served by the `h0x` binary itself — kept out of this file on purpose so it
can never drift from the binary that will actually run your commands.

Engage h0x-ADE whenever its running editor/runtime is the source of truth: h0x-ADE-managed
worktrees, folder contexts, terminals, repos, automations, worktree comments, and the
browser embedded inside the h0x-ADE app. Triggers include "$orca-cli", "h0x-ADE worktree",
"child worktree", "spawn codex/claude in a worktree", "read/wait/send h0x-ADE terminal",
"full handoff" / "handover" / "give this to another agent", and "control the browser
inside h0x-ADE". Use plain shell tools when h0x-ADE state does not matter.

## Resolve the CLI for this session

Choose the executable once and reuse it for every later command:

- If the `ORCA_CLI_COMMAND` environment variable is set, use its value. h0x-ADE exports this
  for managed WSL sessions.
- Otherwise, in a dev checkout whose session exposes `ORCA_DEV_REPO_ROOT`, use `h0x-dev`.
- Otherwise, on Linux outside an h0x-ADE-managed terminal, use `h0x`. Never run bare
  `orca` there — outside Orca's terminals it normally resolves to the
  GNOME Orca screen reader (`/usr/bin/orca`) and starts speech on the user's machine.
- Otherwise, use `orca`.

Below, `ORCA` is a placeholder for the executable you resolved. Substitute it before
running anything; do not create a shell variable or run `ORCA` literally. This works the
same way in POSIX shells, PowerShell, and cmd.exe.

If the selected executable cannot run, report its exact error and stop. Do not fall through
to another executable, which could silently target a different h0x-ADE build.

## Load the full guide before running h0x commands

```text
ORCA skills get orca-cli
```

That prints the complete, version-matched guide for the exact binary that will handle your
next commands — worktrees, handoffs, terminals, automations, and the built-in browser.
Read it first, then run the specific command you need.

Don't guess subcommands or flags from memory or from a cached copy of this stub. They
change between h0x-ADE releases, and this file deliberately no longer lists them. Confirm the
app is up with `ORCA status --json` (start it with `ORCA open --json` if needed), and
prefer `--json` for agent-driven calls.

## If an older Orca does not recognize `skills get`

Use this fallback only when the selected binary explicitly reports that `skills get` is an
unknown command. Another failure is not proof of an older binary; report it rather than
guessing or changing executables. For a confirmed pre-guide binary, use only this bounded,
read-only bootstrap to orient. Do not dead-end and do not invent commands:

```text
ORCA status --json
ORCA worktree ps --json
ORCA terminal list --json
```

Then tell the user that updating h0x-ADE restores the full, version-matched guide via
`ORCA skills get orca-cli`. Beyond these commands, ask the user rather than guessing a
command surface this older binary may not support.
