---
id: "deterministic-time-tests"
title: "Deterministic tests for time-dependent code"
category: "testing"
summary: "Test time boundaries without wall-clock sleeps or flaky assumptions about scheduling."
aliases: ["fake clock","fake timers","test expiry","time zones test","deterministic time","zamanı kontrol ederek test","sahte saat","uyuma olmadan son kullanma süresi testi"]
decisions: [{"when":"The decision can read time through a small seam","use":"Inject a clock and advance it directly in tests.","tradeoff":"The integration path still needs a check for the production time source."},{"when":"Framework timers drive the real flow","use":"Use supported fake timers with explicit promise and task flushing, plus a narrow real-time smoke test.","tradeoff":"Clock simulation may differ from distributed time behavior."}]
checks: ["Verify before, at and after the boundary without sleeps.","Test clock jumps, timezone conversion or process restart when relevant."]
sources: [{"title":"Node.js test runner","url":"https://nodejs.org/api/test.html"},{"title":"TC39 Temporal specification","url":"https://tc39.es/proposal-temporal/"}]
---

<!-- Generated record title. -->
# Deterministic tests for time-dependent code

## Scenario

A trial expiry job sets remaining access based on a clock. Tests should check exact expiration and delayed worker starts.

## Failure modes

Sleeping creates slow flaky tests. A mocked clock does not model database time or process scheduling unless the production time source is explicit.

## Explain it simply

Let tests choose the time so they can check what happens just before and just after a deadline.

## Implementation guidance

Identify production time sources that determine eligibility, including scheduler or database clocks if relevant. Inject the clock for pure rules and explicitly advance and drain tasks when using fake timers. Document whether equality triggers expiry. Verify just before, exactly at, and just after the boundary as well as a worker that missed its planned start.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The decision can read time through a small seam** Inject a clock and advance it directly in tests. The integration path still needs a check for the production time source.
- **Framework timers drive the real flow** Use supported fake timers with explicit promise and task flushing, plus a narrow real-time smoke test. Clock simulation may differ from distributed time behavior.

## Verification

- Verify before, at and after the boundary without sleeps.
- Test clock jumps, timezone conversion or process restart when relevant.

## Sources

- [Node.js test runner](https://nodejs.org/api/test.html)
- [TC39 Temporal specification](https://tc39.es/proposal-temporal/)

<!-- End generated record details. -->
