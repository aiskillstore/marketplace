# OT Authority and Cost-Sharing Reference

Use the statute and current DoD guidance as the controlling sources. This reference prevents an analytical workbook from silently making an Agreements Officer decision.

## 1. Authority map

### 10 U.S.C. 4021 Research OT

- Applies to basic, applied, and advanced research projects.
- Under subsection (e)(2), to the extent the Secretary determines practicable, Government funds should not exceed the total amount provided by other parties.
- This is not an automatic 50/50 rule, and it is not authority to default to 100% Government funding.
- Require the user-supplied, approved contribution arrangement and record its rationale and source.

### 10 U.S.C. 4022 Prototype OT

Require the user or Agreements Officer to identify one subsection (d)(1) condition:

| Path | Statutory condition | Workbook handling |
|---|---|---|
| A | At least one nontraditional defense contractor or nonprofit research institution participates to a significant extent | Record the participant and user-supplied basis. Do not decide significance. No statutory ratio follows from Path A alone. |
| B | All significant non-Government participants are small businesses or nontraditional defense contractors | Record the participant list and user-supplied status. No statutory ratio follows from Path B alone. |
| C | At least one-third of total prototype-project cost is paid from non-Federal sources | Require performer ratio `>= 1/3` of total project cost. Reject `0.33` if it rounds below exactly one-third. |
| D | The senior procurement executive determines in writing that exceptional circumstances justify the OT | Record the determination date or `PENDING`; do not invent it. No statutory ratio follows from Path D alone. |

There is no 4022(d)(1)(D) competition-commitment path.

### 10 U.S.C. 4022(f) Follow-On Production

- Section 4022(d) does not apply to a follow-on production contract or transaction under subsection (f).
- Do not carry the prototype ratio automatically. Do not set the production ratio to zero automatically. Use the negotiated arrangement supplied by the user.
- Record, without deciding, whether the user states that competitive procedures selected the prototype participants and that the relevant participant successfully completed the prototype.
- Do not originate the follow-on eligibility finding or characterize a prototype as successfully completed.

## 2. Cost-share denominator and reconciliation

The approved performer ratio applies to total project cost, not only to the Government-requested payment.

```text
total project cost = Government project share + performer project share
performer share    = total project cost * performer ratio
Government share   = total project cost - performer share
```

For 4022 Path C:

```text
performer ratio >= 1 / 3
Government ratio <= 2 / 3
```

Keep cash and in-kind contributions visible. Record the source, valuation method, timing, and tracking responsibility for in-kind contributions. Do not treat an undocumented asserted value as validated.

## 3. Proposed-amount normalization

Confirm one basis for each submitted amount:

- Total project cost
- Requested Government funding
- Fixed milestone payment
- Cost-type estimated cost
- Cost-type ceiling
- Consortium or administrative fee

Normalize before comparison. For example, a Government funding request under a one-third performer share is not comparable to the workbook's total project cost without converting one side.

## 4. Fees

Do not default a consortium or administrative fee. Require:

- Percentage or fixed amount
- Cost base
- Per-milestone, one-time, or other timing
- Whether the fee is Government-paid, shared, or included in total project cost
- Source document or user approval

The workbook's default fee input is zero. A fee added after project-cost shares must not be presented as part of the statutory Path C denominator unless the user supplies that treatment.

## 5. Price-reasonableness boundary

The workbook may report:

- Proposed and normalized amount bases
- Dollar and percentage variances
- BLS and CALC+ benchmark positions
- Analogous-price comparisons
- Low, working, and high scenario positions
- Sensitivity to labor, material, schedule, cost share, and fee assumptions

It may not originate a conclusion that a price is fair, reasonable, acceptable, justified, competitive, aggressive, or premium. The Agreements Officer owns the conclusion and negotiation position.

For controlled memo fill, reproduce the user's rationale and determination verbatim, label it `DRAFT - USER-SUPPLIED DETERMINATION TEXT`, and keep the neutral analysis distinct.

## 6. Primary sources

- 10 U.S.C. 4021, Research projects: transactions other than contracts and grants
- 10 U.S.C. 4022, Authority of the Department of Defense to carry out certain prototype projects
- DoD Other Transaction Guide, OUSD(A&S), July 2023, Version 2.0
- Guide to Research Other Transactions, OUSD(R&E), February 2026
