# Method Selection Rules

## Fit checks
For every recommendation, ask:
- Does it fit the scientific question?
- Does it fit the data type?
- Does it fit the likely sample size?
- Does it fit the interpretability requirement?
- Does it fit the user’s validation reality?
- Do published downstream use papers support its directional relevance, or is the fit still mostly theoretical?

## Downgrade when needed
Downgrade or reject a method if:
- it is recent but poorly matched to the project
- it demands large-scale labels that the project likely lacks
- it creates black-box complexity without meaningful biological gain
- it does not improve on a simpler baseline in a way that matters
- it has a valid identity paper but no convincing downstream use signal for similar directions and the fit claim would otherwise be overstated

## Explicit comparison requirement
Always distinguish:
- baseline comparator
- primary matched recommendation
- frontier upgrade

## Honesty rule
A recent method may be impressive yet still be the wrong recommendation.
A real primary method paper does not automatically mean the algorithm is directionally appropriate.
