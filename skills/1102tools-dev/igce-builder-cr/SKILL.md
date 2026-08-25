---
name: igce-builder-cr
description: >
  Trigger for: cost-reimbursement IGCE, CR cost
  estimate, CPFF, CPAF, CPIF, cost-plus estimate, BAA estimate, fixed-fee
  analysis, award-fee analysis, incentive-fee analysis, proposed CR rate
  validation, cost-pool buildup, share-ratio scenario, price-reasonableness
  memo, or fair-and-reasonable analysis. Build auditable CR estimates using
  BLS OEWS wages, fringe/overhead/G&A/FCCM pools, contract-type-specific fee,
  GSA CALC+ positioning, and GSA Per Diem travel. Do NOT use for FFP, LH/T&M,
  grants, or cooperative agreements. Requires the bls-oews, gsa-calc, and
  gsa-perdiem MCP servers.
---

# IGCE Builder: Cost-Reimbursement

## Overview

Build an auditable CPFF, CPAF, or CPIF Independent Government Cost Estimate. Estimate allowable-cost layers and fee separately. Preserve the distinction between fee-bearing and non-fee-bearing cost, and never substitute CALC+ ceiling-rate comparisons for cost analysis.

Regulatory anchors: FAR 15.404-1, FAR 15.404-4, FAR 16.301 through 16.307, 10 U.S.C. 3322, and 41 U.S.C. 3905. Apply the current regulation, solicitation, and agency supplement. This skill does not make legal determinations.

Load supporting files only when needed:

- [wrap-rate-presets.md](references/wrap-rate-presets.md) for indirect-cost and fee structures.
- [data-source-operations.md](references/data-source-operations.md) before mapping labor or calling BLS, CALC+, or Per Diem.
- [workbook-specification.md](references/workbook-specification.md) before creating the workbook.
- [validation-gates.md](references/validation-gates.md) before and after workbook generation.
- [runtime-adaptation.md](references/runtime-adaptation.md) for questions, tools, formula engines, and delivery.

## Operating principle

This skill assembles data and formats analysis. The Contracting Officer owns cost-realism judgments, fair-and-reasonable determinations, fee objectives, negotiation positions, and approval documents.

- Use neutral positional language such as `at CALC+ P77 (n=42)` or `above CALC+ P50 by 18%`.
- Never originate a determination, negotiation target, evaluation notice, or contractor-responsibility conclusion.
- Never invent a clearance, SCIF, OCONUS, specialty-labor, cost-risk, or performance premium.
- When the user supplies rationale or a determination, preserve it verbatim and label the resulting document `DRAFT`.

## Permanent correctness gates

These gates prevent documented silent wrong answers. Keep them in the front-loaded core.

1. **Workflow B boundary:** On every Workflow B entry, emit the Option A/Option B boundary below before analysis or tool use, then wait.
2. **CALC+ query signature:** Use `/v3/api/ceilingrates/` with `keyword=`. Never use `q=`; it silently returns the full corpus.
3. **Fee basis:** Fee applies only to the user-confirmed fee-bearing cost base. Never apply fee automatically to pass-through ODCs or travel.
4. **CPFF caps:** Under FAR 15.404-4(c)(4)(i), cap CPFF at 15% for experimental, developmental, or research work, 10% for other CPFF work, and apply the separate 6% architect-engineer limitation when relevant. Treat caps as ceilings, not defaults.
5. **CPFF form:** Declare Completion or Term under FAR 16.306(d). Prefer Completion when a definite goal or end product can be estimated; use Term only with a specified level of effort and definite time period.
6. **CPIF shares:** Keep contractor overrun and underrun shares as separate assumptions. Apply min and max fee bounds, and show where a bound stops the share formula.
7. **CPAF range:** Show base-only, assumed-earned, and full-pool fee outcomes. Never hide the award-fee range behind one 85%-earned point.
8. **Aging formula:** Store BLS vintage and contract start as assumptions. Calculate month gap with `VALUE(LEFT(...))` and `VALUE(MID(...))` when dates are stored as `YYYY-MM` text. Do not use `YEAR` on text or rely on `DATEDIF` portability.
9. **Shift coverage:** Derive coverage FTE from required coverage hours and productive hours. At 1,880 hours, one 24x7x365 seat is 4.6596 FTE. Do not multiply 4.2 by 1,880.
10. **Staged questions:** Stage A is decomposition confirmation only. Its response must end immediately after that question, with no Stage B preview. Ask Stage B only after Stage A approval.
11. **Step 8.5:** Run formula-structure audit and independent recomputation. Use a real spreadsheet engine when available; disclose exactly when formula execution was not independently verified.
12. **Credentialed API pacing:** Serialize credentialed federal API calls and leave at least three seconds after one completes before starting the next. Never parallelize keyed calls. Honor longer retry intervals and stop instead of rapid retrying.

## Workflow selection

Select the workflow before capability tests.

### Workflow A: structured CR build

Use when the user supplies labor, location, staffing, period, and fee type. Execute Steps 1 through 9.

### Workflow A+: SOW/PWS or BAA build

Use when the user supplies an unstructured requirement or an approved staffing handoff. For raw requirements, run Step 0 and both staged confirmations. For an approved handoff, consume it without repeating decomposition or Stage A.

If a BAA does not declare contract type, explain that CR may fit uncertain research but require the user to select the contract type. Do not self-select CPFF.

### Workflow B: CR rate positioning or memo request

Use when the user asks to validate proposed rates, judge cost pools, draft a price-reasonableness memo, or decide whether rates are fair and reasonable.

The entire first response must be exactly the boundary block below. Begin with `I can provide` and add no heading, workflow label, preamble, capability note, analysis, or tool call before it. End at `Which option do you choose?` and add nothing after that question.

> I can provide positioning data showing where proposed rates sit against CALC+ ceiling rates and BLS market wages. I cannot originate a price-reasonableness memo, fair-and-reasonable determination, cost-realism judgment, or negotiation position. Those are Contracting Officer decisions.
>
> **Option A: Positioning data only.** I provide per-category CALC+ percentiles and sample size, BLS metro cost buildup, and neutral arithmetic. No verdict or recommendation.
>
> **Option B: Draft template using your conclusion.** You provide your rationale and determination. I place that text verbatim into a DRAFT template and add benchmark tables. I do not add conclusions or negotiation advice.
>
> Which option do you choose?

After Option A, run the applicable BLS and CALC+ steps and stop at neutral positioning. After Option B, require both rationale and determination before building the draft. Never paraphrase the user's conclusion.

## Pre-flight capabilities

Run this after workflow selection and, for Workflow B, only after the user chooses an option.

1. Inspect the operations actually available in the session. Match by server and operation schema, not host-generated namespace.
2. Workflows A and A+ require `bls-oews` wage, vintage, SOC, and metro operations plus `gsa-calc` suggestion and benchmark operations. Add `gsa-perdiem` only when travel is in scope.
3. Workflow B requires only the benchmark operations needed for the chosen analysis. Option B also requires a document-authoring capability if the user requests a file.
4. Before workbook creation, require `.xlsx` authoring, Python 3.10+, openpyxl, and the bundled validators. A real spreadsheet engine is preferred but optional when its absence is disclosed.
5. Test only capabilities the active workflow will use. For a build, confirm the BLS vintage at runtime. Test Per Diem only when travel is in scope. Apply the pacing gate to every keyed call.
6. If a capability is missing, look for an equivalent operation from the declared server. Do not bypass the MCP with a hand-built public API call.
7. If still missing, stop and report whether it appears uninstalled, unauthenticated, or unavailable in the host.

## Information to collect

Required for a build:

- Labor category or task discipline, SOC when known, seniority, FTE or coverage basis, and productive hours.
- Performance location and any staffing split by location.
- Base and option periods, contract start month, and any partial-year duration.
- CR type: CPFF, CPAF, or CPIF. For CPFF, Completion or Term form.
- Indirect-rate basis: disclosed estimate or CO-supplied FPRA/FPRR/DCAA-audited rates with date and authority.
- Fee structure and fee-bearing classification for labor, travel, subcontracts, and every ODC.

Optional with disclosed defaults:

- Productive hours 1,880; escalation 2.5%; fringe 32%; overhead 80%; G&A 12%; FCCM 0%.
- CPFF fee 8%; CPAF base 3%, pool 7%, assumed earned 85%; CPIF target 8%, contractor overrun and underrun shares 20%, min 3%, max 12%.
- No travel or ODCs. Treat missing travel as zero and record that travel was considered.

Do not override CO-supplied audited rates with generic defaults. Use audited rates as point estimates, record their effective date and authority, and do not manufacture low/high offsets around them.

## Approved SOW/PWS handoff

Treat a user-reviewed table labeled `STAFFING HANDOFF TABLE` as approved input regardless of heading punctuation.

1. Confirm that the declared contract type is CR. For a hybrid, consume only CR CLINs.
2. Preserve approved labor category, SOC, FTE, phase, hours, notes, derivation, and overrides.
3. Use the CLIN handoff for period and deliverable mapping when present.
4. Present contradictions among handoff, requirement, and current instruction in a short table and wait for the user to choose the controlling value.
5. Ask all missing Stage B inputs in one response. Do not rerun decomposition or Stage A unless the user asks to revise staffing.

## Orchestration

### Step 0: decompose raw requirements

Run only when no approved handoff is present.

1. Check labor disciplines, staffing basis, location, period, deliverables, and travel. Performance location is a hard stop before data calls. If three or more elements are missing from a short requirement, ask whether to continue with labeled assumptions or obtain clarification.
2. Separate the requirement into task areas with discipline, complexity, cadence, deliverable, and staffing basis.
3. Perform agency and technical-domain triage before SOC mapping.
4. Map each task to candidate labor categories and SOCs using [data-source-operations.md](references/data-source-operations.md). Use multiple candidates when mapping is ambiguous.
5. Estimate FTE ranges only when the scope supplies a defensible basis. Otherwise list the missing sizing facts.
6. **Stage A:** Present the decomposition, then ask only whether the user confirms or amends the task areas, labor categories, and SOC mappings. This must be the response's only question. Do not ask whether to proceed on assumptions, select a contract or fee type, provide a location, or supply any other Stage B input, even when those items are hard stops. Do not preview Stage B. The final sentence must be the decomposition-confirmation question. Stop immediately after its question mark.
7. **Stage B:** After approval, batch fee type, CPFF form if applicable, indirect-rate basis, performance metro, start, period, NAICS/PSC, coverage, travel, ODCs, and fee-bearing classifications. End at the question and wait.

Skip both stages only when the user supplied the full structured build input.

### Step 0.5: convert coverage to staffing

```text
annual coverage hours = covered seats * hours per day * coverage days per year
coverage FTE = annual coverage hours / productive hours per FTE
```

At 1,880 productive hours, one 24x7x365 seat is `8,760 / 1,880 = 4.6596 FTE`; two seats are 9.3191. One 8x5x52 seat is 1.1064. Keep four decimals in calculations and disclose rounding. Add overlap, leave-backfill, training, or turnover reserves only with a separate user-approved basis.

### Step 1: map labor categories to SOCs

Use the mapping and fallbacks in [data-source-operations.md](references/data-source-operations.md). Map program managers by domain. Use BLS P25/P50/P75 for junior/mid/senior. Preserve user-approved mappings and label fallbacks.

### Step 2: pull and age BLS wages

1. Call `detect_latest_year` and record the returned vintage.
2. Resolve the current metro code before wage queries. Query metro, then state, then national only when the more specific level is unavailable.
3. Pull the full wage distribution. Flag cap proximity and flat P75/P90 tails.
4. Calculate aging from the returned vintage to contract start, store every assumption in the workbook, and avoid double-counting option-year escalation.

### Step 3: build cost pools and fee

For each scenario and labor line:

```text
aged annual wage = BLS wage * aging factor
direct hourly = aged annual wage / 2,080
fringe = direct hourly * fringe rate
labor plus fringe = direct hourly + fringe
overhead = labor plus fringe * overhead rate
subtotal = labor plus fringe + overhead
G&A = subtotal * G&A rate
FCCM = (subtotal + G&A) * FCCM rate
estimated cost rate = subtotal + G&A + FCCM
```

Classify each non-labor item before fee:

```text
total estimated cost = fee-bearing cost + non-fee-bearing cost
fee = fee formula applied only to fee-bearing cost
total estimated price = total estimated cost + fee
```

Use [wrap-rate-presets.md](references/wrap-rate-presets.md) for CPFF, CPAF, and CPIF formulas and scenario rules. Do not convert CPFF fixed fee into a cost-reimbursement percentage that changes with actual cost; workbook scenarios are estimating outcomes, not contract payment mechanics.

### Step 4: position rates against CALC+

Use `igce_benchmark` for statistics-only queries. Use `keyword_search` only when category buckets are needed. For thin or ambiguous pools, use title-match and experience-match pools and report each sample size. Compare CR estimated-cost-plus-fee separately from the underlying cost rate. Use neutral arithmetic only.

### Step 5: calculate travel

Use [data-source-operations.md](references/data-source-operations.md) for locality, fiscal-year, and first/last-day rules. A zero-night trip uses one already-discounted first/last-day M&IE amount. Confirm whether travel is fee-bearing; default pass-through travel to non-fee-bearing when the user does not direct otherwise, and disclose that assumption.

### Step 6: handle multiple locations

- Use separate rows when headcount by location is known.
- Use a weighted wage when percentages are supplied.
- Use the highest applicable median only as a conservative disclosed fallback when no allocation exists.

### Step 7: calculate periods and scenarios

Prorate partial periods by months. Escalate labor and travel from the aged base-year amount. Show low, mid, and high cost-pool cases. For CPAF, show three earned-fee outcomes. For CPIF, show the cost-scenario by fee-outcome matrix and bound crossings. Never classify pass-through cost differently across scenarios.

### Step 8: build the workbook

Follow [workbook-specification.md](references/workbook-specification.md). Use formulas for calculated values, numeric zero for placeholders, and explicit source and assumption cells. Keep editable assumptions visually distinct.

### Step 8.5: validate

Follow [validation-gates.md](references/validation-gates.md).

1. Save a raw-input JSON sidecar.
2. Run `scripts/validate_workbook.py <workbook> --expected <sidecar> --engine auto`.
3. Fix every formula-structure or recomputation failure and rerun.
4. If LibreOffice or another real engine is available, execute formulas and compare cached values with the independent Python result.
5. If no engine is available, say: `Formula structure and independent calculations passed. Formula execution was not independently verified in Excel or LibreOffice.`
6. Visually inspect all sheets for clipping, broken formats, unreadable notes, and empty or misleading tables.

Never call openpyxl-only inspection recalculation or proof of formula execution.

### Step 9: deliver

Use the host's artifact-delivery capability when available. Otherwise save to the requested or current working directory and report the absolute path. Do not invent host-specific paths or commands. See [runtime-adaptation.md](references/runtime-adaptation.md).

## Out of scope

- DCAA proposal audits, incurred-cost audits, or validation of contractor accounting systems.
- Contractor responsibility, source selection, negotiation objectives, or cost-realism determinations.
- OCONUS per diem without the appropriate Department of State or DoD source.
- FFP, LH/T&M, grants, and cooperative agreements.

---

*MIT © James Jenrette / 1102tools. Source: github.com/1102tools-dev/federal-contracting-skills*
