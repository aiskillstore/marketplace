# Audit Checklist - Robots Sitemap Validator

## Claimed Capability Coverage

- Whole-site robots block: backed by rule RSV001.
- Malformed or unknown robots directive: backed by rule RSV002.
- Missing Sitemap directive: backed by rule RSV003.
- Sitemap directive points to absent sibling file: backed by rule RSV004.
- Sitemap XML parse failure: backed by rule RSV005.
- loc URL missing scheme or absolute URL: backed by rule RSV006.
- Sitemap count or size guidance issue: backed by rule RSV007.
- Mixed http and https locs: backed by rule RSV008.

Unbacked claims to resolve: none.

## Manual Review Checklist

- Confirm the local files match the production domain.
- Confirm intentional private-area disallow rules.
- Confirm referenced sitemap files exist in the deploy output.
