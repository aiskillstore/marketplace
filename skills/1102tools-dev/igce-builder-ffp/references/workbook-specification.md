# FFP IGCE Workbook Specification

Read this file in full before generating the workbook. Use formulas for every derived value and keep hardcoded assumptions visibly separate from calculations.

## Contents

1. Required workbook structure
2. Summary assumptions and pricing table
3. Cost Buildup blocks
4. Scenario Analysis
5. Rate Validation
6. Travel Detail
7. Methodology and Raw Data
8. Formatting and formula rules
9. Validation sidecar

## 1. Required workbook structure

Create these seven sheets in this order:

1. IGCE Summary
2. Cost Buildup
3. Scenario Analysis
4. Rate Validation
5. Travel Detail
6. Methodology
7. Raw Data

Use these exact names so the validator can apply structural gates.

## 2. Summary assumptions and pricing table

Use this fixed assumption block:

```text
A1  IGCE Assumptions (FFP)             B1  merged title
A2  Fringe Rate                        B2  editable numeric rate
A3  Overhead Rate                      B3  editable numeric rate
A4  G&A Rate                           B4  editable numeric rate
A5  Profit Rate                        B5  editable numeric rate
A6  Escalation Rate/Yr                 B6  editable numeric rate
A7  Productive Hours/Year              B7  editable numeric hours
A8  Base Year Months (or PoP Months)   B8  editable numeric months
A9  BLS Vintage (YYYY-MM)              B9  editable text such as 2025-05
A10 Contract Start (YYYY-MM)           B10 editable text such as 2026-10
A11 Months Gap                         B11 formula below
A12 Aging Factor                       B12 =(1+B6)^(B11/12)
A13 blank separator
A14 pricing-table header
```

The B11 formula is mandatory:

```excel
=(VALUE(LEFT(B10,4))-VALUE(LEFT(B9,4)))*12+(VALUE(MID(B10,6,2))-VALUE(MID(B9,6,2)))
```

Do not use `YEAR()` against the text cells. Do not replace the tested pattern with `DATEDIF`.

Use real numeric cells for B2:B8, text cells for B9:B10, and formulas for B11:B12. Make B2:B10 visually identifiable as editable assumptions.

Format the B12 Aging Factor as `0.0000`, not as a percentage. A factor such as 1.0499 must display as `1.0499`, not `105.0%`.

### Summary pricing table

For FFP by period:

- Put labor categories in rows.
- Put base and option periods in columns.
- Show the fully burdened hourly rate and FTE basis.
- Calculate each period from FBR, productive hours, FTE, period months, and escalation.
- For continuous or shift coverage, show annual coverage hours and the productive-hours basis used to derive FTE. The priced annual hours (`productive hours * FTE`) must reconcile to the required annual coverage hours.

For FFP by deliverable:

- Put labor categories in rows.
- Put deliverables or CLINs in columns.
- Apply the selected uniform, per-LCAT, or staffing-profile allocation.
- Keep the allocation basis visible or linked to Raw Data.

Place Travel, Airfare, Ground Transportation, ODCs, and Grand Total below labor. Use numeric zero for unknown or excluded amounts. Put `TBD`, `Not Applicable`, or another explanation only in an adjacent note cell.

When no travel is required, include a numeric zero Travel row and a Not Applicable note.

Record the exact workbook cell containing the grand total and each validation target in the temporary validation JSON.

## 3. Cost Buildup blocks

Use one 19-row block per labor category. The first block starts at row 1. Block `i` starts at:

```text
base row = 1 + (i - 1) * 19
```

The block-relative rows are fixed:

| Offset from base | Block 1 row | Label | Formula or value |
|---:|---:|---|---|
| 0 | 1 | Cost Buildup: [Labor Category] | Header |
| 1 | 2 | BLS Base Wage (Annual, raw) | Hardcoded selected wage |
| 2 | 3 | Aging Factor | `='IGCE Summary'!$B$12` |
| 3 | 4 | Aged Annual Wage | `=B2*B3` |
| 4 | 5 | Direct Labor Rate (Hourly) | `=B4/2080` |
| 5 | 6 | blank | blank |
| 6 | 7 | Fringe Rate | `='IGCE Summary'!$B$2` |
| 7 | 8 | Fringe Amount | `=B5*B7` |
| 8 | 9 | Labor + Fringe | `=B5+B8` |
| 9 | 10 | Overhead Rate | `='IGCE Summary'!$B$3` |
| 10 | 11 | Overhead Amount | `=B9*B10` |
| 11 | 12 | Subtotal (Labor+Fringe+OH) | `=B9+B11` |
| 12 | 13 | G&A Rate | `='IGCE Summary'!$B$4` |
| 13 | 14 | G&A Amount | `=B12*B13` |
| 14 | 15 | Total Cost | `=B12+B14` |
| 15 | 16 | Profit Rate | `='IGCE Summary'!$B$5` |
| 16 | 17 | Profit Amount | `=B15*B16` |
| 17 | 18 | Fully Burdened Rate | `=B15+B17` |
| 18 | 19 | Implied Multiplier | `=B18/B5` |

Format each block's Aging Factor cell as `0.0000`, matching Summary B12. Do not use a percentage format for an aging multiplier.

Shift every in-block row reference by `(i-1)*19`. Do not shift the cross-sheet Summary assumption references.

For block `i`:

```text
aged annual wage row = 4 + (i - 1) * 19
direct hourly row    = 5 + (i - 1) * 19
FBR row              = 18 + (i - 1) * 19
multiplier row       = 19 + (i - 1) * 19
```

### Critical cross-sheet rule

Summary, Scenario Analysis, and Rate Validation formulas must use the FBR row for burdened rates and the direct hourly row for direct labor. Never use the aged annual wage row as an hourly rate.

The validator flags cross-sheet references to `Cost Buildup` column B rows where the block-relative row is 4. The documented failure used annual wage as an hourly rate and produced a $16.9 billion total.

## 4. Scenario Analysis

Display LOW, MID, and HIGH component rates and totals when the selected rate basis permits scenarios. Use independent component rates, not a single hardcoded burden multiplier.

```text
FBR = direct rate
      * (1 + fringe)
      * (1 + overhead)
      * (1 + G&A)
      * (1 + profit)
```

Keep travel unchanged across scenarios. Apply the same period-month treatment used on the Summary. Do not silently calculate full-year scenario totals when the Summary is partial-year.

For approved point-estimate rates, use one authoritative column. Add sensitivity columns only when the user requests them and label them as sensitivity display.

## 5. Rate Validation

Include:

- Labor category and SOC
- FFP fully burdened rate
- CALC+ P25, P50, P75, and sample size
- Optional P90 and min/max
- Divergence from P50 as a formula
- Neutral positioning status
- Title-match and experience-match pools for senior categories

Use neutral status text:

```text
0% to 15% above P50: Expected 0-15% positioning range
15% to 40% above P50: FFP premium band, 15-40% above P50
More than 40% above P50: Above 40%; see stacked-factor arithmetic
Below P25: Below P25; review pool and input alignment
```

Do not use `Competitive`, `Reasonable`, `Defensible`, or `Outlier` as a status.

Document the CALC+ operation, exact buckets or keyword, and sample counts in Raw Data. The Methodology must state that keyword calls used `/v3/api/ceilingrates/` with `keyword=`.

## 6. Travel Detail

When no travel is required, retain this block:

```text
A1 Travel Detail: Not Applicable
A3 No travel required per PWS/SOW. Placeholder retained for contract-file completeness.
A4 If travel is later added, populate destination, nights, trips, and travelers.
```

When travel is required, use a 17-row block per destination. Block `i` starts at `1 + (i-1)*17`.

| Block 1 row | Label | Formula or value |
|---:|---|---|
| 1 | Travel Detail: [Destination] | Header |
| 3 | Fiscal Year | MCP input |
| 4 | Nightly Lodging Rate | MCP result |
| 5 | M&IE Daily Rate | MCP result |
| 6 | First/Last Day M&IE | MCP discounted result, already 75% |
| 7 | Nights per Trip | Editable input, zero for a day trip |
| 8 | Travel Days | `=IF(B7=0,1,B7+1)` |
| 9 | Lodging per Trip | `=B4*B7` |
| 10 | M&IE per Trip | `=IF(B7=0,B6,B5*MAX(0,B8-2)+B6*2)` |
| 11 | Trip Total | `=B9+B10` |
| 12 | Trips per Year | Editable input |
| 13 | Travelers | Editable input |
| 14 | Annual Travel Cost | `=B11*B12*B13` |

Do not multiply B6 by 0.75 again. The MCP already returns the discounted value.

Summary travel formulas must sum each destination block's Annual Travel Cost row. Retain the 0-night branches even if current trips are overnight.

## 7. Methodology and Raw Data

### Methodology

Write a concise contract-file methodology that covers:

- Pricing structure and scope basis
- Labor-category and SOC decisions
- BLS geography, percentile, vintage, and aging
- Wrap-rate basis and each cost pool
- FFP risk allocation without making a reasonableness determination
- CALC+ pool construction and positioning
- Travel method and fiscal-year fallback
- Multi-location and shift-coverage choices
- Exclusions and user-supplied assumptions
- FAR 15.402, FAR 15.404-1(a) and (b), FAR 15.404-4, and FAR 16.202

Tie every derived number in prose to a cell formula. Examples:

```excel
="Aging factor: "&TEXT('IGCE Summary'!B12,"0.0000")
="Implied multiplier: "&TEXT('Cost Buildup'!B19,"0.00x")
```

Do not hardcode a displayed aging factor, multiplier, FBR, total hours, or grand total into narrative text.

### Raw Data

Record compact reproducibility tables, not full JSON dumps. Include operation names, inputs, returned vintage, geography, SOC, percentiles, exact CALC+ buckets or keyword, sample counts, Per Diem locality and fiscal year, and every fallback or proxy.

## 8. Formatting and formula rules

- Blue font for editable hardcoded inputs
- Black font for formulas
- Bold headers with light gray fill
- Freeze Summary panes below row 13
- Currency formats with negative values in parentheses
- Percentages as `0.0%` unless precision requires `0.00%`
- Multipliers as `0.00"x"`
- Quoted cross-sheet references such as `='Cost Buildup'!B18`
- Numeric zeros in calculation ranges
- No text beginning with `=`, `+`, `-`, or `@` unless it is an intentional formula
- No formula errors, unintended circular references, or stale hardcoded narrative figures

Auto-size with sensible caps so headers and values remain readable.

## 9. Validation sidecar

Create a temporary JSON file that follows [validation-gates.md](validation-gates.md). Include:

- Raw rate assumptions
- Each labor line's annual wage, aging factor, hours, FTE, months, and escalation multiplier
- Non-labor amounts
- Expected FBR and total workbook cell references
- The grand-total cell reference
- Any additional exact formula assertions
- `annual_coverage_hours` on each shift-coverage labor line so independent recomputation can reject an incompatible FTE and productive-hours basis

Use the same raw source values that populated the workbook, not values read back from its formulas. Delete or retain the temporary file according to the host's normal temporary-file policy. Do not present it as a contract deliverable unless the user requests it.
