# Adding an adapter

Adapters should be small, testable, public-content-only components.

## 1. Define URL ownership

Create a class derived from sharextract.extractors.base.Extractor.

supports(url) must narrowly match the platform and link shape. Do not claim an entire domain when the adapter only handles one share route.

Set a priority lower than the generic web extractor. Native protocols should generally run before media and HTML fallbacks.

## 2. Choose the least brittle public source

Preference order:

1. documented public API;
2. oEmbed or another open protocol;
3. first-party unauthenticated public JSON;
4. hydration / JSON-LD / semantic HTML;
5. a mature open-source extractor invoked as an optional dependency;
6. browser rendering of the same public page.

Do not introduce login automation, account cookies, CAPTCHA solvers, fingerprint spoofing, WAF bypasses, private signatures, or credential rotation.

## 3. Normalize

Return ExtractedContent.

Always populate source_url, canonical_url, platform, kind, extraction_method, and confidence.

Populate messages for conversations. Preserve media as references rather than downloading by default. Put platform-specific fields inside metadata.

If the endpoint is undocumented, add a warning and identify its stability level.

## 4. Test with fixtures

Do not make ordinary unit tests depend on live platform responses.

Add a sanitized fixture or fake client payload, then assert URL matching, title/body/message extraction, canonical URL, method/confidence, graceful missing-field handling, and absence of credentials in output.

A separate manual/live smoke test may be used before release.

## 5. Register the adapter

Export it from sharextract/extractors/__init__.py and place it in the relevant order in sharextract/router.py.

Never remove the generic fallback solely because a native adapter exists; public implementations change.

## 6. Document the platform

Update references/platform-matrix.md with preferred route, fallback, stability level, and known limitations.

If integrating another open-source project, document its license and use it as an optional dependency or subprocess/API boundary unless license compatibility and maintenance justify tighter coupling.

## Health and fixture requirements

A new router adapter must also add a registry entry and at least one packaged route-contract fixture. Run sharextract --health before submitting a PR. Add a fixed live sample only when it is durable and genuinely public; CI intentionally does not depend on live third-party availability. See references/adapter-health.md.
