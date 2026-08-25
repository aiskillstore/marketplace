# CR Workbook Validation Gates

Run all applicable gates after workbook creation and before delivery.

## Layer 1: formula-structure audit

The bundled validator checks:

- All seven required sheets exist.
- `IGCE Summary!B11` computes the month gap from `YYYY-MM` text using `VALUE`, `LEFT`, and `MID`, without `DATEDIF` or `YEAR`.
- `IGCE Summary!B12` computes the aging factor from escalation and month gap.
- Every Cost Buildup block follows the 23-row layout.
- Direct labor is the fifth row of each block and cross-sheet formulas do not use the aged-wage row by mistake.
- Fringe, overhead, G&A, FCCM, fee, and price formulas preserve the required bases.
- The workbook contains formulas and no formula-error tokens in formula text.
- Text beginning with formula-trigger characters is escaped.
- Optional custom formula assertions in the JSON sidecar pass.

## Layer 2: independent recomputation

Create a JSON sidecar from the raw inputs, not from workbook formula results. Minimum shape:

```json
{
  "assumptions": {
    "fee_type": "CPFF",
    "primary_fee_rate": 0.08,
    "fringe_rate": 0.32,
    "overhead_rate": 0.80,
    "ga_rate": 0.12,
    "fccm_rate": 0.0,
    "aging_factor": 1.025,
    "productive_hours": 1880
  },
  "labor_lines": [
    {
      "name": "Research Scientist",
      "annual_wage": 140000,
      "fte": 3,
      "months": 12,
      "workbook_cost_rate_cell": "'Cost Buildup'!B17",
      "workbook_price_rate_cell": "'Cost Buildup'!B21"
    }
  ],
  "non_labor_lines": [
    {
      "name": "Travel",
      "amount": 12000,
      "fee_bearing": false,
      "workbook_total_cell": "'Travel Detail'!B14"
    }
  ],
  "workbook_fee_bearing_cost_cell": "'IGCE Summary'!B28",
  "workbook_total_cost_cell": "'IGCE Summary'!B29",
  "workbook_total_fee_cell": "'IGCE Summary'!B30",
  "workbook_total_price_cell": "'IGCE Summary'!B31"
}
```

For CPAF, add `award_pool_rate` and `assumed_earned`. For CPIF, the primary recomputation verifies the target case; add formula assertions for overrun and underrun shares and bounds in `Scenario Analysis`.

If continuous coverage is present, put `annual_coverage_hours` on the relevant labor line. The recomputation rejects an FTE and productive-hours combination that does not reconcile within 0.5% or one hour.

Run:

```text
python scripts/recompute_expected_values.py validation-input.json
python scripts/validate_workbook.py output.xlsx --expected validation-input.json --engine auto
```

## Layer 3: real spreadsheet engine

With `--engine auto`, the validator looks for LibreOffice. When found, it performs a headless conversion cycle, reopens the calculated workbook with `data_only=True`, checks cached errors, and compares named workbook values against the independent Python result.

If formula execution cannot run, do not call the workbook fully recalculated. Use the exact disclosure required by the core skill.

## CR-specific manual gates

Confirm each item even when a script passes:

- Fee-bearing and non-fee-bearing amounts are visibly separate.
- CPFF form is Completion or Term and the rationale follows FAR 16.306(d).
- CPFF fee does not exceed the applicable ceiling.
- CPAF shows base-only, assumed-earned, and full-pool outcomes.
- CPIF uses separate contractor overrun and underrun shares and applies min/max bounds.
- Audited indirect rates are point estimates with date and authority, not scenario midpoints.
- CALC+ results are neutral positioning and distinguish estimated cost from cost plus fee.
- Day-trip M&IE is discounted once, not twice.
- BLS vintage is runtime-confirmed and aging is cell-referenced.
- No formula range contains text `TBD`.

## Fault injection

At minimum, test copies with these deliberate defects and confirm rejection:

1. Replace `keyword=` with `q=` in a recorded CALC+ query.
2. Change the month-gap formula to `DATEDIF` or `YEAR` on text.
3. Point a summary rate to the aged-annual-wage row instead of Direct Labor.
4. Apply fee to total estimated cost when a non-fee pass-through is present.
5. Remove the FCCM layer or apply it to the wrong base.
6. Change a CPIF underrun formula to use the overrun share.
7. Multiply 4.2 FTE by 1,880 hours against an 8,760-hour coverage requirement.

Document which faults were automated and which were manually inspected in `test.md`.
