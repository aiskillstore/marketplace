---
id: "road-traffic-estimation"
title: "Traffic estimation from location samples"
category: "geospatial"
summary: "Estimate road-segment slowdown from noisy location measurements without overclaiming certainty."
aliases: ["traffic estimation","gps probes","crowdsourced traffic","trafik tespiti","vehicle speed","trafik sıkışıklığını telefon konumlarından tahmin","araç hızı GPS"]
decisions: [{"when":"Enough credible samples arrive for each segment","use":"Map-match samples, aggregate robust window statistics and compare with time-of-day baselines.","tradeoff":"Accuracy depends on coverage and careful control of correlated observations."},{"when":"Coverage is low or collection is unnecessary","use":"Use historic or public traffic estimates and mark the freshness and confidence.","tradeoff":"The result may miss incidents that have just started."}]
checks: ["Simulate duplicate passengers, stationary points and a genuine traffic delay.","Verify sparse windows and retention limits produce the expected output."]
sources: [{"title":"OSRM HTTP API and map matching","url":"https://project-osrm.org/docs/v5.24.0/api/#match-service"},{"title":"Herrera et al., Mobile Century field experiment with GPS probe vehicles","url":"https://bayen.berkeley.edu/sites/default/files/tr_c09_v2.pdf"}]
---

<!-- Generated record title. -->
# Traffic estimation from location samples

## Scenario

A fleet operator wants alerts on sudden slowdown across delivery routes using only consenting fleet vehicle observations.

## Failure modes

Stationary phones and groups in the same vehicle bias aggregates. Sparse windows, GPS errors and route mis-matching produce false alerts.

## Explain it simply

Compare recent vehicle speeds with normal speeds for that road and show uncertainty when observations are sparse.

## Implementation guidance

Attach uncertainty to each map-matched observation and aggregate only sufficiently supported windows for a defined road segment and direction. Exclude stationary or duplicate samples using documented rules and compare to a same-weekday local baseline. Treat stale or sparse inputs as unknown instead of normal traffic. Replay a known rush-hour slowdown, a GPS jump near parallel roads and a cluster of devices travelling together.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Enough credible samples arrive for each segment** Map-match samples, aggregate robust window statistics and compare with time-of-day baselines. Accuracy depends on coverage and careful control of correlated observations.
- **Coverage is low or collection is unnecessary** Use historic or public traffic estimates and mark the freshness and confidence. The result may miss incidents that have just started.

## Verification

- Simulate duplicate passengers, stationary points and a genuine traffic delay.
- Verify sparse windows and retention limits produce the expected output.

## Sources

- [OSRM HTTP API and map matching](https://project-osrm.org/docs/v5.24.0/api/#match-service)
- [Herrera et al., Mobile Century field experiment with GPS probe vehicles](https://bayen.berkeley.edu/sites/default/files/tr_c09_v2.pdf)

<!-- End generated record details. -->
