---
id: "n-plus-one-queries"
title: "N+1 queries and bounded batching"
category: "performance"
summary: "Remove repeated per-item reads while bounding response size and preserving access rules."
aliases: ["n plus one","n+1","eager loading","dataloader","batch database reads","her kayıt için ayrı veritabanı sorgusu","toplu ilişkili veriyi çek","N artı bir sorgu","separate SELECT per collection row","database query inside row loop","liste satırı başına ayrı sorgu"]
decisions: [{"when":"A page needs a bounded set of related rows","use":"Use a join, eager loading or batched keyed fetch with stable mapping.","tradeoff":"Result shape and payload size require verification."},{"when":"Optional relationships are large or often unused","use":"Fetch them on demand with independent pagination and a request-specific batching layer.","tradeoff":"Extra calls remain possible but loaded data stays proportional to use."}]
checks: ["Assert query counts stay bounded as page size increases.","Verify ordering, missing related rows and separate authorization contexts."]
sources: [{"title":"DataLoader batching and caching","url":"https://github.com/graphql/dataloader"},{"title":"PostgreSQL table expressions and joins","url":"https://www.postgresql.org/docs/current/queries-table-expressions.html"}]
---

<!-- Generated record title. -->
# N+1 queries and bounded batching

## Scenario

A report lists 50 fields and loads the most recent note for each field with a separate request.

## Failure modes

Joining unbounded relations can expand rows dramatically. Shared caches can leak authorization-sensitive data across requests.

## Explain it simply

Fetch related details for the current page together, then attach them to the right items.

## Implementation guidance

Capture query count in the real report path. Fetch the latest note for all visible field IDs in a scoped batch, or join only the relation needed by each row. Map results by ID and preserve ordering and missing notes. Keep caches request-local where access differs by account and verify that doubling visible fields does not double queries or reveal another tenant’s note.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A page needs a bounded set of related rows** Use a join, eager loading or batched keyed fetch with stable mapping. Result shape and payload size require verification.
- **Optional relationships are large or often unused** Fetch them on demand with independent pagination and a request-specific batching layer. Extra calls remain possible but loaded data stays proportional to use.

## Verification

- Assert query counts stay bounded as page size increases.
- Verify ordering, missing related rows and separate authorization contexts.

## Sources

- [DataLoader batching and caching](https://github.com/graphql/dataloader)
- [PostgreSQL table expressions and joins](https://www.postgresql.org/docs/current/queries-table-expressions.html)

<!-- End generated record details. -->
