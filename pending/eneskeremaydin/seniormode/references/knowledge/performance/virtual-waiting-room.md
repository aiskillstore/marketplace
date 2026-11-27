---
id: "virtual-waiting-room"
title: "Virtual waiting rooms for traffic spikes"
category: "performance"
summary: "Meter entry to a scarce service while making fairness and failure behavior explicit."
aliases: ["virtual waiting room","admission control","ticket queue","sanal bekleme odası","flash crowd","bilet satışında sanal bekleme odası","konser bileti trafik artışı","sayfayı yenileyince sıra korunuyor"]
decisions: [{"when":"Temporary arrival rate greatly exceeds safe capacity","use":"Use a server-managed queue, scoped queue token and measured admission budget.","tradeoff":"Users wait and operational fairness rules must be clearly defined."},{"when":"Demand is predictable and a queue would add friction","use":"Apply capacity controls or scheduled reservations with clear per-user limits.","tradeoff":"The approach depends on forecasts and can still require a fallback."}]
checks: ["Load-test admission, refresh, reconnect and queue token reuse protections.","Check transparent handling of sold-out events and abandoned admissions."]
sources: [{"title":"Cloudflare Waiting Room","url":"https://developers.cloudflare.com/waiting-room/"},{"title":"Google SRE on handling overload","url":"https://sre.google/sre-book/handling-overload/"}]
---

<!-- Generated record title. -->
# Virtual waiting rooms for traffic spikes

## Scenario

Twenty thousand alumni request a limited ticket inventory at opening time. The payment and inventory path can accept a capped arrival rate.

## Failure modes

Browser refreshes can bypass naive queues, and a queue token can be reused if not scoped. A late checkout must not hold inventory indefinitely.

## Explain it simply

Give arrivals a stable place in line and admit only as many as checkout can handle.

## Architecture notes

Admit from an authoritative queue using observed inventory and checkout throughput. A time-limited admission identity should preserve one place across refreshes and remain separate from a booking hold. Define whether an expired pass can rejoin. Exercise multiple tabs for one shopper and a sudden reduction in admission capacity.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Temporary arrival rate greatly exceeds safe capacity** Use a server-managed queue, scoped queue token and measured admission budget. Users wait and operational fairness rules must be clearly defined.
- **Demand is predictable and a queue would add friction** Apply capacity controls or scheduled reservations with clear per-user limits. The approach depends on forecasts and can still require a fallback.

## Verification

- Load-test admission, refresh, reconnect and queue token reuse protections.
- Check transparent handling of sold-out events and abandoned admissions.

## Sources

- [Cloudflare Waiting Room](https://developers.cloudflare.com/waiting-room/)
- [Google SRE on handling overload](https://sre.google/sre-book/handling-overload/)

<!-- End generated record details. -->
