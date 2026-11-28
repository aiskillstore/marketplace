---
id: "readiness-liveness"
title: "Readiness, liveness and startup checks"
category: "reliability"
summary: "Route traffic only to ready instances without restarting healthy processes during dependency incidents."
aliases: ["readiness probe","liveness probe","startup probe","health check","graceful draining","hazır olma ve canlılık kontrolü","veritabanı yokken yeniden başlatma döngüsü","sağlık kontrolü"]
decisions: [{"when":"A long startup and recoverable readiness failures are normal","use":"Use distinct startup, liveness and readiness checks tied to real capabilities.","tradeoff":"Thresholds and dependency criteria must be observed under load."},{"when":"A simple process reliably starts and serves immediately","use":"Use a minimal health strategy with a bounded shutdown and a test of the real route.","tradeoff":"Simpler probes provide fewer diagnostic distinctions."}]
checks: ["Delay startup and verify no traffic arrives before readiness.","Simulate a dependency outage and verify the chosen restart and drain behavior."]
sources: [{"title":"Kubernetes liveness, readiness and startup probes","url":"https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/"},{"title":"Kubernetes deployments","url":"https://kubernetes.io/docs/concepts/workloads/controllers/deployment/"}]
---

<!-- Generated record title. -->
# Readiness, liveness and startup checks

## Scenario

A web process warms an index before accepting requests. A short database outage should temporarily remove it from traffic when requests cannot be served.

## Failure modes

Treating every dependency outage as a liveness problem causes restart loops. Too-short startup thresholds can keep slow instances from ever becoming ready.

## Explain it simply

Check separately whether the process is alive and whether it can safely serve real requests right now.

## Implementation guidance

Use startup checks during warm-up, readiness to decide whether an instance should receive its real traffic, and liveness for a process that cannot recover. A remote outage can fail readiness without restarting healthy processes. Test a slow initial index build, a temporary dependency outage and graceful removal from traffic.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A long startup and recoverable readiness failures are normal** Use distinct startup, liveness and readiness checks tied to real capabilities. Thresholds and dependency criteria must be observed under load.
- **A simple process reliably starts and serves immediately** Use a minimal health strategy with a bounded shutdown and a test of the real route. Simpler probes provide fewer diagnostic distinctions.

## Verification

- Delay startup and verify no traffic arrives before readiness.
- Simulate a dependency outage and verify the chosen restart and drain behavior.

## Sources

- [Kubernetes liveness, readiness and startup probes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/)
- [Kubernetes deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

<!-- End generated record details. -->
