---
id: "cursor-pagination"
title: "Stable cursor pagination"
category: "backend"
summary: "Preserve deterministic traversal when rows arrive between paginated reads."
aliases: ["cursor pagination","keyset pagination","offset pagination","akış sayfalama","infinite scroll duplicates","sonraki sayfada kayıt tekrarı","akışa yeni kayıt gelince sayfalama","imleç ile sayfalama","liste kaydırırken yeni kayıt","kayıtlar tekrarlanıyor","akışta öğeler iki kez görünüyor","feed items show up twice"]
decisions: [{"when":"New rows arrive while a chronological walk continues","use":"Use a cursor with stable timestamp and unique tie-breaker, aligned composite index and explicit filter scope.","tradeoff":"Jump-to-page and arbitrary sort patterns become less direct."},{"when":"The collection is small, stable and random page jumps matter","use":"Use offset pagination with deterministic ordering and documented consistency.","tradeoff":"Deep offsets cost more and edits between reads can shift results."}]
checks: ["Insert new rows after the first response and assert no duplicates on the next page.","Test identical timestamps, invalid cursors and changed filters."]
sources: [{"title":"Relay GraphQL Cursor Connections specification","url":"https://relay.dev/graphql/connections.htm"},{"title":"PostgreSQL LIMIT and OFFSET remarks","url":"https://www.postgresql.org/docs/current/queries-limit.html"}]
---

<!-- Generated record title. -->
# Stable cursor pagination

## Scenario

An incident dashboard loads 25 records at a time while new incidents continue to appear at the top. Two records can share a timestamp.

## Failure modes

An offset shifts when rows arrive. Timestamp alone cannot uniquely order ties. Changing filter or sort on a reused cursor can return misleading results.

## Explain it simply

Keep a bookmark for the last item you saw, so new entries at the top do not move your bookmark.

## Implementation guidance

For a newest-first feed, sort by (timestamp DESC, ID DESC), and resume with timestamp < t OR (timestamp = t AND ID < id). Align the index with the actual filter and sorted columns. Bind values and reject a bookmark reused with incompatible filters. Insert two new rows and another row with the same timestamp between requests. Document whether a bookmark is a live seek or a versioned snapshot, especially when rows can be updated or deleted.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **New rows arrive while a chronological walk continues** Use a cursor with stable timestamp and unique tie-breaker, aligned composite index and explicit filter scope. Jump-to-page and arbitrary sort patterns become less direct.
- **The collection is small, stable and random page jumps matter** Use offset pagination with deterministic ordering and documented consistency. Deep offsets cost more and edits between reads can shift results.

## Verification

- Insert new rows after the first response and assert no duplicates on the next page.
- Test identical timestamps, invalid cursors and changed filters.

## Sources

- [Relay GraphQL Cursor Connections specification](https://relay.dev/graphql/connections.htm)
- [PostgreSQL LIMIT and OFFSET remarks](https://www.postgresql.org/docs/current/queries-limit.html)

<!-- End generated record details. -->
