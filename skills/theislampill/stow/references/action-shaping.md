# Action-shaping reference

Application guidance for the active ACT rule group (`category: action-shaping`). These rules shape the surface form of a
user-facing reply so the reader can act on it. They all carry
`precedence: presentation` (the lowest tier, so they yield to `profile` and
`system` rules). The ordinary payload carries the broadly applicable action
rules. ACT-004, ACT-005, and ACT-006 stay cold until a secondary issue,
multi-turn continuity state, or requested effort estimate makes one relevant.
No ACT rule applies inside `code`, `structured-data`, `quoted-text`, or
`identifiers`.

This file is a scanned surface: it tells STOW *when* each rule fires, *which
region* of the output it governs, and *how* the check runs. It does not restate
the rules themselves. For the normative wording of any rule, open the
`corpus_ref` cited under it. Shared entry shape below: **Trigger** (the
observable condition in a draft that makes the rule relevant), **Region** (where
in the output to look), **Check** (the registry `enforcement` mechanism), and
the corpus citation.

## Per-rule application

**STOW-ACT-001: Action-first response opening**
- Trigger: the draft's first line announces intent, greets, or clears its
  throat before anything actionable appears.
- Region: line one of the reply.
- Check: `heuristic` validator `lead-with-action` inspects the opening line.
- Boundary: context can precede the action when the reader must understand it
  to decide or act safely. An informational request leads with its answer.
- Full text: see corpus/action-shaping.md#STOW-ACT-001

**STOW-ACT-002: Bounded, task-complete ordered work**
- Trigger: the work decomposes into more than one ordered step, but the draft
  renders it as running prose or undifferentiated bullets.
- Region: the body of any procedure or plan.
- Check: `heuristic` validator `numbered-multistep`. Make each step one
  task-complete action. Do not impose an arbitrary item cap or drop required
  inventory, evidence, or safety content; number only the actions whose order
  the reader must follow.
- Full text: see corpus/action-shaping.md#STOW-ACT-002

**STOW-ACT-004: Defer secondary issues without dropping them**
- Trigger: a side observation or "by the way" aside is spliced into the main
  answer.
- Region: the body, between the primary action and its close.
- Check: `semantic-review`. Answer a blocking question in place because it is
  part of the active task. Otherwise preserve the secondary issue once in a
  bounded later note instead of splicing it into the main path or deleting it.
- Full text: see corpus/action-shaping.md#STOW-ACT-004

**STOW-ACT-005: Surface changed progress and remaining state**
- Trigger: a continuing multi-turn task has material changed state, or the
  reader needs a resume boundary that is not visible on screen.
- Region: the status line at the top of each turn.
- Check: `semantic-review`; report only material state changes and the minimum
  done, open, or blocked context needed to resume. Do not repeat the full plan
  or ledger when nothing material changed.
- Full text: see corpus/action-shaping.md#STOW-ACT-005

**STOW-ACT-006: Concrete effort estimates**
- Trigger: the reply proposes work whose size or duration the reader must weigh.
- Region: wherever proposed work is introduced.
- Check: `semantic-review`. Conflict: `STOW-PRO-002` (require attributable
  numbers) outranks this on accuracy: supply an estimate only when a defensible
  range exists, otherwise omit it rather than invent a number.
- Full text: see corpus/action-shaping.md#STOW-ACT-006

**STOW-ACT-007: Surface completed outcomes**
- Trigger: work ran and produced a result, but the outcome is buried in the
  body or left implicit.
- Region: the result or status area after an action runs.
- Check: `heuristic` validator `surface-outcomes`.
- Full text: see corpus/action-shaping.md#STOW-ACT-007

**STOW-ACT-008: Neutral error reporting**
- Trigger: a failure or error is being reported with an alarmed or apologetic
  opener.
- Region: the line that first reports the failure.
- Check: `deterministic` validator `no-alarm-openers`.
- Full text: see corpus/action-shaping.md#STOW-ACT-008

**STOW-ACT-011: Lists, not tables, for action sequences**
- Trigger: a table encodes steps or actions the reader is meant to perform in
  sequence.
- Region: any tabular block that carries actions.
- Check: `heuristic` validator `no-action-tables`; convert the table to a
  numbered list under `STOW-ACT-002`.
- Full text: see corpus/action-shaping.md#STOW-ACT-011

## Secondary modules

Three module files support the group. Cite them for the reasoning and the
pre-send discipline; do not inline their content.

- **When the defaults yield**: the conditions under which an ACT rule is
  correctly overridden (for example, an explicit request to explain at length,
  or a destructive action that must be confirmed first). See
  corpus/action-shaping.md
- **Pre-send self-review**: a contextual self-review of the first line, last
  line, tangents, action tables, and scan shape before delivery. This G1 guidance
  does not implement a delivery gate or final-output custody. It cannot delete
  required exhaustive or discursive content. See
  corpus/action-shaping.md
- **Rationale**: the reader model that motivates the whole group. See
  corpus/action-shaping.md

## Precedence note

Every ACT rule is `presentation` tier. Where an ACT rule meets a `profile` or
`system` rule, the higher tier wins. The one recorded intra-registry conflict is
`STOW-ACT-006` against `STOW-PRO-002`, resolved in favor of factual accuracy as
noted under that rule above.
