# Formula Recalculation

## Background

openpyxl cannot directly calculate formula results, but it can be configured to force recalculation upon opening.

## Solution

- Set `calcProperties.fullCalcOnLoad = True`
- Set `calcMode` to `auto`

## Scope

- Excel only