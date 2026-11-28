---
id: "transaction-isolation"
title: "Transaction isolation for cross-row invariants"
category: "data"
summary: "Pick isolation or explicit locking based on the anomaly that would break a business invariant."
aliases: ["transaction isolation","write skew","serializable","snapshot isolation","database invariants","veritabanı işlem yalıtımı","eşzamanlı işlemlerde veri kuralı","seri hale getirilebilir işlem"]
decisions: [{"when":"A clear row or unique constraint represents the invariant","use":"Use a constraint or a short transaction with the specific guarded row.","tradeoff":"Hot coordination rows can cause contention."},{"when":"The invariant spans rows without a stable lock key","use":"Use serializable isolation and retry the full transaction on serialization failure.","tradeoff":"Aborts become expected and hooks must not duplicate external effects."}]
checks: ["Reproduce write skew with two connections and verify the invariant stays true.","Exercise transaction retry after a serialization abort and check effect boundaries."]
sources: [{"title":"PostgreSQL transaction isolation","url":"https://www.postgresql.org/docs/current/transaction-iso.html"},{"title":"PostgreSQL constraints","url":"https://www.postgresql.org/docs/current/ddl-constraints.html"}]
related: ["reservation-concurrency"]
---

<!-- Generated record title. -->
# Transaction isolation for cross-row invariants

## Scenario

An on-call roster can release a person only if at least one other person remains on duty. Two operators make independent changes simultaneously.

## Failure modes

Two transactions may read the same safe amount and update different rows under snapshot isolation. Retrying the final statement alone can retain stale assumptions.

## Explain it simply

Make the database reject one of two changes if accepting them together would violate the rule.

## Implementation guidance

Define the invariant across all rows that matter. If each operator independently updates a different roster row, checking the remaining count first can allow both changes. Guard a shared row or use a fully serializable transaction and retry it from its first read on a serialization conflict. Keep retries bounded and postpone irreversible external actions until the commit outcome is known. Test two transactions that read before either attempts a write.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A clear row or unique constraint represents the invariant** Use a constraint or a short transaction with the specific guarded row. Hot coordination rows can cause contention.
- **The invariant spans rows without a stable lock key** Use serializable isolation and retry the full transaction on serialization failure. Aborts become expected and hooks must not duplicate external effects.

## Verification

- Reproduce write skew with two connections and verify the invariant stays true.
- Exercise transaction retry after a serialization abort and check effect boundaries.

## Sources

- [PostgreSQL transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)

## Related decisions

- [Concurrent reservations and expiring holds](../concurrency/reservation-concurrency.md)

<!-- End generated record details. -->
