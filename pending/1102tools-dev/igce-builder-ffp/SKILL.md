---
name: igce-builder-ffp
description: >
  Trigger for: FFP IGCE, firm-fixed-price estimate,
  FFP cost model, proposed FFP rate validation, wrap-rate analysis, Agency
  BPA rate comparison, price-reasonableness memo, or fair-and-reasonable
  analysis. Build auditable Firm-Fixed-Price federal estimates using BLS
  OEWS wages, layered fringe/overhead/G&A/profit, GSA CALC+ positioning, and
  GSA Per Diem travel. Use for FFP-by-period, FFP-by-deliverable, SOW/PWS
  decomposition, implied-multiplier analysis, and fixed-price scenario
  comparisons. Do NOT use for Labor Hour, T&M, or cost-reimbursement IGCEs
  (use IGCE Builder LH/T&M or IGCE Builder CR). Do NOT use for grant budgets.
  Requires the bls-oews, gsa-calc, and gsa-perdiem MCP servers.
---

# IGCE Builder: Firm-Fixed-Price (FFP)

## Purpose and operating boundary

Build an auditable FFP Independent Government Cost Estimate from BLS wages, layered indirect rates, CALC+ positioning data, travel inputs, and the Contracting Officer's assumptions. Keep the BLS wage, aging adjustment, fringe, overhead, G&A, profit, and fixed-price calculations visible and formula driven.

Assemble data and format workbooks. Do not originate professional judgments reserved to the Contracting Officer:

- Do not determine that a price or rate is fair and reasonable.
- Do not invent premiums for clearance, SCIF, OCONUS, specialty labor, or other conditions that the available data does not quantify.
- Do not draft a determination, negotiation position, responsibility finding, or signature-ready FAR memorandum unless the user supplies the rationale and conclusion. If supplied, reproduce that text verbatim and mark the output DRAFT.
- Use neutral positioning language such as "at CALC+ P77" or "above P50 by 22%." Avoid "reasonable," "defensible," "acceptable," "competitive," and similar conclusions.
- Workflow B produces positioning data only unless the user chooses the controlled memo-fill path and supplies the required determination text.

If a sentence concludes whether a number is right or wrong, stop and replace it with sourced data, arithmetic, and the decision left to the Contracting Officer.

## Reference map

Read only the references needed for the active workflow:

- Read [wrap-rate-presets.md](references/wrap-rate-presets.md) before selecting or testing indirect-rate assumptions.
- Read [data-source-operations.md](references/data-source-operations.md) before mapping SOCs or calling BLS, CALC+, or Per Diem operations.
- Read [workbook-specification.md](references/workbook-specification.md) in full before generating the workbook.
- Read [validation-gates.md](references/validation-gates.md) before building and again before delivering the workbook.
- Read [runtime-adaptation.md](references/runtime-adaptation.md) when collecting structured answers, locating tools, selecting a calculation engine, or delivering files.

## Non-negotiable gates

These gates prevent documented silent wrong answers. Keep them active even when shortening or adapting the workflow.

1. **CALC+ query signature:** Use the CALC+ `/v3/api/ceilingrates/` endpoint with the `keyword=` parameter when a keyword query is required. Never use `q=`. The wrong parameter can silently return the full corpus. Preserve the discovery path `aggregations.labor_category.buckets` with each bucket's `key` and `doc_count` in the data-source reference.
2. **Cross-sheet hourly-rate index:** In each 19-row Cost Buildup block, row 4 is Aged Annual Wage and row 5 is Direct Labor Rate (Hourly). Summary, scenario, and validation formulas that need hourly direct labor must reference `5 + (i-1)*19`, never `4 + (i-1)*19`. The wrong row produced a documented $16.9 billion result.
3. **Month-gap formula:** Store BLS vintage and contract start as `YYYY-MM` text and compute months with `VALUE(LEFT(...))` and `VALUE(MID(...))`. Do not use `YEAR()` on text and do not substitute `DATEDIF` for this tested pattern.
4. **Step 8.5 validation:** Run the formula-structure audit, independent Python recomputation, and real spreadsheet-engine verification when available. Never call an openpyxl-only check recalculation or proof of formula execution.
5. **AI boundary:** Never originate a fair-and-reasonable determination. Workflow B is data only unless the user supplies verbatim Option B rationale and determination text.
6. **BLS vintage:** Treat May 2025 only as the current documented baseline. Call `detect_latest_year` at runtime and use its result. Never age wages from a stale hardcoded vintage.
7. **Rate-positioning bands:** Report 0-15% above CALC+ P50 as the expected range, 15-40% as the FFP premium band, and anything above 40% with explicit stacked-factor arithmetic. These are positioning bands, not determinations.
8. **Staged questions:** For SOW/PWS decomposition, complete Stage A decomposition confirmation before Stage B build parameters. The Stage A response must end immediately after the decomposition-confirmation question. Do not preview, list, or request any Stage B input in that response. End each response at its question and wait. Never self-approve either stage.
9. **Aging factor:** Put the aging assumptions in named or clearly labeled assumption cells. Reference those cells from formulas. Never hardcode an aging multiplier into labor formulas or methodology prose.
10. **Credentialed API pacing:** Serialize calls to credentialed federal APIs and leave at least three seconds between calls. Never parallelize keyed calls. Honor a longer server-provided retry interval, and stop with a rate-limit report instead of rapid retrying.

## Pre-flight: capabilities and dependencies

Select the workflow first, then run this before its first MCP-dependent step. For Workflow B, emit the required boundary and wait for the user's option before making a tool call.

1. Inspect the operations available in the current session. Match by advertised MCP server and operation name or by equivalent operation schema. Do not depend on a host-generated namespace or separator.
2. Confirm the operation groups required by the active workflow:
   - Workflows A and A+ require `bls-oews` operations `detect_latest_year`, `get_wage_data`, and the SOC/metro lookups, plus `gsa-calc` operations `suggest_contains`, `exact_search`, `keyword_search`, `igce_benchmark`, and `price_reasonableness_check`.
   - Add `gsa-perdiem` operations `estimate_travel_cost`, `lookup_city_perdiem`, and `get_mie_breakdown` only when travel is in scope.
   - Workflow B requires the listed `bls-oews` and `gsa-calc` operations but not `gsa-perdiem` unless the user also requests travel analysis.
3. Before a build calls a data source, confirm an `.xlsx` authoring capability plus Python 3.10 or later with openpyxl for the bundled validators. A real spreadsheet engine is preferred but optional when its absence is disclosed exactly as required in Step 8.5.
4. Test only capabilities the active workflow will use. For a build, call `detect_latest_year`. If travel is in scope, test the Per Diem capability when it is first needed. For Workflow B, test BLS and CALC+ only after the user selects an option. Apply the credentialed API pacing gate to every test call. Do not expose keys or credentials.
5. If an operation is unavailable, look for a semantically equivalent operation exposed by the same server. Do not replace the MCP with a hand-built public API call.
6. If a required capability remains missing, stop and list it. State whether it appears uninstalled, unauthenticated, or unavailable in the current host.

Use this message when installation is missing:

> The active workflow requires these MCP capabilities: [list]. Missing: [list]. Install and configure them in this client, restart or refresh the client, and try again.

Use this message when authentication is missing:

> [server] is available, but its required API key is not configured or was rejected. Configure the provider key in the MCP server, restart or refresh the client, and try again.

## Select a workflow

### Workflow A: Full FFP IGCE build

Use when the user supplies structured labor and contract inputs. Execute Steps 1 through 9.

### Workflow A+: SOW/PWS-driven FFP build

Use when the user supplies a SOW, PWS, unstructured requirement, or the approved staffing handoff from `sow-pws-builder`. For an unstructured requirement, execute Step 0 and obtain both staged confirmations when required. For an approved handoff, consume it as described below and do not repeat decomposition or Stage A.

### Workflow B: FFP rate positioning

Use when the user asks whether proposed FFP rates are reasonable, asks to validate a proposal, or requests price-reasonableness analysis.

On the first Workflow B response, do not call tools or begin analysis. Emit this boundary and stop:

> I can pull positioning data that shows where each proposed rate sits against CALC+ ceiling rates and BLS market wages. I cannot draft a price reasonableness memo, write a "fair and reasonable" determination, or recommend negotiation positions. Those are Contracting Officer decisions under FAR 15.404-1, not skill outputs.
>
> Tell me which you want:
>
> **Option A: Positioning data only.** I produce a table with each proposed rate, CALC+ P25/P50/P75/P90 and sample size, plus a BLS metro burdened equivalent. I provide no verdict or recommendation.
>
> **Option B: Memo template fill.** You provide your rationale and determination. I reproduce your text verbatim in a DRAFT memo and place the benchmark tables underneath it. I do not originate conclusions or negotiation positions.
>
> Which option?

Proceed only after the user selects Option A or supplies both Option B rationale and determination text. For Option A, return neutral benchmark tables and stop. For Option B, reproduce user-supplied rationale and determination verbatim, mark the memo DRAFT, and use placeholders for the Contracting Officer and agency.

## Collect inputs

Collect missing information in the fewest useful stages. Use the host's structured question tool when it is available. Otherwise present numbered choices in chat and accept a number, label, or free-text answer.

Required for a build:

- Labor categories or priceable task areas
- Performance location or metro
- FTE or other staffing basis
- Productive hours per person, default 1,880
- Period of performance and pricing structure
- Contract start month
- Contract vehicle or indirect-rate basis

Optional with disclosed defaults:

- Fringe, overhead, G&A, profit, and escalation rates
- Travel destinations, frequency, nights, travelers, months, and origin
- NAICS and PSC
- Partial-period months
- Shift-coverage requirement
- Deliverable weights or per-LCAT allocation matrix

Do not guess a required discipline, location, staffing basis, vehicle, or pricing structure.

### Consume an approved SOW/PWS handoff

Treat a table labeled `STAFFING HANDOFF TABLE` and identified for the IGCE Builder as user-reviewed input, regardless of the separator punctuation in its heading. Do not decompose the requirement again.

1. Confirm that the declared contract type is FFP. For a hybrid, accept only the FFP CLINs and leave LH/T&M and CR CLINs to their respective skills.
2. Preserve each approved Labor Category, SOC Code, FTE, Phase, Hours/Yr, Notes, derivation, and user override. Do not silently remap or resize staffing.
3. Use the companion CLIN handoff when present to populate the period or deliverable pricing structure.
4. Reconcile any contradiction between the handoff, SOW/PWS, and current user instruction in a short table and wait for the user to choose which value controls.
5. Ask for all missing pricing inputs in one Stage B response: performance location, contract start, vehicle or indirect-rate basis, period mapping, travel or ODC assumptions, and any required allocation choice. Use a structured question tool or one numbered list, end at the question, and wait. Ask sequential one-field questions only when an answer changes the available choices.
6. After the missing inputs are confirmed, proceed to Step 1. Do not rerun Step 0 or Stage A unless the user asks to revisit staffing.

## Orchestration

### Step 0: Decompose requirements for Workflow A+

Run this step only when no approved staffing handoff is present.

1. Check for labor disciplines, staffing indicators, location, period, deliverables, and travel. Hard stop when performance location is absent. If three or more elements are missing from a short requirement, ask whether to continue with labeled assumptions or obtain clarification.
2. Separate the requirement into task areas. Record discipline, complexity, cadence, deliverable, and staffing basis.
3. Map each task to candidate labor categories and SOCs using [data-source-operations.md](references/data-source-operations.md). Use multiple categories when a task spans disciplines.
4. Estimate FTE ranges only when the scope supports them. Identify the basis for every estimate.
5. Present the decomposition table.
6. **Stage A:** Ask the user only to confirm or amend the decomposition. Do not append staffing assumptions, pricing inputs, build-parameter questions, a preview of Stage B, or a list of information that will be needed later. The final sentence of the response must be the decomposition-confirmation question. Stop immediately after its question mark and wait.
7. **Stage B:** After Stage A is confirmed, batch any required staffing quantities or authorization to develop labeled staffing assumptions with vehicle, metro, contract start, NAICS/PSC, pricing structure, deliverable allocation, and any shift-density decision. End the response at the question and wait.

Skip both stages only when the user already supplied labor categories with discipline, metro, FTE, period, and the remaining build parameters.

### Step 0.5: Convert shift coverage to staffing

Separate the coverage requirement from the productive-hours assumption. Derive staffing from the hours that must actually be covered:

```text
annual coverage hours = covered seats * hours per day * coverage days per year
coverage FTE          = annual coverage hours / productive hours per FTE
```

At the default 1,880 productive hours, one 24x7x365 seat requires `8,760 / 1,880 = 4.6596 FTE`; two seats require 9.3191 FTE. One 8x5x52 seat requires `2,080 / 1,880 = 1.1064 FTE`. Keep at least four decimal places in calculations and disclose the rounding used for presentation or staffing.

The familiar 4.2 FTE shorthand is a scheduled-hours convention based on about 2,080 hours per FTE. Do not multiply 4.2 FTE by the workbook's 1,880 productive-hour default: that prices only 7,896 hours and leaves 864 of the required 8,760 hours unreconciled. If the user requires a 4.2 headcount convention, price the 8,760 coverage hours directly or use a compatible scheduled-hours basis. Add any overlap, leave-backfill, training, or turnover reserve separately and only with a disclosed user-approved basis.

Do not price one FTE as continuous coverage. Distinguish standalone Tier 2 coverage from a Tier 2 on-call overlay. Ask which applies. For shift teams with travel, default to one representative per trip unless the requirement says otherwise. Do not silently add clearance or compliance buffers.

### Step 1: Map labor categories to SOCs

Classify the requirement as IT/software, physical engineering, science/research, medical, operations, or professional services before selecting codes. A Program Manager is context dependent: use 11-3021 for IT, 11-9041 for engineering, and 11-1021 for operations unless better evidence supports another code. Load the complete mapping and specialty fallback rules from [data-source-operations.md](references/data-source-operations.md).

Document every ambiguous mapping and any alternative queried.

### Step 2: Pull and age BLS wage data

1. Call `detect_latest_year` and record the returned vintage.
2. Query mean and P10/P25/P50/P75/P90 using `get_wage_data` for every SOC and location.
3. Follow metro to state to national fallback only after confirming that the metro series is unavailable, not merely renumbered.
4. Apply the documented seniority convention when BLS lacks job-level tiers. Do not invent a team mix when no tiers are supplied.
5. Age the selected wage to contract start using assumption cells and the month-gap formula in the workbook specification.

Use May 2025 only as the current baseline for comparison. The runtime result controls the workbook.

### Step 3: Build FFP wrap rates

Calculate each cost pool separately:

```text
direct labor rate = aged annual wage / 2,080
fringe amount     = direct labor rate * fringe rate
labor + fringe    = direct labor rate + fringe amount
overhead amount   = (labor + fringe) * overhead rate
subtotal          = labor + fringe + overhead amount
G&A amount        = subtotal * G&A rate
total cost        = subtotal + G&A amount
profit            = total cost * profit rate
fully burdened    = total cost + profit
```

Use the vehicle preset selected from [wrap-rate-presets.md](references/wrap-rate-presets.md). User-supplied rates override presets. DCAA-audited or otherwise approved rates are authoritative point estimates and do not receive invented low/high bookends. Create sensitivity scenarios only when the basis permits them.

### Step 4: Position rates against CALC+

Use the operation flow in [data-source-operations.md](references/data-source-operations.md). Preserve these rules in every run:

- Discover labor-category buckets first.
- Use exact buckets when the matched pool is adequate.
- Use `keyword_search(keyword=<term>)` only when exact buckets are fragmented. The underlying CALC+ signature is `/v3/api/ceilingrates/` with `keyword=`. Never use `q=`.
- Use `igce_benchmark` for compact percentile statistics.
- For senior categories, present title-match and experience-match pools separately.
- Label small pools as directional.
- Report the 0-15%, 15-40%, and above-40% positioning bands without converting them into a determination.

### Step 5: Price travel when required

Use `estimate_travel_cost` and the locality, fiscal-year fallback, 0-night trip, and installation-crosswalk rules in [data-source-operations.md](references/data-source-operations.md). Do not discount first/last-day M&IE twice. When no travel is required, retain explicit zero and Not Applicable rows so the workbook shows that travel was considered.

### Step 6: Handle multiple locations

Use separate labor lines when the user supplies headcount by location. Use a weighted wage when the user supplies percentages. Use the highest applicable median only as a disclosed fallback when allocation is unknown. Do not ask the user to choose a method already implied by explicit headcount.

### Step 7: Calculate fixed prices

For FFP by period, calculate labor, travel, and ODCs for each base or option period and apply escalation after the wage-aging adjustment.

For FFP by deliverable, select one disclosed allocation method:

- Uniform allocation by scope weight
- Per-LCAT allocation matrix
- Staffing-profile allocation by date range

Require deliverable percentages to total 100%, or ask whether to normalize, reject, or retain with documentation. For a single-period engagement, age wages once to contract start and do not escalate between deliverables. For multi-year milestones, escalate to each deliverable midpoint.

### Step 8: Build the workbook

Read [workbook-specification.md](references/workbook-specification.md) in full before writing code. Build the seven required sheets with formulas, source notes, assumption cells, and editable inputs. Preserve these structural rules:

- Use `YYYY-MM` text for BLS Vintage and Contract Start.
- Compute Months Gap with the tested `VALUE(LEFT(...))` and `VALUE(MID(...))` formula.
- Reference the Aging Factor cell from every labor calculation.
- Use 19-row Cost Buildup blocks. Direct Labor Rate is row 5 of each block, Fully Burdened Rate is row 18, and Implied Multiplier is row 19.
- Never reference row 4 as an hourly rate.
- Keep derived Methodology numbers formula-linked to workbook cells.
- Keep numeric calculation cells numeric. Put TBD or explanatory text only in adjacent note cells.
- Guard 0-night travel with the required day-trip formulas.

Create a temporary validation-input JSON file using the schema in [validation-gates.md](references/validation-gates.md). It must contain the raw inputs used to build the workbook and the cells where calculated results should appear. Do not deliver the temporary file unless the user requests it.

### Step 8.5: Validate before delivery

Run all available layers described in [validation-gates.md](references/validation-gates.md):

1. Run `scripts/recompute_expected_values.py` against the validation-input JSON.
2. Run `scripts/validate_workbook.py` against the workbook and the same JSON.
3. If LibreOffice or another real spreadsheet engine is available, let the validator recalculate a temporary copy and compare cached results with the independent Python results.
4. If no calculation engine is available, report exactly:

> Formula structure and independent calculations passed. Formula execution was not independently verified in Excel or LibreOffice.

Do not claim full workbook validation when the third layer did not run. Fix every structural or numerical mismatch before delivery. The grand total must also pass the dimensional sanity check against fully burdened rates, productive hours, FTE, periods, travel, and ODCs.

### Step 9: Deliver the workbook

Use the host's file-output or attachment capability when available. Otherwise write to the user-supplied path or current working directory and return the absolute path. Do not assume a host sandbox path, a particular file-presentation function, or an OS-specific open command. Follow [runtime-adaptation.md](references/runtime-adaptation.md).

State which validation layers passed and whether a real spreadsheet engine ran. Do not bury the limitation when only static and independent checks ran.

## Edge conditions

- Mid-scenario multipliers must be checked against the selected vehicle's expected band, not a universal band. High sensitivity cases may legitimately exceed 3.5x.
- Treat text beginning with `=`, `+`, `-`, or `@` as a formula-injection risk. Prefix or rewrite explanatory text.
- Keep same-metro travel, OCONUS travel, airfare, ground transportation, equipment, subscriptions, subcontractors, clearance processing, SCIF construction, TEMPEST, and COMSEC as separately sourced inputs or explicit exclusions.
- Use the LH/T&M or Cost-Reimbursement skill for those contract types. Do not reuse this FFP wrap workflow.

---

*MIT copyright James Jenrette / 1102tools. Source: github.com/1102tools-dev/federal-contracting-skills*
