# Networking and delivery

- [DNS TTL and service cutover](../knowledge/networking/dns-time-to-live.md) · Plan a DNS change around resolver caches, connection reuse and reversible origin transitions.
- [HTTP validators and cache freshness](../knowledge/networking/http-conditional-cache.md) · Let clients validate cached representations while preserving authorization and variant boundaries.
- [Segmented live streaming latency](../knowledge/networking/live-stream-latency.md) · Trade live delay against playback stability and origin load when delivering a live stream.
- [Token-bucket rate limiting](../knowledge/networking/rate-limiting.md) · Bound sustained requests and explicitly allow or reject bursts for a scoped resource.
- [HTTP compression with explicit variants](../knowledge/networking/response-compression.md) · Reduce response transfer size without overloading the server or mixing encoding variants in caches.
- [Server-sent events for one-way updates](../knowledge/networking/sse-notifications.md) · Deliver small one-way progress events with bounded reconnect and replay behavior.
- [WebSocket presence and reconnect](../knowledge/networking/websocket-presence.md) · Maintain low-latency presence updates with expiration, recovery and explicit scale limits.
