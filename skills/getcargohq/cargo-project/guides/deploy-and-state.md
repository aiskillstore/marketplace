# Deploy & state

The deploy engine compiles your `define*` graph, diffs it against
`cargo.state.json`, and reconciles the difference to live Cargo infrastructure in
dependency order — persisting state after **each** resource so a mid-deploy crash
leaves a recoverable file.

For every flag, see [`../references/commands.md`](../references/commands.md).

## plan → deploy → destroy

```bash
# Offline: compile the graph and diff against cargo.state.json. No API calls.
cargo-ai project plan --dir my-workspace

# Create/update resources in dependency order; write cargo.state.json.
cargo-ai project deploy --dir my-workspace          # prompts for confirmation
cargo-ai project deploy --dir my-workspace --yes    # non-interactive (CI)

# Tear down.
cargo-ai project destroy --dir my-workspace --target model:contacts   # one resource
cargo-ai project destroy --dir my-workspace --all                     # everything in state
```

Re-running `deploy` only changes what changed — an unchanged workspace is a no-op.
`deploy` is idempotent: for each resource it updates by uuid if state has one,
otherwise adopts a slug-addressable match (connector/model) that already exists,
otherwise creates.

## The deploy state, and the pointer you commit

A project's **deploy state** is the link from your code to the resources Cargo
created. It lives **in your workspace**; the repo commits only a pointer to it:

```json
{ "stateUuid": "8f2c…" }
```

`cargo-ai project init` creates the state and writes that `cargo.state.json`, so the
pointer is in the scaffold commit. The state records only uuids, hashes and outputs
per resource — **never secret values**.

**Commit the pointer.** Without the uuid a fresh checkout cannot find its state, and
a deploy will *not* quietly create a replacement — that would orphan everything the
old state tracks. The state is still the only handle on a deployed **play**,
**agent** or **alert**, which have no slug (unlike connectors and models, which
self-heal by slug). If the pointer is lost, recover it with `state bind` below, or
re-establish links one resource at a time with `import`.

### One state per repo, ten per workspace

```bash
cargo-ai project state list            # every state in this workspace, and which one this project is on
cargo-ai project state create          # create one for this project and write the pointer
cargo-ai project state bind <uuid>     # point cargo.state.json at an existing state
```

`state create` takes `--force` to create a new state even though `cargo.state.json`
already names one, and `--json` to print the created state. `state list` takes
`--json`. All of them take `--dir <path>`.

Deleting a state (`state remove <uuid>`, which drops the state without touching the
live resources it tracked) is documented in the CDK README but is **not** in CLI
1.0.96 — it ships in the next release.

### Migrating a pre-remote-state project

A project scaffolded before states moved to the workspace has the resource map
**inline** in `cargo.state.json`, and keeps deploying against that file for as long
as you leave it there. Nothing migrates behind your back.

`cargo-ai project state create` is what moves it: the map goes onto a new workspace
state, the file becomes a pointer, and you commit it. Coordinate before you do —
a teammate who deploys after the migration but before pulling the new pointer is
deploying from a state that no longer exists.

### Git-ignore the working files

Git-ignore the generated types and the CDK's working files (but **not**
`cargo.state.json`). `cargo-ai project init` scaffolds this:

```gitignore
.cargo-ai/
cargo.state.lock
cargo.state.bak.json
cargo.state.cache.json
cargo.state.audit.jsonl
```

The `cargo.state.lock` prevents two deploys racing; `--force` steals a stale lock.

**Workspace guard:** state records the workspace it was deployed to; the CDK
refuses to `deploy`/`destroy` when the state's workspace ≠ the currently selected
workspace, so you can't accidentally reconcile a dev definition into prod. Select
the right workspace at `login` (or with the workspace flag) before deploying.

## Prune — deleting resources removed from code

`deploy` does **not** delete a resource just because you removed it from code —
that would make a typo destructive. To also remove resources that are in state but
no longer in code:

```bash
cargo-ai project deploy --dir my-workspace --prune
```

Prune deletes in reverse dependency order (dependents before their dependencies).
Adopted resources (linked via `adopt: true` or `import`) are **released** from
state, not deleted.

## Drift — `refresh` and `deploy --refresh`

A resource can change outside the CDK (someone edits an agent in the Cargo UI).
The CDK captures a fingerprint of each resource at deploy and compares on refresh:

```bash
cargo-ai project refresh --dir my-workspace          # read-only: report what drifted
cargo-ai project deploy  --dir my-workspace --refresh # re-read live, re-apply your code over drift
```

`refresh` reports resources changed or deleted out-of-band; `deploy --refresh`
makes your code the source of truth again.

## Adopting existing resources — `import`

To bring an already-live resource under CDK management, bind it into state by
mapping its **code id** to its **live uuid**:

```bash
cargo-ai project import model:contacts 6f0c8e2a-… --dir my-workspace
```

The code id is `kind:slug` (e.g. `connector:hubspot`, `model:contacts`,
`agent:sdr`). After import, `deploy` updates that resource instead of creating a
duplicate. Slug-addressable kinds (connector, model) can also self-adopt on deploy
by matching slug; uuid-only kinds (play, agent, capacity, territory, segment) need
`import` to recover a lost link. See
[`../recipes/migrate-existing-workspace.md`](../recipes/migrate-existing-workspace.md).

## Recovery — `rollback`

`deploy` snapshots the pre-deploy state to `cargo.state.bak.json`. If a deploy went
wrong, restore the snapshot:

```bash
cargo-ai project rollback --dir my-workspace
```

This restores the state file — it does not undo live API changes already made;
follow with a corrected `deploy`.

## Async resources — workers & apps

Most resources create synchronously. **Workers and apps build server-side**: on
deploy the reconciler uploads the bundle, waits for the build, and promotes it —
so a deploy touching a worker/app takes longer. Author worker runtime code with
`createWorker` (`@cargo-ai/worker-sdk`) and build to `index.js` before deploying;
the CDK validates the bundle files (`index.js`, `manifest.json`, `package.json`,
`package-lock.json`) exist at define time. The live URL is exposed on the handle
(`webhook.url`, `dashboard.url`). For imperative one-off hosting operations, see
[`../../cargo-hosting/SKILL.md`](../../cargo-hosting/SKILL.md).
