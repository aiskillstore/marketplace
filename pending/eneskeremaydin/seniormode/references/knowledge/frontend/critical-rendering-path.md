---
id: "critical-rendering-path"
title: "Rendering priority and loading strategy"
category: "frontend"
summary: "Prioritize the first useful content and delay resources that are unnecessary for the initial interaction."
aliases: ["critical rendering path","lcp","render blocking","lazy loading","web performance","ilk ekran açılışı yavaş","sayfa görünmeden önce yüklenen kaynaklar","geç görüntülenen büyük görsel"]
decisions: [{"when":"A small above-the-fold artifact determines perceived load time","use":"Prioritize critical content and measure navigations under realistic cache, CPU and network conditions.","tradeoff":"Priority hints must remain selective and responsive to changes."},{"when":"Large media is below the initial viewport","use":"Defer offscreen assets with known sizes and test scrolling and slow networks.","tradeoff":"Content arrives later and should not jump the layout."}]
checks: ["Measure render timing and layout shifts before and after the change.","Verify the critical content is not deferred and remains usable without optional analytics."]
sources: [{"title":"Google web.dev Largest Contentful Paint","url":"https://web.dev/articles/lcp"},{"title":"Google web.dev browser-level lazy loading","url":"https://web.dev/articles/browser-level-image-lazy-loading"}]
---

<!-- Generated record title. -->
# Rendering priority and loading strategy

## Scenario

A product catalog loads a large gallery and analytics before rendering the main title and hero content.

## Failure modes

Lazy-loading the largest above-the-fold image can delay it. Preloading too much competes for bandwidth and a lab run can miss slow device behavior.

## Explain it simply

Load the content people need first, then fill in the rest as bandwidth and rendering time allow.

## Implementation guidance

Identify the actual largest content element on cold, throttled navigations. Keep its resource discoverable early and avoid deferring it solely because images elsewhere are lazy-loaded. Defer nonessential modules and size visible assets before they arrive to limit layout shifts. Compare field or representative lab measurements for both initial paint and interaction, and remeasure if an optimization changes which element is largest.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A small above-the-fold artifact determines perceived load time** Prioritize critical content and measure navigations under realistic cache, CPU and network conditions. Priority hints must remain selective and responsive to changes.
- **Large media is below the initial viewport** Defer offscreen assets with known sizes and test scrolling and slow networks. Content arrives later and should not jump the layout.

## Verification

- Measure render timing and layout shifts before and after the change.
- Verify the critical content is not deferred and remains usable without optional analytics.

## Sources

- [Google web.dev Largest Contentful Paint](https://web.dev/articles/lcp)
- [Google web.dev browser-level lazy loading](https://web.dev/articles/browser-level-image-lazy-loading)

<!-- End generated record details. -->
