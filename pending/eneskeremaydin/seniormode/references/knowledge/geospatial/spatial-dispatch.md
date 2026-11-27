---
id: "spatial-dispatch"
title: "Spatial indexes for driver dispatch"
category: "geospatial"
summary: "Narrow driver candidates spatially before evaluating travel time and availability."
aliases: ["h3","geospatial index","driver matching","yakındaki araç","hexagonal cells","en yakın aracı eşleştir","altıgen hücre koordinatları","coğrafi indeks"]
decisions: [{"when":"Regular grid cells fit update and lookup patterns","use":"Index live locations by cell and expand neighboring rings within a search budget.","tradeoff":"Resolution trades index churn for candidate volume."},{"when":"Accuracy depends on geographic predicates","use":"Use a geographic database index and radius query before route-time ranking.","tradeoff":"More precise geometry costs more and still needs fresh availability."}]
checks: ["Compare candidates against a brute-force oracle near cell boundaries.","Cover stale pings, isolated regions and a river crossing."]
sources: [{"title":"H3 grid traversal","url":"https://h3geo.org/docs/api/traversal/"},{"title":"PostGIS ST_DWithin","url":"https://postgis.net/docs/ST_DWithin.html"}]
---

<!-- Generated record title. -->
# Spatial indexes for driver dispatch

## Scenario

A campus shuttle dispatcher must choose from live vehicle locations, including vehicles just across an index cell boundary.

## Failure modes

A fixed cell ring can miss nearby vehicles at borders or in sparse areas. Straight-line proximity and road travel time differ across barriers.

## Explain it simply

Look in nearby areas first, then estimate which available vehicle can actually arrive soonest.

## Implementation guidance

Use geographic search to build candidates and road travel time, eligibility and observation freshness for final ranking. Include adjacent cells or expand the search radius until its explicit budget, and expose when that budget prevents a global optimum guarantee. Check a vehicle closer across a cell boundary, one across an impassable river and one with stale location whose apparent distance is deceptively small.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Regular grid cells fit update and lookup patterns** Index live locations by cell and expand neighboring rings within a search budget. Resolution trades index churn for candidate volume.
- **Accuracy depends on geographic predicates** Use a geographic database index and radius query before route-time ranking. More precise geometry costs more and still needs fresh availability.

## Verification

- Compare candidates against a brute-force oracle near cell boundaries.
- Cover stale pings, isolated regions and a river crossing.

## Sources

- [H3 grid traversal](https://h3geo.org/docs/api/traversal/)
- [PostGIS ST_DWithin](https://postgis.net/docs/ST_DWithin.html)

<!-- End generated record details. -->
