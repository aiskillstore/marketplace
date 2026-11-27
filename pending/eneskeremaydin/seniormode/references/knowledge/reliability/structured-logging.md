---
id: "structured-logging"
title: "Structured logs and request correlation"
category: "reliability"
summary: "Capture events that let operators trace a failure without logging sensitive inputs or drowning in noise."
aliases: ["structured logging","correlation id","log redaction","trace id","diagnostic logs","yapılandırılmış günlük kaydı","istek kimliğiyle logları eşleştir","günlüklerde hassas bilgi"]
decisions: [{"when":"Several components process one request or job","use":"Use structured event fields and propagate validated request and trace identifiers.","tradeoff":"High-cardinality values need a retention and indexing policy."},{"when":"An isolated process has a simple failure model","use":"Write a small set of structured lifecycle and error events with stable meanings.","tradeoff":"Fewer signals may limit diagnosis of later cross-component failures."}]
checks: ["Trigger a controlled error and find its related events across components.","Pass representative sensitive inputs and verify the log output redacts them."]
sources: [{"title":"OpenTelemetry logs data model","url":"https://opentelemetry.io/docs/specs/otel/logs/data-model/"},{"title":"OWASP logging guidance","url":"https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html"}]
---

<!-- Generated record title. -->
# Structured logs and request correlation

## Scenario

Customer support sees a sporadic checkout failure across an API and worker but cannot correlate their messages.

## Failure modes

Free-form messages are hard to query. Logging request bodies can expose personal data. User-controlled IDs should not be trusted as diagnostic identity.

## Explain it simply

Give each request a safe tracking ID and record the facts needed to find where it failed.

## Implementation guidance

Emit a stable event name and fields for operation, result, stage and a validated request or trace ID. Propagate IDs before asynchronous handoff rather than copying whole requests to logs. Audit retention, sampling and redaction rules. Deliberately fail a checkout and reconstruct its path across service and worker events without revealing payment or personal values.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Several components process one request or job** Use structured event fields and propagate validated request and trace identifiers. High-cardinality values need a retention and indexing policy.
- **An isolated process has a simple failure model** Write a small set of structured lifecycle and error events with stable meanings. Fewer signals may limit diagnosis of later cross-component failures.

## Verification

- Trigger a controlled error and find its related events across components.
- Pass representative sensitive inputs and verify the log output redacts them.

## Sources

- [OpenTelemetry logs data model](https://opentelemetry.io/docs/specs/otel/logs/data-model/)
- [OWASP logging guidance](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)

<!-- End generated record details. -->
