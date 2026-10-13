# Troubleshooting

## `✗ Deploy failed: connector:<slug>: Invalid configuration`

The connector's `config` doesn't match the integration's schema. Most often the
credential wasn't wrapped in `secret()` — a data connector's credential field
expects an encryption envelope, and `secret("ENV_VAR")` produces it. Fix:

```ts
config: { method: "privateApp", accessToken: secret("HUBSPOT_API_KEY") }, // not a bare string
```

Run `cargo-ai project types` so the config type-checks against the real schema at
author time and surfaces the required shape (see
[`../guides/typed-config.md`](../guides/typed-config.md)). The deploy error now also
surfaces the API's structured detail (which field, the reason) — read past the
terse "Invalid configuration" summary.

## `unresolved placeholder "${NAME}"`

A `secret("NAME")` or `env("NAME")` had no matching environment variable at deploy.
The CDK refuses to send a literal `${NAME}` to the API. Export it first:

```bash
export NAME=...
cargo-ai project deploy
```

## Deploy refuses: workspace mismatch

`cargo.state.json` records the workspace it was deployed to; `deploy`/`destroy`
refuse when that ≠ the currently selected workspace (a guard against reconciling a
dev definition into prod). Select the right workspace at `login`, or use a separate
state file per environment.

## `.cargo-ai/` or `cargo.state.json` landed in the wrong directory

On CLI ≥ 1.0.83 this should not happen from inside the repo: commands walk **up** to
the package root where `@cargo-ai/cdk` is declared, then back **down** to the resource
directory (`infra/`). If the files still land somewhere unexpected, you are either on
an older CLI, outside the repo entirely, or in a tree with no `@cargo-ai/cdk` in any
parent `package.json`. Pass `--dir <project-root>` explicitly.

## `integrations.<slug>` is `any` / not callable, or `config` isn't type-checked

Types aren't generated or aren't wired in. Run `cargo-ai project types`, ensure
`tsconfig.json` `include` has the explicit glob `".cargo-ai/**/*.d.ts"` (a bare
`.cargo-ai` dot-dir is ignored by TypeScript), and `import "./.cargo-ai/cargo-register.js";`
at the top of workflow modules that use `integrations.*`. Re-run `project types` after
changing workspace integrations.

## `could not parse the workflow body`

A `defineWorkflow` body must be a supported JS subset — it's **parsed, not
executed**. Remove `await`, `throw`, `try/catch`, closures over outer variables,
and destructuring; compile workflow files with a modern target (ES2022+) and don't
instrument them with coverage tools (they rewrite the function source). Use
`js(({ nodes }) => …)` for logic outside the supported subset.

## Deploy is slow / seems to hang on a worker or app

Workers and apps **build server-side** — the reconciler uploads the bundle, waits
for the build, and promotes. This is expected to take longer than other resources.
Ensure the worker bundle dir has a built `index.js` (+ `manifest.json`,
`package.json`, `package-lock.json`) before deploying.

## A play or agent got orphaned (state lost)

Plays, agents and alerts have no slug, so the deploy state is the only link to them.

**If you lost the `cargo.state.json` pointer** but the state still exists in the
workspace, this is recoverable without touching resources: `cargo-ai project state list`
shows every state in the workspace, then `cargo-ai project state bind <uuid>` repoints
the repo at the right one. Commit the restored pointer.

**If the state itself is gone**, find each live uuid via the matching capability skill
and rebind one at a time: `cargo-ai project import agent:<slug> <uuid>`.

Never delete `cargo.state.json` to "start clean" — on a pre-remote-state project that
is the resource map itself, and on a current one it is the only record of which of the
workspace's states is yours.

## `zod` errors, or schemas that should match don't

`@cargo-ai/cdk` takes **zod as a peer dependency** (`^4.4.3`, since `@cargo-ai/cdk`
1.0.76) precisely so a project resolves exactly one copy. Two copies in the tree give
you two different `z` identities and schemas built with one won't satisfy the other.
Check with `npm ls zod` — one entry, on a `4.x` matching the peer range.

## `plan` shows `create` for a resource that already exists

Its `kind:slug` id didn't match state. Either the slug in the `define*` changed, or
you migrated a workspace without importing — bind it: `cargo-ai project import <kind:slug> <uuid>`
(see [`../recipes/migrate-existing-workspace.md`](../recipes/migrate-existing-workspace.md)).

## Still stuck

File a report so the Cargo team sees it:
`cargo-ai workspaceManagement report create --title "<summary>" --description "<commands tried, errorMessage, expected vs actual>"`
— see [`../../cargo-workspace-management/SKILL.md`](../../cargo-workspace-management/SKILL.md).
