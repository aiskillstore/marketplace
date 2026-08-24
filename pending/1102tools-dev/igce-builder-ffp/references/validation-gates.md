# FFP Workbook Validation Gates

Use this reference to prepare validator inputs, run all available validation layers, interpret failures, and preserve the April regression gates.

## Contents

1. Validation contract
2. Validation-input JSON
3. Formula-structure audit
4. Independent recomputation
5. Real-engine verification
6. Named regression assertions
7. Result language

## 1. Validation contract

Run three layers:

1. Formula-structure audit
2. Independent Python recomputation from raw inputs
3. Real spreadsheet-engine execution and cached-value comparison when available

Openpyxl does not evaluate formulas. Never call an openpyxl-only operation recalculation or use it as proof that Excel formulas execute.

The validator must not modify the delivered workbook. Real-engine verification operates on a temporary copy.

## 2. Validation-input JSON

Build a temporary JSON file from the same raw input objects used to construct the workbook.

Minimal schema:

```json
{
  "assumptions": {
    "fringe_rate": 0.32,
    "overhead_rate": 0.80,
    "ga_rate": 0.12,
    "profit_rate": 0.10,
    "aging_factor": 1.035,
    "productive_hours": 1880
  },
  "labor_lines": [
    {
      "name": "Software Developer",
      "annual_wage": 132000,
      "fte": 2,
      "months": 12,
      "period_multiplier": 1.0,
      "workbook_fbr_cell": "'Cost Buildup'!B18",
      "workbook_total_cell": "'IGCE Summary'!D15"
    }
  ],
  "non_labor_lines": [
    {
      "name": "Travel",
      "amount": 0,
      "workbook_total_cell": "'IGCE Summary'!D20"
    }
  ],
  "workbook_grand_total_cell": "'IGCE Summary'!D25",
  "required_sheets": [
    "IGCE Summary",
    "Cost Buildup",
    "Scenario Analysis",
    "Rate Validation",
    "Travel Detail",
    "Methodology",
    "Raw Data"
  ],
  "formula_assertions": [
    {
      "cell": "'IGCE Summary'!B11",
      "contains": ["VALUE(LEFT(B10,4))", "VALUE(MID(B10,6,2))"],
      "not_contains": ["DATEDIF", "YEAR("]
    }
  ]
}
```

Supported labor-line overrides:

- `fringe_rate`
- `overhead_rate`
- `ga_rate`
- `profit_rate`
- `aging_factor`
- `productive_hours`

Use overrides for approved rates, different scenarios, or lines with a distinct basis. Otherwise the script uses the top-level assumptions.

`period_multiplier` carries option-year escalation or a deliverable timing factor. Set it to 1.0 for the base period. `months` prorates productive hours. For a deliverable allocation, represent each LCAT/deliverable combination as its own labor line with the allocated hours or equivalent FTE-month basis.

For continuous or shift coverage, add `annual_coverage_hours` to each affected labor line. The recomputation script requires `productive_hours * FTE` to reconcile to that annual requirement within 0.5% or one hour, whichever is larger. Do not use a 4.2 scheduled-hours shorthand with the 1,880 productive-hour default.

Use numeric non-labor amounts. Include travel, airfare, ground transportation, ODCs, and other costs that feed the grand total.

## 3. Formula-structure audit

Run:

```text
python scripts/validate_workbook.py workbook.xlsx --expected validation-inputs.json --engine none
```

The audit checks:

- Required sheet names
- The B11 month-gap formula and absence of `DATEDIF`
- The B12 aging-factor formula
- Cost Buildup block spacing and critical formula rows
- Cross-sheet use of aged annual wage as an hourly rate
- Formula assertions supplied in the JSON
- Formula error tokens and broken references
- Cached error values when present

Treat a formula-structure failure as a delivery blocker.

### Formula assertions

Each assertion accepts:

```json
{
  "cell": "'Sheet Name'!B2",
  "equals": "=A1*2",
  "contains": ["A1", "*2"],
  "not_contains": ["A2"]
}
```

Use only the keys needed. Comparisons ignore whitespace and ASCII letter case.

Add assertions for the actual Summary grand-total formula, deliverable allocations, option-year escalation, Travel day-trip branch, and any special approved-rate treatment.

## 4. Independent recomputation

Run:

```text
python scripts/recompute_expected_values.py validation-inputs.json
```

The script calculates:

```text
aged annual wage = annual wage * aging factor
direct hourly     = aged annual wage / 2,080
FBR               = direct hourly
                    * (1 + fringe)
                    * (1 + overhead)
                    * (1 + G&A)
                    * (1 + profit)
labor total       = FBR * productive hours * FTE * months / 12 * period multiplier
grand total       = sum(labor totals) + sum(non-labor amounts)
```

This calculation is independent of workbook formulas. It catches dimensional and arithmetic errors even when the workbook looks plausible.

When `annual_coverage_hours` is present, the script also checks:

```text
annual priced hours = productive hours * FTE
annual priced hours approximately equals annual coverage hours
```

Do not derive validator inputs by reading formula results back from the workbook. That would compare the workbook to itself.

## 5. Real-engine verification

Run:

```text
python scripts/validate_workbook.py workbook.xlsx --expected validation-inputs.json --engine auto
```

With `auto`, the validator looks for `soffice` and the standard macOS LibreOffice application path. If found, it converts a temporary copy through LibreOffice, reopens the calculated file with `data_only=True`, and compares cached FBR, line totals, and grand total with the independent computation.

Use `--engine libreoffice` to require the engine. A missing or failed engine is then an error.

Default comparison tolerance is 1% relative, with a small absolute floor. Tighten it when the workbook and source values use full precision. Explain intentional differences such as rounded displayed rates only when the underlying formulas remain full precision.

LibreOffice verification increases confidence but does not replace final testing in Microsoft Excel when the deliverable depends on Excel-specific functions or formatting.

## 6. Named regression assertions

Preserve these checks in the core and grader.

### CALC+ query signature

- Methodology or Raw Data records `/v3/api/ceilingrates/` and `keyword=` for keyword searches.
- No instruction or recorded call uses `q=` as the search parameter.
- Raw Data records `aggregations.labor_category.buckets`, selected keys, and counts when discovery is used.

### Cross-sheet hourly index

- Direct hourly rate is row 5 of each 19-row block.
- Summary, Scenario Analysis, and Rate Validation do not use row 4 as an hourly rate.
- Grand total passes dimensional comparison. A result above twice the independent expected band is a hard failure.

### Month gap and aging

- B9 and B10 contain `YYYY-MM` text.
- B11 uses `VALUE(LEFT(...))` and `VALUE(MID(...))`.
- B11 contains no `DATEDIF` and no `YEAR(`.
- B12 references B6 and B11.
- Summary B12 and each Cost Buildup aging-factor cell display as a four-decimal multiplier, not a percentage.
- Every labor block references Summary B12.
- Methodology displays aging through a cell-linked formula.

### AI boundary

- Workflow B first response stops at the Option A or Option B choice.
- Option A contains positioning data and no determination.
- Option B contains only the user's rationale and determination text in the conclusion fields.
- No generated workbook calls a rate reasonable, defensible, acceptable, competitive, or an outlier.

### BLS vintage

- `detect_latest_year` ran successfully.
- The returned year controls B9 and Raw Data.
- May 2025 is not trusted when runtime data reports a newer year.

### Rate positioning

- 0-15%, 15-40%, and above-40% bands are present.
- Above 40% includes stacked-factor arithmetic.
- Band labels remain positional and do not become determinations.

### Staged questioning

- Stage A ends with decomposition confirmation.
- Stage B occurs only after Stage A confirmation.
- Stage B ends with its question.
- No tool calls or build steps occur while a required stage is unanswered.

### SOW/PWS handoff

- An approved Staffing Handoff Table bypasses decomposition and Stage A.
- Labor Category, SOC Code, FTE, Phase, Hours/Yr, Notes, derivations, and user overrides carry forward unchanged unless the user approves a revision.
- The skill confirms FFP before pricing. For a hybrid, it processes only FFP CLINs.
- All missing pricing inputs are requested together in one Stage B response before Step 1, unless an answer changes the available choices.
- Contradictory source values are presented for user resolution rather than silently reconciled.

### Credentialed API pacing

- Keyed calls are serialized, never parallelized.
- At least three seconds elapse between credentialed federal API calls.
- A longer server-provided retry interval controls when present.
- A rate-limit response stops rapid retries and is reported to the user.

### Shift-coverage reconciliation

- Annual coverage hours are derived from seats, hours per day, and coverage days.
- FTE is derived from annual coverage hours divided by the approved productive-hours basis.
- A 24x7x365 single seat at 1,880 productive hours requires 4.6596 FTE before any separately approved reserve.
- A 4.2 FTE shorthand may be used only with a compatible scheduled-hours basis or when the workbook prices 8,760 coverage hours directly.
- `productive hours * FTE` must not understate required annual coverage hours.

### Workbook safety

- Step 8.5 ran before delivery.
- Day trips use one 75% M&IE partial day and zero lodging.
- Day trips use `lookup_city_perdiem`; they never pass `num_nights=0` to `estimate_travel_cost`, which requires at least one night.
- First/last-day M&IE is not discounted twice.
- Calculation cells contain numeric zero rather than `TBD`.
- Formula-linked Methodology text does not go stale when assumptions change.
- Text beginning with formula-trigger characters is escaped or rewritten.

## 7. Result language

When all three layers pass, state:

> Formula structure, independent calculations, and LibreOffice formula execution passed.

When the first two pass and no real engine is available, state:

> Formula structure and independent calculations passed. Formula execution was not independently verified in Excel or LibreOffice.

When any layer fails, do not present the workbook as complete. Fix the failure and rerun the validator.
