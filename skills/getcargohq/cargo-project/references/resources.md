# Resource reference

Every builder is imported from `@cargo-ai/cdk`, takes `(slug, spec)` (except
`defineContext`, which takes only a spec — it's a workspace singleton), and returns
a **handle** carrying deferred output tokens (`uuid`, and for connectors
`datasetUuid`; for workers/apps `url`). Wire resources by passing a handle where a
reference is expected; use `xxRef("uuid")` for a resource not defined in code.

The tables below list the **commonly used** spec fields — the TypeScript types on
each builder are the source of truth for the complete set. Fields that take a
**ref** accept a handle or an `xxRef` (and `{ ref, …options }` when they carry
per-call options).

## Builders

| Builder | Purpose | Key spec fields | Ref fields | Outputs |
|---|---|---|---|---|
| `defineConnector(slug, spec)` | Data source or LLM provider | `integration`, `config` (typed per integration), `adopt?`, `rateLimit?`, `cacheTtlMilliseconds?` | — | `uuid`, `datasetUuid` (data connectors) |
| `defineModel(slug, spec)` | Table sourced from a connector's dataset | `dataset`, `extractSlug`, `config`, `schedule?`, `folder?` | `dataset` (connector/dataset), `folder` | `uuid` |
| `defineTool(slug, spec)` | Tool backed by a workflow | `workflow`, `description?`, `emojiSlug?`, `triggers?`, `folder?` | `folder` | `uuid` |
| `definePlay(slug, spec)` | Per-row automation over a model | `model`, `workflow`, `changeKinds`, `runCreationRule`, `schedule`, `folder?` | `model`, `folder` | `uuid` |
| `defineAgent(slug, spec)` | AI agent | `connector`, `languageModel`, `systemPrompt`, `models?`, `tools?`, `subAgents?`, `connectorActions?`, `capabilities?`, `maxSteps?`, `triggers?`, `evaluator?`, `color?`, `folder?`, `harness?`, `repository?` | `connector`, `models`, `tools`, `subAgents`, `folder` | `uuid` |
| `defineMcpServer(slug, spec)` | MCP endpoint bundling resources | `name?`, `description?`, `uses?` (tools, agents, models, connector + native actions in one array), `capabilities?`, `folder?` | everything in `uses`; `folder` | `uuid` |
| `defineFolder(slug, spec)` | Per-kind folder | `kind`, `name`, `parent?` | `parent` | `uuid` |
| `defineFile(slug, spec)` | Content file from a local path | `path`, `name`, `folder?` | `folder` | `uuid` |
| `defineContext(spec)` | Workspace context repo (singleton) | `dir?`, `files?` | — | `uuid` |
| `defineSegment(slug, spec)` | Saved view over a model | `model` (immutable), `filter` (required) | `model` | `uuid` |
| `defineCapacity(slug, spec)` | Revenue-org capacity | `model`, `color?`, `description?`, member capacity fields | `model`, members | `uuid` |
| `defineTerritory(slug, spec)` | Revenue-org territory | `model`, `members`, `color?`, `description?`, `fallbackMember?` | `model`, `members` | `uuid` |
| `defineWorker(slug, spec)` | Hosted worker (built bundle) | `path`, `description?`, `folder?` | `folder` | `uuid`, `url` |
| `defineApp(slug, spec)` | Hosted Vite SPA | `path`, `description?`, `folder?` | `folder` | `uuid`, `url` |
| `defineDomain(name, spec)` | Sending domain + its DNS zone | `adopt?`, `dnsRecords?` (**replaces the whole zone**), `redirectUrl?`, `dmarcEmail?` (`rua=`), `dmarcPolicy?` (`p=`: `none`/`quarantine`/`reject`) | — | `uuid` |
| `defineMailbox(slug, spec)` | Sending inbox on a domain (**monthly credit charge**) | `domain`, `type` (`google`/`shared`/`private` — no `outlook`), `username?` (defaults to slug), `firstName`, `lastName`, `signature?`, `folder?`, `adopt?` | `domain`, `folder` | `uuid` |
| `defineAlert(slug, spec)` | Scheduled threshold alert (observability) | `schedule`, `scope`, `threshold`, `actions`, `name?`, `description?`, `enabled?`, `folder?` | scope: `workflow`/`connector`/`tool`/`agent`/`model`; each action's `ref`; `folder` | `uuid` |

`defineWorkflow(slug, { input, output, uses? }, build)` is re-exported from
`@cargo-ai/cdk` for `defineTool`/`definePlay` bodies — see
[`../guides/authoring-resources.md`](../guides/authoring-resources.md).

## Capabilities

`capabilities` on `defineAgent` **and** on `defineMcpServer` (the latter since
`@cargo-ai/cdk` 1.0.70) takes either a bare slug or a `{ slug, config }` object —
`capabilities: ["webSearch"]` and `capabilities: [{ slug: "webSearch", config: {} }]`
are the same thing. The nine slugs:

`sandbox` · `memory` · `context` · `app` · `document` · `webSearch` · `model` ·
`file` · `documentationSearch`

On the CLI the same field is a JSON array:
`cargo-ai ai mcp-server create --capabilities '[{"slug":"webSearch","config":{}}]'`.

## Coding-agent agents (`harness`)

An agent with a `harness` is a **coding** agent: it clones a git repository into a
sandbox and works in it. `harness` takes `claudeCode`, `codex`, `openCode` or
`deepAgents`. (`harnessSlug` is the deprecated spelling; both normalize to the same
spec field, so renaming it is not a diff.)

**Omit `repository` to bind the project's own repo.** `plan`/`deploy` read the git
origin of the checkout they run in and fill `repository`, `defaultBranch` and
`rootDirectory`, taking `connector` from the project's GitHub `defineConnector`.
Declared fields always win, so a partial object is completed the same way — and the
resolved values are what the plan prints and what the content hash covers. With no
`repository` at all and no harness binding, a harness turn provisions an empty
sandbox scoped to the chat.

## Ref helpers

From `@cargo-ai/cdk`: `connectorRef`, `datasetRef`, `modelRef`, `folderRef`,
`playRef`, `memberRef`. From the workflow SDK (re-exported): `toolRef`, `agentRef`.
Each takes a uuid string and returns a kind-branded handle:

```ts
import { defineModel, connectorRef, folderRef } from "@cargo-ai/cdk";

export const leads = defineModel("leads", {
  dataset: connectorRef("6f0c…"),   // existing connector, by uuid
  extractSlug: "fetchRecords",
  folder: folderRef("a1b2…"),
});
```

## Notes on specific fields

- **`defineConnector` `config`** is a per-integration shape — a discriminated union
  for auth (e.g. HubSpot `method: "privateApp" | "oauth"`). `secret()` is accepted
  only on credential/encryption fields. Run `cargo-ai project types` to type it (see
  [`../guides/typed-config.md`](../guides/typed-config.md)).
- **`adopt: true`** on `defineConnector` links an existing authenticated connector
  by slug instead of creating one — for OAuth/key connectors you can't declare.
- **`defineModel` `dataset`** takes the **connector** handle (its dataset uuid is
  injected) or a `datasetRef`/`connectorRef`.
- **`schedule`** shapes: `{ type: "cron", cron: "0 * * * *" }` or
  `{ type: "watch" }` (plays react to row changes).
- **`definePlay` `changeKinds`**: `["added", "updated", …]`; `runCreationRule`:
  e.g. `"always"`.
- **`defineFile` `path`** and **`defineWorker`/`defineApp` `path`** point at local
  files/dirs, typically via `new URL("./x", import.meta.url).pathname`. File content
  is hashed at define time, so edits show as drift. Worker `path` must be a **built**
  bundle dir (`index.js` + `manifest.json` + `package.json` + `package-lock.json`).
- **`defineAlert` `scope` + `threshold`** are a **matched pair** — TS narrows the
  threshold menu by `scope.kind`: `spans`/`runs`/`records` take the telemetry metrics
  (`errorRate`, `duration`+`aggregation`, `credits`+`aggregation`, `count`), `model`
  takes `recordsCount`/`recordsShare`/`freshness`/`syncDuration`, and
  `orchestrationQuery`/`storageQuery` take `{ operator, value }` (the query computes
  the value, so no metric). The scope wires the watched resource **by handle**
  (`workflow:` a `definePlay`/`defineTool` handle or `workflowRef`, plus `connector`/
  `tool`/`agent`/`model`), so the reconciler deploys the producer first and injects
  its uuid.
- **`defineAlert` `actions`** fire as runs on breach. Each is a `{ ref, config }`
  wrapper (`config` required — an alert fires unattended, so a missing input is a type
  error, not a silent `{}`). Prefer the typed helpers `alertConnectorAction({ ref:
  slack.actions.postMessage, config })` / `alertToolAction({ ref: enrich, config })` —
  `config` is checked against the action/tool input schema (connector schemas need
  `cargo-ai project types` to have run) — or a bare `{ ref: agent, config, release?,
  waitUntilFinished? }`. Every `config` leaf accepts a `{{ … }}` template
  (`{{event.value}}`, `{{alert.name}}`, `{{alert.url}}`, …) interpolated against the
  firing context. Like a play, an alert has **no author-set wire slug** — its identity
  on redeploy is the state uuid, so committing `cargo.state.json` is what keeps it
  addressable. Scope/threshold matrix, metric units, and firing semantics:
  [`../../cargo-observability/SKILL.md`](../../cargo-observability/SKILL.md).
