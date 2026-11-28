---
id: "live-stream-latency"
title: "Segmented live streaming latency"
category: "networking"
summary: "Trade live delay against playback stability and origin load when delivering a live stream."
aliases: ["hls","ll-hls","live video","cdn","canlı yayın gecikmesi","komşu golü önce görüyor","canlı yayın geriden geliyor","HLS parça tamponu"]
decisions: [{"when":"Stability and broad device support dominate","use":"Use conventional HLS segments, CDN caching and a measured playback buffer.","tradeoff":"Viewers can sit several segments behind capture."},{"when":"End-to-end latency has a tight target","use":"Use Low-Latency HLS partial segments and verify CDN and player support.","tradeoff":"Expect more requests and lower tolerance for network jitter."}]
checks: ["Measure capture-to-playback latency alongside rebuffering under the same network profile.","Load-test origin requests and verify the player recovers after a missing part."]
sources: [{"title":"Apple Low-Latency HLS","url":"https://developer.apple.com/documentation/http-live-streaming/enabling-low-latency-http-live-streaming-hls"},{"title":"RFC 8216 HTTP Live Streaming","url":"https://www.rfc-editor.org/rfc/rfc8216"}]
---

<!-- Generated record title. -->
# Segmented live streaming latency

## Scenario

A regional esports final needs playback that remains responsive under bursty mobile connections and has a measurable delay target.

## Failure modes

Smaller buffers reduce delay but cause stalls on unstable networks. CDN and player behavior can defeat a format-level latency improvement.

## Explain it simply

Send short pieces through nearby servers and let the player hold enough video to avoid frequent pauses.

## Implementation guidance

Measure from capture to display rather than only segment duration. Tune the player live edge, playlist refresh and CDN behavior together. Compare conventional segmented HLS and a supported low-latency path on unstable connections, capturing rebuffering and startup alongside delay. Offer a sensible fallback for unsupported clients and test origin failover while viewers stay connected.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Stability and broad device support dominate** Use conventional HLS segments, CDN caching and a measured playback buffer. Viewers can sit several segments behind capture.
- **End-to-end latency has a tight target** Use Low-Latency HLS partial segments and verify CDN and player support. Expect more requests and lower tolerance for network jitter.

## Verification

- Measure capture-to-playback latency alongside rebuffering under the same network profile.
- Load-test origin requests and verify the player recovers after a missing part.

## Sources

- [Apple Low-Latency HLS](https://developer.apple.com/documentation/http-live-streaming/enabling-low-latency-http-live-streaming-hls)
- [RFC 8216 HTTP Live Streaming](https://www.rfc-editor.org/rfc/rfc8216)

<!-- End generated record details. -->
