# Testing

Read when writing Domain fixtures, focused tests, demos, or live acceptance journeys.

## Test at the semantic owner

Use the smallest real boundary that proves the behavior:

- test pure projection and rules as ordinary functions;
- test a Query with a narrow `QueryClient` double and assert the exact AST and pagination behavior;
- test a Mutation with a narrow `MutationClient` double and assert the exact atomic document;
- invoke an Action definition's `run` with an admitted, typed context when testing handler
  orchestration;
- invoke a Workflow with an inline Step implementation when testing explicit step order and values;
- realize a Runtime when testing Action/Workflow exhaustiveness and Provider initialization;
- use a real Kernel for installation, identity, callable authority, Policy, routing, and persistence.

Do not create a general fake Kernel. It becomes a second implementation of authority, visibility,
transactions, paging, and error semantics, while still proving none of them.

## Exercise the owner, not its registration

Use `executeQuery(client, domain, recipe, input)` / `executeMutation(client, domain, recipe, input)`
with narrow capability doubles. They exercise SDK recipe realization and projection; invoking a
hand-copied builder or merely asserting an AST version bypasses the behavior being delivered.

Assert the invariant-bearing operations and absence of unintended writes, not only call counts.
A constructed stale-state precondition proves authoring; only transaction execution proves it rejects
a concurrent edit without partial writes.

## Actions and Workflows

Use a fixture that crosses a page boundary for a “complete collection” claim; a tiny dataset cannot
detect first-page truncation. Check a repeated cursor and an exhausted bound reject without publishing
partial business output, rather than merely asserting that `.query` was called.

For a read→Rule→Mutation flow, change the guarded fact between observation and commit. The Rule's
unit test cannot prove the Mutation rejects stale state; use the actual Kernel transaction for that claim.

Actions have no Step API. For a complete Domain delivery, exercise the exposed Action and Workflow
definitions with representative success and applicable refusal inputs. For a focused change, exercise
the affected callables and their dependent invariants. Binding metadata, lower-level AST checks, or
one tested handler cannot stand in for an unexecuted public callable. Compute expected business
results independently of the implementation; tests that reuse the same calculation only prove agreement.

The current inline runner gives structure and observability. It does not prove durable replay,
exactly-once effects, compensation, or crash recovery. Never claim those guarantees from an in-memory
test.

## Core and fixtures

Core is fixed Domain-owned installation data, not demo data, mutable product state, a post-install
hook, or a migration mechanism. Put throwaway sample data in a test fixture or explicitly invoked
demo owner. Runtime- or environment-dependent setup belongs to an Action, Workflow, or operator-owned
journey with declared requirements.

Demo data has one owner: a Dataset under `tests/`, referenced lazily from `astrale.config.ts`
(`tests: tests({ datasets: [dataset('./tests/datasets/demo.ts')] })`). `dataset(path)` is a lazy
coordinate: building or deploying never loads the module, and a Dataset never reaches a Build, a
Release, or an installation. The Domain Studio extracts referenced Datasets on demand and renders
them in its Tests tab; several Datasets per project are fine as long as their ids differ. Production
code never imports `tests/`. How to author a Dataset worth reading: `datasets.md`.

## Live acceptance

For deployment or integration claims, exercise a representative journey on the intended Kernel with
real credentials and the deployment adapter the product ships. For package/release qualification,
also use a packed or published consumer outside the source workspace. A local Kernel is not a
prerequisite for a managed-remote application test. Isolate destructive lifecycle scenarios from
shared instances and record exact deployed and installed revisions.

Observe installation and invocation through public Client APIs. Keep authentication, authority,
Policy, handler, Provider, persistence, update, uninstall, and cleanup evidence distinct. Report what
was locally tested, remotely observed, and not exercised separately. Keep durable regression tests
with their production owner; keep situational logs, credentials, and proof tooling out of delivery.

Cleanup must converge from partial lifecycle states: neither Domain installed, only dependencies
installed, or the complete closure installed. Establish exact Domain presence with a public
Domain-root point observation before querying its Classes; accept only the exact not-found result as
absence. Do not use a Schema-introspection failure as an absence shortcut.
`QUERY_DEFINITION_UNRESOLVED` is an empty cleanup observation only when the owning Domain is already
proven absent; never suppress authentication, authorization, protocol, unknown-outcome, or unrelated
query failures. Delete only independently observed business facts, then uninstall dependents before
dependencies.

### Design focused scenarios

Make each scenario prove one semantic claim with the smallest sufficient criteria. Distinct evidence
classes do not all need to appear in every scenario. Prefer focused proofs such as:

- cross-Domain package boundary, install ordering, and caller-bound dispatch;
- multi-user Policy denial and revocation;
- local service, tunnel, and real external API delivery; and
- a thin integrated smoke that composes already-proven pieces without duplicating every adversarial
  check.

Do not make acceptance stricter than the public product contract. Criteria should observe outcomes
and security boundaries, not prescribe private filenames, arbitrary test counts, one source layout,
or incidental output fields. Add a criterion only when its absence would make the scenario's stated
claim unsupported or dishonest.

### Bound convergence

Keep the scenario's product claim and package versions explicit. Classify newly found issues without
automatically expanding the test framework or the task. If a defect invalidates the claim, retain
the reproduction and fix it at its owner; otherwise track it separately. Do not add more scenarios
or tooling merely to accumulate evidence already supplied by an existing test.
