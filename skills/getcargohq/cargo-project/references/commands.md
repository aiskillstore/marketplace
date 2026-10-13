# Command reference — `cargo-ai project`

All subcommands accept `--dir <path>` (the project root, default `.`) and `--json`
(machine-readable output). Run from the project root so `.cargo-ai/` and
`cargo.state.json` land in the right place. Confirm the surface live with
`cargo-ai project <subcommand> --help`.

| Command | What it does |
|---|---|
| `cargo-ai project init <directory>` | Scaffold a GTM repo from `getcargohq/cargo-manifest`, with the CDK project in `infra/`. `--name <name>`, `--cookbook <slug>` (install a cookbook into the new project), `--force` (write into a non-empty directory). There is no template flag: the scaffold never varies, and what varies is the cookbook layered on top. |
| `cargo-ai project add cookbook/<slug>` | Copy a worked example into this project — resources under `infra/<slug>/`, any helper scripts under `scripts/<slug>/`, and its procedure (`SKILL.md`, `references/`, `evals/`) under **both** `.claude/skills/<slug>/` and `.agents/skills/<slug>/`. Runs `check` afterwards so a duplicate slug surfaces immediately; never deploys, and never touches your `package.json`/`tsconfig.json`. `--overwrite` (replace existing files; default skips them), `--yes`. Omit the address to choose interactively. |
| `cargo-ai project add connector/<integration>` | Authorize a connector in the browser and write its `defineConnector`. `--connector-uuid <uuid>` adopts one already created there. |
| `cargo-ai project cookbook list\|search\|view` | Browse the cookbooks `add` installs — `view <slug>` shows what one deploys, what it will ask you for, and its declared adaptations. |
| `cargo-ai project types` | Generate per-workspace types into `.cargo-ai/` for typed config. |
| `cargo-ai project check` | Offline: validate the resource tree — every body / slug / graph error in one pass, **without** computing the diff, so it needs no state. The fast, CI/editor-friendly subset of `plan`. `--json`. |
| `cargo-ai project plan` | Offline: compile the graph and diff against this project's deploy state. No API calls. |
| `cargo-ai project info` | Print the resolved project — every declared resource, the file that declared it, whether it is deployed, and any diagnostics. Offline, and never fails. `--json`. Also what bare `cargo-ai project` does inside a project. |
| `cargo-ai project deploy` | Create/update resources in dependency order; write state. Prompts unless `--yes`. |
| `cargo-ai project refresh` | Read-only: report resources that drifted from code (changed/deleted out of band). |
| `cargo-ai project import <id> <uuid>` | Bind an existing live resource (`kind:slug`) to a uuid in state. |
| `cargo-ai project pull` | Generate `define*` source from a live workspace **and adopt it** into this project's deploy state, so the next deploy is a no-op rather than a duplicate-create. `--types <kinds>` (comma-separated; default all — connector, customIntegration, model, relationship, segment, folder, capacity, territory, tool, play, mcpServer, agent, alert, file, worker, app, context, mailbox), `--dry-run`, `--no-adopt` (write files but skip adoption — leaves a repo whose deploy would duplicate; advanced), `--force`, `--json`. |
| `cargo-ai project rollback` | Restore the deploy state from the snapshot taken before the last deploy/destroy/import. |
| `cargo-ai project state list\|create\|bind` | Inspect and repoint this project's deploy state — the workspace-held record of which live resource each declared one became. See [`../guides/deploy-and-state.md`](../guides/deploy-and-state.md). |
| `cargo-ai project destroy` | Tear down resources recorded in state. `--target <id>` for one, `--all` for everything. |

## Common flags

- `--dir <path>` — project root (default `.`).
- `--yes` — skip the confirmation prompt (**required in CI / non-interactive**).
- `--json` — machine-readable output.
- `--force` — steal a stale `cargo.state.lock`.

## `deploy` modifiers

- `cargo-ai project deploy --prune` — also **delete** resources that are in state but
  removed from code (reverse dependency order; adopted resources are released, not
  deleted).
- `cargo-ai project deploy --refresh` — re-read live resources and re-apply your code
  over any out-of-band changes.

## `destroy` targets

- `cargo-ai project destroy --target <kind:slug>` — remove one resource (refused if
  other state resources still depend on it).
- `cargo-ai project destroy --all` — remove everything in state, dependents first.

## Examples

```bash
cargo-ai project init acme                        # scaffold
cargo-ai project add cookbook/tam-building --dir acme  # layer a worked example on
cargo-ai project types --dir acme                 # type config
cargo-ai project plan --dir acme                  # preview
cargo-ai project deploy --dir acme --yes          # apply (non-interactive)
cargo-ai project refresh --dir acme               # drift report
cargo-ai project import agent:sdr <uuid> --dir acme  # adopt a live agent
cargo-ai project destroy --dir acme --all --yes   # tear down
```
