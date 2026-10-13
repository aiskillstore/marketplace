# Typed config — `cargo-ai project types`

`defineConnector`/`defineModel` config and the `integrations.*` registry in
workflow bodies are typed against **your workspace's real integration schemas**.
Those types aren't bundled (they're workspace-specific) — you generate them:

```bash
cargo-ai project types --dir my-workspace
```

Typing is a **bonus, never a gate**: an integration you haven't synced (or a
custom one) falls back to a loose `Record<string, unknown>`, so `deploy` works
without ever running `project types`.

## What it generates

Everything lands in `.cargo-ai/` (git-ignored):

- **`.cargo-ai/cargo-types.d.ts`** — `declare module` augmentations:
  - types `@cargo-ai/cdk`'s `defineConnector`/`defineModel` `config` against your
    connector and extractor schemas. E.g. HubSpot's config becomes a discriminated
    union — the editor completes `method` and requires the matching credential,
    and `secret()` is accepted wherever a credential is expected.
  - adds your workspace's integration slugs to the `Integrations` interface, so
    `integrations.<slug>.<action>({ … })` in a workflow body typechecks against the
    real action schema.
- **`.cargo-ai/cargo-register.ts`** — eager `registerIntegration` /
  `registerNative` calls so those slugs are **callable at runtime** in workflow
  bodies.

Re-run `cargo-ai project types` whenever your workspace's integrations change (added a
connector, changed an extractor).

## Wiring it into your project

`project init` sets this up; for a hand-rolled project, two steps:

1. **Add the glob to `tsconfig.json` `include`.** A bare `.cargo-ai` (a dot-dir) is
   ignored by TypeScript — you must use an explicit glob:

   ```jsonc
   // tsconfig.json
   "include": ["**/*.ts", ".cargo-ai/**/*.d.ts"]
   ```

2. **Import the runtime registrations** at the top of workflow modules that use
   `integrations.*`:

   ```ts
   import "./.cargo-ai/cargo-register.js";
   ```

   (`native.*` needs no registration — the platform's native actions are identical
   in every workspace, so their types ship with the SDK. Tools and agents are not a
   registry either — reference them by handle through `defineWorkflow`'s `uses`.)

## Symptoms that mean "run `project types`"

- `config` on a `defineConnector` isn't autocompleting / isn't rejecting a wrong
  credential shape → types not generated (or `.cargo-ai/**/*.d.ts` not in
  `include`).
- `integrations.myConnector` is `any` / not callable at runtime → missing the
  `cargo-register` import, or types are stale after an integration change.
- A connector `deploy` fails with `Invalid configuration` → often the credential
  wasn't wrapped in `secret()`; generating types surfaces the required shape at
  author time. See [`../references/troubleshooting.md`](../references/troubleshooting.md).
