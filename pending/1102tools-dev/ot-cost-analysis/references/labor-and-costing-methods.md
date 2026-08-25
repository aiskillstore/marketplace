# OT Labor and Costing Methods

## 1. Labor basis

Use per-category labor as the canonical method:

```text
direct hourly benchmark = aged annual wage / 2,080
burdened benchmark      = direct hourly benchmark * approved burden multiplier
category hours          = supplied hours, or productive hours * FTE * duration / 12
category cost           = category hours * burdened benchmark
milestone labor         = sum(category cost)
```

Do not use 1,880 productive hours to convert annual BLS wages to hourly. Use 2,080 for wage conversion and the user-approved productive-hours value for staffing capacity.

Use a blended labor rate only for an explicitly approved early planning approximation. Preserve the category mix used to calculate it.

## 2. Staffing and milestone duration

Prefer user-supplied hours or milestone staffing. When deriving a model:

- Give every category a workload, deliverable, coverage, system, site, quantity, or schedule basis.
- Keep performer and location tags on every line.
- Show ramp, overlap, transition, and surge separately.
- Reconcile milestone durations to the total period of performance. When the sum differs by more than 10 percent, stop and ask whether gaps are unstaffed or whether staffing spans the full period.
- Never invent a specialty premium, clearance factor, academic billing range, or team-size table as a fact.

For a 24x7x365 seat:

```text
annual coverage hours = seats * 24 * 365
coverage FTE          = annual coverage hours / productive hours per FTE
```

At 1,880 productive hours, one seat is 4.6596 FTE.

## 3. Institutional performers

When a university, FFRDC, UARC, laboratory, or other institution supplies billing rates or an approved indirect structure, use those values as inputs and record the source. BLS remains a market context or proxy when appropriate, not a substitute for an institutional rate.

Do not claim that all such institutions have a common burden range. Do not assume fee or profit treatment.

## 4. Materials and production

Use a bill of material, quote, analogous buy, quantity estimate, engineering build-up, or user-approved planning factor. Record quantity, unit, source date, and escalation basis.

Default time basis:

```text
escalated materials = base materials * (1 + approved annual rate)^(months from project start / 12)
```

Use a learning curve only when the user supplies or approves:

- Curve method, such as unit or cumulative-average
- Slope
- Lot or unit sequence
- Recurring-cost base
- Excluded nonrecurring cost

No universal 95-percent curve exists.

## 5. Cost-type milestone view

For a cost-type milestone, show:

1. Independent should-cost
2. User-approved estimated-cost or ceiling basis
3. Government and performer shares at the should-cost basis
4. Maximum Government and planned performer exposure at the ceiling basis

The ceiling view is a planning maximum, not actual incurred cost. Both shares must branch on the same ceiling basis or they will not reconcile.

## 6. Funding timing

Do not default every OT to obligation-at-start or payment-at-acceptance. Require the user-supplied convention by milestone and fiscal year. Distinguish:

- Planned obligation
- Milestone payment
- Cost reimbursement
- Holdback or retainage
- Fee payment
- Performer contribution timing

The cumulative funding profile sums the Government funding requirement using the approved timing convention.

## 7. Scenarios

Keep scenario assumptions editable and sourced. Vary the components that drive uncertainty:

- Labor burden or approved indirect rates
- Staffing or hours
- Materials quantities and unit prices
- Escalation
- Travel frequency
- Ceiling margin
- Performer ratio when the Agreements Officer specifically requests sensitivity
- Fee basis

Do not label scenario positions with conclusions such as competitive or premium. Report the proposed amount's numerical position in the range.
