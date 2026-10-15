# Account billing, Workers Logs and Builds

Default scope is offline, read-only source review. Do not log into Cloudflare, inventory account alerts, call account APIs, read live metrics/invoices, change settings, or pause services. If the user separately supplies redacted runtime evidence, interpret only that evidence. Recommend account actions only for separate authorization.

## CF-BUDGET-ALERT-NOT-CAP — notification is not a stop
- Risk conditions: a plan depends on a budget email or usage notification as the mechanism that prevents additional usage.
- Check: source/config for claims about alerts; if the user separately provides redacted screenshots/settings, consider scope and date only. Do not inspect the account yourself by default.
- Mitigation and trade-off: state that alerts notify and do not pause/cap; pair source-side bounded work with an alert strategy. Alerts may arrive after a spike and may be missed.
- Blind spots: Cloudflare documents budget alerts for Pay-as-you-go, not Enterprise contracts; Billable Usage is delayed. This rule does not authorize alert configuration.
- Evidence: guideId cloudflare-budget-alerts; official sourceIds CF-DOC-BILLING-BUDGET-ALERTS, CF-DOC-BILLING-USAGE, CF-DOC-BILLING-USAGE-BASED.

## CF-LOGS-EMISSION-VOLUME — verbose or unsampled logging
- Risk conditions: high-volume routes emit large log/event payloads at high sampling or with no retention/volume bound.
- Meter and boundary (checked 2026-10-12): the current Workers Logs meter is **log events written**, not bytes. Invocation logs and custom `console.log` events can each contribute events; sampling changes the emitted/countable volume. Workers Logpush has a separate request-log meter for logs reaching the destination after filtering/sampling. The official pricing page states that Workers Logs will move to Cloudflare Observability pricing on 2026-12-01; recheck after that date instead of carrying this unit forward.
- Check: source logging calls, observability/sampling configuration committed in the repository, and event count per invocation. Treat config as intended state, not proof of deployed state; do not equate the maximum size of one event with the billing unit.
- Mitigation and trade-off: reduce payloads, sample, filter or limit logs; sampling reduces diagnostic coverage.
- Blind spots: no Billflare Logs case/guide is cited; current usage and plan require separately supplied redacted evidence. Do not confuse Workers Logs with Logpush or future Observability pricing.
- Evidence: Billflare case/guide precedent: none cited; official sourceIds CF-DOC-WORKERS-LOGS, CF-DOC-WORKERS-PRICING.
- Official basis: [Workers Logs](https://developers.cloudflare.com/workers/observability/logs/workers-logs/) (CF-DOC-WORKERS-LOGS) and [Workers pricing: Workers Logs / Logpush](https://developers.cloudflare.com/workers/platform/pricing/#workers-logs) (CF-DOC-WORKERS-PRICING). Checked 2026-10-12.

## CF-BUILDS-TRIGGERED-MINUTES — repeated URL/CI build triggers
- Risk conditions: public or automated Deploy Hook/CI paths can trigger builds repeatedly with no caller auth, debounce, concurrency or monthly count bound.
- Meter and boundary (checked 2026-10-12): the billed unit is **build minutes**, defined as time taken to build a project. A Deploy Hook is a trigger path; its count is not itself the build-minute unit. Repeated triggers/retries matter when they create additional build runtime. Build concurrency/timeout and Deploy Hook rate limits are separate limits, not the billing unit.
- Check: repository workflow definitions including `.github/workflows/*.yml` or `*.yaml`, hook invocation call sites, retries and build duration bounds. Scanner-surfaced YAML is auxiliary evidence, not a complete parser: manually inspect relevant job/condition/command context, and do not infer absence from an omitted file or an incomplete match. Do not call live hooks or enumerate account builds.
- Mitigation and trade-off: secure hook callers, debounce, bound CI retries/concurrency and avoid unnecessary builds. This may delay deployment.
- Blind spots: no Billflare Builds case/guide is cited; this is an official meter/trigger candidate only.
- Evidence: Billflare case/guide precedent: none cited; official sourceIds CF-DOC-WORKERS-BUILDS, CF-DOC-WORKERS-DEPLOY-HOOKS.
- Official basis: [Workers Builds limits and pricing](https://developers.cloudflare.com/workers/ci-cd/builds/limits-and-pricing/) (CF-DOC-WORKERS-BUILDS) and [Deploy Hooks](https://developers.cloudflare.com/workers/ci-cd/builds/deploy-hooks/) (CF-DOC-WORKERS-DEPLOY-HOOKS). Checked 2026-10-12.

## Cross-product read-only boundary
Model exposure as billable operations × trigger count/fan-out/retries × active duration. Quantify only from evidence with a metric, unit, date and period; do not bake rates into this reference or predict an invoice from code alone. If evidence is absent, say so. Do not import any third-party severity tier. A recommendation to stop or alter a service is not permission to perform it.
