# Recipe: scaffold a project from scratch

**Use when** the user wants to stand up a new Cargo **project** — the repo that
declares resources and deploys them into a workspace — reproducibly. Follow these
steps as your execution plan.

## 1. Scaffold

```bash
cargo-ai project init acme-gtm                              # the repo, empty
cargo-ai project init acme-gtm --cookbook tam-building      # the repo plus a worked example
```

The scaffold itself never varies — it is one GTM repo from
`getcargohq/cargo-manifest`, with the resources it deploys in `infra/`. What varies is
whether a cookbook is layered on top, so reach for `--cookbook <slug>` when the
user wants a working pipeline to adapt rather than an empty project.
`cargo-ai project cookbook list` names them; see
[`references/cookbooks.md`](../references/cookbooks.md).

## 2. Install and authenticate

```bash
cd acme-gtm && npm install   # pulls @cargo-ai/cdk + zod
cargo-ai login               # authenticate + select the workspace to deploy INTO
cargo-ai whoami              # confirm the selected workspace
```

## 3. (Optional) Generate typed config

```bash
cargo-ai project types                     # types config against this workspace's integrations
```

Not required to deploy, but it makes `defineConnector`/`defineModel` config and
`integrations.*` in workflow bodies type-check. See
[`../guides/typed-config.md`](../guides/typed-config.md).

## 4. Set secrets

Any `secret("NAME")` in the code resolves from the environment at deploy time.
Export each one first:

```bash
export HUBSPOT_API_KEY=...             # matches secret("HUBSPOT_API_KEY") in connectors/hubspot.ts
```

A missing env var fails the deploy with an unresolved `${NAME}` placeholder.

## 5. Plan, then deploy

```bash
cargo-ai project plan                      # offline diff — review what will be created
cargo-ai project deploy                    # create everything, record it in the deploy state
```

`deploy` prompts for confirmation. Review the plan output first; it lists each
resource as create / update / no-op.

## 6. Commit state

```bash
git add cargo.state.json && git commit -m "Deploy initial workspace"
```

The **deploy state** is the link from code to the deployed resources — and the only
handle on deployed plays/agents. It lives in your workspace; `cargo.state.json` is the
committed pointer to it (`{"stateUuid": "…"}`), written by `project init`, so this
commit is usually just confirming it is tracked. Commit it: without the uuid a fresh
checkout cannot find its state. The `.gitignore` scaffolded by `project init` already
excludes `.cargo-ai/`, the lock, cache, backup, and audit files.

## 7. Iterate

Edit `define*` files, then `cargo-ai project plan` → `cargo-ai project deploy` again — only
what changed is applied. To tear the workspace back down:

```bash
cargo-ai project destroy --all
```

See [`../guides/authoring-resources.md`](../guides/authoring-resources.md) to add
resources and [`../guides/deploy-and-state.md`](../guides/deploy-and-state.md) for
prune/drift/rollback.
