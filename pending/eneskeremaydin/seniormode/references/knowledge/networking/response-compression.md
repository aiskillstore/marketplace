---
id: "response-compression"
title: "HTTP compression with explicit variants"
category: "networking"
summary: "Reduce response transfer size without overloading the server or mixing encoding variants in caches."
aliases: ["gzip","brotli","content encoding","vary accept encoding","http compression","HTTP yanıtını sıkıştırma","Brotli Gzip","sıkıştırılmış önbellek varyantı"]
decisions: [{"when":"Mostly static text is large enough to benefit","use":"Precompress assets or use controlled gzip or Brotli with correct Vary behavior.","tradeoff":"Build storage or runtime CPU is traded for transfer size."},{"when":"Inputs mix already compressed media or sensitive reflected content","use":"Use selective compression and pick conservative rules at the response boundary.","tradeoff":"Some responses remain larger to avoid cost or unwanted leakage."}]
checks: ["Verify headers, decoding and cache behavior for two supported encodings.","Measure compressed bytes and CPU under realistic payload sizes."]
sources: [{"title":"RFC 9110 HTTP semantics","url":"https://www.rfc-editor.org/rfc/rfc9110"},{"title":"NGINX gzip module","url":"https://nginx.org/en/docs/http/ngx_http_gzip_module.html"}]
---

<!-- Generated record title. -->
# HTTP compression with explicit variants

## Scenario

A static catalog contains hundreds of kilobytes of text, while media assets are already compressed.

## Failure modes

Compressing tiny or already compressed responses can waste CPU. Shared caches need correct variants, and sensitive dynamic responses need a reviewed compression policy.

## Explain it simply

Shrink large text responses when the client can decode them, and avoid doing expensive work for files already compressed.

## Implementation guidance

Choose a minimum response size and supported content types at the response boundary, after measuring CPU versus transferred bytes. Negotiate using Accept-Encoding and preserve shared-cache variants and validator semantics. Keep a policy for responses combining secrets and user-controlled data rather than applying the static-asset setting everywhere. Measure cold and warm compression, confirm that already compressed assets are skipped, and query compressed and identity variants through a cache.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Mostly static text is large enough to benefit** Precompress assets or use controlled gzip or Brotli with correct Vary behavior. Build storage or runtime CPU is traded for transfer size.
- **Inputs mix already compressed media or sensitive reflected content** Use selective compression and pick conservative rules at the response boundary. Some responses remain larger to avoid cost or unwanted leakage.

## Verification

- Verify headers, decoding and cache behavior for two supported encodings.
- Measure compressed bytes and CPU under realistic payload sizes.

## Sources

- [RFC 9110 HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [NGINX gzip module](https://nginx.org/en/docs/http/ngx_http_gzip_module.html)

<!-- End generated record details. -->
