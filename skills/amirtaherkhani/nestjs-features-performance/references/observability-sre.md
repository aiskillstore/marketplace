# Observability and SRE

Operate from user impact and service objectives. Logs, metrics, and traces are useful only when they help detect, explain, or safely change the system.

## Start with ownership and objectives

Define:

- service and on-call owner;
- critical user journeys and dependencies;
- service-level indicators (SLIs), objectives (SLOs), and measurement windows;
- error-budget or release policy when reliability risk is material;
- recovery time objective (RTO) and recovery point objective (RPO) for durable data;
- escalation, incident, and communication paths.

An uptime metric from inside the process is not a user-facing availability SLI. Measure success, latency, correctness, freshness, or durability at the boundary consumers experience.

## Instrument useful signals

### Logs

- Emit structured events with timestamp, severity, service/version/environment, operation, outcome, and correlation identifiers.
- Log a failure once at the boundary that owns the diagnostic context; avoid duplicate stacks from every layer.
- Redact credentials, authorization headers, cookies, tokens, secrets, personal data, raw bodies, and signed URLs.
- Keep event names and fields stable enough for queries and alerts.
- Write container logs to stdout/stderr unless the platform contract requires another sink.

### Metrics

Cover traffic, errors, duration, and saturation for HTTP/RPC, plus event-loop delay, CPU, RSS/heap/GC, database pool wait, cache, external dependencies, and queue age/depth/processing outcomes where relevant.

Use histograms for latency distributions and alert on percentiles or SLO-derived ratios where appropriate. Bound dimensions: never use raw user IDs, request IDs, unnormalized URLs, error messages, or other unbounded values as metric labels.

### Traces

- Propagate trace context across incoming/outgoing HTTP, messages, jobs, and supported database/vendor calls.
- Name spans by stable operation, not raw resource identifiers.
- Record useful errors and status without copying sensitive payloads.
- Configure sampling from traffic, cost, and diagnostic needs; preserve critical/error traces deliberately.
- Correlate logs with trace/span identifiers and deployments without turning baggage into an untrusted secret channel.

Use established semantic conventions when stable for the installed instrumentation. Verify current OpenTelemetry JavaScript package compatibility before adding or upgrading instrumentation.

## Build dashboards for decisions

The service landing dashboard should show:

- SLI/SLO state and error-budget consumption;
- request/message traffic, errors, latency, and saturation;
- deployment/configuration markers;
- dependency latency/errors and database/cache/broker capacity;
- queue age/depth and worker outcomes;
- replica/restart/OOM/readiness state when deployed on an orchestrator.

Provide drill-down from symptom to cause: SLO impact → operation/tenant class where safe → dependency/resource → trace/log evidence. A wall of unrelated charts is not an operational model.

## Alert for action

- Page on urgent, actionable user impact or rapidly threatened SLOs.
- Use tickets or lower-severity channels for capacity trends and non-urgent toil.
- Include the service, impact, threshold/window, dashboard, runbook, owner, and recent deployment context.
- Use multiple windows or burn-rate logic where it reduces noisy short spikes and slow unnoticed failures.
- Deduplicate and inhibit dependent alerts so one outage does not page every downstream symptom independently.
- Test alert delivery and runbook links. An unexercised alert path is an assumption.

Do not page solely because a process restarted, CPU crossed a generic threshold, or one health check failed unless that condition requires immediate human action.

## Diagnose incidents from live evidence

1. Declare and assign coordination roles early enough for the impact.
2. Establish user impact, start time, affected scope, and current release/configuration.
3. Compare desired state with the running artifact and live dependency state.
4. Mitigate safely before pursuing a perfect root cause; prefer rollback, traffic reduction, feature disablement, or load shedding with known consequences.
5. Preserve a timeline, commands/changes, evidence, and decision owners.
6. Verify recovery from user-facing signals, not only a green deployment.
7. Produce a blameless follow-up with contributing conditions, concrete actions, owners, and verification.

Avoid speculative configuration changes and simultaneous untracked experiments. Change one causal lever where possible and record the result.

## Recovery and resilience

- Define what is backed up, frequency/retention, encryption, access, region/account isolation, and restore ownership.
- Test restores into an isolated environment and measure actual RPO/RTO; a successful backup job is not proof of recovery.
- Document dependency outage, credential rotation, corrupted message, database failover, and rollback/forward-repair procedures according to risk.
- Run failure drills or game days for critical paths, starting with reversible bounded scenarios.
- Track capacity limits, single points of failure, and manual recovery steps as owned work.

## Control telemetry cost and risk

Set retention, sampling, aggregation, and cardinality budgets. Keep production debugging access least-privileged and audited. Prefer a collector/agent boundary when it centralizes enrichment, buffering, redaction, routing, or vendor portability without creating a new silent failure point.

This reference owns operational telemetry and incident response. [Error handling](error-handling.md) owns failure classification and boundary mapping; both use one primary diagnostic event instead of independently logging the same stack.

See OpenTelemetry guidance on [concepts](https://opentelemetry.io/docs/concepts/), [context propagation](https://opentelemetry.io/docs/concepts/context-propagation/), and [metric cardinality](https://opentelemetry.io/docs/concepts/signals/metrics/), plus the Google SRE Workbook on [monitoring](https://sre.google/workbook/monitoring/) and [incident response](https://sre.google/workbook/incident-response/).
