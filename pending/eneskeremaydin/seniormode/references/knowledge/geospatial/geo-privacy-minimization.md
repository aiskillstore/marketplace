---
id: "geo-privacy-minimization"
title: "Location minimization and aggregation"
category: "geospatial"
summary: "Limit collection and precision according to the purpose of a location feature."
aliases: ["location privacy","location retention","spatial aggregation","coordinate precision","location permissions","konum verisini azaltma","hassas konum bilgisi saklama","anonim konum yoğunluğu"]
decisions: [{"when":"Aggregate spatial patterns meet product requirements","use":"Coarsen at collection or aggregation time, use retention bounds and avoid releasing sparse groups.","tradeoff":"Precision decreases, and coarsening is not a proof of anonymity."},{"when":"A specific user-facing action needs precise location briefly","use":"Use narrowly scoped consent and processing, minimize storage, and document deletion behavior.","tradeoff":"The feature must work or degrade gracefully when users decline."}]
checks: ["Exercise accepted and declined location permissions and verify data collection scope.","Verify sensitive raw samples and sparse aggregates are not exported through public paths."]
sources: [{"title":"W3C Geolocation specification","url":"https://www.w3.org/TR/geolocation/"},{"title":"NIST Privacy Framework","url":"https://www.nist.gov/privacy-framework"}]
---

<!-- Generated record title. -->
# Location minimization and aggregation

## Scenario

A neighborhood activity view needs aggregate hotspots but has no reason to store exact trip traces indefinitely.

## Failure modes

Precise tracks can identify people even without names. Sparse aggregates can expose individual routes and access settings can be broader than intended.

## Explain it simply

Collect only the location detail the feature needs and avoid publishing tiny groups that can identify someone.

## Implementation guidance

Start with the aggregate decision the activity view needs and choose a bin width, time bucket and minimum cohort size that fit it. Suppress sparse buckets and review combinations of outputs that could isolate one trip. If exact coordinates are used during ingestion, restrict access and keep a separate short retention rule. Test a bucket with one participant and successive overlapping windows, not just a well-populated district.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Aggregate spatial patterns meet product requirements** Coarsen at collection or aggregation time, use retention bounds and avoid releasing sparse groups. Precision decreases, and coarsening is not a proof of anonymity.
- **A specific user-facing action needs precise location briefly** Use narrowly scoped consent and processing, minimize storage, and document deletion behavior. The feature must work or degrade gracefully when users decline.

## Verification

- Exercise accepted and declined location permissions and verify data collection scope.
- Verify sensitive raw samples and sparse aggregates are not exported through public paths.

## Sources

- [W3C Geolocation specification](https://www.w3.org/TR/geolocation/)
- [NIST Privacy Framework](https://www.nist.gov/privacy-framework)

<!-- End generated record details. -->
