---
name: cargo-project
description: "Manage a whole Cargo workspace as code — declare connectors, models, plays, tools, agents, MCP servers, segments, context, folders, files, workers, and apps in TypeScript, then reconcile them with `cargo-ai project` (init → types → plan → deploy), the way you would run Pulumi or the AWS CDK. Triggers: \"as code\", \"in git\", \"version-controlled\", \"reproducible\", \"Terraform for Cargo\", \"set up a whole workspace\", \"staging and production\", \"deploy the workspace from CI\", \"review this in a PR\", \"cargo.state.json\", \"scaffold from a template\", \"is there a cookbook for this\", \"start from a cookbook\". Skills with a CDK example (TAM building, account scoring, call capture, inbound qualification, CRM enrichment, standup) live in gtm-skills; menu in references/cookbooks.md. Skip when: it is a one-off operation, a read, or an ad-hoc query — use the matching capability skill."
version: "3.1.0"
compatibility: Requires @cargo-ai/cli (npm). Sign in or create an account with `cargo-ai login --email` (emailed code, no browser), `--oauth`, or an API token
homepage: https://github.com/getcargohq/cargo-skills
metadata:
  author: getcargo
  openclaw:
    requires:
      bins:
        - cargo-ai
    install:
      - kind: node
        package: "@cargo-ai/cli@latest"
        bins:
          - cargo-ai
    homepage: https://github.com/getcargohq/cargo-skills
---

# Cargo project — a Cargo workspace, declared in a repo

Use this skill to define a Cargo workspace in TypeScript (`define*` builders from
`@cargo-ai/cdk`) and reconcile it to live infrastructure with `cargo-ai project deploy`.
It is the **declarative** counterpart to the imperative capability skills: instead
of running one CLI command per resource, you write the whole graph once and deploy
it repeatably, with a **deploy state** — held in your workspace, pointed at by a
committed `cargo.state.json` — linking your code to what Cargo created.

> **"Project" and "workspace" are two different things — keep them apart.** A
> **workspace** is the Cargo tenant you sign into: it holds the models, connectors,
> agents, mailboxes and credits, and it is what `login --workspace-name` selects and
> what `whoami` reports. A **project** is the *repo* that declares resources and
> deploys them into a workspace: it is what `project init` scaffolds, what
> `cargo.state.json` points from, and what `--dir` locates. One project deploys into
> one workspace at a time — the workspace guard refuses a deploy when the state's
> workspace isn't the selected one — and the same project reaches a dev and a prod
> workspace through a different deploy state each. Say "project" for the repo, and
> don't name a project directory `my-workspace`.

## Bootstrap

Already signed in (`cargo-ai whoami` returns a workspace)? Skip to the next section.

```bash
npm install -g @cargo-ai/cli            # no global install? prefix every command with `npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # emailed code, no browser; creates the account on first use
                                        # alternatives: --oauth (browser) · --token <api-token> (CI)
cargo-ai whoami                         # confirm the active workspace before any write
cargo-ai project --help                     # `unknown command` = CLI too old; reinstall @cargo-ai/cli@latest
```

Two CDK-specific extras: the project needs **`@cargo-ai/cdk` as a dependency** for the `define*` builders you import (`cargo-ai project init` scaffolds a `package.json` with it — then `npm install`), and the `cargo-ai project` domain ships with the CLI itself.

Every command prints JSON to stdout; failures exit non-zero with `{"errorMessage": "..."}`. Anything that creates a run or a batch is async — pass `--wait-until-finished` or poll the matching `get`. When the full skill bundle is installed, [`../cargo/references/prerequisites.md`](../cargo/references/prerequisites.md) adds the CLI version pin, token scopes, and the admin-only surface.

## 1) What this skill governs

- **Authoring** every Cargo resource with a `define*` builder that returns a
  **handle**; wiring resources by passing handles to each other (the dependency
  graph is your variable graph).
- **Deploying** the graph: `plan` (offline diff) → `deploy` (create/update, write
  state) → `destroy` (tear down). Plus drift (`refresh`), adoption (`import`), and
  recovery (`rollback`).
- **Typing** the config against your workspace's real integration schemas
  (`cargo-ai project types`).

The CDK spans **every** resource kind — so it overlaps every imperative capability
skill (`cargo-connection`, `cargo-storage`, `cargo-ai`, `cargo-orchestration`,
`cargo-content`, `cargo-hosting`, …). Which to reach for is the first decision:

## 2) CDK or the CLI? — the routing decision

> **Declarative (this skill) vs imperative (a capability skill).**

Use the **CDK** when the user is **managing resources as an artifact**:

- "Set up / stand up / bootstrap a whole workspace (as code / from a template)."
- "Make this reproducible / version-controlled / in git / repeatable across
  environments (dev → prod)."
- "Deploy these connectors + models + agents together" (a multi-resource graph
  wired by dependency).
- Anything that should be re-runnable and diffable, where losing the definition
  would be a problem.

Use the matching **capability skill** (imperative `cargo-ai <domain>`) when the
user is doing a **one-off operation** or **exploring**:

- "Create one connector", "add a column to this model", "list connectors",
  "run this workflow", "query storage", "read this agent's memory."
- Any read, ad-hoc query, or single mutation that doesn't need to live in code.

When unsure, ask whether the result should be committed and re-deployable. If yes
→ CDK. If it's a quick action or a read → the capability skill (see the
[`cargo` router](../cargo/SKILL.md) to pick the right domain).

## 3) The lifecycle

```
cargo-ai project init <dir>     scaffold from getcargohq/cargo-manifest; resources in infra/
        │
cargo-ai project types          generate per-workspace types for typed config (optional)
        │
   (author define* files)   importing a .ts file IS registration — no manifest
        │
cargo-ai project plan           offline: compile the graph, diff against the deploy state
        │
cargo-ai project deploy         create/update resources in dependency order, write state
        │
cargo-ai project destroy        tear down resources recorded in state
```

> **`project plan` says what resources change; it doesn't show what a play does.**
> For a `definePlay` / `defineTool` graph past three nodes, present a Mermaid
> flowchart of the node graph alongside the plan — routing, fallbacks, and which
> nodes bill on every scheduled run are what the reviewer is approving. Generate it
> from the deployed release after the first deploy, or from the node array while
> authoring:
> [`../cargo-orchestration/references/node-diagram.md`](../cargo-orchestration/references/node-diagram.md).

Side branches: `cargo-ai project check` (validate the tree, no state, no API calls —
the CI/editor subset of `plan`) · `cargo-ai project info` (what is here: every declared
resource, the file that declared it, whether it is deployed) · `cargo-ai project refresh`
(read-only drift report) · `deploy --refresh` (re-apply code over out-of-band edits) ·
`deploy --prune` (delete resources removed from code) · `cargo-ai project import <id> <uuid>`
(bind an existing live resource into state) · `cargo-ai project pull` (generate `define*`
source from a live workspace and adopt it) · `cargo-ai project rollback` (restore the
pre-deploy state snapshot) · `cargo-ai project state` (inspect and repoint the deploy state).

**`plan` and `info` answer different questions.** `plan` answers *what will deploy do* —
its unit is the change, and it exits non-zero so CI can gate on it. `info` answers *what
is here* — its unit is the resource, and it never fails. `check` is `plan` minus the diff:
it needs no state, so it is what an editor or a pre-commit hook runs. Running `cargo-ai
project` with no arguments does `info` inside a project and `init` outside one.

## 4) Documentation hierarchy

- **Level 1** — `SKILL.md` (this file): the decision model, lifecycle, critical
  rules, and routing.
- **Level 2** — Guides:
  [`guides/authoring-resources.md`](guides/authoring-resources.md),
  [`guides/deploy-and-state.md`](guides/deploy-and-state.md),
  [`guides/typed-config.md`](guides/typed-config.md).
- **Level 2.5** — Recipes: [`recipes/*.md`](recipes/) — step-by-step playbooks to
  follow as your execution plan.
- **References** — [`references/resources.md`](references/resources.md) (the full
  builder catalog), [`references/commands.md`](references/commands.md) (every
  `cargo-ai project` subcommand + flags),
  [`references/troubleshooting.md`](references/troubleshooting.md), and
  [`references/examples/full-workspace.md`](references/examples/full-workspace.md).

## 5) Read behavior — match the task to a doc and READ IT

| When the task involves… | Read this first | What it gives you |
|---|---|---|
| Writing `define*` files, wiring resources, `secret()`/`env()`, `defineWorkflow` bodies (tool/play logic) | [`guides/authoring-resources.md`](guides/authoring-resources.md) | The builder catalog, the handle/ref model, secrets, and how workflow bodies compile. |
| `plan` / `deploy` / `destroy`, the state file, drift, adopting existing resources, CI | [`guides/deploy-and-state.md`](guides/deploy-and-state.md) | The deploy lifecycle, `cargo.state.json` semantics, drift/import/rollback, async builds. |
| Typed config, `cargo-ai project types`, tsconfig wiring, `integrations.*` in workflow bodies | [`guides/typed-config.md`](guides/typed-config.md) | What `project types` generates and how to wire it into your project. |
| A field/spec/output for a specific builder | [`references/resources.md`](references/resources.md) | Every builder → spec fields → which ref each takes → outputs. |
| Exact command flags | [`references/commands.md`](references/commands.md) | Every `cargo-ai project` subcommand and its flags. |
| A deploy error / footgun | [`references/troubleshooting.md`](references/troubleshooting.md) | The known failure modes and fixes. |
| A known GTM outcome, before authoring one; or what to suggest after one is set up | [`references/cookbooks.md`](references/cookbooks.md) | The cookbook menu, in stage order: gtm-skills that carry a worked CDK example, the adaptations each supports, and which to suggest next. |

### Cookbooks — check the menu before authoring a known outcome from scratch

[`getcargohq/gtm-skills`](https://github.com/getcargohq/gtm-skills) holds, beside its
one-off skills, **cookbooks**: skills that carry worked CDK resources, the same job as a deployed
pipeline that keeps producing the result (TAM building, account scoring, call capture,
inbound qualification, CRM enrichment, stalled-deal nudges, …). Every folder is self-contained: its
own models, connectors and folders, no shared foundation, no requires graph.

**The menu is local: [`references/cookbooks.md`](references/cookbooks.md).** Read it
before authoring a common GTM outcome from scratch, and again once a cookbook is set up:
it lists them in stage order, and that order is what to suggest next — the earliest
cookbooks not set up yet. It is generated from gtm-skills' `catalog.json`, so it cannot
drift.

**A cookbook is a worked example, not a template to fill in.** Each one declares in its `SKILL.md` what may be reshaped, what must hold or it stops
working, and what has to be answered either way, and it carries its own procedure.
`project add` is the copy step in that procedure:

```sh
cargo-ai project add cookbook/tam-building               # inside a CDK project
cargo-ai project init my-project --cookbook tam-building # no project yet: both at once
```

That writes the resources to `infra/tam-building/` and the procedure to
`.claude/skills/tam-building/`, skipping any file it would overwrite. **Then start the
skill at its Adapt section** — its opening steps are written for someone who found the
folder on GitHub and still has to place it, so following them from the top scaffolds a
second project and copies the folder in again.

What is left after the copy is the part only you can do: reconcile it with what is
already declared, adapt the copied files **in place** to the project's real shape (do not
regenerate them from the skill's prose — the safety lives in the TypeScript), plan and
stop, deploy on a yes, walk its `Done when`.

**If you are mid-task and the skill is not in this session**, `npx skills add
getcargohq/gtm-skills/<slug>` fetches the procedure alone and you can read
`.agents/skills/<slug>/SKILL.md` directly; no reload needed. To read one without
installing, `npx skills use getcargohq/gtm-skills@<slug>` prints it. Neither brings the
CDK resources — for those you still want `project add`.

**Routing rule: one-off versus standing.** A user who wants the list today wants
`cargo-gtm` (or gtm-skills' one-off `build-tam-list`); a user who wants a pipeline
that keeps producing it wants `tam-building`. The same words describe both ("build
our TAM"), so listen for whether the result is meant to keep arriving. A cookbook
matches → install it and follow it. No match → author from the recipes below.

**Never `cargo-ai project init --force` into a directory that is not empty.** It replaces
the project's `package.json` and reverts adapted code, while `cargo.state.json`
survives, so the next `plan` diffs a live workspace against code nobody wrote. Copy the
skill folder in as a sibling instead.

Caveat: the examples typecheck, but they are not yet deploy-verified against a live
workspace, and every one is `to-be-approved`. Treat each skill's `Done when` as the
acceptance test, and always review `cargo-ai project plan` before deploying.

### Recipes — follow step-by-step when one matches

| Recipe | Use when… |
|---|---|
| [`recipes/scaffold-a-project.md`](recipes/scaffold-a-project.md) | Standing up a new project from scratch (`init` → types → plan → deploy). |
| [`recipes/add-connector-and-model.md`](recipes/add-connector-and-model.md) | Adding a data source + a model sourced from it, wired by handle. |
| [`recipes/build-an-agent.md`](recipes/build-an-agent.md) | Composing a model + tool + agent (with `uses` / `models` / `tools`) and deploying. |
| [`recipes/migrate-existing-workspace.md`](recipes/migrate-existing-workspace.md) | Bringing an already-live workspace under a project via `project import`. |
| [`recipes/deploy-from-ci.md`](recipes/deploy-from-ci.md) | Deploying non-interactively from CI (token auth + committed state). |

## 6) Critical rules

- **Commit `cargo.state.json` — it is a pointer now, not the state.** The deploy
  state lives in your **workspace**; the repo commits only
  `{"stateUuid": "8f2c…"}`. `project init` creates the state and writes that
  pointer, so it lands in the scaffold commit. Commit it: without the uuid a fresh
  checkout can't find its state, and a deploy will **not** quietly create a
  replacement (that would orphan everything the old one tracks). The state records
  only uuids, hashes and outputs — never secret values. It is still the **only**
  handle on a deployed **play**, **agent**, or **alert** (they have no slug);
  recover a lost link with `project state bind <uuid>`, or per-resource with
  `cargo-ai project import`. Git-ignore the working files (`project init` scaffolds
  this):
  ```gitignore
  .cargo-ai/
  cargo.state.lock
  cargo.state.bak.json
  cargo.state.cache.json
  cargo.state.audit.jsonl
  ```
  One state per repo, and at most **10 live states per workspace**:
  ```bash
  cargo-ai project state list            # every state here, and which one this project is on
  cargo-ai project state create          # create one for this project, write the pointer
  cargo-ai project state bind <uuid>     # repoint at an existing one
  ```
  A project scaffolded before states moved to the workspace has the resource map
  **inline** in `cargo.state.json`, and keeps deploying against that file for as
  long as you leave it there — nothing migrates behind your back. `state create` is
  what moves it: the map goes onto a new state, the file becomes a pointer, and you
  commit it. Don't migrate without telling the team, since a teammate who deploys
  before pulling the new pointer is deploying from a state that no longer exists.
  (Deleting a state — `state remove` — is in the CDK README but is **not** in CLI
  1.0.96; it lands in the next release.)
- **Three ways to get a value in, and they are not interchangeable.**
  - `secret("ENV_VAR")` — read from **your** environment at deploy time, excluded
    from the content hash and from state. Export the env var before deploying; a
    missing one fails the deploy with an unresolved `${ENV_VAR}` placeholder.
  - `env("ENV_VAR")` — read from your environment at **load** time, and its value
    *enters* the spec and therefore the content hash, so changing it shows as drift.
    Use it for non-secret config you *want* tracked.
  - `workspaceEnv("NAME")` — a **pointer** at a workspace env-var catalog entry.
    Nothing is read locally and nothing can fail; the value stays server-side and is
    re-read on every use, so rotating it in the workspace reaches the resource with
    **no redeploy**. Manage the catalog with `cargo-ai workspaceManagement envVar`
    (see [`../cargo-workspace-management/SKILL.md`](../cargo-workspace-management/SKILL.md)).

  `secret()` and `workspaceEnv()` are accepted at **secret-typed schema positions
  only** — `cargo-ai project types` prints the union at exactly those positions. A
  resource's own `env` block takes `env()` or `secret()` and **rejects** a pointer,
  because a worker, app, agent or script already inherits the whole workspace
  catalog; a pointer there could only restate a variable it can read anyway.
- **A rotated `secret()` needs more than a plain deploy to land.** Keeping the value
  out of the content hash is what stops rotation reading as drift — and it is also
  why `deploy` won't push the new value: nothing in the hash changed, so the
  resource isn't re-applied. Roll it with `deploy --refresh`, or any other edit to
  that resource. `workspaceEnv()` has no such step; that is most of its appeal.
- **Wire by handle, never by `.uuid`.** Pass a `define*` handle directly
  (`dataset: hubspot`, `tools: [enrich]`), or `xxRef("uuid")` for a resource you
  didn't define in code (`connectorRef`, `modelRef`, `folderRef`, `toolRef`,
  `agentRef`, …). Where a reference needs per-call options, wrap it as
  `{ ref, …options }` (e.g. `models: [{ ref: contacts, readOnly: true }]`).
- **Run `cargo-ai project types` after workspace integrations change** — it
  regenerates `.cargo-ai/` so `defineConnector`/`defineModel` config (and
  `integrations.*` in workflow bodies) type-check against the real schemas. Typing
  is a bonus, never a gate: deploy works without it.
- **Any subdirectory of the repo is fine (CLI ≥ 1.0.83).** Commands walk **up** to
  the package root where `@cargo-ai/cdk` is declared, then back **down** to the
  resource directory (`infra/` in a scaffolded repo), so `.cargo-ai/` and
  `cargo.state.json` land in the right place from anywhere inside the project.
  `--dir <path>` still overrides it. This is why resources live in `infra/` and not
  at the root: the loader imports *every* `.ts` under the directory it is given, and
  a repo root also holds `scripts/` — whose files run on import. Pointing a command
  at the root would execute them.
- **`--yes` in CI.** `deploy` and `destroy` prompt for confirmation; non-interactive
  runs must pass `--yes`.
- **A `definePlay`/`defineTool` graph with paid nodes gets a sample run before it
  goes wide.** Deploying is not running, but the first thing that runs a deployed
  play is usually a batch over the whole segment — and a scheduled play re-bills
  every node on every run. Before enrolling everything (or enabling a schedule),
  run the deployed workflow on **10–20 records** — `cargo-ai orchestration batch
  create --data '{"kind":"filter","modelUuid":"…","filter":…,"limit":15}'`, or
  `batch create --file ./plays/x.ts` to test-run the module without deploying —
  then ask the user to approve the full enrollment with the **record count** and
  **credit estimate**. Read the provider's playbook
  (`../cargo-gtm/provider-playbooks/<slug>.md`, esp. its *Recurring use* section)
  and the gate in
  [`../cargo-gtm/references/cost-discipline.md`](../cargo-gtm/references/cost-discipline.md).
- **A `defineAlert` whose actions call paid nodes re-bills on every breach.** An
  alert's `actions` fire as real runs, so a badly-sized `threshold` on a tight
  `schedule` can breach — and bill — every tick. Size the threshold with
  `cargo-ai observability alert preview` before deploying, prefer cheap notification
  actions (an agent that posts, a connector notification) over anything that fans
  out, and apply the same cost gate above when an action calls a credits-based
  provider. Scope/threshold and firing semantics:
  [`../cargo-observability/SKILL.md`](../cargo-observability/SKILL.md).
- **`defineMailbox` bills monthly, and `defineDomain` rewrites a DNS zone.** A
  mailbox is 100–160 credits *per month* for as long as it exists (`cargo-ai
  mailboxManagement pricing get` for live figures), so a `+ create mailbox:…` line
  in the plan is a recurring charge the user approves, not a one-off. Its `domain`,
  `username` and `type` are **create-only** — changing any of them is destroy +
  recreate, i.e. a brand-new inbox back at the bottom of a 45-day warm-up ramp. The
  deploy polls `refreshStatus` for up to 5 minutes waiting for `active`. On
  `defineDomain`, `dnsRecords` is the **whole zone, not a patch**: declaring it
  replaces every live record (including the ones the registrar wrote at purchase),
  and omitting it leaves the zone untouched. `redirectUrl`, `dmarcEmail` and
  `dmarcPolicy` are **additive** and are the supported way to configure a zone
  without replacing it, so reach for `dnsRecords` only when you mean to own every
  record. Use `adopt: true` for a domain or mailbox bought in the UI. Ramp,
  suppression and sending:
  [`../cargo-mailbox-management/SKILL.md`](../cargo-mailbox-management/SKILL.md).
- **Route CDK-managed resources into a clearly-labelled folder.** Set `folder:` on
  each builder so everything CDK owns lands in a dedicated folder whose name signals
  "owned by code — don't hand-edit" to anyone in the UI (manual UI edits read back as
  drift on the next `plan`). Folders are per-kind, so give each kind its own but share
  one short, recognizable prefix — recommended: **`🔒 CDK`** (e.g. `🔒 CDK Models`,
  `🔒 CDK Agents`). Keep names short (long labels truncate in the folder tree); the
  lock emoji is the "don't touch" cue. See
  [`guides/authoring-resources.md`](guides/authoring-resources.md).

## Help

- `cargo-ai project --help` and `cargo-ai project <subcommand> --help` for the live flag
  surface.
- When a documented command/flag/response doesn't match what you observe, file a
  report: `cargo-ai workspaceManagement report create` (see
  [`../cargo-workspace-management/SKILL.md`](../cargo-workspace-management/SKILL.md)).
