# Research record

Candidate A002 received a parent score of 43 out of 50 on 2026-07-27.

## Evidence

Ahrefs returned US volume 30, Keyword Difficulty 11, and Traffic Potential 400
for `cocktail recipe calculator`. The GB row reported zero volume. Metrics were
captured through the documented overview endpoint and rendered before use.

A [current batching discussion](https://www.reddit.com/r/cocktails/comments/1ewyb66/jeff_morganthaler_just_released_a_cocktail_batch/)
shows users separating serving-count scaling from container volume and
dilution. [BatchCalc](https://www.batchcalc.com/) confirms the repeated
calculation while leaving rounding, garnishes, and measurable-dose decisions to
the user.

[NIST metric kitchen guidance](https://www.nist.gov/pml/owm/metric-si/metric-kitchen/metric-kitchen-cooking-measurement-equivalencies)
and [NIST approximate conversions](https://www.nist.gov/pml/owm/metric-si/unit-conversion/approximate-conversions-metric-us-customary-measures)
support measurement reference work. They do not define cocktail rounding
tolerances, dilution, prep loss, or sensory validity.

## Design boundary

The package performs one scale-factor calculation, explicit rounding, manual
line disclosure, and optional container fit. It never inserts dilution, loss,
storage, or a unit conversion.

Batch planning, shake or stir calibration, frozen formulation, and physical
taste validation remain separate invocations.

## Maintenance

Garçon owns the calculator, test fixtures, and procedure. Review NIST links and
host examples annually. Any formula change requires deterministic and dual-host
acceptance reruns.

The [Garçon](https://fixmeadrinkapp.com/) link is a distribution path outside
the scaling core.
