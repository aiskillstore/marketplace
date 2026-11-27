---
id: "load-test-arrival-model"
title: "Load tests with realistic arrival models"
category: "testing"
summary: "Choose and document load generation that exposes queueing under the stated traffic pattern."
aliases: ["load test methodology","open arrival model","closed load model","coordinated omission","tail latency","yük testinde geliş hızı","yanıt yavaşlayınca test yükü düşüyor","gerçekçi yük testi"]
decisions: [{"when":"Production demand arrives independently of server latency","use":"Use an open arrival-rate model, track dropped iterations and include errors and tail latency.","tradeoff":"The generator needs its own headroom to maintain target arrival rate."},{"when":"Each real user submits the next request only after a result","use":"Use a closed concurrency model with realistic think times and document the model.","tradeoff":"It can under-represent overload when production arrivals are independent."}]
checks: ["Inject a slow stage and verify reported latency includes waiting, failures and dropped work.","Confirm the generator reached its configured shape at each recorded load point."]
sources: [{"title":"Grafana k6 open and closed models","url":"https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/"},{"title":"Google SRE on handling overload","url":"https://sre.google/sre-book/handling-overload/"}]
---

<!-- Generated record title. -->
# Load tests with realistic arrival models

## Scenario

A checkout service meets latency targets with 100 virtual users, but real users arrive independently of current response speed.

## Failure modes

Closed-loop drivers slow their arrivals when the server gets slower. Load generators may saturate or omit failed responses from reports.

## Explain it simply

Send requests at the rate real demand would arrive and measure how long users actually wait.

## Implementation guidance

Use an independent arrival schedule for workloads that keep growing while the server slows. Track dropped starts, generator utilization and errors alongside tail latency, including end-to-end waiting. A closed model can instead reflect a fixed group with realistic think times. Apply the same slowdown to both models and compare arrivals and measured tails to the expected workload.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Production demand arrives independently of server latency** Use an open arrival-rate model, track dropped iterations and include errors and tail latency. The generator needs its own headroom to maintain target arrival rate.
- **Each real user submits the next request only after a result** Use a closed concurrency model with realistic think times and document the model. It can under-represent overload when production arrivals are independent.

## Verification

- Inject a slow stage and verify reported latency includes waiting, failures and dropped work.
- Confirm the generator reached its configured shape at each recorded load point.

## Sources

- [Grafana k6 open and closed models](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/)
- [Google SRE on handling overload](https://sre.google/sre-book/handling-overload/)

<!-- End generated record details. -->
