# Intake Examples

Worked gate decisions and one filled charter. Illustrative only — the
timestamps and IDs here are examples, never a template to copy values from.
Real documents take their timestamps from an executed `date -u` and their IDs
from `exec-initiative new` / `exec-id`.

## Worked classifications

### 1. "Can we serve the admin dashboard from the same process without a second port?"

**Spike.** A feasibility question whose output is an answer. Present the
probe in two sentences, get a nod, try it as cheaply as correctness allows,
report a recommendation. **No initiative** — and if the probe's code works,
keeping it is a *new* request that gets classified from scratch.

### 2. "Add a `--dry-run` flag to the importer."

**Bounded.** `importer/run.ts` exists and the flow is here to read. Ask the
questions that matter (what does dry-run print, does it still validate), a
short design in chat, explicit yes, implement. **No initiative** — unless an
active initiative already owns the importer under its approved charter, in
which case this is one task of a plan under that initiative.

### 3. "We keep getting paged for tenant noisy-neighbour issues — can you fix it?"

**Architectural.** No existing isolation flow to read, multiple components,
interfaces others depend on. **Allocate.** Note that the request names a
symptom; the charter's Problem section must state the observed evidence (the
page count, the affected tenants) and its Goals must be outcomes, not "build
cells."

### 4. "Just wire up the new pricing table — should be a one-file change."

**Bounded on arrival, architectural by the third file.** The pricing table
turns out to need a migration, a cache invalidation path, and a change to
the public quote API. The ratchet fires: stop, say so, allocate the
initiative now, and record in the charter's Problem section what was already
changed and where it stands. Nothing downgrades back.

### 5. "Same tenant work, but now also multi-region failover."

**Attach or allocate?** The existing charter's success criteria are about
placement latency and isolation; failover introduces a criterion about
recovery time that is not there. Making it fit means widening approved
Goals, which invalidates the approval. **New initiative**, with
`depends_on: [INIT-0004]` declared in its charter frontmatter — and no
document inside it ever citing an `INIT-0004` ID.

## A filled charter

`docs/executor/INIT-0004-cloud-tenant-cells/charter.md`

```markdown
---
id: INIT-0004-CHTR-01
initiative: INIT-0004
kind: charter
title: Cloud tenant cells
status: active
created_at: 2026-08-30T09:12:04Z
updated_at: 2026-08-30T16:40:51Z
supersedes: null
superseded_by: null
phase: specification
skipped_phases: [design]
depends_on: []
supersedes_initiative: null
superseded_by_initiative: null
related: []
owner: R. Okonjo (platform)
---

# Cloud tenant cells

## Problem

All 8,400 tenants share one Postgres primary and one worker pool. Between
2026-07-01 and 2026-08-29 we paged 14 times for tenant-caused saturation;
in 11 of those, one tenant's bulk import degraded every other tenant's API
latency. Incident IDs are in the on-call log; the saturation metric is
`db.primary.active_connections` from the existing dashboards. There is no
mechanism today that bounds one tenant's impact on another.

## Why now

The two largest incoming accounts contractually require a 99.9% monthly API
availability target that our current blast radius cannot support. Both
onboard in Q4. Waiting means either missing the target or manually pinning
those tenants to hand-built infrastructure.

## Goals

- One tenant's load cannot degrade another tenant's API latency beyond a
  stated bound.
- Tenants are assigned to an isolation cell automatically, with no manual
  step during onboarding.
- Operators can move a tenant between cells without downtime for that
  tenant.

## Non-goals

- Cross-region failover. Cells are single-region for this initiative.
- Per-tenant custom resource limits sold as a product feature.
- Migrating the analytics pipeline, which reads replicas and is unaffected.
- Changing the public API surface. Cell placement is invisible to clients.

## Success criteria

1. p99 API latency for a tenant stays under 200ms while a co-resident
   tenant runs the 10k-row bulk import fixture — measured with the existing
   load harness (`tools/loadgen`), reported per-tenant.
2. A tenant created through the normal onboarding path is placed in a cell
   with zero manual operator actions, verified by running onboarding against
   a staging environment and reading the placement record.
3. Moving a tenant between cells produces no failed requests for that
   tenant, measured as zero non-2xx responses in the harness during a move.
4. Saturation pages attributable to one tenant affecting others: zero over
   the 30 days following rollout, measured against the on-call log.

## Scope boundaries

May touch: `services/router/`, `services/placement/` (new),
`db/migrations/`, the onboarding worker in `services/accounts/`.

May not touch: `services/analytics/`, the public API schema in
`api/openapi.yaml`, the billing pipeline.

## Constraints

- Postgres 15 only; no new datastore may be introduced.
- No client-visible API change, so no client release is required.
- Deployment stays on the existing Kubernetes cluster and Helm chart.
- Placement service credentials come from the deployment's secret store and
  are read from `PLACEMENT_DB_URL` at startup. Value not recorded here;
  shape is `postgres://<user>:<pass>@<host>:5432/<db>`.
- Rollout must be reversible per-tenant within one deploy cycle.

## Stakeholders

- **Approves phase gates:** R. Okonjo (platform lead).
- **Must be consulted:** on-call rotation (runbook changes), account
  management (onboarding flow change).
- **Affected:** every tenant, invisibly, if criterion 4 holds.

## Skipped phases

- **design** — the initiative adds one new component (the placement
  service) behind one interface. Its internals are specified directly in
  `INIT-0004-SPEC-01` rather than in a separate design document. Waived by
  R. Okonjo at the architecture gate on 2026-08-31.
```

### What makes this charter pass the gate

| Section | The property that matters |
|---|---|
| Problem | A number, a date range, and a named metric — a reader can check it |
| Goals | Outcomes ("cannot degrade"), not activities ("write a service") |
| Non-goals | Names the four things a reader would assume were included |
| Success criteria | Each one states the observation *and* the instrument, so verification has nothing left to invent |
| Constraints | The credential appears as an existence statement with a shape, never a value |
| Stakeholders | One named approver, not "the team" |
| Skipped phases | Says which phase, why, who waived it, and when |
