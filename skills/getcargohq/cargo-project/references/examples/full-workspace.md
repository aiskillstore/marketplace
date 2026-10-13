# Example: a full GTM workspace end-to-end

This walks a complete, runnable Cargo workspace defined in code that exercises
every resource type and wires them by **handle**. It is a reading example, not
something a command scaffolds: `cargo-ai project init` produces one repo shape, and a
worked pipeline comes from `cargo-ai project add cookbook/<slug>`.

## The graph

```
hubspot (connector) ──dataset──▶ contacts (model) ──model──────────┬─▶ onboarding (play)
                                                                    ├─▶ sdr (agent)
openai (connector) ──connector──▶ enricher (agent) ──subAgent──▶ sdr│
                    └────────connector──────────────────▶ sdr ─────┘
enrich (tool, backed by a workflow) ─┐
sdr (agent) ─────────────────────────┼─▶ crm (mcpServer)
contacts (model) ────────────────────┘
playbook (file)   webhook (worker)   dashboard (app)   context (repo)
```

## Project layout

```
acme-gtm/
  package.json            # depends on @cargo-ai/cdk + zod
  tsconfig.json           # include: ["**/*.ts", ".cargo-ai/**/*.d.ts"]
  .gitignore              # .cargo-ai/, cargo.state.lock, cargo.state.bak.json, cargo.state.audit.jsonl
  connectors/hubspot.ts   # defineConnector + secret()
  connectors/openai.ts    # defineConnector adopt: true
  folders/crm.ts          # defineFolder (per-kind)
  models/contacts.ts      # defineModel dataset: hubspot
  tools/enrich.ts         # defineWorkflow + defineTool
  agents/enricher.ts      # defineAgent (sub-agent)
  agents/sdr.ts           # defineAgent (model + tool + sub-agent + trigger + evaluator)
  plays/onboarding.ts     # definePlay + defineWorkflow
  mcp/crm.ts              # defineMcpServer
  context/context.ts      # defineContext dir: "context" (+ context/*.md)
  files/playbook.ts       # defineFile (+ playbook.md)
  workers/webhook.ts      # defineWorker (+ webhook/ built bundle)
  apps/dashboard.ts       # defineApp (+ dashboard/ Vite app)
```

Importing a `.ts` file **is** registration — there is no manifest. The loader
imports every `.ts` under the project (skipping the worker/app bundle sub-dirs,
which have their own `package.json`), and each `define*` registers as a side
effect.

## A wired slice

```ts
// connectors/hubspot.ts
export const hubspot = defineConnector("hubspot", {
  integration: "hubspot",
  config: { method: "privateApp", accessToken: secret("HUBSPOT_API_KEY") },
});

// models/contacts.ts
export const contacts = defineModel("contacts", {
  dataset: hubspot,                       // handle → connector deployed first, dataset injected
  extractSlug: "fetchRecords",
  config: { objectType: "contacts", columnSelectionMode: "all" },
  folder: modelsFolder,
  schedule: { type: "cron", cron: "0 * * * *" },
});

// agents/sdr.ts
export const sdr = defineAgent("sdr", {
  connector: openai,
  languageModel: "gpt-4o",
  systemPrompt: "You qualify inbound leads and route hot ones to Slack.",
  models: [{ ref: contacts, readOnly: true }],
  tools: [enrich],
  subAgents: [{ ref: enricher, waitUntilFinished: true }],
  folder: agentsFolder,
});
```

## Deploy walkthrough

```bash
cd acme-gtm && npm install

cargo-ai login                 # authenticate + select the workspace
cargo-ai project types             # type defineConnector/defineModel config against this workspace
export HUBSPOT_API_KEY=...      # matches secret("HUBSPOT_API_KEY")

cargo-ai project plan
# → lists every resource as create / update / no-op, in dependency order:
#   create connector:hubspot, create connector:open_ai (adopt), create folder:crm-models, …

cargo-ai project deploy
# → creates each in order, recording each in the workspace-held deploy state.
#   Workers/apps build server-side (slower). Live URLs appear as webhook.url / dashboard.url.

git add cargo.state.json && git commit -m "Deploy full workspace"
```

Re-run `cargo-ai project deploy` after editing a file — only the changed resource is
applied. Tear it all down with `cargo-ai project destroy --all`.

Secrets referenced with `secret("HUBSPOT_API_KEY")` resolve from the environment at
deploy time and stay out of the content hash — only `{hash, uuid, outputs}` land in
the deploy state, never secret values. (`cargo.state.json` itself holds just the
`stateUuid` pointer.)
