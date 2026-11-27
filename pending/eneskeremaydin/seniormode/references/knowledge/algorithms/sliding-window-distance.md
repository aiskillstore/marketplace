---
id: "sliding-window-distance"
title: "Sliding-window distance queries"
category: "algorithms"
summary: "Find best fixed-distance or fixed-threshold intervals using monotone boundaries and explicit interpolation."
aliases: ["sliding window","fastest kilometer","gps analytics","kayan pencere","running segment","GPS örneklerinden en hızlı kilometre","kayan pencereyle hız","koşu verisinde en hızlı bölüm"]
decisions: [{"when":"Cumulative distance is monotone and segments follow one path","use":"Use two pointers with deadline or distance constraints and interpolate elapsed time at boundaries.","tradeoff":"Noisy data and a chosen interpolation model determine real accuracy."},{"when":"Many ad hoc thresholds need repeated exact lookups","use":"Precompute prefix distance and timestamp arrays, then binary-search the boundary for each query.","tradeoff":"More indexing work can improve reuse but does not remove measurement uncertainty."}]
checks: ["Compare against a brute-force reference on small clean tracks.","Verify duplicate distances, holes in sampling and sub-sample boundaries."]
sources: [{"title":"Blelloch, Prefix Sums and Their Applications","url":"https://www.cs.cmu.edu/~guyb/papers/Ble93.pdf"},{"title":"NumPy linear interpolation and monotonically increasing sample points","url":"https://numpy.org/doc/stable/reference/generated/numpy.interp.html"}]
---

<!-- Generated record title. -->
# Sliding-window distance queries

## Scenario

A cycling app finds the fastest 500-meter segment of a ride using irregularly sampled GPS points with repeated stationary readings.

## Failure modes

Treating samples as equally spaced introduces error. Coordinates can jump and cumulative distance must stay monotone after filtering.

## Explain it simply

Move a start and end point forward together instead of restarting the calculation at every sample.

## Implementation guidance

Treat cumulative distance as a nondecreasing axis and elapsed time as a separate axis. A 500-m boundary often falls between samples, so define whether linear interpolation after filtering is appropriate for the product and handle flat distance intervals explicitly. Reject segments with gaps or location jumps outside your continuity policy. Test an exact boundary, a stop spanning several samples, a noisy jump, and a ride shorter than the target distance.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Cumulative distance is monotone and segments follow one path** Use two pointers with deadline or distance constraints and interpolate elapsed time at boundaries. Noisy data and a chosen interpolation model determine real accuracy.
- **Many ad hoc thresholds need repeated exact lookups** Precompute prefix distance and timestamp arrays, then binary-search the boundary for each query. More indexing work can improve reuse but does not remove measurement uncertainty.

## Verification

- Compare against a brute-force reference on small clean tracks.
- Verify duplicate distances, holes in sampling and sub-sample boundaries.

## Sources

- [Blelloch, Prefix Sums and Their Applications](https://www.cs.cmu.edu/~guyb/papers/Ble93.pdf)
- [NumPy linear interpolation and monotonically increasing sample points](https://numpy.org/doc/stable/reference/generated/numpy.interp.html)

<!-- End generated record details. -->
