---
id: "feature-flags"
title: "Feature flags and safe rollout"
category: "product"
summary: "Release behavior gradually with stable assignment, fallback defaults and an end-of-life plan."
aliases: ["feature flag","rollout cohort","kill switch","experiment exposure","flag cleanup","özellik bayrağı","gruplara aşamalı yayına alma","özelliği hızlı kapatma"]
decisions: [{"when":"Behavior is safe to gate and effects are reversible","use":"Use deterministic targeting, documented fallback, rollout metrics and a removal owner.","tradeoff":"Both branches need coverage while the flag exists."},{"when":"State changes are irreversible or schema-dependent","use":"Plan compatibility and explicit data transitions before enabling flags that select writers.","tradeoff":"A flag rollback may not revert data already written."}]
checks: ["Verify stable assignment across restarts and flag-provider outages.","Test disabling after real writes and confirm the rollback contract."]
sources: [{"title":"OpenFeature specification","url":"https://openfeature.dev/specification/"},{"title":"Stripe Engineering online migrations","url":"https://stripe.com/blog/online-migrations"}]
---

<!-- Generated record title. -->
# Feature flags and safe rollout

## Scenario

A team enables a redesigned export process for a small cohort and wants to disable it when error rates rise.

## Failure modes

Random assignment per request produces inconsistent user experience. Cached flags can delay shutdown and unretired flags create conflicting paths.

## Explain it simply

Turn the feature on for a steady group first and give operators a clear way to disable it.

## Edge cases

Choose assignment by stable identity and define defaults for missing configuration and stale decisions. If a flag selects code that writes new data, verify old readers and rollback before enabling it. Exercise the same identity across replicas and disable the flag during work. Give the flag an owner and a retirement condition.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Behavior is safe to gate and effects are reversible** Use deterministic targeting, documented fallback, rollout metrics and a removal owner. Both branches need coverage while the flag exists.
- **State changes are irreversible or schema-dependent** Plan compatibility and explicit data transitions before enabling flags that select writers. A flag rollback may not revert data already written.

## Verification

- Verify stable assignment across restarts and flag-provider outages.
- Test disabling after real writes and confirm the rollback contract.

## Sources

- [OpenFeature specification](https://openfeature.dev/specification/)
- [Stripe Engineering online migrations](https://stripe.com/blog/online-migrations)

<!-- End generated record details. -->
