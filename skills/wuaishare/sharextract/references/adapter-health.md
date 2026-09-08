# Adapter health and fixture corpus

ShareXtract treats adapter health as a machine-readable engineering contract, not a manually maintained badge.

## Sources of truth

sharextract/registry.py is the authoritative adapter metadata registry. It records each adapter's:

- stable name, platform and normalized kind;
- router priority;
- provenance and stability class;
- expected extraction methods;
- contract fixture IDs;
- baseline verification date/mode;
- optional runtime dependency;
- optional fixed public live-verification sample.

get_capabilities() derives adapter capability rows from this registry. This avoids maintaining a second platform list that can silently drift from health metadata.

## Offline health

Run:

    sharextract --health

or:

    python -m sharextract --health --format markdown

Offline health is deterministic and is the mode used by CI. It checks:

1. the registry entry is represented by the auto router, or by its declared integration;
2. router priority matches registry priority;
3. every declared contract fixture exists in the packaged fixture corpus;
4. fixture adapter/platform/kind/method/priority expectations match the registry;
5. the fixture URL is accepted by the intended adapter's supports() contract;
6. optional dependencies are reported without making the core unhealthy.

A missing optional executable such as yt-dlp is reported as optional_unavailable, not as an adapter failure.

## Live verification

Run all configured public samples:

    sharextract --health --live

Or target one or more adapters:

    sharextract --health --live --adapter x-oembed --adapter chatgpt-share

Live checks use only fixed public sample URLs declared in the registry. They run through the normal sharextract.extract() router and verify both the normalized platform and extraction method. A simple HTTP 200 is not considered sufficient.

A transport/extraction exception gets one confirmation retry by default before live health is marked degraded. Platform or extraction-method drift is treated as a semantic failure immediately rather than being hidden by retries. The report records the number of attempts and any transient errors.

Adapters whose usable public sample depends on transient share context or optional browser execution (for example a Xiaohongshu xsec_token URL, a Kuaishou current Share / Copy Link redirect, or Kuaishou atlas rendering) should not register that context as a fixed live sample. Use deterministic fixtures plus manual live verification with a current official share URL and the required optional runtime instead.

LinkedIn uses a fixed Public post whose anonymous Embed representation is eligible off LinkedIn. Health validates the activity-ID keyed public Embed contract. If LinkedIn changes visibility/embed eligibility or the public DOM structure, that should surface as protocol drift rather than triggering authentication fallback.

Threads, Instagram and Facebook use layered health in the same spirit as Reddit: the fixed expected extraction method is the standard Open Graph content contract, while Meta tokenless oEmbed is an enhancement. Temporary Graph oEmbed failure must not make readable public OG content appear unhealthy.

The default ShareXtract HTTP User-Agent includes the runtime package version. This is part of protocol-drift observability: live diagnostics should identify which ShareXtract version made the request.

Pinterest uses a fixed public Pin whose standard Open Graph contract is stable enough for Live Health. Health validates the requested Pin identity and extraction method; Pinterest-declared canonical URLs are metadata only because they may point at different Pin IDs/content.

Telegram provides a good fixed documented live sample because the Post Widget is an official public embedding surface. Health checks validate the documented widget extraction method rather than any client-side auth/upload helper scripts.

Reddit is a useful example of layered health: the fixed live contract is the documented oEmbed method, while Atom thread RSS is an optional enhancement. RSS rate limiting must not change the adapter's expected extraction method or make the stable oEmbed contract appear unhealthy.

Live verification is intentionally not a required CI gate. Public sites, DNS, regional routing, provider maintenance, and rate limits can all create transient failures unrelated to a code change. CI therefore runs deterministic offline health; live checks are suitable for scheduled monitoring and release validation.

## Status meanings

| Status | Meaning |
| --- | --- |
| healthy | Offline contract checks pass; requested live check also passes when configured. |
| degraded | Offline contract is intact but a requested live sample fails or drifts. |
| unhealthy | Registry/router/fixture contract is inconsistent. |
| optional_unavailable | Core contract passes, but an optional runtime dependency is absent. |

The top-level report is ok when there are no degraded/unhealthy adapters and no fixture-corpus integrity problems.

## Contract fixture corpus

Packaged fixtures live in sharextract/fixtures/.

The first corpus is deliberately a route-contract corpus. Each adapter has a small JSON fixture declaring:

- representative input URL shape;
- intended adapter;
- normalized platform and kind;
- expected router priority;
- allowed extraction methods.

These fixtures catch routing, registry and capability drift without storing large third-party page snapshots.

Provider payload regression remains covered by adapter unit tests. For high-risk undocumented/page-structure adapters, raw/redacted payload fixtures can be added over time when they materially improve regression coverage. They should never contain credentials, private conversations, account cookies, access tokens, or internal reasoning traces.

## Service surfaces

HTTP:

    GET /v1/health/adapters
    GET /v1/health/adapters?adapter=x-oembed
    GET /v1/health/adapters?live=true&adapter=x-oembed

MCP exposes:

    get_sharextract_adapter_health

These surfaces call the same health engine as the CLI.

## Adding an adapter

A new router adapter is incomplete until it has:

1. a registry entry;
2. at least one packaged route-contract fixture;
3. parser/unit coverage;
4. capability metadata derived from the registry;
5. a stability/provenance classification;
6. a live sample only when a durable public sample is appropriate.

The CI Offline adapter health step will fail when the registry/router/fixture contract is inconsistent.
