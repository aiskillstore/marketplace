---
id: "knapsack-dp"
title: "Knapsack and capacity-bounded optimization"
category: "algorithms"
summary: "Select indivisible items under a capacity constraint when simple greedy ordering is insufficient."
aliases: ["knapsack","dynamic programming","capacity selection","dinamik programlama","bagaj problemi","ağırlık sınırı","çantaya en değerli eşyaları sığdırma","kapasiteye göre seçim"]
decisions: [{"when":"Capacity is a manageable discrete integer","use":"Use descending-capacity 0/1 dynamic programming and keep reconstruction data if needed.","tradeoff":"Runtime depends on numeric capacity, so changing units can change cost substantially."},{"when":"Capacity is large or the constraints are richer","use":"Consider a solver, meet-in-the-middle for small item sets, or a documented approximation.","tradeoff":"More dependencies or approximate optimality require explicit need."}]
checks: ["Compare with exhaustive enumeration for small test sets.","Cover zero capacity, an item heavier than capacity and reconstruction ties."]
sources: [{"title":"NIST dictionary entry on knapsack","url":"https://www.nist.gov/dads/HTML/knapsackProblem.html"},{"title":"Google OR-Tools knapsack","url":"https://developers.google.com/optimization/pack/knapsack"}]
---

<!-- Generated record title. -->
# Knapsack and capacity-bounded optimization

## Scenario

A rescue kit has a fixed weight budget. Each indivisible component contributes a different score and may be picked once.

## Failure modes

Ratio sorting is not exact for 0/1 choices. One-dimensional DP updated forward silently allows reusing items and very large capacity makes the table impractical.

## Explain it simply

Compare which combinations fit in each capacity instead of choosing the most expensive or lightest item first.

## Implementation guidance

For capacity 10 and one weight-3 item of value 5, an ascending one-dimensional update incorrectly builds value 15 by using that item three times. Update the capacity states from high to low for each item. When the chosen items matter, retain stage-aware parent information or rebuild against the decision table to avoid following states overwritten by later items. Reject units that turn the capacity into an impractically large state space and cross-check small inputs by enumerating subsets.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Capacity is a manageable discrete integer** Use descending-capacity 0/1 dynamic programming and keep reconstruction data if needed. Runtime depends on numeric capacity, so changing units can change cost substantially.
- **Capacity is large or the constraints are richer** Consider a solver, meet-in-the-middle for small item sets, or a documented approximation. More dependencies or approximate optimality require explicit need.

## Verification

- Compare with exhaustive enumeration for small test sets.
- Cover zero capacity, an item heavier than capacity and reconstruction ties.

## Sources

- [NIST dictionary entry on knapsack](https://www.nist.gov/dads/HTML/knapsackProblem.html)
- [Google OR-Tools knapsack](https://developers.google.com/optimization/pack/knapsack)

<!-- End generated record details. -->
