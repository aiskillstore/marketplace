---
id: "slo-error-budget"
title: "Service-level objectives and burn alerts"
category: "reliability"
summary: "Define an observable reliability target from user outcomes and alert on meaningful consumption."
aliases: ["slo","error budget","sli","burn rate","availability target","hizmet seviyesi hedefi","hata bütçesi","kullanıcı hataları uyarısı"]
decisions: [{"when":"A user outcome has stable success and eligibility signals","use":"Define a request-based SLI with an explicit window and alert on fast and sustained error-budget burn.","tradeoff":"Eligibility and low-volume behavior require careful definitions."},{"when":"A normal interaction cannot be measured from server logs","use":"Add representative synthetic or client instrumentation and compare its coverage.","tradeoff":"Synthetic paths may miss browser, geography and account-specific conditions."}]
checks: ["Replay a known outage and verify alerts and eligible-event counts.","Confirm benign maintenance and a real user-visible failure have the intended accounting."]
sources: [{"title":"Google SRE workbook on SLOs","url":"https://sre.google/workbook/implementing-slos/"},{"title":"Google SRE workbook on SLO alerts","url":"https://sre.google/workbook/alerting-on-slos/"}]
---

<!-- Generated record title. -->
# Service-level objectives and burn alerts

## Scenario

A file editor needs to know whether save failures are frequent enough to slow feature rollout. Server CPU rises on unrelated tasks.

## Failure modes

Measuring instance uptime can miss failed saves. Low traffic and short windows can make ratios noisy.

## Explain it simply

Track whether users can do what they need and use failures over time to decide when to prioritize reliability.

## Worked example

Define a save SLI from eligible user-visible requests and a success deadline. With a 99.9% target, a 1% failure ratio corresponds to ten times the allowed fraction. Use short and long windows to distinguish rapid budget loss and sustained burn, and document sparse traffic. Show that injected save failures can trip the alert while an unrelated CPU spike does not.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A user outcome has stable success and eligibility signals** Define a request-based SLI with an explicit window and alert on fast and sustained error-budget burn. Eligibility and low-volume behavior require careful definitions.
- **A normal interaction cannot be measured from server logs** Add representative synthetic or client instrumentation and compare its coverage. Synthetic paths may miss browser, geography and account-specific conditions.

## Verification

- Replay a known outage and verify alerts and eligible-event counts.
- Confirm benign maintenance and a real user-visible failure have the intended accounting.

## Sources

- [Google SRE workbook on SLOs](https://sre.google/workbook/implementing-slos/)
- [Google SRE workbook on SLO alerts](https://sre.google/workbook/alerting-on-slos/)

<!-- End generated record details. -->
