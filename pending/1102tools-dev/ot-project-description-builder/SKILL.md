---
name: ot-project-description-builder
description: >
  Trigger for: OT project description, OTA scope, Research OT under 10 U.S.C.
  4021, Prototype OT under 10 U.S.C. 4022, follow-on production scope under
  10 U.S.C. 4022(f), milestone-based project scope, prototype objective,
  phase or go/no-go structure, BAA white-paper conversion, SOO conversion,
  transition planning, or scope reduction before OT cost analysis. Produce a
  milestone-based .docx plus a separate chat-only handoff to OT Cost Analysis.
  Use TRL only when the project supports it. Never place cost estimates,
  funding profiles, contribution calculations, prices, or skill-routing
  content in the document. Do NOT use for a FAR SOW/PWS, OT cost analysis,
  IGCE, agreement terms and conditions, or an Agreements Officer's authority,
  participant-status, successful-completion, or follow-on determination.
---

# OT Project Description Builder

## Purpose and operating boundary

Create a milestone-based `.docx` project description for a Research OT under 10 U.S.C. 4021, Prototype OT under 10 U.S.C. 4022, or a follow-on production action under 10 U.S.C. 4022(f). Define the technical outcome, phase logic, deliverables, completion evidence, Government responsibilities, and agreement-specific controls without making the Agreements Officer's authority, participant-status, successful-completion, or follow-on-eligibility determination.

Produce two separate outputs:

1. One project-description `.docx` suitable for the agreement file. It contains no cost estimate, should-cost, labor rate, milestone amount, funding profile, Government budget, or pricing conclusion.
2. One `MILESTONE HANDOFF TABLE` in chat after document validation. It is an internal workpaper for OT Cost Analysis and never a document section, appendix, or companion file.

No external API is required.

## Reference map

Load only what the active workflow needs:

- [authority-and-scope-rules.md](references/authority-and-scope-rules.md) before stating authority, participant status, contribution treatment, prototype scope, or follow-on provisions.
- [question-blocks.md](references/question-blocks.md) when collecting or confirming inputs.
- [document-specification.md](references/document-specification.md) in full before building the `.docx`.
- [handoff-specification.md](references/handoff-specification.md) before presenting the chat-only milestone handoff.
- [validation-gates.md](references/validation-gates.md) before generation and again before delivery.
- [runtime-adaptation.md](references/runtime-adaptation.md) when selecting input, document-generation, rendering, validation, or delivery capabilities.

## Non-negotiable gates

1. **Correct authority:** 10 U.S.C. 4021 covers basic, applied, and advanced research. 10 U.S.C. 4022 covers prototype projects. Section 4022(f) covers follow-on production contracts or transactions. Never label a prototype as a 4021 action.
2. **Authority is supplied, not selected:** Explain the three paths when needed, but require the user or Agreements Officer to identify the authority. Do not default an uncertain request to Prototype OT.
3. **Correct prototype conditions:** Under 4022(d)(1), Path A is significant participation by a nontraditional defense contractor or nonprofit research institution; Path B covers all significant non-Government participants being small businesses or nontraditional defense contractors; Path C requires at least one-third of total project cost from non-Federal sources; Path D is a senior procurement executive's written exceptional-circumstances determination. There is no Path D competition-commitment option.
4. **Status and contribution facts are not inferred:** Do not decide nontraditional status, small-business status, significant participation, the applicable 4022(d) path, contribution ratio, contribution valuation, or fee. Record the user's approved facts and source. Research and follow-on production contribution arrangements are also supplied, not defaulted.
5. **TRL is optional:** Use TRL only when supplied or genuinely useful. A prototype can address a proof of concept, model, process, agile development, novel commercial application, operational utility, or a combination. Do not force every project through a hardware-style TRL ladder.
6. **Milestones precede prose:** Present the derived phase and milestone structure, including completion evidence and pending decisions, then end at the approval question. Do not generate the `.docx` in the same response.
7. **Artifact separation:** Keep pricing, labor hours, contribution arithmetic, cost figures, funding, and skill-routing language out of the document. Keep the milestone handoff in chat only.
8. **Data rights are negotiated:** Record the supplied posture by deliverable and distinguish background from agreement-generated material. Do not state that FAR or DFARS clauses control unless the agreement incorporates them.
9. **Follow-on language stays conditional:** Record user-supplied predecessor, competitive-selection, and successful-completion facts without deciding eligibility. Do not promise award or say 4022(d) is a follow-on requirement.
10. **Every placeholder closes:** Each `[TBD]` must name an owner, trigger, and disposition method in Constraints and Assumptions.
11. **Independent document validation:** Run the bundled validator, render the document, inspect every page, fix defects, and repeat. Do not treat DOCX creation alone as proof of usability.

## Pre-flight: capabilities and inputs

1. Inspect attached source documents with the host's native document or PDF reader. Preserve explicit decisions and identify contradictions instead of silently resolving them.
2. Require a `.docx` authoring path, Python 3.10 or later with `python-docx` for the bundled validator, and a rendering path such as LibreOffice when available.
3. Use an agency or consortium template when supplied. Otherwise use the formal document baseline in the document specification.
4. Confirm that a source document's prices, rates, CLINs, budgets, and funding values will be excluded. Record only that excluded pricing data exists; the user can provide it separately to OT Cost Analysis with a confirmed amount basis.
5. If document generation or rendering is unavailable, stop before promising a validated artifact and report the missing capability.

## Select a workflow

### Workflow A: build from a concept

Use when the user supplies an objective, problem, requirement, or early concept but no approved milestone structure.

### Workflow B: convert an existing document

Use for a white paper, proposal abstract, SOO, SOW, draft project description, or similar source. Extract settled technical facts; remove FAR clause, CLIN, QASP, staffing, and pricing content from the project-description artifact. Do not re-ask settled questions.

### Workflow C: revise or reduce scope

Use when an existing project description or approved milestone structure must be changed. Preserve unaffected decisions, identify the technical and schedule effect of each proposed deletion or deferral, and obtain approval for the revised milestones before editing the document.

## Stage A: authority and acquisition frame

Read [authority-and-scope-rules.md](references/authority-and-scope-rules.md) and collect only missing items:

- User-confirmed authority: 4021 research, 4022 prototype, or 4022(f) follow-on production
- For a prototype, user-confirmed 4022(d)(1) Path A, B, C, or D and source
- Participant and significant-participation facts as confirmed by the Agreements Officer
- Approved contribution arrangement and source, or `PENDING`
- Direct or consortium structure and any controlling template
- Project purpose, present technical or operational baseline, and source documents
- For follow-on production, predecessor prototype and user-supplied selection and completion facts

Use the host's structured question tool when available. Otherwise use numbered questions and accept numbers, labels, or free text. If authority is uncertain, explain the differences neutrally and end at the authority question. Do not continue to scope derivation.

When required authority items are complete, show a short authority record and ask the user to confirm or correct it. End at that question.

## Stage B: scope and milestone decisions

After Stage A approval, read [question-blocks.md](references/question-blocks.md). Collect missing scope inputs in related batches:

- Outcome and measurable success conditions
- Existing baseline and major risks
- Phase logic, schedule, and external dependencies
- Test, demonstration, or acceptance environment
- Systems, interfaces, prototype units, data, and security boundaries
- Deliverables and objective completion evidence
- Data-rights posture by deliverable category
- Government-furnished property, information, facilities, and personnel
- Key roles, reviews, reporting, off-ramps, and transition intent

Use TRL only when supported. Otherwise describe maturity through observable baseline, target capability, and completion evidence.

Derive a candidate structure with:

`Milestone ID | Phase | Objective | Estimated Duration | Deliverables | Completion Evidence | Timing or Sequence | Payment Type | TRL In/Out | Notes`

Payment Type remains `PENDING` unless supplied. Do not infer Fixed, Cost-Type, or Mixed from milestone wording.

### Decision Summary gate

Present:

1. The confirmed authority record
2. Explicit user decisions
3. Derived assumptions and their rationale
4. Pending items and their owner
5. The full candidate milestone table

Ask the user to confirm, amend, or reject the structure. End immediately after that question. A request to skip questions does not waive this gate unless the user explicitly approves the displayed structure.

## Build the project description

After approval:

1. Read [document-specification.md](references/document-specification.md) and [validation-gates.md](references/validation-gates.md) in full.
2. Apply the supplied template or the formal baseline. Use real Word heading styles, lists, tables, page-number fields, and a dynamic TOC when required.
3. Preserve approved milestone IDs, phase relationships, deliverables, completion evidence, timing, payment-type status, and user overrides.
4. Carry each phase-exit criterion into both the Technical Approach by Phase section and the corresponding Milestone Schedule row.
5. Include a Contribution Arrangement section only when an approved arrangement affects the agreement. State ratios and cash or in-kind treatment without dollar amounts or funding calculations. Label pending facts.
6. Include Production Follow-On Provisions only when the user requests them. State conditions and transition planning without making an eligibility finding or promising an award.
7. Keep the performer responsible for the technical approach unless the Government has intentionally prescribed a method.
8. Save only the project-description `.docx` as the document artifact.

## Validate and deliver

1. Run `scripts/validate_docx.py <document> --json`.
2. Render the `.docx` to page images with the available document renderer.
3. Inspect every page for clipping, overlap, broken tables, blank pages, bad page breaks, unreadable density, missing glyphs, placeholder leakage, and inconsistent hierarchy.
4. Correct every failure, rerun the validator, rerender, and inspect again.
5. State whether LibreOffice or Microsoft Word performed the render. Do not claim Word compatibility from LibreOffice alone.
6. Read [handoff-specification.md](references/handoff-specification.md) and emit the approved milestone handoff in chat. Never save it as a file or add it to the `.docx`.
7. Report unresolved `[TBD]` items, the source and date of authority facts, and any validation layer that could not run.
8. If the document contains a dynamic TOC, tell the user: `Open the document in Word, press Ctrl+A (Cmd+A on Mac), then F9 (or Fn+F9) to update all fields and page numbers.` Do not rely on a right-click-only instruction.

## Out of scope

- OT should-costs, proposed-amount comparisons, funding profiles, and price-reasonableness determinations
- FAR-based SOW, PWS, IGCE, solicitation Section B, CLIN, or QASP artifacts
- Agreements Officer authority, participant-status, significant-participation, successful-completion, or follow-on-eligibility findings
- Legal opinions, agreement terms and conditions, and intellectual-property negotiation
- Unsupported TRL, cost-share, milestone payment type, fee, staffing, schedule, or performance threshold assumptions

---

*MIT © James Jenrette / 1102tools. Source: github.com/1102tools-dev/federal-contracting-skills*
