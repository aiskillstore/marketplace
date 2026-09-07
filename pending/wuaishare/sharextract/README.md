English | [简体中文](README.zh-CN.md)

# ShareXtract

**Protocol-first public share content extraction for AI chats, social posts, media, and the open web.**

ShareXtract accepts a public URL, chooses the highest-fidelity extraction route available, and returns one normalized JSON model with provenance, confidence, warnings, conversation messages, media references, and readable text/Markdown.

It is both a small Python library/CLI and an installable Agent Skill using SKILL.md and agents/openai.yaml.

> Status: **v0.23 alpha**. The architecture and contract are usable today; platform coverage will grow through adapters and community PRs.

Adapter reliability is machine-readable: [Adapter health and fixture corpus](references/adapter-health.md) documents the registry, deterministic offline health gate, packaged contract fixtures, and optional live verification.

## Why this exists

The extraction ecosystem is excellent but fragmented. AI conversation exporters focus on chat shares, media tools focus on video/audio, article extractors focus on readable web pages, and social crawlers tend to be platform-specific.

ShareXtract adds the missing orchestration layer:

**URL → platform detection → best public protocol → safe fallback → normalized content contract**

It deliberately reuses mature tools where they are stronger than custom code.

## Extraction ladder

ShareXtract prefers methods in this order:

1. **Documented public API / oEmbed**
2. **First-party public JSON or hydration data**
3. **JSON-LD / OpenGraph / structured HTML**
4. **Specialized open-source adapter**, for example yt-dlp in metadata-only mode
5. **Readable static HTML**, optionally enhanced by Trafilatura
6. **Public browser rendering** as an optional last resort

It does **not** bypass login, CAPTCHA, paywalls, WAF challenges, private links, or platform access controls.

## Current v0.23 coverage

| Surface | Current method | Status |
| --- | --- | --- |
| DeepSeek public share | First-party public JSON endpoint | Native adapter |
| ChatGPT public share/content | First-party React Router turbo-stream for /share and /s; legacy JSON fallback | Native adapter |
| Claude public share | First-party anonymous chat snapshot JSON | Native adapter |
| Grok public share | Direct public share-data JSON when reachable; anonymous X GrokShare GraphQL browser transport otherwise | Native + optional browser |
| Qwen public share | First-party anonymous share JSON API; final answer phases only | Native adapter |
| Kimi public share | First-party anonymous GetChatShare JSON API | Native adapter |
| Gemini public share | First-party anonymous public share RPC, then web fallback | Native adapter |
| Bluesky public post | Documented AT Protocol public AppView + handle resolution | Native adapter |
| Mastodon-compatible public status | Documented instance REST API | Native adapter |
| Any public JSON URL | Safe HTTP + normalized JSON | Generic |
| Articles / blogs / news | oEmbed, JSON-LD, OG, structured HTML | Generic |
| RSS / Atom feeds | Open-standard XML normalization; feed-entry/media extraction | Built-in standard |
| WebVTT / SRT / TTML | Timed-text cue normalization into transcript metadata/text | Built-in standard |
| HTML caption/subtitle tracks | Discover public captions/subtitles/descriptions track URLs | Generic metadata |
| Web pages with declared feeds | Discover `<link rel=alternate>` RSS/Atom endpoints | Generic metadata |
| Better article readability | Optional Trafilatura | Optional |
| X / Twitter public post | Documented public oEmbed | Native adapter |
| YouTube public video | Documented public oEmbed | Native adapter |
| Vimeo public video | Documented public oEmbed | Native adapter |
| TikTok public video | Documented public oEmbed | Native adapter |
| Reddit public post/thread | Documented public oEmbed + standard Atom thread RSS enhancement | Native adapter + built-in standard |
| Telegram public channel/group post | Official anonymous Post Widget HTML | Native adapter |
| Pinterest public Pin | Standard Open Graph on anonymous public Pin HTML | Native adapter |
| Threads public post | Standard Open Graph content + Meta tokenless oEmbed enhancement | Native adapter |
| Instagram public post / Reel | Standard Open Graph content + Meta tokenless oEmbed enhancement | Native adapter |
| Facebook public post | Standard Open Graph content + Meta tokenless oEmbed enhancement | Native adapter |
| LinkedIn public post | Official anonymous public Embed representation | Native adapter |
| Douyin public video | Anonymous first-party Jingxuan SSR metadata; schema.org fallback | Native metadata-only adapter |
| Xiaohongshu public note | Current official share token/short link → first-party SSR initial state | Native adapter |
| Bilibili public video | First-party public metadata JSON | Native adapter |
| Zhihu public answer | Anonymous first-party Tardis SSR reader; no signed API/cookies | Native adapter |
| Zhihu Zhuanlan article | Embedded first-party initial state; anonymous Tardis SSR fallback | Native adapter |
| Weibo public status | Anonymous first-party mobile PWA JSON; public long-text extend only when needed | Native adapter |
| Instagram / Twitch / SoundCloud / Facebook and other supported media URLs | Optional yt-dlp, metadata-only | Optional |
| Doubao public share | First-party router JSON embedded in public thread/share HTML | Native adapter |
| Kuaishou public video | Current official share context → anonymous first-party PC Apollo SSR | Native metadata-only adapter |
| Kuaishou public atlas/image post | Current official public share page → isolated anonymous browser DOM | Native route + optional browser |

“Supported” never means permanently guaranteed: websites and undocumented endpoints change. The router records the method actually used and falls back when possible.

### LinkedIn public posts

LinkedIn officially allows posts whose visibility is Public/Anyone and whose author settings permit off-LinkedIn embedding to be embedded on third-party sites. ShareXtract consumes that anonymous public Embed representation directly; no LinkedIn login, OAuth token, access token, copied li_at cookie, or browser runtime is required.

The stable identity is the LinkedIn activity ID. ShareXtract accepts normal /posts/...-activity-{id}-... URLs plus /feed/update/urn:li:activity:{id} and public embed forms, then normalizes to the activity feed URL.

The public Embed DOM exposes a stable actor link, commentary, relative publication display, reaction count, comment count, and explicit media/attachment structures. ShareXtract exports only images explicitly contained in feed-images content. Profile images, company logos and generic Open Graph preview images are not treated as post media.

Article/link attachments are normalized separately with attachment URL, title, subtitle and thumbnail. Comment bodies are intentionally not exported; only the public comment count exposed by the Embed is retained.

If LinkedIn does not make a post embeddable outside LinkedIn because of visibility or post-type restrictions, the adapter stops instead of attempting authentication or bypassing that policy.

### Meta tokenless public embeds: Threads, Instagram and Facebook

Meta's official Meta Embeds for WordPress project documents tokenless oEmbed endpoints for Threads, Instagram and Facebook. ShareXtract validates the same anonymous endpoints but treats them as an enhancement layer rather than the only source of content.

For all three platforms, the public page's standard Open Graph representation is the primary readable-content layer. The tokenless oEmbed result contributes official embed HTML and provider metadata. If the oEmbed enhancement is temporarily unavailable, already-public Open Graph content remains usable.

Threads public pages expose post text through og:description. Their og:image can be the account profile image even for a text post, so ShareXtract intentionally records it only as preview metadata and does not export it as post media.

Instagram public Post/Reel pages expose caption, author clues, like/comment display counts, post type and a public thumbnail through Open Graph. The shortcode is the stable identity. If a legacy /p/ URL declares the same shortcode as a Reel, ShareXtract normalizes the route to /reel/ while keeping the shortcode identity. No video stream URL is exported.

Facebook public Post pages expose author, post summary and preview image through Open Graph. pfbid URLs may declare a numeric post canonical; ShareXtract records that declaration but keeps the requested public post identifier as the stable identity unless a stronger identity contract is validated.

No Meta access token, developer app, login cookie or browser runtime is required for these adapters. The oEmbed calls are tokenless and the default HTTP User-Agent now tracks the actual ShareXtract runtime version instead of remaining hard-coded to 0.1.

### Pinterest public Pins

Pinterest public Pin pages expose enough standard Open Graph metadata in anonymous static HTML that ShareXtract does not need Pinterest internal PWS state, historical undocumented pidgets endpoints, API tokens, or browser rendering.

The dedicated Pinterest adapter normalizes the requested Pin ID, title, description, image URL and dimensions, updated time, source link, and Pinterest-declared metadata. Public images are returned directly from i.pinimg.com when present.

Pinterest has one important identity quirk: a public Pin page may declare both link rel=canonical and og:url pointing to a different Pin ID, and fetching that declared Pin can return different title/image content. ShareXtract therefore does not treat Pinterest's declared canonical as the current Pin identity. The requested Pin ID is normalized to https://www.pinterest.com/pin/{id}/ and remains the dedupe identity; Pinterest's declared canonical/OG URL is recorded separately with a mismatch flag when IDs differ.

This keeps the adapter standards-based while avoiding false deduplication across Pinterest's internal content aggregation/canonicalization behavior.

### Telegram public channel/group posts

Telegram officially documents a Post Widget for messages from public channels and groups. ShareXtract reads the same anonymous widget representation directly from the public t.me message URL with embed mode enabled; no Telegram account, Bot Token, login flow, or browser runtime is required.

The widget HTML exposes the public author/channel name, message text, exact datetime, view count, verification state, reactions, link-preview metadata, and public photo backgrounds. ShareXtract normalizes those fields and exports public photo URLs when present.

The widget page also includes client scripts containing auth/upload API configuration and may include temporary audio/video playback details for richer media posts. ShareXtract deliberately ignores those script/API parameters and does not export temporary stream URLs. The adapter only consumes the already-rendered public Post Widget HTML.

### Reddit public posts and threads

Reddit's current anonymous access surface has changed: legacy-style post .json URLs can return HTTP 403 even for public threads. ShareXtract does not work around that restriction and does not require Reddit OAuth, login cookies, or browser automation.

Instead, the Reddit adapter uses the documented public https://www.reddit.com/oembed?url=... endpoint as its stable primary contract. This provides the public post title, author, provider metadata and official embed HTML.

For richer public Thread extraction, ShareXtract then attempts the thread's standard .rss URL, which currently returns Atom. The existing built-in Atom parser is reused rather than introducing a Reddit-specific XML stack. The first Atom entry becomes the post body and later entries become normalized comment messages with author, timestamp and permalink.

Atom RSS is intentionally an enhancement, not a success requirement. If Reddit temporarily returns 429 or otherwise withholds the feed, the documented oEmbed result is preserved and the RSS status is recorded in metadata. The adapter never falls back to the blocked .json surface, OAuth, copied credentials, or authenticated browser state.

### Weibo public statuses

ShareXtract reads public Weibo status URLs through the anonymous first-party mobile PWA JSON route at m.weibo.cn/statuses/show?id={bid}. Desktop weibo.com/{uid}/{bid} and mobile m.weibo.cn/detail/{bid} / status/{bid} URLs are normalized to the same route.

The public PWA endpoint currently requires only the same request semantics used by the anonymous mobile frontend: MWeibo-Pwa: 1, X-Requested-With: XMLHttpRequest, and a mobile-Weibo Referer. No account cookie, login token, browser fingerprint, or authenticated session is used.

Short statuses require one JSON request. Only when the status explicitly reports isLongText=true does ShareXtract request m.weibo.cn/statuses/extend?id={bid} for public longTextContent. If that second public route is temporarily unavailable, the shorter status/show body remains available with a warning.

The adapter normalizes author metadata, timestamp, repost/comment/attitude counts, images, defensive video/page references, and basic retweeted-status metadata. It is explicitly labeled as an undocumented first-party public frontend route and is monitored separately through Adapter Health.

### Zhihu public answers and articles

Zhihu uses different public surfaces for answers and Zhuanlan articles, so ShareXtract keeps them as two independently monitored native adapters.

For public answers, the ordinary question/answer page and /api/v4/answers/{id} can reject anonymous HTTP with 403. ShareXtract does not generate Zhihu's private x-zse signing headers, copy d_c0, or reuse account cookies. Instead, it reads the anonymous first-party Tardis SSR reader at www.zhihu.com/tardis/zm/ans/{answer_id}, which currently exposes the public answer body plus question, author, timestamp, and public interaction counts in window.g_initialProps.

For Zhuanlan articles, ShareXtract first reads js-initialData -> initialState.entities.articles[id] from the anonymous public article page. This exposes full rich-text content, author, topics, created/updated timestamps, public statistics, and image references. If that richer hydration entity is unavailable, the anonymous tardis/zm/art/{id} reader is used as a lower-fidelity fallback.

Both routes strip script/style tracking content from exported rich text and remain explicitly labeled undocumented first-party public structures. They require no login, copied cookies, private signatures, CAPTCHA solving, or browser session state.

### Timed text, captions, and transcripts

ShareXtract directly normalizes public WebVTT, SubRip/SRT, and TTML documents into a transcript contract with cues, normalized timestamps, optional speaker labels, language, cue count, duration, and readable text/Markdown.

Ordinary HTML pages also expose public caption/subtitle/description track declarations through metadata.subtitle_tracks. Track discovery does not fetch those files automatically; the discovered public URL can be passed back to ShareXtract when the transcript itself is needed.

WebVTT NOTE/STYLE/REGION blocks are excluded from transcript text. TTML containing DTD/ENTITY declarations is rejected before parsing. For language-less VTT/SRT files, a clear filename language suffix such as name.en.vtt can be used as a language hint.

### RSS / Atom feeds and discovery

ShareXtract recognizes RSS 2.0, RSS 1.0/RDF, and Atom from the HTTP response and XML root rather than guessing from URL suffixes. Feed title, home/feed URLs, timestamps, authors, entries, summaries/full text, categories, and enclosure/media references are normalized into the same result contract.

Normal HTML pages also expose declared syndication endpoints through `metadata.syndication_feeds` when they include standard `<link rel="alternate" type="application/rss+xml|application/atom+xml">` elements. No second request is made just to discover those links. XML containing DTD/entity declarations is rejected.

## Install as an Agent Skill

The GitHub repository is the canonical Skill source. Agent Skills-compatible installers can install the root `SKILL.md` directly:

```bash
npx skills add wuaishare/sharextract
```

This installs the **Agent Skill instruction layer**. ShareXtract also has a deterministic Python runtime; install the Python package below when the agent needs to execute the CLI/library/MCP/HTTP adapters locally.

See [DISTRIBUTION.md](DISTRIBUTION.md) for marketplace/registry status, ownership verification requirements, and licensing boundaries.

## Install

Core has no required third-party Python dependency:

    git clone https://github.com/wuaishare/sharextract.git
    cd sharextract
    python -m pip install -e .

For stronger readable-page extraction:

    python -m pip install -e ".[web]"

For optional media metadata extraction:

    python -m pip install -e ".[media]"

Everything:

    python -m pip install -e ".[all]"

For public browser fallbacks:

    python -m pip install -e ".[browser]"
    playwright install chromium

You can point browser fallbacks at an existing Chromium/Chrome binary with SHAREXTRACT_BROWSER_EXECUTABLE. Browser fallbacks never import account cookies or logged-in profiles.


## CLI

Normalized JSON:

    sharextract "https://chat.deepseek.com/share/..." --format json

Markdown:

    sharextract "https://example.com/article" --format markdown

Force generic web extraction:

    sharextract "https://example.com/article" --strategy web

Media metadata only:

    sharextract "https://www.youtube.com/watch?v=..." --strategy media

Write to a file:

    sharextract "https://example.com/article" -o result.json

## Python

    from sharextract import extract

    result = extract("https://example.com/article")
    print(result.title)
    print(result.extraction_method)
    print(result.markdown)


### ChatGPT public shares and shared content

ChatGPT currently embeds public `/share/{id}` conversations and newer `/s/{id}` shared content in first-party React Router turbo-stream data inside the public HTML. ShareXtract decodes that structured stream directly with ordinary HTTP and exports only public user/assistant content. The older `/backend-api/share/{id}` JSON route remains a compatibility fallback when available. System/tool/developer nodes and internal reasoning are not exported.

### Documented oEmbed adapters

X public posts, YouTube videos, and Vimeo videos have explicit first-party oEmbed routes. ShareXtract calls those documented endpoints before yt-dlp or generic HTML, preserving author/title/embed metadata and visible X post text without requiring developer tokens.

### Kuaishou public video metadata

Kuaishou's public PC video page currently has two anonymous representations. A normal desktop-browser representation can embed window.__APOLLO_STATE__, while bare direct short-video URLs may intermittently return only site configuration without the requested visionVideoDetail object. Current official Share / Copy Link URLs are therefore the preferred input.

ShareXtract accepts v.kuaishou.com and kuaishou.com/f/ share links, follows their normal public redirect in a single GET, and consumes the resulting public share context only for that response. It then resolves the Apollo relation from $ROOT_QUERY.visionVideoDetail(...) to the exact VisionVideoDetailPhoto and VisionVideoDetailAuthor objects instead of guessing unrelated entities.

The normalized output includes caption, author, publish time, duration, cover image, exact/display like counts, display view count and tags. Bare short-video URLs are still recognized, but when their anonymous Apollo page omits detail ShareXtract stops with guidance to use a fresh official share link.

Kuaishou Apollo state also contains photoUrl, manifests, adaptive representations and temporary CDN MP4 URLs. ShareXtract deliberately excludes all of those stream URLs and returns metadata only. It does not pre-seed did device cookies, call Kuaishou's private GraphQL detail API, generate signatures, solve slider CAPTCHA, or reuse account state.

Because official share context can be transient, Kuaishou intentionally has no fixed Live Health URL. The adapter uses deterministic route-contract fixtures and release-time manual verification with a current official share link.

### Kuaishou public atlas / image posts

Kuaishou atlas/image share pages currently ship an empty static window.INIT_STATE = {} and load the actual public work through normal client-side execution. ShareXtract therefore treats this as a browser-last-resort route rather than pretending the page exposes stable SSR JSON.

With the optional browser extra installed, ShareXtract opens the current public share URL in a fresh anonymous browser context with no imported cookies, storage, or account state. It snapshots only the active .swiper-slide-active .player work after normal page rendering, so recommendation cards below the current work are not mixed into the result.

The normalized result includes the author, caption, topics, visible like/comment/collection counts, avatar, music title, and the public /ufile/atlas/ image URLs. A validated live sample currently exposes 31 original atlas images from the active work.

During ordinary page execution Kuaishou may set its own ephemeral visitor cookies and generate protected request parameters. ShareXtract does not copy, pre-seed, manufacture, export, persist, or replay those values, and does not convert those protected requests into a private API integration. Only the final public DOM and public atlas image URLs are used.

Audio/video playback URLs, protected request URLs, device state, share tokens, and browser storage are excluded from normalized output. This route intentionally remains an optional-browser capability; users without Playwright/Chromium still retain the rest of ShareXtract's core adapters.

### Xiaohongshu public notes

Xiaohongshu public note access currently has an important constraint: a bare /explore/{note_id} URL can be redirected to a security 404 even when the note itself is public. Current official Share / Copy Link URLs carry a transient xsec_token and xsec_source context. ShareXtract consumes that token when it is already present in the user's current public share URL; it never generates, refreshes, signs, or transfers tokens between notes.

Official xhslink.com / xhslink.cn short links are resolved through their public redirect. The resulting tokenized www.xiaohongshu.com/explore/... or /discovery/item/... page is fetched anonymously with the normal ShareXtract HTTP client. No browser session, login cookie, X-s / X-t / X-s-common request signing, or account state is used.

The public page currently embeds a Vue SSR window.__INITIAL_STATE__ object. ShareXtract normalizes title/description, author, note type, publish/update times, IP location, likes/collections/comments/shares, tags, images, and video duration. Bare JavaScript undefined values are safely normalized while parsing the SSR state.

Video-note SSR can also contain temporary MP4/subtitle URLs and nested signed stream data. ShareXtract deliberately does not export those stream URLs. The current share token is preserved only in the canonical public note URL because the page may be inaccessible without it; unrelated tracking parameters are removed.

Because xsec_token values are transient, Xiaohongshu intentionally has no fixed public Live Health sample. The adapter is covered by deterministic routing/fixture tests and can be manually live-verified with a current official share link.

### Douyin public video metadata

Douyin's ordinary desktop video page currently returns an application shell to anonymous non-browser clients, and the historical/public-looking aweme detail/iteminfo JSON routes can return HTTP 200 with an empty body. ShareXtract therefore does not depend on those unstable routes and does not implement private a_bogus/device-signing logic.

Instead, direct public Douyin video IDs are read through the anonymous first-party Jingxuan reader at jingxuan.douyin.com/m/video/{id}. Under an ordinary anonymous mobile-browser representation this page currently embeds both window._SSR_DATA and schema.org VideoObject metadata. ShareXtract prefers the richer SSR result and falls back to VideoObject when the SSR shape changes.

The normalized result includes title/abstract, author, publish time, duration, cover image, play count, digg count, orientation and basic author statistics. v.douyin.com short links are only resolved to discover the public video ID; metadata is still read from the same Jingxuan reader.

The embedded SSR may also contain temporary playback/CDN URLs inside video_model. ShareXtract intentionally parses only safe metadata such as duration and never exports those playback/download stream URLs. The adapter is therefore metadata-only and requires no login cookies, private signatures, CAPTCHA/WAF bypass, or authenticated browser state.

### TikTok documented oEmbed

TikTok public video URLs use TikTok's documented oEmbed API before yt-dlp or generic HTML. The provider's current developer documentation explicitly defines GET /oembed with a TikTok video URL and returns the standard oEmbed object including title, author, embed HTML, and thumbnail metadata.

ShareXtract therefore treats direct www.tiktok.com/@user/video/{id} URLs as a documented native route. It requires no TikTok login, user authorization, developer access token, or browser session. The richer Display API is a separate authenticated product and is not required for public video embedding metadata.

### Bilibili public video metadata

Bilibili video URLs are normalized through the first-party `/x/web-interface/view` JSON route. ShareXtract returns title, author, description, publication time, duration, page metadata, public statistics, and thumbnail references; it does not fetch or download protected video streams.

### Doubao public shares

ShareXtract reads public doubao.com/thread/{id} and doubao.com/share/{id} pages with the standard HTTP client and extracts the first-party Modern Router loader JSON embedded in the public HTML. The payload contains share metadata plus message_snapshot.message_list, so no Doubao login, copied cookies, browser runtime, or secondary private API is required.

Only public text blocks and normal public media variants are normalized. The adapter intentionally does not select image_ori_raw or other raw/no-watermark-specific fields, and internal reasoning/thinking fields are not exported.

### Qwen public shares

ShareXtract reads chat.qwen.ai/s/{id} through Qwen's anonymous first-party /api/v2/chats/share/{id} JSON route. Qwen may expose internal reasoning/thinking fields alongside the public answer; ShareXtract intentionally excludes those fields and normalizes only public user content, final phase=answer blocks, files, model metadata, and timestamps.

### Kimi public shares

Kimi previously embedded share data in server-rendered hydration state, but the current site loads a generic application shell. ShareXtract now calls the same anonymous first-party ChatService/GetChatShare JSON route used by the public share page. The request body contains only the public share ID, so no Kimi login, copied cookies, or browser runtime is required.

### Grok public shares

ShareXtract first attempts Grok's first-party public share-data JSON route with the standard HTTP client. If Grok returns a Cloudflare challenge, ShareXtract does not bypass it. When the optional browser extra is installed, it instead opens the anonymous public X Grok share page and reads only the first-party GrokShare GraphQL JSON response that the page itself requests.

This fallback does not import cookies, copy tokens, attach to a logged-in browser profile, solve challenges, or reuse private session state.

### Claude public shares

ShareXtract reads public claude.ai/share/{uuid} snapshots through Claude's anonymous first-party /api/chat_snapshots/{uuid} JSON endpoint. This avoids the Cloudflare-protected share-page shell entirely and requires no Claude account, cookies, browser automation, or copied session state.

The route is labeled first_party_undocumented_public_json: it is provider-owned and publicly readable for public snapshots, but it is not a documented external developer API contract.

### Gemini public shares

ShareXtract recognizes g.co/gemini/share/{id}, gemini.google.com/share/{id}, and the newer share.gemini.google/{token} short links. The adapter resolves new short links to the canonical share ID, then calls the same unauthenticated first-party share RPC used by Gemini's public frontend. No Google account, cookies, Playwright, or browser session is required.

The RPC is intentionally labeled first_party_undocumented_public_rpc: it is public and provider-owned, but it is not a documented external API contract. The generic public-page fallback remains available if Google changes the frontend implementation.

## Adapter health

Every router adapter is registered in one machine-readable registry with priority, provenance, stability, expected extraction methods, verification metadata, and packaged contract fixtures.

Offline deterministic validation:

    sharextract --health
    sharextract --health --format markdown

Optional real-public-sample verification:

    sharextract --health --live
    sharextract --health --live --adapter x-oembed --adapter chatgpt-share

CI runs offline health only, so provider outages or rate limits do not make ordinary pull requests flaky. Live health runs through the normal extraction router and verifies the actual normalized platform and extraction method, not merely HTTP availability.

HTTP exposes GET /v1/health/adapters and MCP exposes get_sharextract_adapter_health.

## MCP and HTTP/OpenAPI services

The same extraction core can be exposed without duplicating adapter logic.

Install the HTTP API:

    python -m pip install -e ".[service]"
    sharextract-api --host 127.0.0.1 --port 8787

Endpoints:

- GET /health
- GET /v1/capabilities
- GET /v1/health/adapters
- POST /v1/extract
- GET /docs for Swagger UI
- GET /openapi.json

Example request:

    curl -X POST http://127.0.0.1:8787/v1/extract       -H "Content-Type: application/json"       -d '{"url":"https://bsky.app/profile/atproto.com/post/3molpqvzz3d2r"}'

Install the MCP server:

    python -m pip install -e ".[mcp]"
    sharextract-mcp

The default MCP transport is stdio. For a deployable Streamable HTTP endpoint:

    sharextract-mcp --transport streamable-http --host 127.0.0.1 --port 8788 --json-response

The MCP server exposes extract_public_url and list_sharextract_capabilities. Both service layers call the same sharextract.extract() function used by the CLI and Python API.

## Normalized result

A successful extraction returns source and canonical URLs, platform and semantic kind, extraction method and confidence, title/author/body, normalized conversation messages, media references, platform metadata, warnings, and retrieval time.

This contract is intentionally platform-neutral so downstream agents, RAG pipelines, publishers, archives, and knowledge bases do not need to understand every source platform.

## Security and ethics

ShareXtract is public-content-first:

- only HTTP and HTTPS inputs;
- localhost, private, loopback, link-local, reserved, multicast, and unspecified destinations are blocked;
- redirects are revalidated to reduce SSRF risk;
- responses are size-bounded;
- media adapters are metadata-only by default;
- no imported/copied cookies, logged-in account sessions, CAPTCHA solving, WAF bypass, private signatures, or credential collection in the core project.

Platform terms, copyright, privacy rights, robots directives, and local law still apply. Being technically reachable does not grant redistribution rights.

## Agent Skill

The repository root follows the Agent Skills layout:

    sharextract/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── sharextract/
    ├── references/
    └── tests/

An Agent Skills-compatible client can use SKILL.md as the procedural layer while the Python package provides deterministic extraction.

## Architecture

Every new platform should be a small adapter with three responsibilities:

1. detect only URLs it truly understands;
2. extract the highest-fidelity public representation available;
3. map the result into ExtractedContent with explicit provenance and warnings.

If a mature open-source project already solves the hard platform-specific parsing, prefer a thin integration adapter over copying or reimplementing its internals.

See references/adding-adapters.md and references/ecosystem.md.

## Contributing

Platform adapters are ideal community contributions. A good PR adds a narrowly matched adapter, sanitized static fixtures, success/failure tests, provenance/stability notes, and no credentials or access-control bypass.

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues and PRs are welcome.

## License

Apache-2.0. See [LICENSE](LICENSE).
