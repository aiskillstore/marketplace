---
id: "websocket-presence"
title: "WebSocket presence and reconnect"
category: "networking"
summary: "Maintain low-latency presence updates with expiration, recovery and explicit scale limits."
aliases: ["websocket","heartbeat","online status","typing indicator","çevrimiçi durum","metroya inince çevrimiçi görünmeye devam","mesaj yazıyor göstergesi","WebSocket bağlantısı koptu","çevrimiçi durum gecikmesi"]
decisions: [{"when":"Updates are frequent or bidirectional","use":"Use WebSockets with heartbeat, lease expiration and reconnect snapshot or replay.","tradeoff":"Long-lived connections require backpressure, routing and capacity planning."},{"when":"Updates are infrequent or travel only server-to-client","use":"Use bounded polling or server-sent events with a fresh snapshot on reconnect.","tradeoff":"Polling increases round trips and SSE is a one-way channel."}]
checks: ["Test abrupt link loss, reconnect and overlapping sessions.","Apply slow-client backpressure and assert connections do not accumulate unbounded data."]
sources: [{"title":"RFC 6455 WebSocket Protocol","url":"https://www.rfc-editor.org/rfc/rfc6455"},{"title":"WHATWG server-sent events","url":"https://html.spec.whatwg.org/multipage/server-sent-events.html"}]
---

<!-- Generated record title. -->
# WebSocket presence and reconnect

## Scenario

A collaboration room wants users to see who is online and typing even when switches between mobile and Wi-Fi interrupt connections.

## Failure modes

A transport connection can become half-open. Multiple devices need aggregation and an old disconnect can overwrite a newer session.

## Explain it simply

Use an open channel for updates and expire a session when it stops checking in.

## Implementation guidance

Assign each connection a distinct identity so an older disconnect cannot erase a newer session for the same user. Heartbeats renew a bounded lease and a disconnect updates that connection alone. Aggregate across a user’s devices before displaying presence. On reconnect, send a versioned snapshot or sequence-consistent replay. Test half-open Wi-Fi, two devices, and an expired connection whose event arrives after the newer session opens.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Updates are frequent or bidirectional** Use WebSockets with heartbeat, lease expiration and reconnect snapshot or replay. Long-lived connections require backpressure, routing and capacity planning.
- **Updates are infrequent or travel only server-to-client** Use bounded polling or server-sent events with a fresh snapshot on reconnect. Polling increases round trips and SSE is a one-way channel.

## Verification

- Test abrupt link loss, reconnect and overlapping sessions.
- Apply slow-client backpressure and assert connections do not accumulate unbounded data.

## Sources

- [RFC 6455 WebSocket Protocol](https://www.rfc-editor.org/rfc/rfc6455)
- [WHATWG server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html)

<!-- End generated record details. -->
