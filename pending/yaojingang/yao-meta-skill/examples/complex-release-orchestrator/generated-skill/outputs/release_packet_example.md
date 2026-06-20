# Release Packet: 2026.03.31-search-hardening

## Scope
Adds query guardrails, dependency upgrades, and an index migration for the search service.

## Risks
- [HIGH] Index migration must complete before traffic shift.
- [MEDIUM] Cache warm-up may temporarily increase search latency.

## Migrations
Run search_index_v7 migration before rollout. Rollback is safe only before background reindex completion.

## Rollout
- Run migration in primary region.
- Verify index health and shard count.
- Shift 10 percent traffic and monitor search latency.
- Shift remaining traffic after 15 minutes of stable metrics.

## Rollback
- Search error rate above 2 percent for 5 minutes.
- Median latency increases above 400ms after warm-up window.

## Stakeholder Communication
- engineering-oncall: Monitor search dashboards during the first 15 minutes after traffic shift.
- support: Watch for search degradation tickets during the release window.
- leadership: Release is go-with-conditions because migration timing is critical.

## Final Decision
GO WITH CONDITIONS
