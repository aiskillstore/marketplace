---
id: "geometry-coordinate-systems"
title: "Coordinate systems and distance correctness"
category: "geospatial"
summary: "Choose units and coordinate models appropriate to spatial predicates, display and distance."
aliases: ["coordinate reference system","crs","geographic coordinates","great circle","lat lon","enlem boylamdan mesafe","koordinat sistemi","kilometre cinsinden uzaklık"]
decisions: [{"when":"Data spans broad geographic regions","use":"Use geography-aware distance or a geodesic calculation with explicit axis order and units.","tradeoff":"Some operations are more expensive and projections still matter for display."},{"when":"Data is limited to a known local area","use":"Use an appropriate projected coordinate system for planar analysis.","tradeoff":"Results depend on the projection's region and distortion characteristics."}]
checks: ["Verify distances with known reference points at multiple latitudes.","Cover longitude wrap and reject swapped or out-of-range coordinates."]
sources: [{"title":"PostGIS ST_DWithin","url":"https://postgis.net/docs/ST_DWithin.html"},{"title":"RFC 7946 GeoJSON","url":"https://www.rfc-editor.org/rfc/rfc7946"}]
---

<!-- Generated record title. -->
# Coordinate systems and distance correctness

## Scenario

A delivery app compares radius eligibility in kilometers across shops near the equator and far north.

## Failure modes

Euclidean distance on longitude and latitude degrees gives different scales by latitude. Axis order and crossing the date line can invalidate fixtures.

## Explain it simply

Store what the coordinates mean and calculate distance in a unit that is consistent across regions.

## Implementation guidance

Record the coordinate reference system and distance unit at the API boundary. GeoJSON positions are longitude then latitude, while planar distance requires a projection suited to the region. A nationwide or date-line-spanning radius query needs geography-aware handling. Use fixtures that deliberately swap axes, straddle the date line, and place close points at very different latitudes.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Data spans broad geographic regions** Use geography-aware distance or a geodesic calculation with explicit axis order and units. Some operations are more expensive and projections still matter for display.
- **Data is limited to a known local area** Use an appropriate projected coordinate system for planar analysis. Results depend on the projection's region and distortion characteristics.

## Verification

- Verify distances with known reference points at multiple latitudes.
- Cover longitude wrap and reject swapped or out-of-range coordinates.

## Sources

- [PostGIS ST_DWithin](https://postgis.net/docs/ST_DWithin.html)
- [RFC 7946 GeoJSON](https://www.rfc-editor.org/rfc/rfc7946)

<!-- End generated record details. -->
