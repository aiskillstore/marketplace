# Implementation plans

An **implementation plan** turns a spec or goal into an ordered, reviewable set
of phases and tasks, each with acceptance criteria and a gate, executable by a
**different session** and survivable when picked up cold. It is the artifact a
writing pass produces and an executing pass consumes; both may run in fresh
contexts, so the plan must stand alone under the cold-reader rule of the
meta-code layer (see `references/meta-code.md`).

This page is a scanned surface, not rule text. For the wording of any governed
prose rule named below, open its cited `corpus_ref` module.

## When this page applies

- **Predicate:** a goal is being decomposed into phases and tasks that another
  session will execute and review, or an existing plan is being audited for
  executability.

## Governing STOW families

- **Procedures (profile, band 7).** Each task step is a single imperative
  instruction, one instruction per step; see corpus/procedures.md#STOW-PRC-002
  and corpus/procedures.md#STOW-PRC-003. Multi-step work is rendered as numbered
  steps, per corpus/action-shaping.md#STOW-ACT-002.
- **Accuracy (band 5).** An effort or size estimate is supplied only when a
  defensible range exists, and omitted otherwise rather than invented; see
  corpus/action-shaping.md#STOW-ACT-006.
- **Terminology (band 6).** Task IDs are stable and reused wherever the task is
  named, per corpus/words/usage.md#STOW-WRD-011.
- **Presentation (band 8).** Phase headings are concrete and descriptive
  (`SKILL.md` section 4).

## Governing schema + template

- **Schema.** `schemas/plan.schema.json` validates the plan's fenced task-DAG
  block (plan id, phases with terminal states, tasks with observable
  acceptance). A task dispatched FROM a plan validates separately against
  `schemas/task-packet.schema.json`. Each task carries an `id`, an `acceptance[]`
  (each a `{predicate, method, expected}` where `method` is one of
  `command | parse | schema | review`), and a gate. Acceptance criteria are the
  same shape a dispatched task packet uses, so a plan task and a task packet
  validate against one contract.
- **Template.** `templates/PLAN.md`, a valid instance: ordered phases, each with
  a gate and an observable acceptance line, dependencies forming a DAG.

## Validation contract

Validate the plan document (its fenced task-DAG block) against the plan schema;
a task dispatched FROM the plan validates separately as a task packet:

```
python skills/stow/runtime/validate.py --schema plan templates/PLAN.md
python skills/stow/runtime/validate.py --schema task-packet <packet-file>
```

The load-bearing rules: every task has an `id`, an `acceptance`, and a gate;
dependencies form a DAG with no cycle; every phase has a defined terminal state;
each acceptance criterion is a single observable predicate that is either
mechanical or explicitly tagged `method: review`; no task is orphaned from a
phase. **Cold-reader gate:** a fresh executor can act on each task from the plan
alone, with no reference to the planning conversation.
