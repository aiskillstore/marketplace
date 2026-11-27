---
id: "short-url-identifiers"
title: "Short URL identifier allocation"
category: "backend"
summary: "Allocate compact resolvable IDs with collision handling and explicit predictability requirements."
aliases: ["base62","url shortener","id blocks","short link collision","url kısaltıcı","kısa bağlantı kodu","URL kısaltma","benzersiz bağlantı kimliği"]
decisions: [{"when":"Predictability is acceptable for public links","use":"Allocate unique IDs centrally or in disjoint blocks and encode them in Base62.","tradeoff":"Block allocation trades throughput for gaps and preserves some ordering information."},{"when":"Guessing a link would disclose an unlisted resource","use":"Use sufficiently random identifiers with a unique constraint and enforce authorization at the destination.","tradeoff":"Longer IDs reduce guessing and the database remains the collision authority."}]
checks: ["Generate concurrent IDs on separate workers and assert uniqueness.","Check expired, updated and unauthorized destinations through the redirect entry point."]
sources: [{"title":"PostgreSQL sequence functions","url":"https://www.postgresql.org/docs/current/functions-sequence.html"},{"title":"RFC 3986 URI generic syntax","url":"https://www.rfc-editor.org/rfc/rfc3986"},{"title":"RFC 4086 randomness requirements","url":"https://www.rfc-editor.org/rfc/rfc4086"}]
---

<!-- Generated record title. -->
# Short URL identifier allocation

## Scenario

An event platform creates compact public share links. It must support bursty creation while targets remain mutable after publication.

## Failure modes

Base62 is an encoding, not an entropy source. Sequential IDs leak order and may be enumerated. A cached destination can outlive a change.

## Explain it simply

A short code can represent a unique number, and the service stores the destination it points to.

## Implementation guidance

Specify whether the link is public, merely hard to guess, or actually authenticated. Encoding an allocated sequence makes it compact, while random identifiers need enough entropy and a uniqueness constraint with bounded collision retries. Treat the mapping as its own authoritative record so expiration, revocation or destination edits can invalidate caches. Test parallel allocation and an expired or edited mapping at a caching boundary.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Predictability is acceptable for public links** Allocate unique IDs centrally or in disjoint blocks and encode them in Base62. Block allocation trades throughput for gaps and preserves some ordering information.
- **Guessing a link would disclose an unlisted resource** Use sufficiently random identifiers with a unique constraint and enforce authorization at the destination. Longer IDs reduce guessing and the database remains the collision authority.

## Verification

- Generate concurrent IDs on separate workers and assert uniqueness.
- Check expired, updated and unauthorized destinations through the redirect entry point.

## Sources

- [PostgreSQL sequence functions](https://www.postgresql.org/docs/current/functions-sequence.html)
- [RFC 3986 URI generic syntax](https://www.rfc-editor.org/rfc/rfc3986)
- [RFC 4086 randomness requirements](https://www.rfc-editor.org/rfc/rfc4086)

<!-- End generated record details. -->
