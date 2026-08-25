# Cost Pool and Fee Reference

Use this reference only after the user confirms the indirect-rate basis and CR type. These are estimating assumptions, not approved contractor rates.

## Indirect-cost scenarios

| Component | Low | Mid | High | Application base |
|---|---:|---:|---:|---|
| Fringe | 25% | 32% | 40% | Direct labor |
| Overhead | 60% | 80% | 120% | Direct labor plus fringe |
| G&A | 8% | 12% | 18% | Labor plus fringe plus overhead |
| FCCM | 0% | 0% | 0.5% | Subtotal plus G&A |

Use FCCM only with a CO-supplied basis tied to FAR 31.205-10 and CAS 414. If the user supplies an FPRA, FPRR, or audited indirect rates, use those rates as the point estimate and document the effective date and approving authority. Do not create artificial low and high offsets around audited rates.

## Fee-bearing classification

Classify every cost element before calculating fee.

| Cost element | Default estimating treatment | Required action |
|---|---|---|
| Contractor labor and allocable indirects | Fee-bearing | Confirm with the selected fee structure |
| Contractor-developed deliverable or managed subcontract | Undetermined | Ask the user |
| Travel reimbursed at government rates | Non-fee-bearing pass-through | Disclose and allow the user to override |
| Commercial license or third-party hardware at cost | Non-fee-bearing pass-through | Disclose and allow the user to override |
| Government-furnished-equivalent material | Non-fee-bearing | Keep outside the fee base |

Never infer that all ODCs bear fee. Keep fee-bearing cost, non-fee-bearing cost, total estimated cost, fee, and total estimated price as separate workbook lines.

## CPFF

Record Completion or Term form.

```text
fixed fee = confirmed fee-bearing estimated cost * fixed-fee rate
total estimated price = total estimated cost + fixed fee
```

The fixed fee is set at award and does not vary with actual incurred cost, except for changes in the work. Workbook low, mid, and high calculations are alternative Government estimate scenarios, not a formula for paying fee as actual cost changes.

Apply the current FAR 15.404-4(c)(4)(i) ceilings:

- 15% for experimental, developmental, or research CPFF work.
- 10% for other CPFF work.
- The separate 6% architect-engineer limitation when applicable.

Do not treat any ceiling as a recommended rate.

## CPAF

```text
base fee = fee-bearing estimated cost * base-fee rate
award pool = fee-bearing estimated cost * award-pool rate
assumed earned award fee = award pool * assumed-earned percentage
estimated fee = base fee + assumed earned award fee
```

Show all three outcomes:

1. Base fee only.
2. Base fee plus assumed-earned pool, default 85% when the user accepts it.
3. Base fee plus full award pool.

Describe the 85% case as an estimating assumption, never as an expected performance judgment.

## CPIF

Keep overrun and underrun contractor shares separate.

```text
target fee = target fee-bearing cost * target-fee rate

overrun fee = target fee
              - (actual fee-bearing cost - target fee-bearing cost)
              * contractor overrun share
overrun fee = max(overrun fee, target fee-bearing cost * minimum-fee rate)

underrun fee = target fee
               + (target fee-bearing cost - actual fee-bearing cost)
               * contractor underrun share
underrun fee = min(underrun fee, target fee-bearing cost * maximum-fee rate)
```

Run at least target, 10% overrun, and 10% underrun. Also run a wide-enough case, often 25%, to show each fee bound if the inputs permit. State the exact cost at which each bound takes effect.

## Scenario rules

- Use low, mid, and high indirect-cost scenarios only when the rates are estimating assumptions.
- When audited rates control, use the audited point estimate across the primary workbook and show sensitivity only if the user requests it.
- Keep travel and pass-through classifications constant across scenarios.
- Recompute fee on each Government estimate scenario using that scenario's confirmed fee-bearing base.
- In every scenario, show both estimated cost and estimated price. Do not call estimated price `cost`.
