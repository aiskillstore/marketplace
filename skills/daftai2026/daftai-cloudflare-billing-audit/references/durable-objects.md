# Durable Objects

Default scope is offline, read-only source review; do not query a live account. Runtime state is unknown unless the user separately supplies redacted evidence. Trace alarm, request, storage and duration paths. Binding presence is not enough to infer whether an object is active or billable.

## Storage meter and backend boundary

- **SQLite-backed:** Storage operations are metered as rows read/written plus stored data over time. KV-style `get`/`put`/`delete`/`list` use an internal SQLite table; each `setAlarm()` is one row write, and deletes count as rows written. Stored data remains billable until removed.
- **Legacy key-value-backed:** Read/write operations use request units, with one unit per 4 KB of data (larger reads/writes use multiple units); `list()` is measured by data examined. Each `setAlarm()` is one write request unit. Delete calls are counted per delete request, not per 4 KB chunk; stored data remains until removed. This backend is limited to existing namespaces on Workers Paid; Workers Free supports SQLite only.
- These are **storage** units; DO request count and duration are separate compute meters. A generic DO binding does not prove the deployed namespace backend. If repository/config evidence does not establish it, report the backend and resulting storage meter as unknown rather than choosing one.
- Official basis: [Durable Objects pricing: storage billing](https://developers.cloudflare.com/durable-objects/platform/pricing/#storage-billing) (CF-DOC-DO-PRICING). Checked 2026-10-12. Rates are intentionally omitted.

## CF-DO-ALARM-LOOP — self-renewing alarm chain
- Risk conditions: constructor/wake code calls setAlarm without checking existing work, or alarm() schedules the next alarm on every exit without a persisted stop condition/minimum delay. Repeated setAlarm calls replace the single pending alarm; they do not queue multiple future alarms.
- Check: call sites for setAlarm/getAlarm/deleteAlarm; constructor/wake → alarm handler → next alarm; Date.now scheduling; cron/health-check cadence; bounded storage operations per alarm. Trace the actual progress field from read to write and confirm it is the same key/column/row identity the next run reads; a stored refresh/deadline value already in the past makes `setAlarm()` run again in the immediate future. Check that idle and terminal/tripped branches delete/avoid the next alarm. Review actual alarm counts only from separately supplied redacted evidence.
- Mitigation and trade-off: schedule only while work remains, persist a deadline/attempt count and terminal/tripped state, enforce a justified minimum delay, make the handler idempotent and test that idle/terminal paths leave no alarm. In-memory flags alone do not survive eviction or restart. Stopping may leave a job incomplete; provide resume handling.
- Blind spots: repeated scheduling is not multiple queued alarms; `setAlarm()` replaces the single pending alarm. A timestamp at or before now schedules the alarm for asynchronous execution in the immediate future, so a stale progress time can repeat quickly; this does not prove deployed frequency. Its storage-write unit depends on the backend described above. External triggers may not be visible in source; a case report is not proof another project has the same defect.
- Evidence: caseIds willmoss-durable-object-alarm, shmily7-durable-object-alarm; guideIds cloudflare-durable-objects-alarms, layercache-cloudflare-cost-guard-skill, cloudflare-cost-guard; official sourceIds CF-DOC-DO-PRICING, CF-DOC-DO-ALARMS, CF-DOC-DO-BASE (related pages CF-DOC-DO-STORAGE and CF-DOC-DO-STATE-STORAGE). Checked 2026-10-12.

## CF-DO-RETRY-AMPLIFICATION — repeated alarm failures
- Risk conditions: alarm handler can throw uncaught errors after side effects, or retry non-idempotent work without attempt/deadline bounds.
- Check: exception paths, side effects before failure, retry state, alarm scheduling and duplicate suppression. Verify breaker/tripped/attempt state is persisted and still applies after object eviction, restart, or a new alarm; check reservation occurs before an expensive operation when the design uses a finite job budget.
- Mitigation and trade-off: make side effects idempotent, persist attempts and terminal state, and cap retries with explicit handling for permanent failures. A durable reservation can bound application work, but a DO storage transaction cannot include a remote API side effect; a crash between reservation, side effect and completion marker can consume a reservation or repeat the external action, so reconcile/idempotency is still required. A strict retry cap may abandon transiently failing work; reservation may also consume budget on a failed attempt.
- Blind spots: cited alarm-loop cases do not establish an uncaught-exception retry incident; this is an official API behavior to check, not a case-derived frequency. A static source review cannot prove restart/crash behavior or guarantee a global spend cap.
- Evidence: guideIds cloudflare-durable-objects-alarms, cloudflare-cost-guard; official sourceIds CF-DOC-DO-BASE, CF-DOC-DO-ALARMS (related pages CF-DOC-DO-STORAGE and CF-DOC-DO-STATE-STORAGE). Checked 2026-10-12.

## CF-DO-IDLE-PINNING — unexpectedly long active duration
- Risk conditions: evidence shows pending I/O or non-hibernating WebSocket activity keeps an object active beyond the intended idle interval.
- Check: lifecycle, pending I/O, websocket APIs, and bounded duration traces only if the user supplies them in redacted form. Do not infer this from an object binding.
- Mitigation and trade-off: allow idle eligible WebSockets to hibernate and end unnecessary I/O; this can require reconnect/state restoration design.
- Blind spots: no cited Billflare case proves this specific duration mechanism; the case examples focus on alarm/storage loops.
- Evidence: guideIds durable-objects-websocket-hibernation, cloudflare-optimize-costs; official sourceIds CF-DOC-DO-PRICING, CF-DOC-DO-HIBERNATION.
