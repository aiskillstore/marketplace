# Maintaining projects

Run commands from the project root or append `--cwd /actual/project/path`. Resolve one CLI version and retain it throughout an operation. The examples use the newest published release. For preview and application, pin the package to the same exact version, for example `vibestart-cli@0.1.0-beta.1`.

`vibestart.jsonc` is the whole maintenance state: the choices, the project `name`, and the `version` of the release that generated it. The CLI regenerates that release's templates as the merge base, running it from npm when it is not the running release. A project whose record lacks `name` or `version` cannot be maintained; restore them from Git history rather than guessing.

## Inspect project state

```sh
npx --yes vibestart-cli doctor --offline --json
```

`doctor` is read-only. Inspect `issues`, `conflicts`, `updates`, `manual`, `release`, and `status`. With `--offline`, a project recorded by another release returns `updates: null` and `manual: null`: not compared, not up to date. Without `--offline`, it also looks up npm’s `latest` channel, not the `beta` channel; `latest: null` is not proof that no release exists. A healthy result checks configuration and maintenance state, not application behavior.

## Add capabilities

```sh
npx --yes vibestart-cli add --list --json
npx --yes vibestart-cli add knip ultracite --dry-run --json
npx --yes vibestart-cli add knip ultracite --yes --json
```

Pass capability IDs as separate positional arguments. Currently Knip, Ultracite, and Docker support addition; use the live list for the running release. Add Docker with `npx --yes vibestart-cli add docker`, following the same preview/apply workflow. Already selected capabilities are not duplicated.

`requires-upgrade` means the recorded template and current CLI release differ. Preview an upgrade first; apply it only if it fits the user's requested scope. `add` is not a framework, database, runtime, or package-manager migration command.

## Upgrade templates

```sh
npx --yes vibestart-cli upgrade --check --json
npx --yes vibestart-cli upgrade --dry-run --json
npx --yes vibestart-cli upgrade --yes --json
```

The target is the template bundled with the running CLI, not implicitly the latest npm release. `--to VERSION` selects an exact published version; replace `VERSION` with an actual version and use the same value for preview and application. Tags such as `beta` or `latest` and semver ranges are not accepted by `--to`. Fetching a different release executes its generator and requires registry access.

The CLI compares the original template, current project, and target template. `changes` updates supported configuration and dependency files while preserving business edits, and records the target release in `vibestart.jsonc`. `manual` lists template changes to files the project owns, such as starter source, with the previous (`before`) and target (`after`) template content; the CLI never writes them. This command does not promise arbitrary application migrations or update every dependency to npm's latest version.

Review the returned changes, conflicts, and manual entries before applying. The default write flow installs dependencies through `vp install`, runs `vp check`, runs Knip if selected, and runs the existing unit test project if present. It does not automatically initialize, migrate, or reset a database.

- `--full-check` on `add` or `upgrade` selects `vp run ready` instead of the default checks. It may need databases, listening ports, and a browser.
- `--no-install` on `add` or `upgrade` writes files and returns `needs-install`; `next` names the installation and checks to run. Only use it when deferral is intentional; report the operation as unfinished.
- These two flags cannot be combined.

## Finish a write

A write starts from a clean Git worktree, so `git diff` is exactly the change. The write is finished when no conflict markers remain, every `manual` entry is ported or deliberately declined with the user, and the installation and checks in `next` pass.

- **`conflicts`**: the files hold both sides between `<<<<<<< project`, `||||||| previous template`, `=======`, and `>>>>>>> target template`; installation was skipped. Resolve each using the user's code and the intended template change, rather than choosing every incoming side. A maintained file the user had deleted is restored; ask whether to keep it.
- **`manual`**: port each template change into the user's code. Diff `before` against `after` to see the intent, then apply it where the user's version of the file differs.
- **A failed installation or check** leaves the files written. Fix the cause and rerun the failed step.

To abandon the write, `git restore . && git clean -fd` returns the project to the commit it started from. It does not restore `node_modules` or database data.

## Automation contract

Maintenance JSON includes `ok`, `exitCode`, and `status`. Caught errors use an `error` string; creation instead uses an error object. Non-interactive writes require `--yes` as well as `--json`.

| Result                  | Interpretation                                                              |
| ----------------------- | --------------------------------------------------------------------------- |
| `planned`               | Preview only; nothing applied                                               |
| `no-op`                 | No change required                                                          |
| `needs-install`         | Files written; installation and validation unfinished                       |
| `conflicts`             | A preview found conflicts, or a write left conflict markers in the files    |
| `completed`             | Operation finished with its checks; `manual` may still hold changes to port |
| `healthy` / `attention` | Doctor's configuration and maintenance assessment                           |
| `failed`                | Inspect the error and `git status` before choosing the next action          |

Exit `0` includes previews and deferred installation. Exit `1` includes failures, conflicts, and available changes from `upgrade --check`; inspect the result instead of blindly retrying. Invalid maintenance arguments exit `2`; cancellation exits `130`. Do not combine `--check` with `--dry-run`.
