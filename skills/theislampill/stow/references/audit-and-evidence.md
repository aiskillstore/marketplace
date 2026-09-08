# Audit and evidence records

An **audit / evidence record** is the unit a read-only reviewer or a CI gate
produces so a decision-maker can act: a fact, a recommendation, or a finding,
each carrying verifiable evidence and reaching a terminal disposition. This page
also governs **acceptance criteria** (the binary, observable conditions that
decide whether a task, phase, or change is done), because an acceptance criterion
is an evidence-bound predicate of the same shape as an audit finding.

This page is a scanned surface, not rule text. For the wording of any governed
prose rule named below, open its cited `corpus_ref` module.

## When this page applies

- **Predicate:** a review produces findings a reader will act on, or a task
  declares the observable conditions under which it is complete. Both must be
  mechanically checkable to prevent overclaim: a status asserted without evidence.

## Repository public-document review method

Runtime public-document writing semantics live in the direct
`references/public-documentation.md` route. A repository acceptance review can
separately inspect public-owner placement, current authority, generated or
rendered consumer meaning, and material limitations. This is development
methodology, not a second semantic owner or a deterministic documentation
validator.

## Governing STOW families

- **Accuracy and integrity (band 5, always on).** Every finding cites evidence
  (a file-and-line locator, a hash, or command output) and adds no fabricated
  specificity (`SKILL.md` section 3). Facts and recommendations stay separate
  records, never merged.
- **Literals (band 4).** Paths and line numbers in a locator are byte-exact.
- **Presentation (band 8).** The verdict comes first and detail follows on demand
  (see corpus/action-shaping.md#STOW-ACT-001), and an outcome is surfaced, not
  buried, per corpus/action-shaping.md#STOW-ACT-007.
- **Safety (band 1, system precedence).** A risk-bearing finding carries a
  risk-level label and a stated consequence, per corpus/safety.md#STOW-SAF-001.

## Governing schema + template

- **Schema.** `schemas/evidence-record.schema.json`. Required fields include
  `record_id`, `kind` (`fact | recommendation | finding`), `statement`,
  `locators[]` (each a `{type, value}`), `severity`
  (`info | low | medium | high | blocker`), `disposition` (a terminal value such
  as `fixed`, `already-covered`, `rejected-with-evidence`, `owner-decision`,
  `blocked`, or `deferred`), and `verified`. A finding also requires a
  `failure_scenario`.
- **Template.** `templates/AUDIT.md`: a valid instance separating facts from
  recommendations, each finding with locators, severity, and a terminal
  disposition.

## Validation contract

Validate against the schema:

```
python skills/stow/runtime/validate.py --schema evidence-record <file>
```

The load-bearing rules: a `fact` requires at least one resolvable locator; every
`disposition` is in the terminal set; a `finding` with `verified == true` carries
a non-empty `failure_scenario`; an acceptance criterion is a single observable
predicate with a named `method` and an `expected` result, never compound.
**Cold-reader gate:** a reader can resolve every locator and reach the disposition
from the record alone.
