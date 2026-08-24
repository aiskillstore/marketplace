# LH/T&M Workbook Validation Gates

Run all applicable gates before delivery.

## Automated structure

The bundled validator checks:

- All seven required sheets exist.
- Summary month-gap and aging formulas use the portable `YYYY-MM` pattern.
- Scenario Analysis blocks follow the 13-row layout.
- Direct hourly is the fifth row of each block and cross-sheet formulas do not reference the aged-wage row.
- Low, mid, and high burdened rates use only labor and the stated multiplier.
- Formula text contains no error tokens and annotations are escaped.
- Custom formula assertions from the JSON sidecar pass.

## Independent recomputation

Create a sidecar from raw inputs. Example:

```json
{
  "assumptions": {
    "contract_type": "T&M",
    "burden_low": 1.8,
    "burden_mid": 2.0,
    "burden_high": 2.2,
    "aging_factor": 1.025,
    "productive_hours": 1880,
    "ceiling_price": 900000
  },
  "labor_lines": [
    {
      "name": "Software Developer",
      "annual_wage": 135000,
      "fte": 2,
      "months": 12,
      "ceiling_hours": 3760,
      "workbook_low_rate_cell": "'Scenario Analysis'!B8",
      "workbook_mid_rate_cell": "'Scenario Analysis'!B10",
      "workbook_high_rate_cell": "'Scenario Analysis'!B12"
    }
  ],
  "non_labor_lines": [
    {
      "name": "Cloud hosting",
      "category": "materials",
      "amount": 24000,
      "workbook_total_cell": "'Materials Detail'!B10"
    }
  ],
  "material_handling_assertions": [
    {
      "cell": "'Materials Detail'!G10",
      "equals": 1250,
      "basis": "User-supplied accounting practice dated 2026-08-23"
    }
  ],
  "workbook_low_total_cell": "'IGCE Summary'!B30",
  "workbook_mid_total_cell": "'IGCE Summary'!B31",
  "workbook_high_total_cell": "'IGCE Summary'!B32",
  "workbook_ceiling_price_cell": "'IGCE Summary'!B13"
}
```

The recomputation rejects positive materials in an LH estimate. For continuous coverage, add `annual_coverage_hours`; incompatible FTE and productive hours are rejected.

Material handling defaults to numeric zero. Every nonzero input or formula in a `Material Handling` column must have a matching `material_handling_assertions` entry containing the exact cell, value or formula, and a non-empty user-supplied accounting or solicitation basis. An undisclosed percentage formula is a validation failure.

Run:

```text
python scripts/recompute_expected_values.py validation-input.json
python scripts/validate_workbook.py output.xlsx --expected validation-input.json --engine auto
```

## Real-engine verification

When LibreOffice is present, `--engine auto` executes formulas headlessly and compares cached values with independent Python results. Without a real engine, use the exact disclosure in Step 8.5 and do not call openpyxl recalculation.

## Manual gates

- Contract type is user-confirmed as LH or T&M.
- Labor-category ceiling hours and total ceiling price are shown as inputs.
- The IGCE total is not mislabeled as the binding ceiling.
- Burden applies only to labor.
- T&M materials, including travel and computer usage, remain outside labor burden.
- Material handling is supported indirect cost, not an arbitrary fee or profit percentage.
- Every nonzero material-handling input or formula resolves to the exact sidecar cell, value or formula, and disclosed basis.
- LH has no positive materials amount.
- Day-trip M&IE is discounted exactly once.
- CALC+ comparison uses burdened labor and neutral language.
- BLS vintage is runtime-confirmed and aging is cell-referenced.

## Fault injection

At minimum, confirm rejection of:

1. `DATEDIF` or `YEAR` on text for aging.
2. A summary formula that references the aged-wage row instead of a rate.
3. Positive materials in an LH sidecar.
4. A 4.2 FTE by 1,880-hour basis against 8,760 coverage hours.
5. A material formula multiplied by the labor burden.
6. A material-handling percentage with no disclosed source.

Record automated and manual results in `test.md`.
