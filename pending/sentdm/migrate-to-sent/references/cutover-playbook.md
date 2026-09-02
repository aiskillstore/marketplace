# Cutover playbook

## Table of contents

- [Phase overview](#phase-overview)
- [Phase 1: inventory](#phase-1-inventory)
- [Phase 2: mapping and rewrite list](#phase-2-mapping-and-rewrite-list)
- [Phase 3: parallel build](#phase-3-parallel-build)
- [Phase 4: sandbox and cohort verification](#phase-4-sandbox-and-cohort-verification)
- [Phase 5: dual-run](#phase-5-dual-run)
- [Phase 6: staged cutover](#phase-6-staged-cutover)
- [Phase 7: decommission](#phase-7-decommission)
- [Rollback triggers](#rollback-triggers)
- [Comparison metrics](#comparison-metrics)
- [Data migration rules](#data-migration-rules)

## Phase overview

| Phase | Exit gate |
| --- | --- |
| 1. Inventory | Every send call site, handler, template, and credential is listed |
| 2. Mapping | Each item has a target and a rewrite classification |
| 3. Parallel build | Sent sends and receives in a lower environment |
| 4. Verification | Sandbox parity plus a live cohort reaching `DELIVERED` |
| 5. Dual-run | Delivery, latency, and cost within agreed tolerances |
| 6. Cutover | All message classes on Sent, incumbent idle but reversible |
| 7. Decommission | One clean billing cycle, then credentials revoked |

Do not compress phases 4 and 5. The failure modes that matter — broadcast duplication, mishandled `FILTERED`, and dropped webhook events — appear under real traffic and correct cost accounting, not in tests.

## Phase 1: inventory

Enumerate mechanically rather than from memory:

- send call sites, including background jobs, cron tasks, and admin tools;
- webhook handlers and their signature verification code;
- every branch on a provider status string or numeric error code;
- template inventory with variable style and approval state;
- suppression and opt-out storage;
- credentials per environment and per tenant;
- observability: dashboards, alerts, and log fields that reference provider identifiers.

`scripts/inventory_scan.py` scans a repository for provider SDK imports, endpoint URLs, signature header names, status strings, numeric error codes, and ordered channel arrays, and reports each with a migration classification. Treat its output as the starting checklist, not the whole picture — configuration-driven senders and no-code automations will not appear in source.

## Phase 2: mapping and rewrite list

Classify every inventory item:

| Classification | Meaning | Examples |
| --- | --- | --- |
| Direct map | Same concept, different syntax | Recipient, message body, delivery status branch |
| Rewrite | Concept exists but works differently | Fallback, templates, tenancy, consent checks |
| New code | No equivalent exists | Webhook signature verification, idempotency keys |
| Delete | The incumbent workaround is unnecessary | Provider-specific retry ladders that conflict with Sent's error contract |
| Review | Logic remains useful but changes responsibility | Keyword matchers become exact local consent mirrors and must not write consent to Sent again |

The rewrite list is the real project plan. Prioritize by blast radius: ordered fallback arrays first, then status and error branching, then the receiver, then templates.

## Phase 3: parallel build

Stand Sent up beside the incumbent without removing anything:

1. Create credentials per environment, and profile-scoped keys for runtime send paths.
2. Provision Sender Profiles for tenancy, with inheritance and sharing flags set deliberately.
3. Register one webhook per environment; never share an endpoint across environments, because auto-disable is per endpoint.
4. Build the receiver as new code with its own signature tests.
5. Re-register templates and wait for approval events; approval is asynchronous and gates go-live.
6. Add `Idempotency-Key` to every mutating call, derived from your own domain objects.
7. Introduce a feature flag or router that chooses provider per message class and tenant.

## Phase 4: sandbox and cohort verification

Sandbox first: `"sandbox": true` authenticates and validates without executing, so payload shape and credential wiring can be proven in continuous integration. Remember it does not perform resource lookups, so it cannot confirm a template id exists.

Then a live cohort — internal staff or a small opt-in group. Gates:

- a send returns `202` and every `message_id` is persisted with tenant, profile, and logical send id;
- events arrive, verify, and deduplicate;
- a message reaches `DELIVERED` and the application state reflects it;
- a deliberately induced failure produces the expected terminal state without a retry storm;
- a suppressed contact produces `FILTERED` and no retry;
- a template send renders correctly with named parameters;
- an inbound `STOP` updates the exact-match local consent mirror without writing consent to Sent again.

## Phase 5: dual-run

Split traffic by tenant or message class and compare like with like. Both providers must carry comparable message mixes, since transactional and marketing traffic have different delivery profiles.

Requirements during dual-run: one application operation ledger that assigns each logical send to exactly one provider, Sent idempotency keys on every Sent mutation, equivalent incumbent safeguards where available, a single source of truth for delivery state per provider message id, and cost accounting that counts messages rather than requests. Never send the same user-facing notification through both providers merely to compare them.

Run long enough to cover a weekly seasonality cycle and at least one deliberate failure drill.

## Phase 6: staged cutover

Order by risk, lowest first:

1. internal and staff notifications;
2. low-volume transactional messages such as receipts;
3. high-volume transactional messages such as OTP and delivery alerts;
4. conversational and support traffic;
5. marketing and campaign traffic.

Keep the incumbent receiver live throughout, because in-flight messages sent before the switch still deliver status callbacks there. Cut per message class and per tenant, and hold each step long enough to see a full daily cycle.

## Phase 7: decommission

Decommission only after one full billing cycle of clean Sent data. Then, in order: disable incumbent send paths in code, remove the router flag, revoke incumbent credentials, archive incumbent delivery and consent records for the applicable retention period, and remove incumbent-specific dashboards and alerts after confirming Sent equivalents exist.

Retain the exported incumbent suppression list permanently as consent evidence, independent of the platform that now enforces it.

## Rollback triggers

Define these before dual-run so the decision is not made under pressure:

| Trigger | Action |
| --- | --- |
| Delivery rate falls below the agreed tolerance for a message class | Roll that class back |
| Duplicate messages observed in production | Halt immediately; check for ordered channel arrays and missing idempotency keys |
| Webhook `consecutive_failures` rising toward auto-disable | Roll back the receiver, fix, re-enable in the dashboard |
| `FILTERED` volume above baseline | Halt; the local suppression mirror is likely stale |
| Cost per delivered message above the agreed ceiling | Halt; verify channel arrays and message counts |
| Auth lockout on a credential | Stop all retries; ten consecutive failures escalate the lockout |

Rollback is a router flag flip per message class, which is why the router must remain in place until decommissioning.

## Comparison metrics

| Metric | Definition | Why it matters |
| --- | --- | --- |
| Delivery rate | `DELIVERED` divided by accepted, per message class | The primary quality signal |
| Filtered rate | `FILTERED` divided by accepted | Consent-mirror drift |
| Blocked rate | `BLOCKED` divided by accepted | Balance and account preconditions |
| Reroute rate | Messages with more than one attempted route | Routing health |
| Time to delivered | `DELIVERED` timestamp minus accepted timestamp | Latency comparison |
| Messages per logical send | Messages created divided by intended sends | Catches broadcast duplication |
| Cost per delivered message | Spend divided by `DELIVERED` count | The number finance will ask for |

Messages per logical send should be exactly one for single-channel intent. Anything above one means a multi-channel array is in play.

## Data migration rules

| Data | Rule |
| --- | --- |
| Contacts | Re-create in Sent with E.164 numbers; contacts are validated endpoints, not a copied CRM table |
| Suppression list | Export before cutover; treat any incumbent opt-out as a global Sent opt-out |
| Templates | Re-register and await approval; convert positional variables to named parameters |
| Message history | Leave in the incumbent, archived; do not attempt to import history |
| Credentials | Create fresh in Sent; never reuse incumbent secrets |
| Webhook secrets | New per environment; store keyed by webhook id |

Never clear `opt_out` during data migration. A migrated opt-out is consent evidence, and clearing it to reconcile row counts is a compliance failure rather than a data cleanup.
