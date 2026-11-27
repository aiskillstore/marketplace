---
id: "composite-indexes"
title: "Composite indexes for access patterns"
category: "data"
summary: "Design database indexes around actual filters, sorting, selectivity and write costs."
aliases: ["composite index","multi column index","sql query plan","covering index","database performance","çok sütunlu indeks","sorgu planı","filtre sırasına göre birleşik indeks"]
decisions: [{"when":"Equality filters and a bounded ordered read dominate","use":"Use a composite index aligned with equality keys and the ordered range, validating with plans.","tradeoff":"Index maintenance adds write and storage cost."},{"when":"Multiple independent query shapes have different cardinalities","use":"Choose indexes from measured workload and validate each representative plan.","tradeoff":"Specialization can make maintenance harder and redundant indexes should be removed."}]
checks: ["Compare EXPLAIN estimates with realistic data and verify examined rows.","Measure write overhead and test ordering for equal sort values."]
sources: [{"title":"PostgreSQL multicolumn indexes","url":"https://www.postgresql.org/docs/current/indexes-multicolumn.html"},{"title":"PostgreSQL using EXPLAIN","url":"https://www.postgresql.org/docs/current/using-explain.html"}]
related: ["cursor-pagination"]
---

<!-- Generated record title. -->
# Composite indexes for access patterns

## Scenario

A support queue lists recent open tickets per tenant. A generic status-only index remains slow for busy tenants.

## Failure modes

Column order may prevent useful ordering. Too many indexes slow writes and increase disk and maintenance costs. A small test table can hide poor plans.

## Explain it simply

Arrange the index in the order that matches how most queries narrow and sort the data.

## Implementation guidance

For WHERE tenant_id = ? AND status = 'open' ORDER BY created_at DESC, id DESC, a starting candidate is an index beginning with the equality columns followed by the sorted columns. Verify with actual plans and data distributions across tenants, including rows with equal timestamps. Validate the exact query shape and compare index size, write cost and lookup latency before removing old indexes.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Equality filters and a bounded ordered read dominate** Use a composite index aligned with equality keys and the ordered range, validating with plans. Index maintenance adds write and storage cost.
- **Multiple independent query shapes have different cardinalities** Choose indexes from measured workload and validate each representative plan. Specialization can make maintenance harder and redundant indexes should be removed.

## Verification

- Compare EXPLAIN estimates with realistic data and verify examined rows.
- Measure write overhead and test ordering for equal sort values.

## Sources

- [PostgreSQL multicolumn indexes](https://www.postgresql.org/docs/current/indexes-multicolumn.html)
- [PostgreSQL using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)

## Related decisions

- [Stable cursor pagination](../backend/cursor-pagination.md)

<!-- End generated record details. -->
