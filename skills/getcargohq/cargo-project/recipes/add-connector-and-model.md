# Recipe: add a connector and a model sourced from it

**Use when** the user wants a new data source plus a model built from it, managed
in the project. The key move is wiring the model to the connector **by handle** — the CDK
deploys the connector first and injects its dataset uuid.

## 1. Define the connector

Creating a data connector auto-creates a **dataset** that models source from. Put
the credential behind `secret()`.

```ts
// connectors/hubspot.ts
import { defineConnector, secret } from "@cargo-ai/cdk";

export const hubspot = defineConnector("hubspot", {
  integration: "hubspot",
  config: { method: "privateApp", accessToken: secret("HUBSPOT_API_KEY") },
});
```

For an OAuth/key connector you authenticated in the UI and can't declare in code,
use `adopt: true` so the reconciler links the existing instance instead of creating
one:

```ts
export const openai = defineConnector("open_ai", { integration: "openAi", adopt: true });
```

## 2. Define the model, wired to the connector

Pass the **connector handle** as `dataset` — not `hubspot.datasetUuid`:

```ts
// models/contacts.ts
import { defineModel } from "@cargo-ai/cdk";
import { hubspot } from "../connectors/hubspot";

export const contacts = defineModel("contacts", {
  dataset: hubspot,                 // ← handle: model depends on connector
  extractSlug: "fetchRecords",
  config: { objectType: "contacts", columnSelectionMode: "all" },
  schedule: { type: "cron", cron: "0 * * * *" },  // refresh hourly
});
```

If the connector already exists (not defined in code), reference it by uuid:
`dataset: connectorRef("<connector-uuid>")` — or `datasetRef("<dataset-uuid>")` to
point at a specific dataset.

## 3. Type the config (optional but recommended)

```bash
cargo-ai project types    # now `config` on both builders type-checks against HubSpot's schema
```

## 4. Deploy

```bash
export HUBSPOT_API_KEY=...
cargo-ai project plan       # shows: create connector:hubspot, create model:contacts
cargo-ai project deploy
git add cargo.state.json && git commit -m "Add HubSpot connector + contacts model"
```

The plan orders the connector before the model automatically because the model's
`dataset` handle depends on it. Re-deploying after a config edit updates in place.
