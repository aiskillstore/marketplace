---
name: igce-builder-lh-tm
description: >
  Trigger for: Labor-Hour IGCE, LH estimate,
  Time-and-Materials IGCE, T&M estimate, burdened hourly rate, burden
  multiplier, labor-category ceiling hours, materials estimate, proposed
  LH/T&M rate validation, price-reasonableness memo, or fair-and-reasonable
  analysis. Build auditable LH/T&M estimates using BLS OEWS wages, explicit
  burden multipliers, GSA CALC+ positioning, GSA Per Diem travel, and
  separately priced T&M materials. Do NOT use for FFP, cost-reimbursement,
  grants, or cooperative agreements. Requires the bls-oews, gsa-calc, and
  gsa-perdiem MCP servers.
---

# IGCE Builder: Labor-Hour and Time-and-Materials

## Overview

Build an auditable Labor-Hour or Time-and-Materials Independent Government Cost Estimate. Both contract types use fixed hourly rates that include wages, overhead, G&A, and profit. T&M also reimburses materials at actual cost, subject to the contract and applicable indirect-cost treatment; LH does not include a materials-reimbursement component.

Regulatory anchors: FAR 15.404-1, FAR 16.600 and 16.601, FAR 31.205-26, and FAR 52.232-7. Apply the current regulation, solicitation, clauses, and agency supplement. This skill does not prepare the Determination and Findings required to use T&M/LH or make legal determinations.

Load supporting files only when needed:

- [wrap-rate-presets.md](references/wrap-rate-presets.md) for burden-multiplier scenarios.
- [data-source-operations.md](references/data-source-operations.md) before mapping labor or calling BLS, CALC+, or Per Diem.
- [workbook-specification.md](references/workbook-specification.md) before creating a workbook.
- [validation-gates.md](references/validation-gates.md) before and after workbook generation.
- [runtime-adaptation.md](references/runtime-adaptation.md) for questions, tools, formula engines, and delivery.

## Operating principle

This skill assembles data and formats analysis. The Contracting Officer owns fair-and-reasonable determinations, contract-type decisions, the T&M/LH Determination and Findings, ceiling price, surveillance approach, negotiation positions, and approval documents.

- Use neutral positional language such as `at CALC+ P77 (n=42)` or `above P50 by 18%`.
- Never originate a determination, negotiation target, evaluation notice, or responsibility conclusion.
- Never invent clearance, SCIF, OCONUS, or specialty-labor premiums.
- Preserve user-supplied rationale and conclusions verbatim and label any resulting document `DRAFT`.

## Permanent correctness gates

1. **Workflow B boundary:** On every Workflow B entry, emit the Option A/Option B boundary before analysis or tool use and wait.
2. **CALC+ signature:** Use `/v3/api/ceilingrates/` with `keyword=`. Never use `q=`; it silently returns the full corpus.
3. **Contract type:** Do not silently default an unspecified requirement to LH or T&M. Explain the structural difference and require the user to choose.
4. **Labor-rate content:** Fixed hourly rates include wages, overhead, G&A, and profit. Apply the burden multiplier to labor only.
5. **Materials basis:** T&M materials include direct materials, certain subcontracts, ODCs such as travel or computer usage, and applicable indirect costs. Price at actual cost subject to FAR 16.601 and 52.232-7. Never add labor burden or an arbitrary material-handling profit percentage.
6. **Material handling:** Include only indirect costs clearly excluded from hourly labor rates and allocated to direct materials under the contractor's usual accounting practices. Treat them as cost, not fee. Use zero unless the user supplies a solicitation or accounting basis.
7. **Ceilings:** Show labor-category ceiling hours and a total ceiling-price input. Do not present the IGCE total as the binding contract ceiling unless the user confirms that decision.
8. **Aging formula:** Store BLS vintage and contract start as `YYYY-MM`. Calculate month gap with `VALUE`, `LEFT`, and `MID`; do not use `YEAR` on text or rely on `DATEDIF` portability.
9. **Shift coverage:** Derive FTE from coverage hours and productive hours. At 1,880 hours, one 24x7x365 seat is 4.6596 FTE. Do not multiply 4.2 by 1,880.
10. **Staged questions:** Stage A is decomposition confirmation only. It must end immediately after that question, with no Stage B preview.
11. **Step 8.5:** Run formula-structure audit, independent recomputation, and real-engine verification when available. Disclose when formula execution was not independently verified.
12. **Credentialed API pacing:** Serialize credentialed federal API calls and leave at least three seconds after one completes before starting the next. Never parallelize keyed calls. Honor longer retry intervals and stop instead of rapid retrying.

## Workflow selection

Select the workflow before capability tests.

### Workflow A-LH: structured Labor-Hour build

Use when the user declares LH and supplies structured labor inputs. Include no reimbursable-materials component.

### Workflow A-TM: structured Time-and-Materials build

Use when the user declares T&M. Build labor and materials as separate cost streams. Travel and computer usage are within the FAR definition of materials for T&M treatment.

### Workflow A+: SOW/PWS build or approved handoff

Use for raw requirements or the approved staffing handoff from `sow-pws-builder`. For raw requirements, run Step 0 and both staged confirmations. For an approved handoff, preserve it and skip decomposition and Stage A.

If the requirement does not specify LH or T&M, do not decide from the presence of materials alone. Explain that LH excludes reimbursable materials while T&M includes them, then ask the user to select the contemplated type.

### Workflow B: rate positioning or memo request

Use when the user asks to validate proposed rates, compare vendor pricing, draft a price-reasonableness memo, or decide whether rates are fair and reasonable.

The entire first response must be exactly this boundary. Add no heading, workflow label, preamble, capability note, analysis, or tool call. End at the question:

> I can provide positioning data showing where proposed rates sit against CALC+ ceiling rates and BLS market wages. I cannot originate a price-reasonableness memo, fair-and-reasonable determination, T&M/LH Determination and Findings, or negotiation position. Those are Contracting Officer decisions.
>
> **Option A: Positioning data only.** I provide per-category CALC+ percentiles and sample size, BLS metro burdened equivalents, and neutral arithmetic. No verdict or recommendation.
>
> **Option B: Draft template using your conclusion.** You provide your rationale and determination. I place that text verbatim into a DRAFT template and add benchmark tables. I do not add conclusions or negotiation advice.
>
> Which option do you choose?

After Option A, run the applicable BLS and CALC+ steps and stop at neutral positioning. After Option B, require both rationale and determination. Never paraphrase the user's conclusion.

## Pre-flight capabilities

Run after workflow selection and, for Workflow B, only after the user chooses an option.

1. Inspect available operations and match by server and schema, not generated namespace.
2. Builds require BLS wage, vintage, SOC, and metro operations plus CALC+ discovery and benchmark operations. Add Per Diem only when travel is in scope.
3. Workflow B requires only the benchmark operations needed for the selected option.
4. Before workbook creation, require `.xlsx` authoring, Python 3.10+, openpyxl, and the bundled validators. A real spreadsheet engine is preferred but optional when absence is disclosed.
5. Test only capabilities the active workflow will use. Confirm BLS vintage for every build. Apply the pacing gate to keyed calls.
6. If an operation is unavailable, look for an equivalent operation from the declared server. Do not bypass the MCP with a hand-built API call.
7. If a capability remains missing, stop and report whether it appears uninstalled, unauthenticated, or unavailable in the host.

## Information to collect

Required:

- Contract type: LH or T&M.
- Labor categories or disciplines, SOC when known, seniority, location, FTE, productive hours, and ceiling hours by category.
- Base and option periods, contract start month, and partial-year duration.
- Burden-multiplier basis or user-supplied fully burdened rates.
- Total ceiling-price input or confirmation that the workbook total is only an estimate.
- For T&M, each materials category, cost basis, escalation, and applicable indirect material-handling basis.

Optional with disclosed defaults:

- Productive hours 1,880; escalation 2.5%; burden scenarios 1.8x, 2.0x, and 2.2x.
- No travel and no T&M materials. Use numeric zero and state that each was considered.
- No material-handling indirect cost unless supported by user-supplied accounting or solicitation terms.

User-supplied productive hours control. If total hours and FTE are supplied without productive hours, back-solve `total hours / FTE` and flag deviations above 5% from the 1,880 default. Never hardcode 1,880 into annual formulas when the assumption cell exists.

## Approved SOW/PWS handoff

Treat a user-reviewed `STAFFING HANDOFF TABLE` as approved input regardless of heading punctuation.

1. Consume only LH/T&M CLINs. Route FFP and CR CLINs to their skills.
2. Preserve labor category, SOC, FTE, phase, hours, notes, derivation, and overrides.
3. Use the CLIN handoff for period mapping.
4. Present contradictions in a short table and wait for the user to identify the controlling value.
5. Ask all missing Stage B fields in one response. Do not rerun decomposition or Stage A unless the user asks to revise staffing.

## Orchestration

### Step 0: decompose raw requirements

1. Check labor disciplines, staffing basis, location, period, deliverables, travel, and non-labor costs. Performance location is a hard stop before wage calls.
2. Separate tasks by discipline, complexity, cadence, deliverable, and staffing basis.
3. Perform domain triage before SOC mapping.
4. Map candidate categories and SOCs using [data-source-operations.md](references/data-source-operations.md).
5. Estimate FTE ranges only when the requirement supplies a defensible sizing basis. Otherwise list the missing facts.
6. **Stage A:** Ask only whether the user confirms or amends the task areas, labor categories, and SOC mappings. This must be the only question. Do not ask for contract type, location, burden, materials, ceiling, or other Stage B data. End immediately after the confirmation question.
7. **Stage B:** After approval, batch LH/T&M selection, multiplier basis, location, start, period, productive and ceiling hours, ceiling price, travel, materials, material-handling basis, NAICS/PSC, and coverage. End at the question and wait.

Skip both stages only for complete structured inputs.

### Step 0.5: convert coverage to staffing

```text
annual coverage hours = covered seats * hours per day * coverage days per year
coverage FTE = annual coverage hours / productive hours per FTE
```

At 1,880 hours, one 24x7x365 seat is 4.6596 FTE; two seats are 9.3191. One 8x5x52 seat is 1.1064. Keep four decimals in calculations, disclose rounding, and add overlap or backfill only with a separate approved basis.

### Step 1: map labor categories to SOCs

Use [data-source-operations.md](references/data-source-operations.md). Map program managers by domain. Use BLS P25/P50/P75 for junior/mid/senior. Preserve user-approved mappings and record alternate SOCs when ambiguity materially changes the estimate.

### Step 2: pull and age BLS wages

1. Call `detect_latest_year` and record the runtime vintage.
2. Resolve the current metro before querying. Fall back metro to state to national only when needed and disclose each fallback.
3. Pull the full wage distribution and flag capped or compressed tails.
4. Calculate aging from the runtime vintage to contract start and store every assumption in the workbook.

### Step 3: apply labor burden

```text
aged annual wage = BLS wage * aging factor
direct hourly rate = aged annual wage / 2,080
burdened hourly rate = direct hourly rate * burden multiplier
annual labor = burdened hourly rate * productive hours * FTE
```

Use [wrap-rate-presets.md](references/wrap-rate-presets.md). Vehicle ranges are estimating priors, not facts about a contractor. User-supplied or contract-specific rates control. Do not apply the multiplier to travel, materials, or ODCs.

### Step 4: position labor rates against CALC+

Use `igce_benchmark` for compact statistics. Use `keyword_search` only when category buckets are needed. For thin or ambiguous pools, show title-match and experience-match pools separately. Report exact sample sizes and neutral arithmetic. Compare the burdened hourly labor rate directly with CALC+ ceiling rates.

### Step 5: calculate travel

Follow [data-source-operations.md](references/data-source-operations.md). A zero-night day trip uses zero lodging and one already-discounted first/last-day M&IE amount. In T&M, classify travel under materials. In LH, travel requires a separate reimbursement or CLIN basis supplied by the user; do not silently place it inside the labor rate.

### Step 5B: price T&M materials

Run only for T&M.

1. List direct materials, supply subcontracts, incidental services without a labor category, travel, computer usage, and applicable indirect material-handling costs.
2. Price direct items at actual or estimated cost, adjusted for credits when relevant.
3. Include material-handling indirects only from the user-supplied accounting or solicitation basis and only when excluded from labor rates.
4. Do not add profit, labor burden, or an arbitrary 5% to 10% handling percentage.
5. Use numeric zero for unknown placeholders and label the estimate incomplete until the user supplies the cost.

### Step 6: handle multiple locations

Use separate rows for known headcount by location, weighted wages for supplied percentages, and the highest applicable median only as a conservative disclosed fallback when no allocation exists.

### Step 7: calculate periods and ceilings

Prorate partial periods by months. Escalate labor, travel, and materials separately. Keep non-labor amounts identical across burden scenarios except for their own escalation. Show ceiling hours by labor category and compare estimated hours with those ceilings. Show the total ceiling-price input separately from the IGCE result and flag arithmetic that exceeds it without changing the input.

### Step 8: build the workbook

Follow [workbook-specification.md](references/workbook-specification.md). Use formulas for calculations, numeric zero for placeholders, and explicit source and assumption cells.

### Step 8.5: validate

Follow [validation-gates.md](references/validation-gates.md).

1. Save a raw-input JSON sidecar.
2. Run `scripts/validate_workbook.py <workbook> --expected <sidecar> --engine auto`.
3. Fix every structure or recomputation failure.
4. Run a real spreadsheet engine when available and compare cached values with independent Python results.
5. If no engine is available, say: `Formula structure and independent calculations passed. Formula execution was not independently verified in Excel or LibreOffice.`
6. Inspect all sheets visually.

Never call openpyxl-only inspection recalculation or proof of formula execution.

### Step 9: deliver

Use the host's artifact-delivery capability when available. Otherwise save to the requested or current directory and report the absolute path. See [runtime-adaptation.md](references/runtime-adaptation.md).

## Out of scope

- The Determination and Findings for using T&M/LH.
- Contractor accounting-system, incurred-cost, or material-cost audits.
- Contract administration, surveillance plans, or ceiling-increase approvals.
- FFP, cost-reimbursement, grants, and cooperative agreements.

---

*MIT © James Jenrette / 1102tools. Source: github.com/1102tools-dev/federal-contracting-skills*
