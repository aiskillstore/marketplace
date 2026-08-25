---
name: ot-cost-analysis
description: >
  Trigger for: Other Transaction or OT should-cost,
  cost estimate, cost-share analysis, milestone pricing, funding profile,
  proposed-price comparison, prototype price analysis, research OT budget,
  production follow-on OT estimate, or OT price-reasonableness support under
  10 U.S.C. 4021 or 4022. Build auditable milestone-based .xlsx workbooks using
  BLS OEWS wages, CALC+ positioning, GSA Per Diem, materials, cost sharing, and
  agreement-specific fees. Use for pre-solicitation budgets and proposal
  comparisons. Do NOT use for FAR-based IGCEs, OT project descriptions, grants,
  or an Agreements Officer's determination. Requires the bls-oews, gsa-calc,
  and, when travel applies, gsa-perdiem MCP servers.
---

# OT Cost Analysis

## Purpose and operating boundary

Build an auditable, formula-driven cost analysis organized by OT milestone. Separate total project cost, the non-Federal contribution, any consortium or administrative fee, the proposed payment amount, and the Government funding requirement. Use market evidence and arithmetic to support the Agreements Officer without originating the authority path, eligibility finding, significant-participation finding, successful-completion finding, or price-reasonableness determination.

Do not:

- Decide whether 10 U.S.C. 4021, 4022, or 4022(f) applies.
- Decide whether a participant is a nontraditional defense contractor, nonprofit research institution, small business, or significant participant.
- Invent a cost-share ratio, exceptional-circumstances determination, consortium fee, learning curve, indirect-rate structure, or proposed-price basis.
- State that a proposed amount is fair, reasonable, acceptable, competitive, aggressive, premium, or justified.
- Treat a BLS or CALC+ benchmark as the performer's required rate.
- Call the output a FAR 15.404 analysis or an IGCE.

When a sentence would conclude the Agreements Officer's judgment, replace it with the source data, the variance, the scenario range, and the decision left open.

## Reference map

Load only the references needed for the active workflow:

- [authority-and-cost-sharing.md](references/authority-and-cost-sharing.md) before classifying or applying a cost share.
- [labor-and-costing-methods.md](references/labor-and-costing-methods.md) before deriving labor, materials, scenarios, ceilings, fees, or funding timing.
- [data-source-operations.md](references/data-source-operations.md) before mapping SOCs or calling BLS, CALC+, or Per Diem operations.
- [workbook-specification.md](references/workbook-specification.md) in full before generating the workbook.
- [validation-gates.md](references/validation-gates.md) before building and again before delivery.
- [runtime-adaptation.md](references/runtime-adaptation.md) when collecting structured answers, locating tools, selecting a calculation engine, or delivering files.

## Non-negotiable gates

1. **Authority is supplied, not inferred:** Require the user or Agreements Officer to identify Research OT under 10 U.S.C. 4021, Prototype OT under 10 U.S.C. 4022, or follow-on production under 10 U.S.C. 4022(f). Explain differences but do not choose.
2. **Correct 4022(d) paths:** Path A is significant participation by at least one nontraditional defense contractor or nonprofit research institution. Path B requires all significant non-Government participants to be small businesses or nontraditional defense contractors. Path C requires at least one-third of total project cost from non-Federal sources. Path D is a senior procurement executive's written exceptional-circumstances determination. There is no 4022(d)(1)(D) "competition commitment" path.
3. **Research OT contribution:** For 10 U.S.C. 4021, record that Government funds should, to the extent the Secretary determines practicable, not exceed the total provided by other parties. Do not translate that into an automatic 50/50 rule or automatic 100% Government funding. Require the approved arrangement.
4. **Production follow-on contribution:** Section 4022(d) does not apply to a follow-on under 4022(f). Do not automatically carry the prototype ratio, and do not automatically set Government funding to 100%. Require the negotiated production arrangement.
5. **Proposed-amount basis:** Before comparing numbers, confirm whether each proposed amount represents total project cost, the requested Government payment, a milestone payment, or a cost-type ceiling. Never compare unlike bases.
6. **Cost-share denominator:** Apply a performer ratio to total project cost. For Path C, the non-Federal share must be at least one-third of total project cost. Keep Government share plus performer share equal to the same total project-cost basis before separately treated fees.
7. **Fee basis:** Use a consortium or administrative fee only when the user supplies its rate or fixed amount, base, timing, and cost-share treatment. Default to zero, not five percent.
8. **CALC+ signature:** Use `/v3/api/ceilingrates/` with `keyword=` when keyword search is required. Never use `q=`. Preserve `aggregations.labor_category.buckets[*].key` and `doc_count` when discovery is used.
9. **BLS vintage and aging:** Call `detect_latest_year` at runtime. Store BLS vintage and agreement start as `YYYY-MM`; use `VALUE(LEFT(...))` and `VALUE(MID(...))` for month gap. Never trust a stale constant, use `YEAR()` on text, or substitute `DATEDIF`.
10. **Formula-driven workbook:** User-adjustable assumptions remain inputs. Calculated labor, escalation, ceilings, cost shares, fees, variances, scenarios, and cumulative funding remain formulas that reference those inputs.
11. **Cost-type branch:** Show both independent should-cost and the user-approved ceiling basis. Government maximum exposure and planned performer contribution at ceiling must use the same ceiling basis. Do not represent either as actual incurred cost.
12. **Independent validation:** Run formula structure, independent Python recomputation, and real-engine verification when available. Openpyxl does not calculate formulas.
13. **AI boundary:** Workflow B returns neutral comparison data unless the user supplies the exact determination text for a controlled memo fill. Never originate the conclusion.
14. **Staged approval:** A derived milestone or staffing model must end at its confirmation question and wait. Do not self-approve or begin data calls while approval is pending.
15. **Credentialed API pacing:** Serialize keyed federal API calls and leave at least three seconds between calls. Honor longer server retry instructions and stop rather than rapidly retrying a rate limit.

## Pre-flight: capabilities and dependencies

Select the workflow, then inspect the current session by capability rather than by host-generated tool name.

1. For a build, require `bls-oews` operations `detect_latest_year`, `get_wage_data`, metro lookup, and SOC lookup plus `gsa-calc` operations `suggest_contains`, `exact_search`, `keyword_search`, and `igce_benchmark` or equivalent schemas.
2. Require `gsa-perdiem` operations `estimate_travel_cost`, `lookup_city_perdiem`, and `get_mie_breakdown` only when travel is in scope.
3. Require an `.xlsx` authoring path and Python 3.10 or later with openpyxl for the bundled validators. Prefer a real spreadsheet engine for formula execution.
4. For a build, test `detect_latest_year` before wage retrieval. Test Per Diem only when travel first becomes necessary. Apply the three-second keyed-call spacing to tests and production calls.
5. If an operation is unavailable, inspect the same server for a semantically equivalent operation. Do not silently replace an MCP with an ad hoc public API request.
6. Stop and report missing or unauthenticated capabilities before beginning dependent work. Do not expose credentials.

## Select a workflow

### Workflow A: build from approved milestones

Use when the user supplies a milestone table or the approved handoff from `ot-project-description-builder`. Preserve milestone IDs, descriptions, deliverables, success criteria, dates, payment type, and user overrides. Ask only for missing cost inputs.

### Workflow A+: build from a concept

Use when no approved milestone table exists. Derive a candidate milestone structure from the prototype or research objective, TRL progression when relevant, delivery evidence, and schedule. Present the table, ask the user to confirm or amend it, end at that question, and wait. Do not call pricing MCPs before approval.

### Workflow B: proposed-amount comparison

On the first response, make no tool call. Emit this boundary and stop:

> I can build an independent OT should-cost and show the proposed amount's basis, variance, scenario position, and market benchmarks. I cannot originate the Agreements Officer's price-reasonableness determination or negotiation position.
>
> Choose one:
>
> **Option A: Comparison data only.** I produce neutral tables and a methodology record with no verdict.
>
> **Option B: Controlled memo fill.** You provide the exact rationale and determination text. I reproduce it verbatim in a DRAFT section and place the neutral evidence beneath it.
>
> Which option?

For Option B, proceed only after the user supplies both the rationale and determination text. Never expand or strengthen it.

## Collect and confirm inputs

Use the host's structured question tool when available. Otherwise use numbered choices and accept numbers, labels, or free text. Batch related missing inputs.

Required before cost-share math:

- Authority: 4021 research, 4022 prototype, or 4022(f) follow-on production
- For 4022 prototype, user-confirmed subsection (d) path A, B, C, or D
- Approved performer contribution ratio, cash/in-kind composition, and source
- Performer structure, locations, and Agreements Officer-confirmed status facts
- Proposed-amount basis when a proposal exists
- Consortium or administrative fee facts, or explicit zero

Required before a build:

- Approved milestones with duration, success evidence, payment type, and timing
- Labor categories, staffing or hours, performance location, and start month
- Materials, travel, ODC, and escalation bases
- Productive hours, burden basis, and payment/funding convention
- For cost-type milestones, the approved ceiling or ceiling-margin assumption

Do not guess the authority, statutory path, cost share, location, milestone payment type, fee, proposed-amount basis, or cost-type ceiling.

### Consume an approved OT project handoff

Treat a table labeled `MILESTONE HANDOFF TABLE` and identified for OT Cost Analysis as user-reviewed input.

1. Preserve every milestone field, derivation, pending decision, and override.
2. Do not repeat milestone decomposition.
3. Reconcile contradictions between the handoff and current instruction in a short table and wait for the user to choose.
4. Ask the remaining cost inputs in one stage and end at its question.

## Orchestration

### Step 0: derive milestones only when required

For Workflow A+:

1. Hard stop if the project objective is absent.
2. Identify expected evidence of completion, schedule, technical progression, Government decisions, and performance location.
3. Use TRL only when the project actually uses TRL. Do not force research, software, business-process, or service prototypes into an unsupported TRL ladder.
4. Propose milestone ID, objective, duration, entry conditions, completion evidence, payment type marked `PENDING` unless supplied, and funding timing.
5. Ask the user to confirm or amend the milestone structure. End immediately after the question and wait.

### Step 1: validate authority and economics

Read [authority-and-cost-sharing.md](references/authority-and-cost-sharing.md).

1. Restate the user-supplied authority and path without converting facts into a legal determination.
2. Validate the cost-share arithmetic and source. For 4022 Path C, reject a non-Federal ratio below one-third.
3. Record whether each contribution is cash or in kind and how it will be valued and tracked.
4. Confirm proposed-amount basis and fee treatment.
5. For 4022(f), record the predecessor prototype and user-supplied competitive-selection and successful-completion facts, but do not make the follow-on eligibility finding.

### Step 2: benchmark labor

Read [data-source-operations.md](references/data-source-operations.md) and [labor-and-costing-methods.md](references/labor-and-costing-methods.md).

1. Map each labor category to the best-supported SOC and record proxies.
2. Call `detect_latest_year`, then retrieve metro, state, or national BLS percentiles using the documented fallback ladder.
3. Age the selected direct wage to the agreement start through assumption cells.
4. Apply the user-approved burden method. It is a scenario benchmark, not an audit-approved indirect rate.
5. For institutions with supplied billing rates or approved indirect structures, preserve those rates and label the source. Do not invent academic billing ranges.
6. Keep each performer and location separate. Do not average unlike MSAs or organizations without an approved allocation.

### Step 3: obtain CALC+ positioning

Use the discovery-first operation flow. Keep title-match and experience-match pools separate when useful. Record the pool, count, percentiles, and query date. Sparse or absent results remain a disclosed limitation; they do not authorize an invented specialty premium.

### Step 4: price materials, travel, and ODCs

Use user-supplied bills of material, quotes, analogous prices, quantities, and escalation bases. Apply materials escalation from project start to each milestone start using month-based compounding. A production learning curve is used only when the user supplies the method and factor.

Use GSA Per Diem for authorized CONUS travel and the operation rules in the data-source reference. Keep airfare, local transportation, and OCONUS travel on their supplied source bases.

### Step 5: build milestone should-cost

For each milestone:

```text
labor              = sum(category hours * category burdened benchmark)
materials          = sum(quantity * unit cost * approved escalation)
travel             = sum(validated trip costs)
ODCs               = sum(other direct cost inputs)
total project cost = labor + materials + travel + ODCs
performer share    = total project cost * approved performer ratio
Government share   = total project cost - performer share
fee                = approved fee base * approved fee rate, or approved fixed amount
Government funding requirement = Government share + Government-paid fee
```

For cost-type milestones, calculate the same columns at independent should-cost and at the approved ceiling. Label the ceiling view as maximum exposure, not expected actual cost.

Present the per-milestone build and ask for confirmation before final workbook assembly when staffing, materials, or cost allocation was derived rather than supplied.

### Step 6: scenario analysis

Vary only assumptions with a documented basis. Keep low, working, and high labor burden, materials, and escalation inputs in workbook cells. Do not ship generic 1.8/2.0/2.2 or materials multipliers as facts unless the user approves them for this analysis.

### Step 7: build the workbook

Read [workbook-specification.md](references/workbook-specification.md) in full. Build the seven required sheets and preserve:

- Blank proposed-amount cells when no proposal exists, with conditional variance formulas.
- Formula-driven labor, escalation, ceiling, share, fee, scenario, and cumulative-funding cells.
- Separate performer and Government contributions that reconcile to total project cost.
- Cost-type should-cost and ceiling views using the same contribution basis.
- Compact, reproducible raw-data records rather than full API payloads.
- Neutral methodology language and user-supplied Option B text verbatim when applicable.

### Step 7.5: validate before delivery

Read [validation-gates.md](references/validation-gates.md).

1. Run `scripts/validate_workbook.py <workbook> --expected <inputs.json> --engine none`.
2. Run `scripts/recompute_expected_values.py <inputs.json>`.
3. If LibreOffice is available, rerun the validator with `--engine auto` or `--engine libreoffice`; require the engine layer to reject cached spreadsheet errors anywhere in the recalculated workbook before mapped values are accepted.
4. Inspect every worksheet for formulas, units, source notes, input formatting, broken references, and leaked internal instructions.
5. Verify the workbook as a ZIP and, when practical, open or render it in a real spreadsheet application.
6. Fix failures and repeat all layers.

If no spreadsheet engine is available, state exactly:

> Formula structure and independent calculations passed. Formula execution was not independently verified in Excel or LibreOffice.

### Step 8: deliver

State which validation layers ran. Summarize the authority and contribution facts as user-supplied inputs, the should-cost range, the Government funding range, key sensitivities, missing evidence, and refresh dates. Do not state a price-reasonableness conclusion unless it is the user's verbatim Option B text, visibly marked DRAFT.

## Out of scope

- FAR-based IGCEs and FAR 15.404 determinations
- Authority, eligibility, significant-participation, exceptional-circumstances, or successful-completion findings
- Certified cost or pricing data demands
- Unsupported indirect-rate, profit, fee, learning-curve, or specialty-premium assumptions
- Grants, cooperative agreements, and OT project descriptions
- OCONUS per diem without a supplied State Department or other approved source

---

*MIT © James Jenrette / 1102tools. Source: github.com/1102tools-dev/federal-contracting-skills*
