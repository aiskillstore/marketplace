# Debugging

Debug the deployed lifecycle in order. Source correctness alone does not prove live behavior.

```text
source Schema and Runtime
  -> Build
  -> Release and Addressing
  -> provider deployment
  -> served release (release.json)/JWKS/Bundle
  -> Kernel installation and active revision
  -> authenticated invocation
  -> graph/View observation
```

## Establish exact identities

Record the source SHA, package versions, Schema origin/revision, Build/Release digests, deployment id,
serving URL, installed revision, caller identity coordinates, and callable key. Do not use a serving
URL as Schema identity or assume the newest deployment is installed.

## Issuer, Domain origin, and URL are different coordinates

Use this distinction when discovery, authentication, or routing fails; ordinary Domain code should
use SDK bindings rather than reconstruct these coordinates.

| Coordinate | Selects | Example |
| --- | --- | --- |
| `kernel: IssuerId` | Canonical Kernel security authority | `https://host.example/api` |
| `origin: DomainOrigin` | Semantic Domain | `projects.example` |
| `invocationUrl` | Concrete network resource | `https://host.example/api/invoke` |
| `transportOrigin` | Browser origin: scheme, host, port | `https://host.example` |

- Never normalize an issuer with `new URL(kernel).origin`: it drops the identity-bearing `/api`.
  Derive Kernel protocol endpoints through SDK helpers, not a separately configurable invocation URL.
- Keep independent URLs for bundles, external discovery, provider routes, callbacks, and probes.
  A Router may proxy a Kernel without changing its canonical issuer.
- Authentication identifies an exact `(iss, sub)` pair, not a Domain origin. The verified release
  (`/.well-known/astrale/release.json`) binds semantic origin, issuer/subject, and concrete endpoints; compare those rather than
  hostnames alone.
- One Kernel can publish intrinsic `kernel.astrale.ai` and host installed `projects.example` at the same
  issuer. Select the installed product by its Domain origin, not the intrinsic release's origin.

## Follow an invocation only when diagnosing transport

```text
installed-Domain binding → source Kernel → local result
                                       ↘ verified protocol redirect → destination
                                         subsequent calls may reuse the learned route/credential
```

- The SDK session owns discovery, delegation transport, redirect admission, and credential reuse.
  Do not assume every call performs separate delegate/exchange requests; local and warm calls differ.
- A Domain token exchange changes the authenticated principal to that Domain's installed identity while
  the caller stays the verified source identity, usually the user. This changes principal
  capabilities/ownership, not the caller: Policies still evaluate the user, and Journal records name the
  Domain as principal. Class observation Policies do not require such an exchange merely to supply
  principal Class authority; use the session selected by the host.
- A protocol redirect carries a destination credential, not permission to forward the original token
  to any URL. Only the pinned source may redirect; a destination redirect is rejected.
- Route reuse is partitioned by source, target, credential, delegation, and expected Schema revision.
  Changing identity must not reuse another caller's credential; route artifacts are confidential.
- Cached routes expire with their admitted lifetime/credential. An admitted stale-route or route-miss
  failure can trigger bounded source recovery; business refusals and arbitrary timeouts are not retry signals.
- Kernel admission uses the installed Registry contract while the serving SDK validates the handler against
  its deployed Release. A mismatch requires coherent installation/deployment, not stripped revision checks;
  compare safe route and release metadata without logging credentials.

## Classify admission failures

- Authentication failure: credential/session evidence was not admitted.
- Graph authority failure: distinguish observation with a Class Policy, observation without one, and
  effects. Their principal/caller rules differ; see `policies.md` before adding Class capabilities.
- Callable authority failure: inspect the authenticated principal's effective profile and the caller
  separately. Missing direct `can_use` may be satisfied through groups; a passing callable Policy cannot
  compensate for a failed principal ceiling. The installed executor never substitutes for that principal.
- Policy refusal: distinguish Function Root/owner alternatives from Class capability/owner alternatives;
  Function `can_use` does not bypass a business Policy. Check the deployed Kernel's semantics first.
- Input failure: callable validation rejected input before execution.

Confirm denied calls caused no Action, Workflow step, Provider, or graph effect. Never add a handler
fallback or anonymous/Via bypass to make a test pass.

For a nested Kernel call, inspect the installed Domain's requested and materialized capabilities
before changing auth mode or Policy. Successful remote `Function.admit` followed by `Access denied`
before the expected Kernel syscall suggests a nested authority problem; it does not identify which
edge or traversal failed. Check exact requirements, materialized capabilities, the selected
`caller`/`self` session, and the deployed Kernel revision. Do not grant the human dynamic
authority to conceal the failure. After correcting the proven cause, repeat the call and observe
effects independently.

Treat authentication and registration journal inputs as secret unless their redaction is independently
proven. Do not retain or display a complete journal record merely to learn the phase: proof JWTs,
keys, credentials, or headers may be nested in otherwise useful callable input. Prefer safe outcome,
topic, callable, and capability metadata, and destroy isolated journal state during terminal cleanup.

## Runtime failures

- Runtime initialization errors occur before invocation; inspect admitted environment and Provider
  construction without printing secrets.
- Action dispatch errors involve one registered Action address and have no Step lifecycle.
- Workflow failures should name the stable step that failed; step results must be JSON-serializable.
- Provider response errors belong to Provider admission; unexpected network defects must not become
  caller-input errors.

## Graph failures

Use resolved Schema definitions and public Query/Mutation APIs. Check pagination, receiver identity,
typed Edge direction, live Mutation preconditions, and installed revision. A read before a Mutation is
not transaction evidence.

## Deployment and installation

Fetch the deployment's release (release.json), discovery/JWKS, and Bundle rather than trusting
intended Addressing. Then inspect Kernel installation state. If a Worker cannot reach a local Kernel
tunnel, prove public health and Worker-to-Kernel reachability separately.

## Package drift

For a downstream Domain:

- manifest declares SDK and public adapter, not Kernel implementation packages;
- emitted declarations expose SDK facades;
- lockfile has no source/workspace override for Astrale packages;
- Worker bundle excludes linter, declaration-packaging, compiler, and scaffold closure.

Reproduce from a packed or published package outside every repository before labeling a workspace-only
failure as a product defect.
