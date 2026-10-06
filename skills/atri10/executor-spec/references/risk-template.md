# Risk Template (Pre-Mortem)

Path: `<initiative>/risks/INIT-NNNN-RISK-nn-<topic-slug>.md`

The narrative comes first and everything else traces to it. A risk list
written without the narrative is a checklist from another project.

## Skeleton

````markdown
---
id: INIT-0004-RISK-01
initiative: INIT-0004
kind: risk
title: Cell placement pre-mortem
status: draft
created_at: <UTC from an executed command>
updated_at: <same>
supersedes: null
superseded_by: null
method: pre-mortem
risks_identified: 4
mitigations_planned: 2
accepted_without_mitigation: 2
---

# Cell placement — pre-mortem

## The failure history

<Past tense. Fix a date far enough out that the failure has consequences.
Three to eight sentences. Name what users and operators saw, not what the
code did.>

It is 2027-01. Cell placement shipped in September. By November, placement
latency at 8k tenants had tripled, because the available-cell scan was
linear and nobody measured it above 2k. Two tenants landed on the same
cell despite the isolation rule, and when that cell lost its disk both
were down for eleven hours — the runbook had no entry for a split cell.
We rolled back in December and discovered the migration path back to
shared storage had never been built.

## Causes

Every cause traces to a sentence above. Every sentence above produces at
least one cause.

| ID | Cause | Traces to | Probability | Blast radius | Disposition |
|---|---|---|---|---|---|
| K01 | Available-cell scan is linear; never measured above 2k tenants | "latency had tripled" | high — no load test exists today | initiative | mitigated → R11, V05 |
| K02 | Isolation rule enforced in the caller, not the placement service | "two tenants landed on the same cell" | medium — one caller today, more later | product | mitigated → R09, INIT-0004-ADR-02 revisit |
| K03 | No runbook entry for a split cell | "runbook had no entry" | high — no runbook work is planned | contained | accepted → A01 |
| K04 | No migration path back to shared storage | "had never been built" | low — rollback is rare | irreversible | accepted → A02 |

**Probability** is high / medium / low with the reason in one clause — not
a percentage you cannot defend. **Blast radius** is contained (one
component) / initiative (this initiative's value) / product / irreversible
(unrecoverable: leaked credentials, lost data, a one-way migration).

Sort by blast radius first, probability second: a low-probability
irreversible risk outranks a likely contained one, because contained
things can be fixed twice.

## Mitigations

Every mitigation names its landing site by ID. A mitigation with no
landing site is a wish.

| Cause | Mitigation | Lands in |
|---|---|---|
| K01 | Placement service emits a `placement_latency_ms` histogram; a load check at 10k tenants is part of acceptance | R11 (this spec) + V05 (VRFY) |
| K02 | Isolation is enforced inside the placement service, not the caller | R09 (this spec); INIT-0004-ADR-02 gains the consequence |

Landing sites, in order of preference:

| Site | Form | Note |
|---|---|---|
| This spec | A new or tightened `R<nn>` / `C<nn>` | Strongest — it becomes a requirement a review can cite |
| Verification | A VRFY row that would catch the failure | Use when the behaviour exists and only the check is missing |
| Planning | A named task-shaped deliverable the plan must contain | Weaker — the plan is not written yet; say it here so planning cannot miss it |
| Architecture | An ADR to revisit, by ID | Use when the mitigation changes a decision, not a requirement |

`mitigations_planned` counts landed mitigations only.

## Accepted without mitigation

Each accepted risk names why, and what would change the judgment. Without
the second, "accepted" means "ignored, in writing".

### A01 — No runbook entry for a split cell (K03)

**Accepted because:** runbook authorship is owned by operations and sits
outside this charter's scope; the failure costs recovery time, not data.

**What would change this:** a second team taking on-call for these cells,
or a split cell occurring once in staging.

### A02 — No migration path back to shared storage (K04)

**Accepted because:** building and testing a reverse migration costs more
than the expected loss while cell count is under ten and every tenant can
be re-placed from source data.

**What would change this:** cell count passing ten, or any tenant data
originating in a cell rather than being copied into it.

## Requirements changed by this pre-mortem

Recorded so a reader sees the pre-mortem did work rather than decorating
the folder.

| Requirement | Change | Cause |
|---|---|---|
| R09 | Added — isolation enforced in the placement service | K02 |
| R11 | Added — latency histogram plus a 10k-tenant acceptance check | K01 |
````

## Procedure

1. **Narrative first.** Past tense, dated, consequences named. "Latency
   might degrade" is a worry you can wave away; "latency had tripled by
   November" forces you to say how, and the how is the risk.
2. **Extract causes** from the narrative. Every cause traces to a
   sentence; every sentence yields a cause.
3. **Invert as a second pass.** Ask how you would *guarantee* this fails —
   skip the review, ignore the limit, deploy before the holiday. Merge
   into the cause table, dedupe, and drop anything untethered to the
   narrative; an unnarrated risk usually belongs to another initiative.
4. **Rate** by probability and blast radius, with reasons.
5. **Assign mitigations** with landing sites, or accept explicitly.
6. **Feed requirement-affecting mitigations back into the spec** while it
   is still `draft`. Doing this after a plan exists costs a supersession.
7. **Reconcile the counts** with the body before writing the file.

## Count reconciliation

| Frontmatter field | Must equal |
|---|---|
| `risks_identified` | Rows in the Causes table |
| `mitigations_planned` | Rows in the Mitigations table |
| `accepted_without_mitigation` | `###` blocks under "Accepted without mitigation" |

A count that disagrees with the body is how a risk register becomes
decorative: the human reads the frontmatter, the body says something else,
and nobody notices which is lying.

## Anti-patterns

| Anti-pattern | Fix |
|---|---|
| A generic risk list ("scope creep, key person leaves, tech debt") | Every risk traces to a narrative sentence, or it is cut |
| Probability as a percentage | High / medium / low with a reason clause |
| "Mitigation: monitor closely" | Name the landing site: which requirement, which VRFY row |
| Every risk mitigated | Suspicious. Some risks are worth accepting; say so and name the falsifier |
| An accepted risk with no falsifier | Add the observation that reopens it, or mitigate it |
| A pre-mortem written after the spec was approved | It exists to change the spec. Write it before the gate |
