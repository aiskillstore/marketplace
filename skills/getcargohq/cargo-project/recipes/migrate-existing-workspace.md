# Recipe: bring an existing workspace under a project

**Use when** a workspace already has live resources (built in the UI or the
imperative CLI) and the user wants to manage them from a project going forward —
without creating duplicates.

The tool is `cargo-ai project import <id> <uuid>`, which binds a resource's **code id**
(`kind:slug`) to its **live uuid** in this project's deploy state. After import, `deploy`
updates that resource in place instead of creating a new one.

## 1. Write the `define*` for the resource

Describe the existing resource in code as accurately as you can. Match the slug you
want to address it by:

```ts
// models/contacts.ts — describe the live model
export const contacts = defineModel("contacts", {
  dataset: connectorRef("<connector-uuid>"),
  extractSlug: "fetchRecords",
  config: { objectType: "contacts", columnSelectionMode: "all" },
});
```

## 2. Find the live uuid

Use the matching capability skill to look it up — e.g. models via
[`../../cargo-storage/SKILL.md`](../../cargo-storage/SKILL.md), connectors via
[`../../cargo-connection/SKILL.md`](../../cargo-connection/SKILL.md), agents via
[`../../cargo-ai/SKILL.md`](../../cargo-ai/SKILL.md):

```bash
cargo-ai storage model list        # find the model's uuid
```

## 3. Import each resource into state

```bash
cargo-ai project import model:contacts <model-uuid> --dir acme-gtm
cargo-ai project import connector:hubspot <connector-uuid> --dir acme-gtm
cargo-ai project import agent:sdr <agent-uuid> --dir acme-gtm
```

- The id is `kind:slug` — the same id the plan output uses.
- **Slug-addressable kinds** (connector, model) can also self-adopt on the next
  `deploy` by matching slug, so `import` is optional for them. **Uuid-only kinds**
  (play, agent, capacity, territory, segment) have no slug — `import` is the only
  way to bind them one at a time. If you lost only the *pointer*, `project state list`
  then `project state bind <uuid>` recovers everything at once; `import` is for when the
  state itself is gone.

## 4. Verify with a plan

```bash
cargo-ai project plan --dir acme-gtm
```

Imported resources should show as **update** or **no-op**, not **create**. A
`create` for something that already exists means the id/slug didn't match — fix the
`define*` slug or re-import with the right uuid.

## 5. Deploy and commit

```bash
cargo-ai project deploy --dir acme-gtm
git add cargo.state.json && git commit -m "Adopt existing workspace into CDK"
```

Imported/adopted resources are **released** (dropped from state), not deleted, if
you later `destroy` or `deploy --prune` them — the CDK won't delete something it
only adopted.
