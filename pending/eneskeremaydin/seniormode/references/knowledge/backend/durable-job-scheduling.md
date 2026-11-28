---
id: "durable-job-scheduling"
title: "Durable scheduled work and missed runs"
category: "backend"
summary: "Define scheduling, catch-up and duplicate execution for work that must survive process restarts."
aliases: ["persistent cron","durable jobs","scheduled tasks","missed run","worker lease","kalıcı zamanlanmış iş","yeniden başlatmada kaçan görev","gecelik görev bir kez çalışsın"]
decisions: [{"when":"A missed run has a real business impact","use":"Use a durable scheduler and unique occurrence ID, then lease or claim work atomically.","tradeoff":"Persistent state and clock behavior need monitoring."},{"when":"Work is periodic, cheap and allowed to skip","use":"Use an existing scheduler with an explicit non-overlap and skip policy.","tradeoff":"Downtime leaves gaps that are acceptable only under the stated contract."}]
checks: ["Restart just before and after the scheduled time and verify the catch-up rule.","Run two workers against the same eligible job and assert one durable effect."]
sources: [{"title":"Kubernetes CronJob scheduling","url":"https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/"},{"title":"PostgreSQL constraints","url":"https://www.postgresql.org/docs/current/ddl-constraints.html"}]
---

<!-- Generated record title. -->
# Durable scheduled work and missed runs

## Scenario

A report should run daily. Deploys regularly restart the process, including near its scheduled start.

## Failure modes

In-memory timers lose pending work. Multiple schedulers can duplicate a run, and catching up every missed tick can overwhelm dependencies.

## Explain it simply

Save the schedule and give each planned run an identity so restarting the service does not erase or duplicate the work.

## Implementation guidance

Persist an occurrence identity derived from the schedule and intended firing time, then let an atomic claim determine the owner. Separate schedule planning from the worker completing the occurrence. Declare the restart policy for missed ticks and bound catch-up concurrency. Restart before and after claiming a report job, and use a simulated clock through a timezone transition when recurrence follows local calendar time.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A missed run has a real business impact** Use a durable scheduler and unique occurrence ID, then lease or claim work atomically. Persistent state and clock behavior need monitoring.
- **Work is periodic, cheap and allowed to skip** Use an existing scheduler with an explicit non-overlap and skip policy. Downtime leaves gaps that are acceptable only under the stated contract.

## Verification

- Restart just before and after the scheduled time and verify the catch-up rule.
- Run two workers against the same eligible job and assert one durable effect.

## Sources

- [Kubernetes CronJob scheduling](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)

<!-- End generated record details. -->
