---
name: stockpulse
description: Review manually entered SKU inventory, reorder thresholds, stock exposure, and estimated gross margin for small sellers.
---

# StockPulse

## Purpose
Help a small seller review a manually maintained inventory list and prioritize stock that may need replenishment.

## Workflow
1. Collect only the fields needed: SKU/name, on-hand quantity, reorder threshold, unit cost, selling price, and supplier note if useful.
2. Validate that quantities are non-negative and prices/costs use the same currency and unit.
3. Flag low stock when on-hand quantity is at or below the supplied reorder threshold.
4. Calculate estimated inventory cost value as quantity × unit cost.
5. Calculate estimated gross margin amount as selling price − unit cost and gross margin percentage as (selling price − unit cost) ÷ selling price when selling price is greater than zero.
6. Prioritize reorder candidates and explain the assumptions; do not invent lead times or demand forecasts.
7. Provide a clean CSV-ready summary if requested.

## Limits
- All data is manually entered. The companion browser app does not connect to ecommerce stores, marketplaces, accounting, suppliers, or purchase-order systems.
- Calculations exclude tax, shipping, refunds, discounts, shrinkage, and payment fees unless the user explicitly supplies those inputs.
- This is an operational estimate, not accounting or financial advice.
