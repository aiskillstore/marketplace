---
id: "responsive-table"
title: "Responsive tables and usable data views"
category: "frontend"
summary: "Preserve relationships in dense tabular data while keeping narrow layouts navigable."
aliases: ["responsive table","mobile data table","column visibility","accessible grid","table overflow","mobilde geniş tablo","tablo yatay kaydırma","tablo başlıkları erişilebilirliği"]
decisions: [{"when":"Comparing columns is the main task","use":"Keep semantic table markup with labeled horizontal scrolling and sticky headers where appropriate.","tradeoff":"A small viewport still limits simultaneous context."},{"when":"Reviewing one record is the main mobile task","use":"Offer a compact detail view with clear labels and a route back to the table.","tradeoff":"Maintaining two layouts requires shared data and behavior."}]
checks: ["Test ties between headers and cells with a screen reader.","Verify all required information is reachable at narrow width and high zoom."]
sources: [{"title":"WAI-ARIA table pattern","url":"https://www.w3.org/WAI/ARIA/apg/patterns/table/"},{"title":"W3C Understanding Reflow, data table example","url":"https://www.w3.org/WAI/WCAG22/Understanding/reflow.html"}]
---

<!-- Generated record title. -->
# Responsive tables and usable data views

## Scenario

An operations dashboard compares names, statuses and twelve readings per row on a mobile phone.

## Failure modes

Turning cells into arbitrary cards can remove header associations. Hiding columns by default may hide data required for a decision.

## Explain it simply

Keep the relationships between values and headings clear even when only part of the table fits on the screen.

## Implementation guidance

Retain semantic column and row headers for the comparison table. Let the table scroll in its own region when comparing requires both dimensions, so surrounding content can still reflow. Name the region where appropriate and preserve access to all columns by keyboard and touch. For a detail layout, repeat each field label alongside its value and keep a way back to the originating row. Test long localized headers, zoom, frozen columns and a narrow viewport with a user trying to compare two readings.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Comparing columns is the main task** Keep semantic table markup with labeled horizontal scrolling and sticky headers where appropriate. A small viewport still limits simultaneous context.
- **Reviewing one record is the main mobile task** Offer a compact detail view with clear labels and a route back to the table. Maintaining two layouts requires shared data and behavior.

## Verification

- Test ties between headers and cells with a screen reader.
- Verify all required information is reachable at narrow width and high zoom.

## Sources

- [WAI-ARIA table pattern](https://www.w3.org/WAI/ARIA/apg/patterns/table/)
- [W3C Understanding Reflow, data table example](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html)

<!-- End generated record details. -->
