---
id: "decimal-money"
title: "Exact money values and rounding boundaries"
category: "data"
summary: "Store monetary values without binary floating-point drift or ambiguous rounding."
aliases: ["money decimal","currency minor units","financial rounding","avoid floating point money","ledger cents","para hesabında kuruş yuvarlama","ondalık para hesaplama","kuruş kaybı"]
decisions: [{"when":"Currency uses well-defined minor units and rates are separate","use":"Store integer minor units with the currency and choose checked arithmetic for totals.","tradeoff":"Conversions and percentage calculations still need a rounding policy."},{"when":"Calculations require fractional accounting precision","use":"Use a decimal type with explicit scale and rounding at the agreed boundary.","tradeoff":"Database and application serialization must preserve the same representation."}]
checks: ["Assert that split amounts reconcile to the original total across rounding ties.","Test zero- and three-decimal currencies, negative refunds and configured bounds."]
sources: [{"title":"PostgreSQL numeric types","url":"https://www.postgresql.org/docs/current/datatype-numeric.html"},{"title":"Stripe currency minor units","url":"https://docs.stripe.com/currencies"}]
---

<!-- Generated record title. -->
# Exact money values and rounding boundaries

## Scenario

An invoicing service splits a discount across seats, applies tax and must preserve the total users see on the invoice.

## Failure modes

Currency scales differ. Independent per-line rounding can lose cents, and integer types encounter overflow when aggregated without a limit.

## Explain it simply

Use an exact representation and decide where rounding happens so line items still add to the displayed total.

## Implementation guidance

Represent amounts together with currency and choose the currency-specific unit at system boundaries. In a same-currency 100-cent allocation across three identical lines, one reproducible rule yields 34, 33 and 33 cents by assigning the leftover cent under a stable line order. Define when tax and discount round, and use checked addition and multiplication. Test fractional discounts, signed refunds, unsupported currency scales and totals near the storage limit.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Currency uses well-defined minor units and rates are separate** Store integer minor units with the currency and choose checked arithmetic for totals. Conversions and percentage calculations still need a rounding policy.
- **Calculations require fractional accounting precision** Use a decimal type with explicit scale and rounding at the agreed boundary. Database and application serialization must preserve the same representation.

## Verification

- Assert that split amounts reconcile to the original total across rounding ties.
- Test zero- and three-decimal currencies, negative refunds and configured bounds.

## Sources

- [PostgreSQL numeric types](https://www.postgresql.org/docs/current/datatype-numeric.html)
- [Stripe currency minor units](https://docs.stripe.com/currencies)

<!-- End generated record details. -->
