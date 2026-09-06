# Plan: migrate the session store to a durable backend

Worked-example template for the implementation-plan class. It turns a goal into an
ordered, reviewable set of phases with acceptance criteria and gates, executable by
a different session and survivable when picked up cold. Each task has an `id`, an
observable `acceptance`, and a `gate`; dependencies form a DAG with no cycles;
every phase has a defined terminal state; no task is an orphan. The fenced block is
the machine-readable task DAG.

The scenario is a fictional service, `cart-session-store`, replacing an in-process
session cache with a durable backend so sessions survive a restart.

## Phase P0: design

Choose the durable schema and the key layout, one row per session id.

## Phase P1: dual-write

Write every new session to both the cache and the durable backend behind a flag.

## Phase P2: backfill

Copy historical sessions into the durable backend with an idempotent, resumable job.

## Phase P3: cutover

Read from the durable backend as the source of truth and retire the cache write.

```yaml
schema_version: 1
profile: technical-clarity
plan_id: PLAN-session-store-migration
tasks:
  - id: T-schema
    phase: P0
    depends_on: []
    acceptance: the durable schema stores one row per session id and round-trips a sample
    method: review
    gate: G-schema
  - id: T-dualwrite
    phase: P1
    depends_on: [T-schema]
    acceptance: create, update, and expire write to both stores behind the flag
    method: command
    gate: G-dualwrite
  - id: T-backfill
    phase: P2
    depends_on: [T-dualwrite]
    acceptance: a re-run of the backfill leaves the durable row count unchanged
    method: command
    gate: G-backfill
  - id: T-reconcile
    phase: P2
    depends_on: [T-backfill]
    acceptance: durable and cache session counts agree within the reconciliation window
    method: command
    gate: G-reconcile
  - id: T-cutover
    phase: P3
    depends_on: [T-reconcile]
    acceptance: reads resolve from the durable backend and the cache write is disabled
    method: command
    gate: G-cutover
phases:
  - id: P0
    terminal_state: schema-chosen
  - id: P1
    terminal_state: dual-write-live-behind-flag
  - id: P2
    terminal_state: backfilled-and-reconciled
  - id: P3
    terminal_state: durable-is-source-of-truth
```
