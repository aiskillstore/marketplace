# CR Workbook Specification

Build one `.xlsx` workbook with seven sheets in this order:

1. `IGCE Summary`
2. `Cost Buildup`
3. `Scenario Analysis`
4. `Rate Validation`
5. `Travel Detail`
6. `Methodology`
7. `Raw Data`

Include `Travel Detail` even when travel is zero. Put `Travel Not Applicable` and numeric zero in the total cell so summary formulas retain a valid target.

## 1. IGCE Summary

### Assumption block

Use these exact cells so the validator can inspect the aging formula:

| Cell | Label or value |
|---|---|
| A1:B1 | `IGCE Assumptions (Cost-Reimbursement)` |
| A2 / B2 | Fringe Rate / decimal input |
| A3 / B3 | Overhead Rate / decimal input |
| A4 / B4 | G&A Rate / decimal input |
| A5 / B5 | FCCM Rate / decimal input |
| A6 / B6 | Escalation Rate / decimal input |
| A7 / B7 | Productive Hours per Year / numeric input |
| A8 / B8 | Base Year Months / numeric input |
| A9 / B9 | BLS Vintage / `YYYY-MM` text input |
| A10 / B10 | Contract Start / `YYYY-MM` text input |
| A11 / B11 | Months Gap / formula below |
| A12 / B12 | Aging Factor / formula below |
| A13 / B13 | Fee Type / `CPFF`, `CPAF`, or `CPIF` |
| A14 / B14 | Primary Fee Rate / CPFF fixed, CPAF base, or CPIF target |
| A15 / B15 | Award Pool Rate or Contractor Overrun Share |
| A16 / B16 | Assumed Earned Percentage or Contractor Underrun Share |
| A17 / B17 | Minimum Fee Rate, blank when not applicable |
| A18 / B18 | Maximum Fee Rate, blank when not applicable |

Use these formulas:

```excel
B11 =MAX(0,(VALUE(LEFT(B10,4))-VALUE(LEFT(B9,4)))*12+VALUE(MID(B10,6,2))-VALUE(MID(B9,6,2)))
B12 =(1+B6)^(B11/12)
```

Format B12 as `0.0000`. Never use `YEAR(B9)`, `YEAR(B10)`, or `DATEDIF` on text.

### Summary table

Start at row 20. Show each labor category, SOC, location, FTE, hours, base and option-period estimated cost, fee-bearing cost, non-fee-bearing cost, fee, and estimated price. Label every amount as `Estimated Cost`, `Fee`, or `Estimated Price` correctly.

Keep separate rows for:

- Labor and allocable indirects
- Travel
- Fee-bearing ODCs or managed subcontracts
- Non-fee-bearing pass-through ODCs
- Total estimated cost
- Fee-bearing base
- Fee
- Total estimated price

Never apply a fee formula directly to total estimated cost unless that total equals the confirmed fee-bearing base.

## 2. Cost Buildup

Use a fixed 23-row block for every labor category. Block `N` begins at:

```text
base row = 1 + (N - 1) * 23
```

| Offset | Label | Formula or input |
|---:|---|---|
| 0 | `Cost Buildup: <LCAT>` | header |
| 1 | BLS Base Annual Wage | source input |
| 2 | Aging Factor | `='IGCE Summary'!$B$12` |
| 3 | Aged Annual Wage | base wage times aging factor |
| 4 | Direct Labor Rate Hourly | aged wage divided by 2,080 |
| 5 | blank | separator |
| 6 | Fringe Rate | `='IGCE Summary'!$B$2` |
| 7 | Fringe Amount | direct rate times fringe |
| 8 | Labor plus Fringe | direct plus fringe |
| 9 | Overhead Rate | `='IGCE Summary'!$B$3` |
| 10 | Overhead Amount | labor plus fringe times overhead |
| 11 | Subtotal | labor plus fringe plus overhead |
| 12 | G&A Rate | `='IGCE Summary'!$B$4` |
| 13 | G&A Amount | subtotal times G&A |
| 14 | FCCM Rate | `='IGCE Summary'!$B$5` |
| 15 | FCCM Amount | subtotal plus G&A, times FCCM |
| 16 | Estimated Cost Rate | subtotal plus G&A plus FCCM |
| 17 | Fee Type | `='IGCE Summary'!$B$13` |
| 18 | Primary Fee Rate | `='IGCE Summary'!$B$14` |
| 19 | Estimated Fee Rate | fee-type formula |
| 20 | Estimated Price Rate | estimated cost plus estimated fee |
| 21 | Implied Multiplier | estimated price divided by direct hourly |
| 22 | blank | block separator |

For the first block, Direct Labor Rate Hourly is row 5. Cross-sheet formulas must reference row 5, not row 4, which is Aged Annual Wage.

Fee-rate formulas by type:

- CPFF: estimated cost rate times B14.
- CPAF: estimated cost rate times `(B14 + B15 * B16)`.
- CPIF target: estimated cost rate times B14. Put overrun, underrun, and bound mechanics on `Scenario Analysis` rather than hiding them in the labor block.

## 3. Scenario Analysis

Show low, mid, and high indirect-rate cases. Include component assumptions at the top, cost, fee-bearing base, non-fee cost, fee, and estimated price.

For CPAF, show within every cost scenario:

- Base fee only
- Base plus assumed-earned award pool
- Base plus full award pool

For CPIF, show a matrix with cost scenarios as columns and underrun, target, and overrun outcomes as rows. Include separate overrun and underrun contractor shares, min and max fee, and the first outcome where a bound applies.

For CPFF, label the scenarios as alternative Government estimate cases. Do not imply the negotiated fixed fee later floats with actual incurred cost.

## 4. Rate Validation

Use columns for labor category, BLS estimated cost rate, BLS estimated cost plus fee, CALC+ P25, P50, P75, P90, sample size, arithmetic divergence, and neutral note.

When a comparison pool is thin or contaminated, add title-match and experience-match columns with separate sample sizes. Do not write `reasonable`, `acceptable`, `competitive`, `outlier`, or a negotiation recommendation.

## 5. Travel Detail

Use a 17-row block per destination and sum each block into the Summary. For a day trip, use zero lodging and one already-discounted first/last-day M&IE amount. For overnight trips, calculate first and last day at 75% and intervening days at the full rate.

Include a `Fee-Bearing?` input for each destination. Default pass-through travel to `No` when the user has not directed otherwise, and disclose the assumption.

## 6. Methodology

Keep the narrative concise and auditable. Include:

- CR type and, for CPFF, Completion or Term form
- Regulatory sources and applicable fee ceiling
- Labor/SOC mapping and seniority convention
- BLS vintage, metro, series inputs, aging, and escalation
- Indirect-rate source, including audited-rate authority and effective date
- FCCM basis or explicit zero
- Fee-bearing classifications
- CPAF or CPIF scenario mechanics when applicable
- CALC+ pool construction and limitations
- Travel assumptions and fiscal year
- Coverage math, if applicable
- Exclusions and user-approved overrides
- Formula-validation layers actually run

Do not state that the workbook proves cost realism, fair and reasonable pricing, or contractor accounting-system adequacy.

## 7. Raw Data

Record compact reproducible parameters and result summaries, not full JSON dumps. Include BLS series inputs and selected percentiles, CALC+ query and pool statistics, Per Diem locality and rates, every fallback, and the source of user-supplied rates.

## Formatting and safety

- Blue font for user-editable inputs; black for formulas.
- Currency: `$#,##0.00` or `$#,##0` consistently.
- Percentage: `0.0%`; aging factor: `0.0000`.
- Freeze panes below assumption and header blocks.
- Escape text beginning with `=`, `+`, `-`, or `@` so Excel does not parse it as a formula.
- Use numeric zero, never text `TBD`, in formula ranges.
- Autosize columns within readable limits and wrap long notes.
