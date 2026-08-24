---
name: sow-pws-builder
description: >
  Trigger for: writing, revising, converting, or descoping a federal Statement
  of Work, Performance Work Statement, SOW, PWS, or SOO;
  develop executable requirements; define contract scope; create measurable
  performance standards; or prepare requirements before an IGCE. Produce a
  contract-file-ready .docx plus separate chat-only staffing and Section B
  handoffs. Never place FTEs, SOC codes, staffing estimates, IGCE content,
  CLINs, or pricing schedules inside the SOW/PWS body. Do NOT use for the IGCE,
  market research report, acquisition plan, QASP, or clause-selection matrix.
---

# SOW/PWS Builder

## Overview

Turn program-office scope decisions into a contract-file-ready `.docx` SOW or PWS. Produce three separate outputs:

1. The SOW/PWS `.docx`, containing requirements and measurable acceptance or surveillance content.
2. A chat-only staffing handoff for the FFP, LH/T&M, or CR pricing skill.
3. A chat-only Section B handoff with suggested CLIN structure, labor categories or estimated hours when needed, travel/ODC lines, and the total ceiling-price input for T&M/LH.

Never combine the handoffs with the document. FAR 37.602(b)(1) directs agencies, to the maximum extent practicable, to describe performance work by required results rather than method or hours. FAR 16.601 requires fixed hourly rates by labor category for T&M/LH and an overall ceiling price, but it does not require a labor-category ceiling-hours table inside the PWS. Keep pricing structure in Section B unless the user supplies a controlling solicitation template that places it elsewhere.

No external MCP server is required.

Load supporting files only when needed:

- [question-blocks.md](references/question-blocks.md) for intake and scope questions.
- [document-specification.md](references/document-specification.md) before authoring the `.docx`.
- [regulatory-and-content-rules.md](references/regulatory-and-content-rules.md) for contract-type, security, QASP, and language rules.
- [handoff-specification.md](references/handoff-specification.md) before final chat output.
- [runtime-adaptation.md](references/runtime-adaptation.md) for questions, document tools, TOC handling, and delivery.
- [validation-gates.md](references/validation-gates.md) before delivery.

## Permanent correctness gates

1. **Separation:** The `.docx` contains no staffing handoff, FTE estimate, SOC code, IGCE content, CLIN table, pricing schedule, or skill-chain message. The two handoffs exist only in chat.
2. **No false FAR exception:** Do not cite FAR 37.102(d) as an hours prohibition. Use FAR 37.602(b)(1) for results-oriented PWS language.
3. **T&M/LH structure:** FAR 16.601(c)(2) requires fixed hourly rates by labor category, and FAR 16.601(d)(2) requires an overall ceiling price. Put the pricing schedule and ceiling in the Section B handoff, not the SOW/PWS body.
4. **Contract-type boundary:** Explain how a user-selected type changes the document, but do not originate the FAR Part 16 decision, T&M/LH Determination and Findings, commercial-item determination, or CPFF form selection.
5. **CPFF form:** Require the user to confirm Completion or Term under FAR 16.306(d). Do not default either form. Reflect the confirmed form in the document framework.
6. **Result-oriented PWS:** Organize a PWS around outcomes, measurable standards, AQLs, and assessment methods. Avoid prescribing staffing or contractor method unless a constraint is genuinely Government-controlled.
7. **QASP and CPARS:** QASP payment or administrative consequences must not pre-commit CPARS ratings. Never map an AQL threshold to `Satisfactory`, `Very Good`, `Exceptional`, `Marginal`, or `Unsatisfactory` CPARS ratings.
8. **Key personnel:** Name roles and qualifications only. Do not quantify staff. Never cite FAR 52.237-2 as a key-personnel substitution clause.
9. **Coverage derivation:** For the chat-only staffing handoff, derive coverage as annual coverage hours divided by productive hours. At 1,880 hours, one 24x7x365 seat is 4.6596 FTE, not three and not 4.2.
10. **Tier 1 mapping:** Preserve the project decision that Tier 1 help desk or contact-center agents map to SOC 43-4051. Do not change it during modernization.
11. **Decision gates:** Do not self-approve staffing or the Phase 2 Decision Summary. End each gate response at its confirmation question and wait.
12. **DOCX validation:** Use real heading styles, render every page to images, inspect every page, audit text and OOXML, and do not claim Word compatibility from a fallback renderer alone.

## Workflow selection

### Workflow A: full build

Use for a concept, rough requirements, or a build from scratch. Run intake and all phases.

### Workflow B: SOO conversion

Extract settled objectives, constraints, location, period, systems, volumes, security, and other facts from the SOO. Present the gaps that must be decided, then run the remaining phases without re-asking settled facts.

### Workflow C: scope reduction

Use an existing SOW/PWS and, when available, IGCE cost drivers to present capability and coverage tradeoffs. The user selects reductions. Revise affected requirements and handoffs without placing staff counts in the document.

## Runtime pre-flight

After workflow selection:

1. Confirm the host can read inputs and create `.docx` files.
2. Confirm a DOCX render path is available, preferably LibreOffice through the host's document workflow.
3. Confirm Python and `python-docx` or an equivalent OOXML authoring capability for `scripts/validate_docx.py`.
4. Match capabilities semantically. Do not depend on `/mnt` paths, a named client tool, or a generated namespace.
5. If document authoring is unavailable, stop and report the missing capability. Do not silently substitute Markdown or HTML for the contract-file deliverable.

## Acquisition strategy intake

Collect framing decisions in one pass, skipping facts already supplied:

1. SOW or PWS.
2. User-confirmed contract type: FFP, T&M, LH, CR subtype, or hybrid by CLIN.
3. Commercial, noncommercial, or pending Contracting Officer determination.
4. Agency and solicitation format, if one controls.
5. Purpose, audience, acquisition stage, and desired file name.

If the user is unsure about SOW versus PWS, explain that PWS is outcome-oriented and preferred for performance-based services to the maximum extent practicable. A recommendation about document form is permitted. Do not turn it into the contract-type or commerciality decision.

If T&M or LH is selected, flag the D&F and overall ceiling-price requirement for Contracting Officer action. If CPFF is selected, require Completion or Term. If commerciality is unsettled, record `[DEFAULT: Commerciality determination pending]` in Constraints and Assumptions rather than deciding it.

## Phase 0: SOO or source intake

For a supplied source document:

1. Extract background, purpose, objectives, performance constraints, location, period, systems, volumes, security, Government-furnished resources, and named standards.
2. Distinguish explicit facts from derived assumptions.
3. Present gaps as the questions needed for executable requirements.
4. Carry settled facts forward without asking them again.

If the source is too thin to support task or objective decomposition, state that it can serve as background but additional scope decisions are required.

## Phase 1: scope decision tree

Use [question-blocks.md](references/question-blocks.md). Prefer structured choices when the host supports them; otherwise use numbered choices with a free-text escape. Batch three to four related questions. Ask open text only for values such as system names, volume, or incumbent facts.

Sequence:

1. Mission and service model.
2. Technical scope.
3. Scale and volume.
4. Organizational scope and phasing.
5. Period, transition, and Section B preferences.
6. Quality, oversight, security, and Government-furnished resources.

### Staffing derivation for the internal handoff

Derive a candidate staffing table only after scope decisions. Every row must cite a basis: workload, coverage hours, system/module count, site count, delivery cadence, or an explicit user override. Heuristics are starting points, not facts.

- Continuous coverage: covered seats times annual coverage hours divided by productive hours per FTE.
- Development: derive by system/module count and team design; do not use an unexplained fixed ratio.
- Contact center: annual contacts divided by workdays and contacts per agent-day, adjusted for service level and productive hours.
- Transition and surge: separate time-limited rows.
- O&M: derive from named workload, SLA, or environment size; never assume a fixed percentage of development staffing without user confirmation.

Present the candidate staffing table in chat and ask the user to confirm, amend, or override it. End immediately after that question and wait. Preserve override reasons.

## Phase 2: Decision Summary gate

After staffing approval and before authoring, present a concise Decision Summary containing:

- SOW/PWS, contract type and subtype, CPFF form when relevant, and commerciality status.
- Agency/template and solicitation-stage context.
- All defaults or derived assumptions with one-line rationale.
- Section 3 task areas for a SOW or performance objectives for a PWS.
- Applicable deliverables, QASP or inspection approach, security, period, location, and transition.
- Confirmation that staffing, SOCs, CLINs, and pricing will remain outside the document.

The final sentence must ask the user to proceed or correct the summary. Stop immediately after the question. Do not author the `.docx` in the same response.

## Phase 2: document assembly

After explicit approval:

1. Read [document-specification.md](references/document-specification.md) and [regulatory-and-content-rules.md](references/regulatory-and-content-rules.md).
2. Use the host's document-authoring workflow and a formal business-document design system. Preserve a supplied agency template when one exists.
3. Use real `Heading 1`, `Heading 2`, and `Heading 3` styles, real numbered or bulleted lists, explicit table geometry, page numbers, and accessible repeating table headers.
4. For more than eight main sections, include a dynamic TOC field. Set the document to update fields on open. If Word is available, update and save the field before delivery. Otherwise disclose the exact refresh step in chat. Do not put the refresh instruction inside the document.
5. Run the render, text, structure, and separation gates in [validation-gates.md](references/validation-gates.md).
6. Fix defects and repeat rendering until every page passes.

Do not generate a second DOCX for either handoff.

## Phase 3: final validation and handoff

Before delivery:

1. Confirm every requirement maps to a deliverable or measurable standard.
2. Confirm every deliverable has format, trigger or due date, and acceptance criteria.
3. Confirm document type, contract framework, security, location, period, and transition are consistent.
4. Confirm QASP consequences contain no CPARS rating commitments.
5. Confirm the document contains no staffing, SOC, IGCE, CLIN, pricing, or skill-chain leakage.
6. Run `scripts/validate_docx.py <document> --document-type <sow|pws>`.
7. Render and inspect every page.

Deliver the `.docx`, then present both chat-only handoffs using [handoff-specification.md](references/handoff-specification.md). The pricing skill consumes the approved staffing table without repeating decomposition. The final message must state that the SOW/PWS is the contract-file artifact and the handoffs are internal workpapers outside it.

When a dynamic TOC has not been updated in Word, end with: `Open the document in Word, press Ctrl+A (Cmd+A on Mac), then F9 to populate or refresh the Table of Contents, and save.`

## Out of scope

- IGCE rates, wraps, fee, or cost calculations.
- Acquisition plan, market research report, source-selection plan, J&A, or clause matrix.
- Final contract-type, commerciality, D&F, or inherently-governmental determination.
- Full standalone QASP beyond the embedded summary.
- Section I or L clause selection.

---

*MIT © James Jenrette / 1102tools. Source: github.com/1102tools-dev/federal-contracting-skills*
