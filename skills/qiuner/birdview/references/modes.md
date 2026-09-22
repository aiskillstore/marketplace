# Project Activation Mode

[中文](modes.zh.md)

Birdview is on-demand by default, defaulting to `on-demand`. It runs when the user selects the skill, explicitly requests Birdview or asks for an architecture/constraint/change map. Ordinary coding, small fixes and feature planning do not trigger it; planning alone does not authorize editing.

## Invocation

In Codex, select Birdview through `/skills` or mention `$birdview`; in Claude Code, use `/birdview`. Other hosts use their own skill selector or an explicit request; the same slash commands are not guaranteed. Invocation applies to the current task. Merely discussing Birdview does not start mapping.

## Configuration and migration

```sh
node <skill-root>/scripts/birdview.mjs setup --project <project-root>
node <skill-root>/scripts/birdview.mjs mode auto --project <project-root>
node <skill-root>/scripts/birdview.mjs mode on-demand --project <project-root>
node <skill-root>/scripts/birdview.mjs mode off --project <project-root>
node <skill-root>/scripts/birdview.mjs mode --project <project-root>
node <skill-root>/scripts/birdview.mjs uninstall --project <project-root>
```

`setup` defaults new projects to `on-demand` and preserves any existing `auto`, `on-demand` or `off` mode. Use `mode auto` to opt in to activation before every code-changing task, including small edits, and planning that explicitly analyzes affected modules. Use `mode on-demand` to return to explicit invocation. Queries are read-only. Updating skill files does not rewrite other projects; verify the selected mode in a fresh task.

Foundation rules are separate from map activation. `setup`, `mode auto` and `mode on-demand` install [foundation.txt](foundation.txt), covering focused source reading, evidence, proportional verification and collaboration records without requiring skill reading or mapping. `off` disables foundation and mapping except for explicit invocation in the current task. `uninstall` removes only the project block, preserving the file, other rules, skill and maps; retaining the skill restores default on-demand behavior.

## Storage and boundaries

Use absolute paths for the installed skill and target project root. Without `--project`, only the current directory is used; parents are not searched. `--agent codex` (default) and `--agent deepseek` use `AGENTS.md`; `--agent claude-code` uses `CLAUDE.md`. Use the same agent for reads and writes; files are not synchronized. A source checkout can optionally run `npm link` and use `birdview mode`; Node commands do not require linking.

Only the block between `<!-- birdview:mode:start -->` and `<!-- birdview:mode:end -->` is modified; surrounding bytes are preserved. Repeated configuration is idempotent; malformed or duplicate markers and non-regular files prevent writes. Managed blocks contain English machine instructions.

These settings depend on host loading, not filesystem interception. Do not overwrite conflicting instructions elsewhere; report known conflicts. Existing sessions may retain old instructions, and CLI tests establish configuration behavior only; verify actual skill selection and artifacts in a new task.
