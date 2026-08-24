# OT Project Description Validation Gates

## Before generation

- The user confirmed 4021 research, 4022 prototype, or 4022(f) follow-on production.
- A prototype has a user-confirmed 4022(d)(1) path or is visibly `PENDING`.
- No participant status, significant participation, contribution ratio, fee, successful completion, or follow-on eligibility was inferred.
- The user approved the milestone table and each derived assumption.
- Payment Type is supplied or `PENDING`.
- Each milestone has deliverables and objective completion evidence.
- TRL is used only when supported.
- Data-rights treatment is supplied by deliverable category or marked pending.

## Artifact structure

- Required sections appear in the specified relative order.
- Real heading styles and a dynamic TOC are used when required.
- The Milestone Schedule contains every approved milestone ID.
- Every phase-exit criterion appears in the related milestone completion criteria.
- The Deliverables table maps each artifact to a due trigger and acceptance criterion.
- Each `[TBD]` has an owner and closeout trigger in Constraints and Assumptions.
- Tables have explicit geometry, repeating headers, adequate padding, and no clipped rows.

## Separation and legal accuracy

- No milestone handoff, skill name, prompt, internal path, or routing message appears in the `.docx`.
- No price, cost estimate, labor rate, fee, funding profile, Government budget, or price-reasonableness conclusion appears in the `.docx`.
- Research is cited to 4021, prototypes to 4022, and follow-on production to 4022(f).
- Path D is not described as a competition commitment.
- The document does not make a status, significance, authority, completion, or follow-on determination.
- Follow-on provisions do not promise award or import 4022(d) into the follow-on action.
- FAR or DFARS clauses are not presented as controlling unless incorporated by the agreement.

## Deterministic and visual checks

1. Run `scripts/validate_docx.py <document> --json`.
2. Render the document with a real office engine.
3. Inspect every page at readable zoom.
4. Fix and rerun both checks after any defect.
5. Verify that the delivered file is the validated file.

## Chat-only handoff

- The table exactly identifies itself for OT Cost Analysis.
- It contains all approved milestones, durations, deliverables, completion evidence, timing, payment type, and pending decisions.
- Authority and contribution facts are presented as supplied inputs with provenance.
- It contains no invented price, rate, fee, contribution arithmetic, or determination.
