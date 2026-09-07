# Ownership Review

Use this template before durable complexity crosses into production.

> **If this must be maintained for three years, is it still worth adding?**

## Proposed production capability

What are we considering owning?

## User / system value

What durable value justifies long-term ownership?

## New ownership surface

Check every surface introduced or expanded:

- [ ] Public API / protocol / extension contract
- [ ] Persistent schema / storage / migration duty
- [ ] New UI state / setting / configuration
- [ ] Authentication / authorization / permission boundary
- [ ] Billing / entitlement behavior
- [ ] New service / queue / worker / infrastructure component
- [ ] Long-lived dependency
- [ ] Monitoring / alerting / operational duty
- [ ] Backward-compatibility promise
- [ ] Documentation / support obligation
- [ ] Other:

## Can it be smaller?

What can be removed while preserving the core value?

## Can it remain experimental?

Could the capability stay behind an internal interface, feature flag, beta contract, or disposable environment?

## Can it be more reversible?

What changes would reduce lock-in or rollback cost?

## Decision

Choose one:

- [ ] **OWN** — accept the long-term responsibility intentionally.
- [ ] **REDUCE** — shrink the ownership surface before production.
- [ ] **REJECT** — keep evidence/prototype if useful, but do not add production ownership.

## Rationale

Why does the expected value justify the resulting ownership cost?
