---
id: "sse-notifications"
title: "Server-sent events for one-way updates"
category: "networking"
summary: "Deliver small one-way progress events with bounded reconnect and replay behavior."
aliases: ["server sent events","sse","eventsource","progress stream","last event id","sunucudan tarayıcıya tek yönlü olay","işlem ilerlemesini canlı göster","sunucu olay akışı"]
decisions: [{"when":"Delivery is primarily server-to-client","use":"Use EventSource with stable event IDs, reconnect policy and a bounded history or snapshot.","tradeoff":"Browser and proxy timeout behavior needs practical testing."},{"when":"The protocol requires frequent bidirectional traffic","use":"Choose a WebSocket or explicit request-response interactions based on message semantics.","tradeoff":"Additional connection state and backpressure must be managed."}]
checks: ["Disconnect mid-stream and ensure reconnect resumes or returns a fresh snapshot.","Expire the replay cursor, write an update during the snapshot handoff and verify that the final browser state includes it.","Test proxy buffering and slow readers under the chosen size limits."]
sources: [{"title":"WHATWG server-sent events","url":"https://html.spec.whatwg.org/multipage/server-sent-events.html"},{"title":"RFC 6455 WebSocket Protocol","url":"https://www.rfc-editor.org/rfc/rfc6455"}]
---

<!-- Generated record title. -->
# Server-sent events for one-way updates

## Scenario

A report generator streams progress to the browser while the user can still submit commands through ordinary HTTP requests.

## Failure modes

Reconnects can create gaps or duplicates without IDs. Proxy buffering hides updates, and unbounded replay or buffers hurt slow clients.

## Explain it simply

Keep a one-way feed open while work runs and let it resume from the last event the browser received.

## Implementation guidance

Assign progress events stable IDs and use Last-Event-ID to replay later events within a bounded window. When that cursor is too old, send current report state with the matching high-water event ID, then replay newer changes before continuing live delivery. Capture state and cursor at the same consistency boundary so concurrent progress cannot disappear between them. Disable intermediary buffering where needed, send heartbeats compatible with idle timeout, and cap buffers for slow clients. Recognize repeated event IDs when applying updates.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Delivery is primarily server-to-client** Use EventSource with stable event IDs, reconnect policy and a bounded history or snapshot. Browser and proxy timeout behavior needs practical testing.
- **The protocol requires frequent bidirectional traffic** Choose a WebSocket or explicit request-response interactions based on message semantics. Additional connection state and backpressure must be managed.

## Verification

- Disconnect mid-stream and ensure reconnect resumes or returns a fresh snapshot.
- Expire the replay cursor, write an update during the snapshot handoff and verify that the final browser state includes it.
- Test proxy buffering and slow readers under the chosen size limits.

## Sources

- [WHATWG server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [RFC 6455 WebSocket Protocol](https://www.rfc-editor.org/rfc/rfc6455)

<!-- End generated record details. -->
