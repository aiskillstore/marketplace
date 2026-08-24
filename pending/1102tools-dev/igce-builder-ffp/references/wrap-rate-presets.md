# Wrap Rate Presets and Selection Rules

Use this reference to select the MID indirect-rate basis and to create sensitivity scenarios. Treat every preset as a planning assumption, not an audited contractor rate.

## Contents

1. Selection order
2. Component guidance
3. Vehicle and environment presets
4. Custom and audited rates
5. Scenario construction
6. Arithmetic checks

## 1. Selection order

Apply rate sources in this order:

1. CO-supplied DCAA-audited or otherwise approved rates
2. CO-supplied planning rates
3. A vehicle or environment preset selected with the user
4. Generic component guidance only when no better basis exists

Ask about the contract vehicle and operating environment before selecting a preset. Do not silently apply the generic 32% fringe, 80% overhead, 12% G&A, and 10% profit combination.

## 2. Component guidance

Use this table as a sensitivity envelope, not as the automatic MID case.

| Component | Low | Generic mid | High | Planning note |
|---|---:|---:|---:|---|
| Fringe | 25% | 32% | 40% | Benefits, leave, payroll tax, workers' compensation |
| Overhead | 60% | 80% | 120% | Facilities, supervision, security, shared delivery support |
| G&A | 8% | 12% | 18% | Corporate management and business operations |
| Profit | 7% | 10% | 15% | Risk, investment, complexity, and contract terms |

The generic mid produces an implied multiplier of about 2.93x and aligns most closely with a non-cleared DoD prime environment. It is not the GSA MAS commercial preset.

## 3. Vehicle and environment presets

| Vehicle or environment | Fringe | Overhead | G&A | Profit | Implied multiplier | Expected MID band |
|---|---:|---:|---:|---:|---:|---:|
| GSA MAS commercial | 30% | 60% | 10% | 8% | 2.47x | 2.3x to 2.7x |
| GSA MAS cleared services | 32% | 80% | 12% | 8% | 2.87x | 2.7x to 3.1x |
| Agency BPA or IDIQ, non-cleared | 32% | 75% | 12% | 10% | 2.85x | 2.7x to 3.1x |
| Agency BPA or IDIQ, cleared | 32% | 95% | 12% | 10% | 3.17x | 3.0x to 3.4x |
| DoD BPA, TS/SCI SCIF | 32% | 115% | 13% | 10% | 3.39x | 3.2x to 3.6x |
| DoD prime, non-cleared | 32% | 80% | 12% | 10% | 2.93x | 2.7x to 3.1x |
| DoD prime, Secret non-SCIF | 32% | 100% | 12% | 10% | 3.25x | 3.0x to 3.4x |
| DoD prime, SCIF or deployed | 32% | 120% | 14% | 10% | 3.64x | 3.5x to 3.8x |
| DoE M&O or FFRDC | 35% | 95% | 12% | 8% | 3.18x | 3.0x to 3.4x |
| R&D or BAA cost-reimbursement planning | 32% | 90% | 12% | 8% | 3.03x | 2.9x to 3.3x |
| OCONUS or hostile theater planning | 35% | 120% | 14% | 12% | 3.79x | 3.6x to 4.0x |

Selection signals:

- GSA MAS commercial: ordinary commercial professional services without dedicated cleared facilities.
- Agency BPA or IDIQ cleared: recurring cleared delivery under an agency vehicle.
- DoD SCIF: dedicated secure space, cleared administration, and security infrastructure.
- DoE M&O or FFRDC: higher institutional overhead and fringe, often with lower profit.
- R&D or BAA cost-reimbursement: use the CR skill for the actual estimate. Retain this row only for comparison or a later FFP conversion explicitly requested by the user.
- OCONUS: this skill does not supply State Department per diem or theater-specific costs. Treat the preset as a labor-wrap planning reference only.

## 4. Custom and audited rates

When the CO supplies explicit planning rates:

- Use them as the MID case.
- Create LOW and HIGH around them only if the user wants sensitivity analysis.
- Label the CO-supplied rates as the authoritative planning basis.
- Do not replace them with the nearest preset.

When the CO supplies rates from an FPRA, approved disclosure statement review, bilateral agreement, or another audited basis:

- Use the supplied rates as a single authoritative point estimate.
- Do not create fictional LOW and HIGH cases around the audited rates.
- If a sensitivity display is required, label it "Sensitivity display only; approved rates remain authoritative."
- Record the effective date, approving authority, and cost-pool composition.
- Note a material divergence from the planning preset, but do not reconcile the approved rate to the preset.

## 5. Scenario construction

For a planning MID preset, create LOW and HIGH by moving each component rather than applying a single multiplier. A default planning offset is about 20% of each component rate:

```text
low component  = mid component * 0.80
high component = mid component * 1.20
```

Do not let a component fall below zero. Keep travel unchanged across scenarios because per diem is a published cost, not an indirect-rate assumption.

Check only the MID multiplier against the preset's expected band. A HIGH sensitivity case may legitimately exceed the band.

## 6. Arithmetic checks

Calculate the implied multiplier as:

```text
(1 + fringe) * (1 + overhead) * (1 + G&A) * (1 + profit)
```

Recompute every table multiplier from the component cells in the workbook. Do not type the displayed multiplier as a fixed value. Tie the Methodology display to the calculated workbook cell.

If the MID multiplier falls outside its selected row's expected band, ask the user to review the rate basis and document the source factors. Do not call the result unreasonable.
