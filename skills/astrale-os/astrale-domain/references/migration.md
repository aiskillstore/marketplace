# Schema evolution and data migration

Schema evolution and data migration are distinct decisions.

## Additive evolution

Prefer additions that preserve origin and existing Definition keys: optional properties, new Classes,
new Edges, and new callables. Rebuild and verify that the new Schema revision differs while unchanged
callable/Class keys remain stable. Reinstall through the public installation path and prove existing
data remains valid.

Adding syntax is not necessarily compatible with existing data: a new required property or an Edge
with minimum cardinality `1` can invalidate existing nodes. Introduce an optional form, backfill,
then install the tightened contract; a default in application code is not a persisted backfill.

## Production changes: expand, migrate, contract

For production data, prefer staged compatibility over an immediately breaking change:

1. Expand the Schema to accept both representations. Deploy readers that understand both and writers
   that produce the new form; keep old-data reads working throughout the transition.
2. Move every producer off the old form, including older deployments, jobs, imports, and clients.
   Migrate existing data in bounded, restart-safe batches without overwriting concurrent updates.
3. Verify no old representation remains and no active producer can recreate it. Only then tighten
   the Schema and remove compatibility code; a rollback must not reintroduce an incompatible writer.

For local iteration with disposable data, a direct change or deliberate reset may suffice. Do not
impose a production rollout on every experiment, or treat production data as disposable.

## Upgrade the dependency closure together

- If B depends on A@r1, installing A@r2 alone leaves B incoherent, even when A's change looks additive.
  B pins an exact Schema revision, not an npm semver range or whichever A happens to be active.
- Update B's Schema dependency to A@r2 and rebuild B; B now has a new revision too. Repeat for all
  affected reverse dependents, including C → B → A. A manifest edit without rebuilt artifacts is insufficient.
- Deploy the coherent candidates first: a deploy never installs. Then install A, B, and affected
  consumers as explicit roots of one grouped install, by deployment URL or by version, mixed.
- A dependency embedded in B's bundle is not automatically installed as a root. Sequential single-Domain
  installs can fail in either order; do not uninstall B or discard data to bypass revision coherence.

```sh
astrale domain install "$URL_A" "$URL_B" --allow-issuer-change -i staging  # previews, by URL
astrale domain install a.example@2.1.0 b.example@3.0.0 --allow-issuer-change -i production
```

The grouped install is one atomic Kernel operation: every root moves or none does. After an
outcome-unknown timeout or disconnect, rerun the exact retry command the CLI prints, which reuses the
operation id (`--operation <uuid>`) and names each version exactly as it resolved; do not start a fresh
operation merely because the first call timed out. Inspect both installed revisions afterward.

## Breaking evolution

Removing or renaming a property, Class, Edge, Policy, callable, or origin does not migrate stored data.
Treat it as an explicit compatibility and data-migration design. Do not conceal it in Core data,
Runtime initialization, a Provider, or an undocumented repair Action.

Before reinstalling a Schema that removes a Class (Node or Edge), delete every existing instance of
that Class. The Kernel refuses the reinstall with `DATA_MIGRATION_REQUIRED` while incompatible data
remains.

Deleting the only required Edge first violates the currently installed cardinality; removing its
Class first leaves data in a retired Class. To remove a `1` relationship while retaining its nodes:

1. publish and install an intermediate Schema revision that loosens the endpoint cardinality from
   `1` to optional (`0..1`);
2. delete every existing instance of the Edge Class; and
3. publish and install the final Schema revision that removes the Edge Class.

Qualify each installed revision before proceeding to the next stage. Do not bypass the intermediate
revision or treat `DATA_MIGRATION_REQUIRED` as a transient installation failure.
If other Domains depend on this Schema, rebuild and install their coherent revisions at both Schema
stages above. Deploying the final revision does not make the intermediate data cleanup legal.

## Migration owner

Treat first-class Migration authoring as unavailable unless the installed SDK exposes a public
contract governing the required transition. Inspect its exact declarations and Kernel support; do not
infer an authoring API from linter vocabulary. If no such lifecycle exists, record the product gap
rather than inventing hooks or claiming convergence.

An ordinary Domain-owned Query/Mutation may repair user data only when invoked through a deliberate
authorized product operation. It is not an implicit post-install lifecycle.

## External effects

A migration involving a remote system is a multi-step Workflow with explicit failure and retry
semantics; it cannot be one atomic graph Mutation. Preserve immutable evidence and do not claim
exactly-once execution without a durable runner.

## Qualify a Schema revision

For a change from the current revision to a candidate revision:

1. retain the current origin/revision and representative data evidence;
2. build and deploy the candidate, which installs nothing;
3. verify the release its deployment serves, its Bundle, and its new revision;
4. install it through the public CLI (`astrale domain install`) or Client APIs;
5. repeat the same intent and prove convergence;
6. read existing data and invoke retained behavior;
7. exercise the added behavior;
8. retain exact failures and avoid destructive cleanup until evidence is complete.
